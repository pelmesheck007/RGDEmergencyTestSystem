from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.network.urlrequest import UrlRequest
import json
from kivy.clock import Clock
from datetime import datetime
import logging
from pathlib import Path
from datetime import datetime
from kivymd.uix.snackbar import MDSnackbar

class SafeScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SlideTransition()  # Явная инициализация перехода
class RZDLoginApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.theme_style = "Light"
        self.setup_logging()

        # Цвета РЖД
        self.rjd_dark_red = get_color_from_hex("#CC0000")
        self.rjd_light_red = get_color_from_hex("#FFEBEE")
        self.rjd_white = get_color_from_hex("#FFFFFF")

        # Токен и данные пользователя
        self.token = None
        self.user_data = None
        current_screen = StringProperty('login')

        # Загрузка KV файла
        return Builder.load_file("rzd.kv")


    def on_screen_change(self, screen_name):
        """Обработчик изменения экрана"""
        logging.info(f"Переход на экран: {screen_name}")

        if screen_name == 'main' and not hasattr(self, 'user_data'):
            logging.warning("Попытка перехода на главный экран без авторизации!")
            self.root.current = 'login'

    def show_main_screen(self, user_data):
        """Безопасный переход на главный экран"""
        try:
            self.user_data = user_data
            if not hasattr(self, 'root'):
                raise AttributeError("Root widget not initialized")

            if 'main' not in self.root.screen_names:
                raise ValueError("Экран 'main' не найден")

            main_screen = self.root.get_screen('main')
            main_screen.username = user_data['username']
            main_screen.role = user_data['role']
            main_screen.full_name = user_data.get('full_name', '')

            # Используем безопасный переход
            self.root.safe_switch('main', direction='left')

        except Exception as e:
            logging.error(f"Ошибка перехода на главный экран: {str(e)}")
            self.show_error_dialog("Ошибка перехода", str(e))

    def setup_logging(self):
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        log_file = logs_dir / f"app_{datetime.now().strftime('%Y-%m-%d')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def check_backend_connection(self):
        try:
            UrlRequest(
                'http://localhost:8000/health',
                on_success=lambda req, res: print("Сервер доступен"),
                on_error=lambda req, err: self.show_connection_error(),
                timeout=5
            )
        except Exception as e:
            self.show_connection_error()

    def show_connection_error(self):
        from kivymd.uix.dialog import MDDialog
        MDDialog(
            title="Ошибка соединения",
            text="Не удается подключиться к серверу. Проверьте:\n\n1. Запущен ли сервер\n2. Правильный ли адрес\n3. Сетевое подключение",
            size_hint=(0.8, None)
        ).open()

    def on_start(self):
        print("Доступные экраны:", list(self.root.screen_names))


if __name__ == "__main__":
    RZDLoginApp().run()