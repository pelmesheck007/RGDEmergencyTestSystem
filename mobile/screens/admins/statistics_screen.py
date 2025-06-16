from kivy.clock import mainthread
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
from kivy.network.urlrequest import UrlRequest
import json

from mobile.screens.base_screen import BaseScreen


class UserStatsScreen(BaseScreen):
    def on_enter(self):
        self.load_stats()

    def load_stats(self):
        url = f"{self.app.api_url}/users/admin/user_stats"  # <-- исправлено
        headers = self._auth_headers()
        UrlRequest(
            url,
            req_headers=headers,
            on_success=self.on_stats_success,
            on_error=lambda req, err: toast("Ошибка загрузки статистики"),
            on_failure=lambda req, res: toast("Ошибка загрузки статистики"),
        )

    @mainthread
    def on_stats_success(self, req, result):
        self.ids.total_users.text = str(result.get("total_users", "?"))
        self.ids.active_users.text = str(result.get("active_users", "?"))
        self.ids.new_users_30d.text = str(result.get("new_users_30d", "?"))

        roles = result.get("roles_count", {})
        roles_text = ", ".join(f"{role.capitalize()}: {count}" for role, count in roles.items())
        self.ids.roles_count.text = roles_text if roles_text else "Нет данных"
        latest = result.get("latest_users", [])
        if latest:
            latest_text = "\n".join(f"{u['name']} — {u['registered']}" for u in latest)
            self.ids.latest_users.text = latest_text

    def _auth_headers(self):
        return {
            'Authorization': f'Bearer {self.app.token}',
            'Content-Type': 'application/json'
        }