import logging

from kivy.network.urlrequest import UrlRequest
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivymd.toast import toast
from kivy.clock import Clock
import json


class LoginScreen(MDScreen):
    error_message = StringProperty("")
    api_url = "http://127.0.0.1:8000/auth/login"

    def login(self):
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()
        logging.info(f"Попытка входа пользователя: {username}")

        if not username or not password:
            self.show_error("Введите логин и пароль")
            return
        self.ids.login_btn.disabled = True
        self.error_message = "Авторизация..."
        login_data = {
            "username": username,
            "password": password
        }

        try:
            UrlRequest(
                self.api_url,
                req_body=json.dumps(login_data),
                on_success=self.handle_login_response,
                on_error=self.handle_login_error,
                req_headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                timeout=10,
                method='POST'
            )
        except Exception as e:
            self.handle_login_error(None, str(e))

    def handle_login_response(self, req, result):
        self.ids.login_btn.disabled = False
        if 'user' in result:
            user = result['user']
            logging.info(f"Успешный вход: {user['username']}, роль: {user['role']}")

        if not result:
            self.show_error("Пустой ответ сервера")
            return

        if 'access_token' not in result or 'user' not in result:
            self.show_error("Неверный формат ответа сервера")
            return

        app = MDApp.get_running_app()
        app.token = result['access_token']
        app.user_data = result['user']
        app.user_id = result['user']['id']

        # Явное обновление данных перед переходом
        main_screen = app.root.get_screen('main')
        main_screen.username = result['user']['username']
        main_screen.role = result['user']['role']
        main_screen.full_name = result['user'].get('full_name', '')

        # Переход с анимацией
        app.root.current = 'main'
        app.root.transition.direction = 'left'

    def handle_login_error(self, req, error):
        error_msg = self.extract_error_message(req, error)
        logging.error(f"Ошибка входа: {error_msg}")

        self.ids.login_btn.disabled = False


        error_msg = "Ошибка сервера"
        try:
            if isinstance(error, str):
                error_msg = error
            elif req and req.resp_status:
                if req.resp_status == 404:
                    error_msg = "Сервер не найден (404)"
                elif req.resp_status == 400:
                    # Пытаемся получить детальное сообщение об ошибке
                    try:
                        error_detail = json.loads(req.result).get('detail', 'Неверные данные')
                        error_msg = f"Ошибка: {error_detail}"
                    except:
                        error_msg = "Неверные данные"
                else:
                    error_msg = f"Ошибка HTTP {req.resp_status}"
        except Exception as e:
            print(f"Ошибка обработки ошибки: {e}")

        self.show_error(error_msg)
        self.ids.password.text = ""



    def show_error(self, message):
        self.error_message = message
        toast(message)

    def go_to_register(self):
        self.manager.transition.direction = "left"
        self.manager.current = "register"
