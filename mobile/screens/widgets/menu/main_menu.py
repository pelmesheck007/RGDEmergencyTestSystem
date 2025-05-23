from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.app import MDApp
import logging
from kivy.utils import get_color_from_hex
from kivy.utils import get_color_from_hex
import importlib

class RoleMenu:
    def __init__(self, caller, role):
        self.caller = caller
        self.role = role
        self.menu = None
        self.app = MDApp.get_running_app()
        self.create_menu()

    def create_menu(self):
        """Создание меню в зависимости от роли"""
        try:
            menu_items = [
                self._create_menu_item("Главная", "home", "main", self._navigate_to),
                self._create_menu_item("Профиль", "account", "profile", self._navigate_to),
                self._create_menu_item("Тесты", "play-box", "tests", self._navigate_to),
                self._create_menu_item("Классы", "account-group", "classes", self._navigate_to),
                self._create_menu_item("Статистика", "chart-line", "statistics", self._navigate_to)
            ]

            if self.role == 'admin':
                menu_items.extend([
                    self._create_menu_item("Пользователи", "account-cog", "configuring_users", self._navigate_to),
                    self._create_menu_item("Настройки", "cog", "settings", self._navigate_to)
                ])

            self.menu = MDDropdownMenu(
                caller=self.caller,
                items=menu_items,
                position="bottom",
                width_mult=4,
                max_height=dp(300),
                radius=[24, 0, 24, 0],
                ver_growth="down",
                background_color= get_color_from_hex("#CC0000")
            )
        except Exception as e:
            logging.error(f"Error creating menu: {e}")

    def _navigate_to(self, screen_name):
        """Навигация между экранами"""
        self.menu.dismiss()
        if not self.app.root.has_screen(screen_name):
            self._load_screen_module(screen_name)

        if self.app.root.has_screen(screen_name):
            self.app.root.current = screen_name
            # Обновляем заголовок через сам экран
            screen = self.app.root.get_screen(screen_name)
            if hasattr(screen, 'screen_title'):
                screen.screen_title = self._get_screen_title(screen_name)
        else:
            logging.error(f"Экран {screen_name} не существует")
            self.app.show_error_dialog("Ошибка", f"Экран {screen_name} не доступен")

    def _get_screen_title(self, screen_name):
        """Получение заголовка для экрана"""
        titles = {
            'main': 'Главная',
            'profile': 'Профиль',
            'tests': 'Тесты',
            'classes': 'Классы',
            'statistics': 'Статистика',
            'configuring_users': 'Управление пользователями',
            'settings': 'Настройки системы'
        }
        return titles.get(screen_name, screen_name)

    def _load_screen_module(self, screen_name):
        """Динамическая загрузка модуля экрана"""
        screen_modules = {
            'main': ('screens.main.main_screen', 'MainScreen'),
            'profile': ('screens.menu.profile_screen', 'ProfileScreen'),
            'manage_users': ('screens.admins.configuring_users', 'ConfiguringUsersScreen'),
            'settings': ('screens.admins.settings_screen', 'SettingsScreen')
        }

        if screen_name in screen_modules:
            module_path, class_name = screen_modules[screen_name]
            try:
                module = importlib.import_module(module_path)
                screen_class = getattr(module, class_name)
                self.app.root.add_widget(screen_class(name=screen_name))
                return True
            except ImportError as e:
                logging.error(f"Не удалось импортировать модуль {module_path}: {e}")
            except AttributeError as e:
                logging.error(f"Класс {class_name} не найден в модуле {module_path}: {e}")
            except Exception as e:
                logging.error(f"Неизвестная ошибка при загрузке экрана {screen_name}: {e}")
        return False


    def _create_menu_item(self, text, icon, action, callback):
        """Создание элемента меню"""
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

    def _default_action(self, action):
        """Общие действия для всех ролей"""
        self.menu.dismiss()
        app = MDApp.get_running_app()
        if action == 'profile':
            self._open_profile()
        else:
            logging.info(f"Action: {action}")

    def _admin_action(self, action):
        """Действия для администратора"""
        self.menu.dismiss()
        logging.info(f"Admin action: {action}")

    def _open_profile(self):
        """Открытие профиля"""
        app = MDApp.get_running_app()
        if 'profile' not in app.root.screen_names:
            from mobile.screens.menu.profile_screen import ProfileScreen
            app.root.add_widget(ProfileScreen(name='profile'))
        app.root.current = 'profile'

    def open(self):
        """Открытие меню"""
        if self.menu:
            self.menu.open()
