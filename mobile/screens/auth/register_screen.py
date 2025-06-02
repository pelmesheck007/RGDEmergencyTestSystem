from kivymd.uix.screen import MDScreen
from kivy.network.urlrequest import UrlRequest
from kivymd.toast import toast
from kivy.properties import StringProperty
import json


class RegisterScreen(MDScreen):
    error_message = StringProperty("")
    api_url = "http://127.0.0.1:8000/auth/register"

    def register(self):
        fio = self.ids.fio.text.strip()
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()
        password_confirm = self.ids.password_confirm.text.strip()

        if not fio or not username or not password:
            self.show_error("Заполните все поля")
            return

        if password != password_confirm:
            self.show_error("Пароли не совпадают")
            return

        self.ids.password.text = ""
        self.ids.password_confirm.text = ""

        data = {
            "fio": fio,
            "username": username,
            "password": password,
            "email": None
        }

        self.ids.register_btn.disabled = True
        toast("Отправка данных...")

        UrlRequest(
            self.api_url,
            req_body=json.dumps(data),
            on_success=self.on_success,
            on_error=self.on_error,
            on_failure=self.on_error,
            req_headers={'Content-Type': 'application/json'},
            method="POST"
        )

    def on_success(self, req, result):
        toast("Регистрация успешна")
        self.ids.register_btn.disabled = False
        self.manager.transition.direction = "right"
        self.manager.current = "login"

    def on_error(self, req, error):
        self.ids.register_btn.disabled = False
        try:
            detail = json.loads(req.result).get('detail', 'Ошибка регистрации')
        except:
            detail = "Ошибка регистрации"
        self.show_error(detail)

    def show_error(self, message):
        self.error_message = message
        toast(message)
