from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen
from kivy.network.urlrequest import UrlRequest
from kivymd.toast import toast
from kivy.app import App
import json

from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineListItem
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp

from kivymd.uix.list import OneLineListItem, TwoLineRightIconListItem, IconRightWidget, OneLineAvatarListItem

from mobile.screens.base_screen import BaseScreen
from kivymd.uix.list import MDList, OneLineAvatarListItem, IconRightWidget

class EditGroupScreen(BaseScreen):
    def on_pre_enter(self):
        group = App.get_running_app().current_group
        self.ids.group_name.text = group.get("name", "")
        self.ids.group_description.text = group.get("description", "")
        self.load_members()

    def save_changes(self):
        group = App.get_running_app().current_group
        data = {
            "name": self.ids.group_name.text.strip(),
            "description": self.ids.group_description.text.strip(),
        }

        headers = {
            "Authorization": f"Bearer {App.get_running_app().token}",
            "Content-Type": "application/json"
        }

        UrlRequest(
            url=f"{App.get_running_app().api_url}/groups/{group['id']}",
            req_body=json.dumps(data),
            req_headers=headers,
            method='PUT',
            on_success=self.on_success,
            on_error=self.on_error
        )

    def go_back(self):
        self.manager.current = "groups"

    def on_success(self, req, result):
        toast("Изменения сохранены")
        self.manager.current = "groups"

    def on_error(self, req, error):
        toast("Ошибка сохранения")


    def load_members(self):
        group_id = App.get_running_app().current_group['id']
        headers = {
            "Authorization": f"Bearer {App.get_running_app().token}"
        }

        def on_success(req, result):
            self.ids.members_list.clear_widgets()
            for user in result:
                item = TwoLineRightIconListItem(
                    text=user['full_name'],
                    secondary_text=user['username']
                )
                icon = IconRightWidget(icon="delete", on_release=lambda x, uid=user["id"]: self.remove_member(uid))
                item.add_widget(icon)
                self.ids.members_list.add_widget(item)

        UrlRequest(
            f"{App.get_running_app().api_url}/groups/{group_id}/members/",
            req_headers=headers,
            on_success=on_success,
            on_error=lambda *a: toast("Ошибка загрузки участников"),
            method='GET'
        )

    def remove_member(self, user_id):
        group_id = App.get_running_app().current_group['id']
        headers = {
            "Authorization": f"Bearer {App.get_running_app().token}"
        }

        def on_success(req, result):
            toast("Участник удалён")
            self.load_members()

        UrlRequest(
            f"{App.get_running_app().api_url}/groups/{group_id}/members/{user_id}",
            req_headers=headers,
            method="DELETE",
            on_success=on_success,
            on_error=lambda *a: toast("Ошибка удаления участника")
        )

    def add_member(self):
        username = self.ids.new_member_username.text.strip()
        if not username:
            toast("Введите имя пользователя")
            return

        group_id = App.get_running_app().current_group['id']
        headers = {
            "Authorization": f"Bearer {App.get_running_app().token}",
            "Content-Type": "application/json"
        }

        data = {"username": username}

        def on_success(req, res):
            toast("Пользователь добавлен")
            self.ids.new_member_username.text = ""  # очищаем поле
            self.load_members()

        UrlRequest(
            f"{App.get_running_app().api_url}/groups/{group_id}/add_member/",
            req_body=json.dumps(data),
            req_headers=headers,
            on_success=on_success,
            on_error=lambda *a: toast("Ошибка добавления участника"),
            method='POST'
        )


    def add_member_by_id(self, user_id):
        group_id = App.get_running_app().current_group['id']
        headers = {
            "Authorization": f"Bearer {App.get_running_app().token}",
            "Content-Type": "application/json"
        }
        data = {"user_id": user_id}  # возможно, сервер ожидает именно user_id, уточни API

        def on_success(req, res):
            toast("Пользователь добавлен")
            self.load_members()

        def on_error(req, error):
            toast("Ошибка добавления участника")

        UrlRequest(
            f"{App.get_running_app().api_url}/groups/{group_id}/add_member/",
            req_body=json.dumps(data),
            req_headers=headers,
            on_success=on_success,
            on_error=on_error,
            method='POST'
        )

    def open_add_member_dialog(self):
        headers = {
            "Authorization": f"Bearer {App.get_running_app().token}"
        }
        url = f"{App.get_running_app().api_url}/users/"

        def on_success(req, result):
            # Создаём вертикальный layout для списка
            menu_layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(8),
                padding=dp(8),
                size_hint_y=None
            )
            menu_layout.bind(minimum_height=menu_layout.setter("height"))

            # Оборачиваем layout в ScrollView с фиксированной высотой
            scroll = ScrollView(
                size_hint=(1, None),
                height=dp(300)
            )
            scroll.add_widget(menu_layout)

            for user in result:
                def on_select(_, user_id=user["id"]):
                    self.add_member_by_id(user_id)
                    self.add_member_dialog.dismiss()

                item = OneLineListItem(text=f"{user['full_name']} ({user['username']})")
                item.bind(on_release=on_select)
                menu_layout.add_widget(item)

            self.add_member_dialog = MDDialog(
                title="Выберите пользователя для добавления",
                type="custom",
                content_cls=scroll,
                buttons=[
                    MDFlatButton(text="Отмена", on_release=lambda x: self.add_member_dialog.dismiss())
                ]
            )
            self.add_member_dialog.open()

        def on_error(req, error):
            toast("Ошибка загрузки пользователей")

        UrlRequest(
            url,
            req_headers=headers,
            on_success=on_success,
            on_error=on_error,
            method="GET"
        )