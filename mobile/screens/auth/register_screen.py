from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.screen import MDScreen
from kivy.network.urlrequest import UrlRequest
from kivymd.toast import toast
from kivy.properties import StringProperty
import json


from kivymd.uix.screen import MDScreen
from kivy.network.urlrequest import UrlRequest
from kivymd.toast import toast
import json


class RegisterScreen(MDScreen):
    api_url = "http://127.0.0.1:8000/auth/register"  # или твой IP, если на телефоне

    def register(self):
        fio = self.ids.fio.text.strip()
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()
        password_confirm = self.ids.password_confirm.text.strip()

        if not fio or not username or not password:
            toast("Заполните все поля")
            return

        if password != password_confirm:
            toast("Пароли не совпадают")
            return

        data = {
            "fio": fio,
            "username": username,
            "password": password,
            "email": None  # если добавишь поле email — передавай сюда
        }

        self.ids.password.text = ""
        self.ids.password_confirm.text = ""

        UrlRequest(
            self.api_url,
            req_body=json.dumps(data),
            on_success=self.on_success,
            on_error=self.on_error,
            req_headers={'Content-Type': 'application/json'},
            method="POST"
        )

    def on_success(self, req, result):
        toast("Регистрация успешна")
        self.manager.current = "login"

    def on_error(self, req, error):
        try:
            detail = json.loads(req.result).get('detail', 'Ошибка регистрации')
            toast(detail)
        except Exception:
            toast("Ошибка регистрации")
