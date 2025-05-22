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
        Clock.schedule_once(self.init_menu)

    def init_menu(self, dt):
        """Инициализация меню после загрузки интерфейса"""
        if not self.load_user_data():
            logging.warning("Не удалось загрузить данные пользователя")
            return

        self.create_role_menu()
        self.update_ui()

    def load_user_data(self):
        """Загрузка данных пользователя с проверкой"""
        app = MDApp.get_running_app()
        if not hasattr(app, 'user_data') or not app.user_data:
            return False

        user = app.user_data
        self.username = user.get('username', '')
        self.role = self.get_role_display(user.get('role', 'student'))
        self.full_name = user.get('full_name', '')
        self.email = user.get('email', '')
        return True

    def create_role_menu(self):
        """Создание меню для текущей роли"""
        role = MDApp.get_running_app().user_data.get('role', 'student')

        menu_items = [
            self.create_menu_item("Профиль", "chart-box", "profile", self.default_action),
            self.create_menu_item("Тесты", "play-box", "tests", self.default_action),
            self.create_menu_item("Классы", "chart-box", "classes", self.default_action)
        ]

        if role == 'admin':
            menu_items.extend([
                self.create_menu_item("Управление пользователями", "account-cog", "manage_users", self.admin_action),
                self.create_menu_item("Настройки системы", "cog", "system_settings", self.admin_action)
            ])

        self.menu = MDDropdownMenu(
            caller=self.ids.menu_button,
            items=menu_items,
            position="auto",
            width=dp(220),
            radius=[24, 0, 24, 0],
            ver_growth="down"
        )
        self.menu.md_bg_color = MDApp.get_running_app().rjd_dark_red

    def create_menu_item(self, text, icon, action, callback):
        """Создание элемента меню"""
        return {
            "text": text,
            "icon": icon,
            "viewclass": "OneLineIconListItem",
            "height": dp(48),
            "on_release": lambda x=action: callback(x)
        }

    def update_ui(self):
        """Обновление интерфейса после загрузки данных"""
        if hasattr(self.ids, 'loading_spinner'):
            self.ids.loading_spinner.active = False

    def open_menu(self):
        """Открытие меню с проверкой"""
        if not self.menu:
            self.create_role_menu()

        try:
            self.menu.open()
        except Exception as e:
            logging.error(f"Ошибка открытия меню: {e}")

    def admin_action(self, action):
        logging.info(f"Admin action: {action}")
        self.menu.dismiss()
        # Здесь реализация действий админа

    def teacher_action(self, action):
        logging.info(f"Teacher action: {action}")
        self.menu.dismiss()
        # Здесь реализация действий преподавателя

    def default_action(self, action):
        logging.info(f"Action: {action}")
        self.menu.dismiss()
        # Общие действия для всех ролей

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
        if self.menu:
            self.menu.dismiss()