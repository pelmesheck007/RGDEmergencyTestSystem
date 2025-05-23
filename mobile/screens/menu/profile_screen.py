from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
import json
import logging
from mobile.screens.base_screen import BaseScreen
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.core.window import Window
import os

from kivy.properties import StringProperty

# уже есть: avatar_url = StringProperty("")


class ProfileScreen(BaseScreen):
    username = StringProperty("")
    full_name = StringProperty("")
    email = StringProperty("")
    edit_mode = BooleanProperty(False)
    registration_date = StringProperty("")
    avatar_url = StringProperty("")
    is_active = BooleanProperty(True)
    role = StringProperty("")



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
        self.username = user_data.get('username', '')
        self.full_name = user_data.get('full_name', '')
        self.email = user_data.get('email', '')
        self.registration_date = user_data.get('registration_date', '')
        self.avatar_url = user_data.get('avatar_url', '')
        self.is_active = user_data.get('is_active', True)
        self.role = user_data.get('role', '')

        self.original_data = {
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'registration_date': self.registration_date,  # обычно не редактируемо
            'avatar_url': self.avatar_url
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
            editable_fields = ['username', 'full_name', 'email', 'role', 'avatar_url', 'is_active']
            update_data = {}

            for key in editable_fields:
                current_val = getattr(self, key)
                original_val = self.original_data.get(key)
                if current_val != original_val:
                    update_data[key] = current_val

            if not update_data:
                self.show_info("Нет изменений для сохранения")
                self.show_loading(False)
                self.edit_mode = False
                return

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.app.token}'
            }

            logging.info(f"[PATCH] Отправка данных профиля: {update_data}")

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

    def choose_avatar(self):
        chooser = FileChooserIconView(path=os.getcwd(), filters=["*.png", "*.jpg", "*.jpeg"])
        popup = Popup(title="Выбор аватара",
                      content=chooser,
                      size_hint=(0.9, 0.9))

        def select_file(instance, selection):
            if selection:
                self.avatar_url = f"file://{selection[0]}"
            popup.dismiss()

        chooser.bind(on_submit=lambda instance, selection, touch: select_file(instance, selection))
        popup.open()

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