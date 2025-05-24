from kivy.uix.screenmanager import Screen
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.list import OneLineListItem
from kivymd.toast import toast
from kivy.app import App

from mobile.screens.base_screen import BaseScreen
from mobile.screens.widgets.menu.main_menu import RoleMenu


class GroupsScreen(BaseScreen):
    screen_title = "Учебные группы"

    def on_pre_enter(self):
        self.load_groups()

    def load_groups(self):
        self.ids.groups_box.clear_widgets()
        headers = {
            "Authorization": f"Bearer {App.get_running_app().token}",
            "Content-Type": "application/json"
        }

        UrlRequest(
            url=f"{App.get_running_app().api_url}/groups/",
            req_headers=headers,
            on_success=self.on_success,
            on_error=self.on_error,
            method='GET'
        )

    def on_success(self, req, result):
        for group in result:
            self.ids.groups_box.add_widget(
                OneLineListItem(text=group['name'], on_release=lambda x, g=group: self.open_group(g))
            )

    def open_group(self, group):
        App.get_running_app().current_group = group
        self.manager.current = "edit_group"

    def on_error(self, req, error):
        toast("Ошибка загрузки групп")

    def open_menu(self):
        role = getattr(App.get_running_app(), "user_data", {}).get("role", None)
        if role:
            RoleMenu(self.ids["menu_button"], role).open()
        else:
            self.show_error("Роль пользователя не определена.")

