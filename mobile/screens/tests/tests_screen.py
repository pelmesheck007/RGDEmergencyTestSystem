from datetime import datetime

from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivymd.toast import toast
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget

from mobile.screens.base_screen import BaseScreen
from kivy.metrics import dp

from kivymd.uix.list import TwoLineAvatarIconListItem

class TestListItem(TwoLineAvatarIconListItem):
    test_data = ObjectProperty(None)
    icon = StringProperty("file-document")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._icon_widget = IconLeftWidget(icon=self.icon)
        self.add_widget(self._icon_widget)


class TestsScreen(BaseScreen):
    tests_list = ListProperty([])
    scenario_tests_list = ListProperty([])
    selected_test = ObjectProperty(None, allownone=True)
    selected_theme = StringProperty("")
    theme_menu = ObjectProperty(None)
    type_menu = ObjectProperty(None)
    no_tests_message = StringProperty("Загрузка тестов...")
    can_create_test = BooleanProperty(False)
    all_tests_list = ListProperty([])
    selected_test_type = StringProperty("all")  # all, standard, scenario

    test_themes = ListProperty(["Аварийные ситуации", "Отказ сигнализации", "Охрана труда"])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_title = "Тесты"
        self.show_menu_button = True
        Clock.schedule_once(self._create_theme_menu, 0)
        self.selected_theme = ""
        self.selected_test_type = "all"

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.can_create_test = getattr(self.app, "user_role", "") in ("admin", "teacher")
        self.load_all_tests()

    def load_all_tests(self):
        self.show_loading(True)
        self.load_standard_tests()
        self.load_scenario_tests()

    def create_test(self, *args):
        self.manager.current = "create_test"

    def show_loading(self, state):
        self.loading = state
        if hasattr(self.ids, 'loading_spinner'):
            self.ids.loading_spinner.active = state

    def load_standard_tests(self):
        headers = self._auth_headers()
        UrlRequest(
            f'{self.app.api_url}/tests/',
            on_success=self.on_tests_load_success,
            on_error=self.on_tests_load_error,
            on_failure=self.on_tests_load_error,
            req_headers=headers,
            timeout=10
        )

    def load_scenario_tests(self):
        headers = self._auth_headers()
        UrlRequest(
            f'{self.app.api_url}/scenario-tests/',
            on_success=self.on_scenario_tests_load_success,
            on_error=self.on_tests_load_error,
            on_failure=self.on_tests_load_error,
            req_headers=headers,
            timeout=10
        )

    def _auth_headers(self):
        if not hasattr(self.app, 'token') or not self.app.token:
            return {}
        return {'Authorization': f'Bearer {self.app.token}', 'Content-Type': 'application/json'}

    def on_tests_load_success(self, req, result):
        self.tests_list = result if isinstance(result, list) else []
        self.update_tests_display()
        self.show_loading(False)

    def on_scenario_tests_load_success(self, req, result):
        self.scenario_tests_list = result if isinstance(result, list) else []
        self.update_tests_display()
        self.show_loading(False)

    def on_tests_load_error(self, req, error):
        self.show_loading(False)
        self.no_tests_message = "Не удалось загрузить тесты"
        Snackbar(text="Ошибка загрузки тестов").open()

    from datetime import datetime

    def update_tests_display(self):
        self.ids.tests_container.clear_widgets()

        def matches_theme(t):
            return not self.selected_theme or t.get("theme") == self.selected_theme

        def matches_type(t):
            if self.selected_test_type == "standard":
                return "test_name" in t
            elif self.selected_test_type == "scenario":
                return "title" in t
            return True

        all_tests = self.tests_list + self.scenario_tests_list
        filtered = [t for t in all_tests if matches_theme(t) and matches_type(t)]

        def get_date(t):
            try:
                return datetime.strptime(t.get("created_at", ""), "%Y-%m-%dT%H:%M:%S")
            except:
                return datetime.min

        filtered.sort(key=get_date, reverse=True)

        if not filtered:
            self.ids.tests_container.add_widget(MDLabel(
                text=self.no_tests_message,
                halign="center",
                theme_text_color="Secondary"
            ))
            return

        for test in filtered:
            is_scenario = "title" in test
            item = TestListItem(
                text=test.get("title" if is_scenario else "test_name", "Без названия"),
                secondary_text=f"Тема: {test.get('theme', '—')}",
                icon="script-text-outline" if is_scenario else "file-document",
                test_data=test,
                on_release=lambda _, t=test: (
                    self.show_scenario_test_details(t) if is_scenario else self.show_test_details(t)
                )
            )
            self.ids.tests_container.add_widget(item)

    def _create_type_menu(self, *args):
        items = [
            {"text": "Все типы", "viewclass": "OneLineListItem", "on_release": lambda x="all": self.set_type_filter(x)},
            {"text": "Обычные", "viewclass": "OneLineListItem",
             "on_release": lambda x="standard": self.set_type_filter(x)},
            {"text": "Сценарные", "viewclass": "OneLineListItem",
             "on_release": lambda x="scenario": self.set_type_filter(x)},
        ]
        self.type_menu = MDDropdownMenu(
            caller=self.ids.type_filter,
            items=items,
            width_mult=4
        )



    def set_theme_filter(self, theme):
        self.selected_theme = theme
        self.ids.theme_filter.text = theme or "Все темы"
        if self.theme_menu:
            self.theme_menu.dismiss()
        self.update_tests_display()

    def show_test_details(self, test_data):
        self.selected_test = test_data
        self.dialog = MDDialog(
            title=test_data.get('test_name', 'Инфо'),
            text=self._format_test_details(test_data),
            buttons=[
                MDFlatButton(text="НАЧАТЬ", text_color=self.app.rjd_dark_red, on_release=self.start_test),
                MDFlatButton(text="ЗАКРЫТЬ", on_release=lambda x: self.dialog.dismiss())
            ]
        )
        self.dialog.open()

    def show_scenario_test_details(self, test_data):
        self.selected_test = test_data
        self.dialog = MDDialog(
            title=test_data.get('title', 'Сценарий'),
            text=test_data.get('description', 'Описание отсутствует'),
            buttons=[
                MDFlatButton(text="НАЧАТЬ", text_color=self.app.rjd_dark_red, on_release=self.start_scenario_test),
                MDFlatButton(text="ЗАКРЫТЬ", on_release=lambda x: self.dialog.dismiss())
            ]
        )
        self.dialog.open()

    def start_test(self, *args):
        self.dialog.dismiss()
        self.app.current_test_id = self.selected_test.get("id")
        self.manager.current = "test_taking"

    def start_scenario_test(self, *args):
        self.dialog.dismiss()
        self.app.current_scenario_id = self.selected_test.get("id")
        self.manager.current = "scenario_taking"

    def _format_test_details(self, test_data):
        fields = []
        if test_data.get("description"):
            fields.append(f"Описание: {test_data['description']}")
        if test_data.get("time_limit"):
            fields.append(f"Лимит времени: {test_data['time_limit']} мин")
        if test_data.get("passing_score"):
            fields.append(f"Проходной балл: {test_data['passing_score']}%")
        if test_data.get("theme"):
            fields.append(f"Тема: {test_data['theme']}")
        if test_data.get("attempts_limit"):
            fields.append(f"Попыток: {test_data['attempts_limit']}")
        if test_data.get("created_at"):
            fields.append(f"Создано: {test_data['created_at'].replace('T', ' ').split('.')[0]}")
        return "\n".join(fields) if fields else "Информация отсутствует"

    def _create_theme_menu(self, *args):
        themes = self._collect_themes()
        items = [{"text": "Все темы", "viewclass": "OneLineListItem",
                  "on_release": lambda x="": self.set_theme_filter(x)}]
        for theme in themes:
            items.append({
                "text": theme,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=theme: self.set_theme_filter(x)
            })

        self.theme_menu = MDDropdownMenu(
            caller=self.ids.theme_filter,
            items=items,
            width_mult=4
        )

    def set_type_filter(self, t_type):
        self.selected_test_type = t_type
        self.ids.type_filter.text = {
            "all": "Все типы",
            "standard": "Обычные",
            "scenario": "Сценарные"
        }.get(t_type, "Все типы")
        if self.type_menu:
            self.type_menu.dismiss()
        self.update_tests_display()

    def _collect_themes(self):
        all_tests = self.tests_list + self.scenario_tests_list
        themes = sorted(set(t.get("theme", "") for t in all_tests if t.get("theme")))
        return themes

    def load_themes(self):
        app = App.get_running_app()

        def on_themes_loaded(req, result):
            self.ids.theme_loader.active = False

            if not result or not isinstance(result, list):
                toast("Нет доступных тем или ошибка формата данных")
                return

            print("Полученные темы с сервера:", result)
            self.themes = result

            menu_items = [{
                "text": "Все темы",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="": self.set_selected_theme(x)
            }]

            for theme in self.themes:
                title = theme.get("title")
                if title:
                    menu_items.append({
                        "text": title,
                        "viewclass": "OneLineListItem",
                        "on_release": lambda x=theme: self.set_selected_theme(x)
                    })

            self.theme_menu = MDDropdownMenu(
                caller=self.ids.theme_filter,
                items=menu_items,
                width_mult=4
            )

        self.ids.theme_loader.active = True

        UrlRequest(
            url=f"{app.api_url}/themes/",
            req_headers={"Authorization": f"Bearer {app.token}"},
            on_success=on_themes_loaded,
            on_failure=lambda req, err: toast(f"Ошибка загрузки тем: {err}"),
            on_error=lambda req, err: toast(f"Ошибка сети: {err}")
        )

    def open_theme_dropdown(self):
        if hasattr(self, 'theme_menu'):
            self.theme_menu.open()
        else:
            self.load_themes()

    def set_selected_theme(self, theme):
        self.selected_theme = theme if isinstance(theme, str) else theme.get("title")
        self.ids.theme_filter.set_item(self.selected_theme or "Все темы")
        self.theme_menu.dismiss()
        self.update_tests_display()

    def open_type_dropdown(self):
        if hasattr(self, 'type_menu'):
            self.type_menu.open()
            return

        menu_items = [
            {
                "text": "Все типы",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="all": self.set_test_type_filter(x)
            },
            {
                "text": "Обычные",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="standard": self.set_test_type_filter(x)
            },
            {
                "text": "Сценарные",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="scenario": self.set_test_type_filter(x)
            },
        ]

        self.type_menu = MDDropdownMenu(
            caller=self.ids.type_filter,
            items=menu_items,
            width_mult=3
        )
        self.type_menu.open()

    def set_test_type_filter(self, test_type):
        self.selected_test_type = test_type
        text = "Все типы" if test_type == "all" else test_type.capitalize()
        self.ids.type_filter.set_item(text)
        self.type_menu.dismiss()
        self.update_tests_display()




