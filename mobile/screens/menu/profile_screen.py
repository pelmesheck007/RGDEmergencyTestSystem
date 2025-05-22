from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, ObjectProperty
from kivymd.app import MDApp
from kivy.clock import Clock
import logging


class ProfileScreen(MDScreen):
    username = StringProperty("")
    full_name = StringProperty("")
    email = StringProperty("")
    role = StringProperty("")
    edit_mode = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.load_user_data)

    def load_user_data(self, dt):
        app = MDApp.get_running_app()
        if hasattr(app, 'user_data') and app.user_data:
            self.username = app.user_data.get('username', '')
            self.full_name = app.user_data.get('full_name', '')
            self.email = app.user_data.get('email', '')
            self.role = self.get_role_display(app.user_data.get('role', 'student'))

    def get_role_display(self, role):
        role_map = {
            'admin': 'Администратор',
            'teacher': 'Преподаватель',
            'student': 'Студент'
        }
        return role_map.get(role, role)

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        self.ids.edit_btn.icon = 'pencil-off' if self.edit_mode else 'pencil'

        # Обновляем поля ввода
        if self.edit_mode:
            self.ids.full_name_input.text = self.full_name
            self.ids.email_input.text = self.email

    def save_profile(self):
        new_full_name = self.ids.full_name_input.text
        new_email = self.ids.email_input.text

        # Валидация данных
        if not new_full_name:
            self.ids.snackbar.show("ФИО не может быть пустым")
            return

        # Обновляем данные
        self.full_name = new_full_name
        self.email = new_email

        # Сохраняем в app.user_data
        app = MDApp.get_running_app()
        if hasattr(app, 'user_data') and app.user_data:
            app.user_data['full_name'] = self.full_name
            app.user_data['email'] = self.email

        self.toggle_edit_mode()
        self.ids.snackbar.show("Данные успешно сохранены")

        # Здесь можно добавить вызов API для сохранения на сервере