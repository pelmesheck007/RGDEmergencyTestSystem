import logging

from kivy.clock import Clock
from kivy.uix.screenmanager import NoTransition
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty


class MainScreen(MDScreen):
    username = StringProperty("")
    role = StringProperty("")
    full_name = StringProperty("")
    email = StringProperty("")
    welcome_message = StringProperty("Мы рады, что вы с нами!")

    def on_pre_enter(self):
        user = MDApp.get_running_app().user_data
        if user:
            logging.info(f"Пользователь {user['username']} открыл главный экран")

    def update_user_data(self):
        app = MDApp.get_running_app()
        if not hasattr(app, 'user_data'):
            logging.error("Нет данных пользователя!")
            return

        app = MDApp.get_running_app()
        if app.user_data:
            self.username = app.user_data.get('username', '')
            self.role = self.get_role_display(app.user_data.get('role', ''))
            self.full_name = app.user_data.get('full_name', '')
            self.email = app.user_data.get('email', '')

    def get_role_display(self, role):
        role_map = {
            'admin': 'Администратор',
            'teacher': 'Преподаватель',
            'student': 'Студент'
        }
        return role_map.get(role, role)

    def logout(self):
        app = MDApp.get_running_app()
        try:
            # Очистка данных
            app.token = None
            app.user_data = None

            # Очистка полей входа
            if hasattr(app, 'root') and 'login' in app.root.screen_names:
                login_screen = app.root.get_screen('login')
                if hasattr(login_screen, 'clean_fields'):
                    login_screen.clean_fields()

            # Безопасный переход
            if hasattr(app.root, 'safe_switch'):
                app.root.safe_switch('login', direction='right')
            else:
                app.root.current = 'login'

        except Exception as e:
            logging.error(f"Critical logout error: {str(e)}")
            # Аварийное восстановление
            app.root.current = 'login'

    def clear_login_fields(self):
        """Очистка полей входа"""
        try:
            if hasattr(MDApp.get_running_app(), 'root'):
                login_screen = MDApp.get_running_app().root.get_screen('login')
                if hasattr(login_screen, 'ids'):
                    if 'password' in login_screen.ids:
                        login_screen.ids.password.text = ""
                    if 'username' in login_screen.ids:
                        login_screen.ids.username.text = ""
        except Exception as e:
            logging.warning(f"Не удалось очистить поля входа: {str(e)}")

    def on_screen_leave(self):
        """Вызывается при выходе с экрана"""
        logging.info("Закрытие главного экрана")
        # Очистка ресурсов при необходимости

    def on_screen_enter(self):
        """Вызывается при входе на экран"""
        app = MDApp.get_running_app()
        logging.info(f"Открытие главного экрана. Пользователь: {app.user_data.get('username', 'неизвестен')}")

        # Обновляем данные пользователя
        self.update_user_data()

        # Если у вас есть spinner, убедитесь что он есть в KV-разметке
        if hasattr(self.ids, 'loading_spinner'):
            Clock.schedule_once(lambda dt: self.finish_loading())

    def finish_loading(self):
        """Завершаем загрузку (для анимаций)"""
        if hasattr(self.ids, 'loading_spinner'):
            self.ids.loading_spinner.active = False
        else:
            logging.warning("Spinner не найден в ids")

