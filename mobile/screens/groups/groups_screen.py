from kivy.uix.screenmanager import Screen
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem, TwoLineRightIconListItem, IconRightWidget
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
        self.groups = result  # сохраняем для повторного использования
        for group in result:
            item = TwoLineRightIconListItem(
                text=group["name"],
                secondary_text=f"ID: {group['id']}",
                on_release=lambda x, g=group: self.open_group(g)
            )

            delete_icon = IconRightWidget(
                icon="delete",
                on_release=lambda x, g=group: self.confirm_delete_group(g)
            )

            item.add_widget(delete_icon)
            self.ids.groups_box.add_widget(item)

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

    def confirm_delete_group(self, group):
        self.dialog = MDDialog(
            title="Удалить группу?",
            text=f"Вы уверены, что хотите удалить группу '{group['name']}'?",
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="Удалить", on_release=lambda x: self.delete_group(group)),
            ],
        )
        self.dialog.open()

    def delete_group(self, group):
        self.dialog.dismiss()
        headers = {
            "Authorization": f"Bearer {App.get_running_app().token}",
            "Content-Type": "application/json"
        }

        UrlRequest(
            url=f"{App.get_running_app().api_url}/groups/{group['id']}",
            req_headers=headers,
            method='DELETE',
            on_success=lambda req, res: self.on_group_deleted(group),
            on_error=self.on_delete_error
        )

    def on_group_deleted(self, group):
        toast(f"Группа '{group['name']}' удалена")
        self.load_groups()

    def on_delete_error(self, req, error):
        toast("Ошибка при удалении группы")
