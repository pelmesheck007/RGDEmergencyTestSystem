# mobile/utils/dropdown_manager.py

from kivymd.uix.menu import MDDropdownMenu
from kivymd.toast import toast

class DropdownManager:
    def __init__(self, screen):
        self.screen = screen
        self.theme_menu = None
        self.type_menu = None

    def create_type_menu(self):
        items = [
            {"text": "Все типы", "viewclass": "OneLineListItem", "on_release": lambda x="all": self.set_type_filter(x)},
            {"text": "Обычные", "viewclass": "OneLineListItem", "on_release": lambda x="standard": self.set_type_filter(x)},
            {"text": "Сценарные", "viewclass": "OneLineListItem", "on_release": lambda x="scenario": self.set_type_filter(x)},
        ]
        self.type_menu = MDDropdownMenu(
            caller=self.screen.ids.type_filter,
            items=items,
            width_mult=4
        )

    def open_type_menu(self):
        if not self.type_menu:
            self.create_type_menu()
        self.type_menu.open()

    def set_type_filter(self, test_type):
        self.screen.selected_test_type = test_type
        text = {
            "all": "Все типы",
            "standard": "Обычные",
            "scenario": "Сценарные"
        }.get(test_type, "Все типы")
        self.screen.ids.type_filter.set_item(text)
        if self.type_menu:
            self.type_menu.dismiss()
        self.screen.update_tests_display()

    def open_theme_menu(self):
        self.screen.ids.theme_filter.active = True
        app = self.screen.app

        def on_success(req, result):
            self.screen.ids.theme_filter.active = False

            if not result or not isinstance(result, list):
                toast("Нет доступных тем или ошибка формата данных")
                return

            self.screen.themes = result

            items = [{
                "text": "Все темы",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="": self.set_theme_filter(x)
            }]

            for theme in result:
                title = theme.get("title")
                if title:
                    items.append({
                        "text": title,
                        "viewclass": "OneLineListItem",
                        "on_release": lambda x=theme: self.set_theme_filter(x)
                    })

            self.theme_menu = MDDropdownMenu(
                caller=self.screen.ids.theme_filter,
                items=items,
                width_mult=4
            )
            self.theme_menu.open()

        from kivy.network.urlrequest import UrlRequest
        UrlRequest(
            url=f"{app.api_url}/themes/",
            req_headers={"Authorization": f"Bearer {app.token}"},
            on_success=on_success,
            on_failure=lambda req, err: toast(f"Ошибка загрузки тем: {err}"),
            on_error=lambda req, err: toast(f"Ошибка сети: {err}")
        )

    def set_theme_filter(self, theme):
        title = theme if isinstance(theme, str) else theme.get("title")
        self.screen.selected_theme = title or ""
        self.screen.ids.theme_filter.set_item(title or "Все темы")
        if self.theme_menu:
            self.theme_menu.dismiss()
        self.screen.update_tests_display()
