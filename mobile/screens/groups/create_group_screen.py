
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.network.urlrequest import UrlRequest
from kivymd.toast import toast
import json

from mobile.screens.base_screen import BaseScreen


class CreateGroupScreen(BaseScreen):
    def create_group(self):
        group_data = {
            "name": self.ids.group_name.text,
            "description": self.ids.group_description.text
        }

        app = App.get_running_app()
        headers = {
            "Authorization": f"Bearer {app.token}",
            "Content-Type": "application/json"
        }

        UrlRequest(
            url=f"{app.api_url}/groups/",
            req_body=json.dumps(group_data),
            req_headers=headers,
            on_success=self.on_success,
            on_error=self.on_error,
            method='POST'
        )

    def go_back(self):
        self.manager.current = "groups"

    def on_success(self, req, result):
        toast("Группа успешно создана!")
        self.manager.current = "groups"

    def on_error(self, req, error):
        toast(f"Ошибка создания группы: {error}")
