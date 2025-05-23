import logging
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, ObjectProperty
from kivymd.app import MDApp



class MainScreen(MDScreen):
    username = StringProperty("")
    role = StringProperty("")
    full_name = StringProperty("")
    email = StringProperty("")
    welcome_message = StringProperty("Добро пожаловать в систему тестирования")
    menu = ObjectProperty(None, allownone=True)
    screen_title = StringProperty("Главное меню")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.init_menu, 0.5)

    def init_menu(self, dt):
        """Инициализация меню после загрузки интерфейса"""
        if not self.load_user_data():
            Clock.schedule_once(self.init_menu, 0.5)
            return
        from mobile.screens.widgets.menu.main_menu import RoleMenu
        self.menu = RoleMenu(caller=self.ids.menu_button, role=self.role)
        self.update_ui()

    def load_user_data(self):
        """Загрузка данных пользователя с проверкой"""
        app = MDApp.get_running_app()
        if not hasattr(app, 'user_data') or not app.user_data:
            return False

        try:
            user = app.user_data
            self.username = user.get('username', '')
            self.role = self.get_role_display(user.get('role', 'student'))
            self.full_name = user.get('full_name', '')
            self.email = user.get('email', '')
            return True
        except Exception as e:
            logging.error(f"Error loading user data: {e}")
            return False

    def update_ui(self):
        """Обновление интерфейса после загрузки данных"""
        if hasattr(self.ids, 'loading_spinner'):
            self.ids.loading_spinner.active = False

    def open_menu(self):
        """Открытие меню"""
        if not self.menu:
            self.menu = RoleMenu(caller=self.ids.menu_button, role=self.role)
        self.menu.open()

    def get_role_display(self, role):
        role_map = {
            'admin': 'Администратор',
            'teacher': 'Преподаватель',
            'student': 'Студент'
        }
        return role_map.get(role, role)

    def logout(self):
        """Выход из системы"""
        app = MDApp.get_running_app()
        try:
            app.token = None
            app.user_data = None
            self.clear_login_fields()
            app.root.current = 'login'
        except Exception as e:
            logging.error(f"Ошибка выхода: {e}")
            app.root.current = 'login'

    def clear_login_fields(self):
        """Очистка полей входа"""
        try:
            login_screen = MDApp.get_running_app().root.get_screen('login')
            if hasattr(login_screen, 'ids'):
                login_screen.ids.password.text = ""
                login_screen.ids.username.text = ""
        except Exception as e:
            logging.warning(f"Не удалось очистить поля: {e}")

    def on_screen_enter(self):
        """При входе на экран"""
        Clock.schedule_once(self.init_menu)

    def on_screen_leave(self):
        """При выходе с экрана"""
        if self.menu and self.menu.menu:
            self.menu.menu.dismiss()