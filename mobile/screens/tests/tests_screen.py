from datetime import datetime

from kivy.app import App
from kivy.properties import ListProperty, ObjectProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivymd.toast import toast
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import IconLeftWidget
from kivy.network.urlrequest import UrlRequest

from mobile.screens.base_screen import BaseScreen

from kivymd.uix.list import TwoLineAvatarIconListItem

from mobile.screens.tests.dropdown_manager import DropdownManager


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_title = "Тесты"
        self.show_menu_button = True
        self.selected_theme = ""
        self.selected_test_type = "all"
        self.dropdown_manager = DropdownManager(self)

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
                # СЛЕВА: кнопка "Удалить" — добавлена первой
                MDFlatButton(
                    text="УДАЛИТЬ",
                    theme_text_color="Custom",
                    text_color=self.app.rjd_dark_red,
                    on_release=self.confirm_delete_test
                ),
                # СПРАВА: кнопки "Закрыть" и "Начать тест"
                MDFlatButton(
                    text="ЗАКРЫТЬ",
                    theme_text_color="Custom",
                    text_color=self.app.rjd_dark_red,
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="НАЧАТЬ ТЕСТ",
                    theme_text_color="Custom",
                    text_color=self.app.rjd_dark_red,
                    on_release=self.start_test
                )            ]
        )
        self.dialog.open()

    def confirm_delete_test(self, *args):
        """Подтверждение перед удалением теста"""
        self.dialog.dismiss()
        self.confirm_dialog = MDDialog(
            title="Удаление теста",
            text="Вы уверены, что хотите удалить тест?",
            buttons=[
                MDFlatButton(
                    text="ОТМЕНА",
                    on_release=lambda x: self.confirm_dialog.dismiss()
                ),
                MDFlatButton(
                    text="ПОДТВЕРДИТЬ",
                    text_color=self.app.rjd_dark_red,
                    on_release=lambda x: self._execute_deletion()
                )
            ]
        )
        self.confirm_dialog.open()

    def _execute_deletion(self):
        """Подтвердить и выполнить удаление"""
        self.confirm_dialog.dismiss()
        self.delete_selected_test()

    def delete_test(self, *args):
        test_id = self.selected_test.get("id")
        if not test_id:
            return

        import requests
        try:
            response = requests.delete(f"{self.app.api_base_url}/tests/{test_id}")
            if response.status_code == 200:
                Snackbar(text="Тест удалён").open()
                self.confirm_dialog.dismiss()
                self.refresh_test_list()  # обновление списка
            else:
                Snackbar(text="Ошибка при удалении").open()
        except Exception as e:
            Snackbar(text=f"Ошибка: {e}").open()


    def delete_selected_test(self):
        """Удалить выбранный тест"""
        test_id = self.selected_test.get('id')
        if not test_id:
            self.show_error("ID теста не найден")
            return

        if not hasattr(self.app, 'token') or not self.app.token:
            self.show_error("Требуется авторизация")
            return

        headers = {
            'Authorization': f'Bearer {self.app.token}',
            'Content-Type': 'application/json'
        }

        def on_success(req, result):
            Snackbar(text="Тест удалён успешно").open()
            Clock.schedule_once(lambda dt: self.load_tests(), 0)

        def on_error(req, error):
            self.show_error(f"Ошибка удаления: {error}")

        def on_failure(req, result):
            self.show_error("Не удалось удалить тест")

        UrlRequest(
            f'{self.app.api_url}/tests/{test_id}',
            on_success=on_success,
            on_error=on_error,
            on_failure=on_failure,
            req_headers=headers,
            req_body=None,
            method='DELETE',
            timeout=10
        )

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


    def load_tests(self):
        """Загрузка тестов с сервера"""
        self.show_loading(True)
        if not hasattr(self.app, 'token') or not self.app.token:
            self.show_error("Требуется авторизация")
            self.show_loading(False)
            return

        headers = {
            'Authorization': f'Bearer {self.app.token}',
            'Content-Type': 'application/json'
        }

    def open_type_dropdown(self):
        self.dropdown_manager.open_type_menu()

    def open_theme_dropdown(self):
        self.dropdown_manager.open_theme_menu()



