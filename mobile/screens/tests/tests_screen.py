# tests_screen.py
from kivy.properties import ListProperty, ObjectProperty, StringProperty, partial
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
import json
import logging

from kivymd.uix.label import MDLabel
from mobile.screens.base_screen import BaseScreen
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton


class TestListItem(OneLineAvatarIconListItem):
    """Элемент списка тестов"""
    test_data = ObjectProperty(None)
    icon = StringProperty("file-document")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._icon_widget = IconLeftWidget(icon=self.icon)
        self.add_widget(self._icon_widget)


class TestsScreen(BaseScreen):
    """Экран со списком тестов"""
    tests_list = ListProperty([])
    selected_test = ObjectProperty(None, allownone=True)
    dialog = ObjectProperty(None, allownone=True)
    no_tests_message = StringProperty("Загрузка тестов...")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_title = "Тесты"
        self.show_menu_button = True

    def on_pre_enter(self, *args):
        """Вызывается перед открытием экрана"""
        super().on_pre_enter(*args)
        self.load_tests()

    def load_tests(self):
        """Загрузка тестов с сервера"""
        self.show_loading(True)
        if not hasattr(self.app, 'token') or not self.app.token:
            self.show_error("Требуется авторизация")
            self.show_loading(False)
            return

        headers = {
            'Authorization': f'Bearer {self.app.token}',
            'Content-Type': 'application/json'
        }

        UrlRequest(
            f'{self.app.api_url}/tests/',
            on_success=self.on_tests_load_success,
            on_error=self.on_tests_load_error,
            on_failure=self.on_tests_load_error,
            req_headers=headers,
            timeout=10
        )

    def on_tests_load_success(self, req, result):
        """Обработка успешной загрузки"""
        self.show_loading(False)
        try:
            if isinstance(result, list):
                self.tests_list = result
                self.update_tests_display()
                if not result:
                    self.no_tests_message = "Доступных тестов нет"
            else:
                self.show_error("Некорректный формат данных")
        except Exception as e:
            logging.error(f"Ошибка обработки тестов: {e}")
            self.show_error(f"Ошибка обработки: {str(e)}")

    def on_tests_load_error(self, req, error):
        """Обработка ошибки загрузки"""
        self.show_loading(False)
        error_msg = "Неизвестная ошибка сервера"
        if isinstance(error, dict):
            error_msg = error.get('detail', str(error))
        elif hasattr(req, 'resp_status'):
            if req.resp_status == 401:
                error_msg = "Требуется авторизация"
            elif req.resp_status == 403:
                error_msg = "Доступ запрещен"

        self.show_error(f"Ошибка загрузки: {error_msg}")
        self.no_tests_message = "Не удалось загрузить тесты"

    def update_tests_display(self):
        """Обновление списка тестов в интерфейсе"""
        self.ids.tests_container.clear_widgets()

        if not self.tests_list:
            self.ids.tests_container.add_widget(
                MDLabel(
                    text=self.no_tests_message,
                    halign="center",
                    theme_text_color="Secondary"
                )
            )
            return

        for test in self.tests_list:
            item = TestListItem(
                text=test.get('test_name', 'Без названия'),
                test_data=test,
                on_release=lambda _, t=test: self.show_test_details(t)
            )
            self.ids.tests_container.add_widget(item)

    def show_test_details(self, test_data):
        """Показать детали теста в диалоге"""
        self.selected_test = test_data
        self.dialog = MDDialog(
            title=test_data.get('test_name', 'Информация о тесте'),
            text=self._format_test_details(test_data),
            size_hint=(0.8, None),
            buttons=[
                MDFlatButton(
                    text="ЗАКРЫТЬ",
                    theme_text_color="Custom",
                    text_color=self.app.rjd_dark_red,
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="НАЧАТЬ ТЕСТ",
                    theme_text_color="Custom",
                    text_color=self.app.rjd_dark_red,
                    on_release=self.start_test
                )
            ]
        )
        self.dialog.open()

    def _format_test_details(self, test_data):
        """Форматирование деталей теста"""
        details = []
        if 'description' in test_data and test_data['description']:
            details.append(f"Описание: {test_data['description']}")
        if 'time_limit' in test_data and test_data['time_limit']:
            details.append(f"Лимит времени: {test_data['time_limit']} мин")
        if 'passing_score' in test_data and test_data['passing_score']:
            details.append(f"Проходной балл: {test_data['passing_score']}%")
        if 'theme' in test_data and test_data['theme']:
            details.append(f"Тема: {test_data['theme']}")
        if 'attempts_limit' in test_data and test_data['attempts_limit']:
            details.append(f"Попыток: {test_data['attempts_limit']}")

        return "\n".join(details) if details else "Дополнительная информация отсутствует"


    def start_test(self, *args):
        """Начать выбранный тест"""
        if self.dialog:
            self.dialog.dismiss()

        if not self.selected_test:
            self.show_error("Тест не выбран")
            return

        test_id = self.selected_test.get('id')
        if not test_id:
            self.show_error("Неверный ID теста")
            return

        # Сохраняем ID теста в app
        self.app.current_test_id = test_id

        # Переход на экран прохождения теста
        self.manager.current = "test_taking"

