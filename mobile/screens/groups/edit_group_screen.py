from kivy.uix.screenmanager import Screen
from kivy.network.urlrequest import UrlRequest
from kivymd.toast import toast
from kivy.app import App
import json

from kivymd.uix.list import OneLineListItem, TwoLineRightIconListItem, IconRightWidget

from mobile.screens.base_screen import BaseScreen

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
            self.ids.new_member_username.text = ""
            self.load_members()

        UrlRequest(
            f"{App.get_running_app().api_url}/groups/{group_id}/add_member/",
            req_body=json.dumps(data),
            req_headers=headers,
            on_success=on_success,
            on_error=lambda *a: toast("Ошибка добавления участника"),
            method='POST'
        )

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