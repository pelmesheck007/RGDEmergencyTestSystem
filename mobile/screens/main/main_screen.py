import logging
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, ObjectProperty
from kivymd.app import MDApp



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
        # Убрали вызов create_role_menu() из __init__, так как данные могут быть не готовы
        Clock.schedule_once(self.init_menu, 0.5)  # Задержка для инициализации

    def init_menu(self, dt):
        """Инициализация меню после загрузки интерфейса"""
        print("Initializing menu...")
        if not self.load_user_data():
            logging.warning("Не удалось загрузить данные пользователя")
            # Попробуем загрузить снова через 0.5 секунды
            Clock.schedule_once(self.init_menu, 0.5)
            return

        self.create_role_menu()
        self.update_ui()

    def load_user_data(self):
        """Загрузка данных пользователя с проверкой"""
        app = MDApp.get_running_app()
        if not hasattr(app, 'user_data') or not app.user_data:
            print("User data not available yet")
            return False

        try:
            user = app.user_data
            self.username = user.get('username', '')
            self.role = self.get_role_display(user.get('role', 'student'))
            self.full_name = user.get('full_name', '')
            self.email = user.get('email', '')
            print(f"User data loaded: {self.username}, {self.role}")
            return True
        except Exception as e:
            logging.error(f"Error loading user data: {e}")
            return False

    def create_role_menu(self):
        """Создание меню для текущей роли"""
        try:
            app = MDApp.get_running_app()
            if not hasattr(app, 'user_data') or not app.user_data:
                print("Cannot create menu - user data not available")
                return

            role = app.user_data.get('role', 'student')
            print(f"Creating menu for role: {role}")

            menu_items = [
                self.create_menu_item("Профиль", "account", "profile", self.open_profile),
                self.create_menu_item("Тесты", "play-box", "tests", self.default_action),
                self.create_menu_item("Классы", "account-group", "classes", self.default_action)
            ]

            if role == 'admin':
                menu_items.extend([
                    self.create_menu_item("Управление пользователями", "account-cog", "manage_users", self.admin_action),
                    self.create_menu_item("Настройки системы", "cog", "system_settings", self.admin_action)
                ])

            self.menu = MDDropdownMenu(
                caller=self.ids.menu_button,
                items=menu_items,
                position="bottom",
                width_mult=4,  # вместо фиксированной ширины
                max_height=dp(300),  # чтобы не вытягивалось слишком
                radius=[24, 0, 24, 0],
                ver_growth="down",
                background_color=MDApp.get_running_app().rjd_dark_red
            )
            print("Menu created successfully")
        except Exception as e:
            logging.error(f"Error creating menu: {e}")

    def create_menu_item(self, text, icon, action, callback):
        """Создание элемента меню с безопасным callback"""
        def action_callback(*args):
            try:
                callback(action)
            except Exception as e:
                logging.error(f"Error in menu callback: {e}")

        return {
            "text": text,
            "icon": icon,
            "viewclass": "OneLineIconListItem",
            "height": dp(48),
            "on_release": action_callback
        }

    def open_profile(self):
        app = MDApp.get_running_app()
        if 'profile' not in app.root.screen_names:
            from mobile.screens.menu.profile_screen import ProfileScreen
            app.root.add_widget(ProfileScreen(name='profile'))
        app.root.current = 'profile'



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