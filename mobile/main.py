from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.network.urlrequest import UrlRequest
import logging
from pathlib import Path
from datetime import datetime

class SafeScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.transition = SlideTransition()  # Явная инициализация перехода



class RZDLoginApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Основная информация об приложении
        self.title = "RGDEmergencyTestSystem"
        self.api_url = "http://localhost:8000"  # URL-адрес API
        self.token = None  # Токен авторизации
        self.user_data = None  # Данные пользователя
        # Цвета в стиле РЖД
        self.rjd_dark_red = [0.8, 0, 0, 1]
        self.rjd_light_red = [1, 0.92, 0.93, 1]
        self.rjd_white = [1, 1, 1, 1]

    def build(self):
        """Инициализация и запуск основного интерфейса приложения"""
        self.theme_cls.primary_palette = "Red"  # Основная палитра цветов
        self.theme_cls.theme_style = "Light"    # Светлая тема
        self.setup_logging()  # Настройка логирования
        current_screen = StringProperty('login')  # Стартовый экран
        return Builder.load_file("rzd.kv")  # Загрузка интерфейса из KV-файла

    def on_screen_change(self, screen_name):
        """Обработчик события смены экрана"""
        logging.info(f"Переход на экран: {screen_name}")

        # Защита от перехода на главный экран без авторизации
        if screen_name == 'main' and not hasattr(self, 'user_data'):
            logging.warning("Попытка перехода на главный экран без авторизации!")
            self.root.current = 'login'

    def show_main_screen(self, user_data):
        """Безопасный переход на главный экран после авторизации"""
        try:
            self.user_data = user_data  # Сохраняем данные пользователя
            if not hasattr(self, 'root'):
                raise AttributeError("Root widget not initialized")

            if 'main' not in self.root.screen_names:
                raise ValueError("Экран 'main' не найден")

            # Установка данных пользователя на главный экран
            main_screen = self.root.get_screen('main')
            main_screen.username = user_data['username']
            main_screen.role = user_data['role']
            main_screen.full_name = user_data.get('full_name', '')

            # Переход на главный экран с анимацией
            self.root.safe_switch('main', direction='left')

        except Exception as e:
            logging.error(f"Ошибка перехода на главный экран: {str(e)}")
            self.show_error_dialog("Ошибка перехода", str(e))

    def setup_logging(self):
        """Настройка логирования в файл и консоль"""
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        log_file = logs_dir / f"app_{datetime.now().strftime('%Y-%m-%d')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),     # Запись в файл
                logging.StreamHandler()            # Вывод в консоль
            ]
        )

    def check_backend_connection(self):
        """Проверка доступности сервера (бэкенда)"""
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
        """Отображение диалога при ошибке соединения с сервером"""
        from kivymd.uix.dialog import MDDialog
        MDDialog(
            title="Ошибка соединения",
            text="Не удается подключиться к серверу. Проверьте:\n\n1. Запущен ли сервер\n2. Правильный ли адрес\n3. Сетевое подключение",
            size_hint=(0.8, None)
        ).open()

    def on_start(self):
        """Обработчик запуска приложения"""
        print("Доступные экраны:", list(self.root.screen_names))

    def show_error_dialog(self, title, text):
        """Отображение диалога ошибки"""
        from kivymd.uix.dialog import MDDialog
        MDDialog(
            title=title,
            text=text,
            size_hint=(0.8, None)
        ).open()

    def update_user_data(self, new_data):
        """Обновление сохранённых данных пользователя"""
        if hasattr(self, 'user_data'):
            self.user_data.update(new_data)


if __name__ == "__main__":
    RZDLoginApp().run()