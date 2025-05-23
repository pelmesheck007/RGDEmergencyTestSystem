from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
import json
import logging
from screens.base_screen import BaseScreen
from kivy.properties import StringProperty, BooleanProperty


class ProfileScreen(BaseScreen):
    username = StringProperty("")
    full_name = StringProperty("")
    email = StringProperty("")
    edit_mode = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_data = {}
        self._save_request = None

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        if hasattr(self.app, 'user_data') and self.app.user_data:
            self._load_profile_data(self.app.user_data)
        self.screen_title = "Профиль"

    def _load_profile_data(self, user_data):
        """Загрузка данных профиля"""
        self.username = user_data.get('username', '')
        self.full_name = user_data.get('full_name', '')
        self.email = user_data.get('email', '')
        self.original_data = {
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email
        }

    def toggle_edit_mode(self):
        """Переключение режима редактирования"""
        self.edit_mode = not self.edit_mode
        if not self.edit_mode:
            self._cancel_edits()

    def _cancel_edits(self):
        """Отмена изменений"""
        self.username = self.original_data['username']
        self.full_name = self.original_data['full_name']
        self.email = self.original_data['email']

    def save_profile(self):
        """Инициирование сохранения профиля"""
        if self._save_request:
            self._save_request.cancel()

        self.show_loading(True)
        self._save_request = Clock.schedule_once(
            lambda dt: self._perform_save(), 0.1
        )

    def _perform_save(self):
        """Отправка данных на сервер"""
        try:
            if not hasattr(self.app, 'api_url') or not self.app.api_url:
                raise ValueError("API URL не настроен")
            if not hasattr(self.app, 'token') or not self.app.token:
                raise ValueError("Требуется авторизация")

            update_data = {
                "username": self.username,
                "full_name": self.full_name,
                "email": self.email
            }

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.app.token}'
            }

            UrlRequest(
                f'{self.app.api_url}/users/me',
                on_success=self._save_success,
                on_error=self._handle_save_error,
                on_failure=self._handle_save_error,
                req_headers=headers,
                req_body=json.dumps(update_data),
                method='PATCH',
                timeout=10
            )

        except Exception as e:
            self.show_loading(False)
            self.show_error(f"Ошибка: {str(e)}")
            self._cancel_edits()

    def _save_success(self, req, result):
        """Обработка успешного сохранения"""
        self.show_loading(False)
        self.show_success("Профиль успешно сохранен")
        self.original_data = {
            'username': result.get('username', ''),
            'full_name': result.get('full_name', ''),
            'email': result.get('email', '')
        }
        # Обновляем данные в приложении
        if hasattr(self.app, 'user_data'):
            self.app.user_data.update(self.original_data)
        self.edit_mode = False

    def _handle_save_error(self, req, error):
        """Обработка ошибок сохранения"""
        self.show_loading(False)
        error_msg = "Неизвестная ошибка"
        if isinstance(error, dict):
            error_msg = error.get('detail', str(error))
        elif hasattr(req, 'resp_status'):
            if req.resp_status == 401:
                error_msg = "Требуется авторизация"
            elif req.resp_status == 400:
                error_msg = "Некорректные данные"

        self.show_error(f"Ошибка сохранения: {error_msg}")
        self._cancel_edits()