from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
import logging


class BaseScreen(MDScreen):
    """
    Базовый класс для всех экранов приложения
    """
    screen_title = StringProperty("Заголовок страницы")
    show_back_button = BooleanProperty(True)
    show_menu_button = BooleanProperty(False)
    loading = BooleanProperty(False)
    menu = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()


    def build_content(self):
        """Метод для построения содержимого экрана"""
        pass

    def on_kv_post(self, base_widget):
        self.build_content()

    def on_pre_enter(self, *args):
        """Вызывается перед входом на экран"""
        self.setup_menu()
        if hasattr(self, 'on_refresh'):
            self.on_refresh()

    def on_enter(self, *args):
        """Вызывается при входе на экран"""
        pass

    def on_leave(self):
        """Вызывается при выходе с экрана"""
        if self.menu and hasattr(self.menu, 'menu'):
            self.menu.menu.dismiss()

    def setup_menu(self):
        """Инициализация меню для экрана"""
        if not self.menu and hasattr(self.app, 'user_data') and hasattr(self.ids, 'menu_button'):
            from mobile.screens.widgets.menu.main_menu import RoleMenu
            role = self.app.user_data.get('role', 'student')
            self.menu = RoleMenu(caller=self.ids.menu_button, role=role)

    def open_menu(self):
        """Открытие меню"""
        if not self.menu:
            self.setup_menu()
        if self.menu:
            self.menu.open()

    def logout(self):
        """Выход из системы"""
        self.app.token = None
        self.app.user_data = None
        self.app.root.current = 'login'

    def show_loading(self, state=True):
        """Показать/скрыть индикатор загрузки"""
        if hasattr(self.ids, 'loading_spinner'):
            self.ids.loading_spinner.active = state
            self.loading = state

    def show_error(self, message):
        """Показать сообщение об ошибке"""
        Snackbar(
            text=message,
            bg_color=self.app.rjd_dark_red,
            duration=3
        ).open()

    def navigate_to(self, screen_name, **kwargs):
        """Переход на другой экран"""
        try:
            if screen_name not in self.app.root.screen_names:
                self.create_screen(screen_name, **kwargs)

            self.app.root.current = screen_name
            return True
        except Exception as e:
            logging.error(f"Navigation error: {e}")
            self.show_error(f"Ошибка перехода на страницу {screen_name}")
            return False

    def create_screen(self, screen_name, **kwargs):
        """Динамическое создание экрана"""
        screens = {
            'main': 'screens.main.main_screen.MainScreen',
            'profile': 'screens.menu.profile_screen.ProfileScreen',
            'tests': 'screens.tests.tests_screen.TestsScreen',
            'classes': 'screens.classes.classes_screen.ClassesScreen',
            'manage_users': 'screens.admins.configuring_users.ConfiguringUsersScreen',
            'settings': 'screens.admins.settings_screen.SettingsScreen'
        }

        if screen_name in screens:
            module_path, class_name = screens[screen_name].rsplit('.', 1)
            try:
                module = __import__(module_path, fromlist=[class_name])
                screen_class = getattr(module, class_name)
                screen = screen_class(name=screen_name, **kwargs)
                self.app.root.add_widget(screen)
                return screen
            except Exception as e:
                logging.error(f"Failed to create screen {screen_name}: {e}")
                self.show_error(f"Ошибка создания страницы {screen_name}")
        return None

    def back_to_previous(self):
        """Вернуться на предыдущий экран"""
        if self.manager.current == 'main':
            return
        self.manager.current = 'main'

    def show_success(self, message):
        """Показать сообщение об успешном выполнении"""
        Snackbar(
            text=message,
            bg_color=[0, 0.7, 0, 1],  # Зеленый цвет
            duration=2
        ).open()