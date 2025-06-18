import logging
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivymd.uix.card import MDSeparator, MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, ObjectProperty
from kivymd.app import MDApp

from mobile.screens.widgets.menu.main_menu import RoleMenu


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
        role = getattr(App.get_running_app(), "user_data", {}).get("role", None)
        if role:
            RoleMenu(self.ids["menu_button"], role).open()
        else:
            self.show_error("Роль пользователя не определена.")

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
        self.load_user_main_info()

    def on_screen_leave(self):
        """При выходе с экрана"""
        if self.menu and self.menu.menu:
            self.menu.menu.dismiss()

    def load_user_main_info(self):
        app = MDApp.get_running_app()

        def format_datetime(dt_str):
            if not dt_str:
                return "-"
            try:
                dt = datetime.fromisoformat(dt_str)
                return dt.strftime("%d.%m.%Y %H:%M")
            except Exception:
                return dt_str

        def on_success(req, result):
            box = self.ids.content_box
            box.clear_widgets()

            # Приветствие
            full_name = result.get('full_name') or app.user_data.get('full_name') or 'Пользователь'
            box.add_widget(MDLabel(
                text=f"Привет, {full_name}",
                font_style="H5",
                theme_text_color="Primary",
                halign="left",
                size_hint_y=None,
                height=dp(36)
            ))

            # Учебная группа
            group = result.get("group", {})
            group_name = group.get("name", "Без группы")
            box.add_widget(MDLabel(
                text=f"Учебная группа: {group_name}",
                font_style="Subtitle1",
                theme_text_color="Secondary",
                halign="left",
                size_hint_y=None,
                height=dp(28)
            ))

            box.add_widget(MDSeparator(height=dp(1), color=(0.8, 0.8, 0.8, 1)))

            # Последние тесты
            recent_tests = result.get("recent_tests", [])
            if recent_tests:
                box.add_widget(MDLabel(
                    text="Последние тесты",
                    font_style="Subtitle1",
                    theme_text_color="Primary",
                    halign="left",
                    padding=(0, dp(12)),
                    size_hint_y=None,
                    height=dp(28)
                ))
                seen_ids = set()
                for test in recent_tests:
                    test_id = test.get("id")
                    if test_id in seen_ids:
                        continue
                    seen_ids.add(test_id)

                    status = "Пройден" if test.get("passed") else "Не пройден"
                    score = test.get("score_percent", 0)
                    datetime = test.get("datetime", "")
                    box.add_widget(MDLabel(
                        text=f"{test.get('name', 'Тест')} — {status}, {score} баллов\n{datetime}",
                        font_style="Body2",
                        halign="left",
                        theme_text_color="Secondary",
                        size_hint_y=None,
                        height=dp(42)
                    ))
            else:
                box.add_widget(MDLabel(
                    text="Нет недавно пройденных тестов",
                    halign="left",
                    theme_text_color="Hint",
                    size_hint_y=None,
                    height=dp(28)
                ))

            box.add_widget(MDSeparator(height=dp(1), color=(0.8, 0.8, 0.8, 1)))

            # Последние сценарии
            recent_scenarios = result.get("recent_scenarios", [])
            if recent_scenarios:
                box.add_widget(MDLabel(
                    text="Последние сценарии",
                    font_style="Subtitle1",
                    theme_text_color="Primary",
                    halign="left",
                    padding=(0, dp(12)),
                    size_hint_y=None,
                    height=dp(28)
                ))
                for s in recent_scenarios:
                    name = s.get("name", "Сценарий")
                    result_text = s.get("result", "-")
                    datetime = s.get("datetime", "")
                    box.add_widget(MDLabel(
                        text=f"{name} — результат: {result_text}\n{datetime}",
                        font_style="Body2",
                        halign="left",
                        theme_text_color="Secondary",
                        size_hint_y=None,
                        height=dp(42)
                    ))
            else:
                box.add_widget(MDLabel(
                    text="Нет недавно завершённых сценариев",
                    halign="left",
                    theme_text_color="Hint",
                    size_hint_y=None,
                    height=dp(28)
                ))

        def on_error(req, err):
            print(f"[Main Info] Ошибка: {err}")
            if req.resp_status:
                print(f"Статус ответа: {req.resp_status}")
            if req.result:
                print(f"Ответ сервера: {req.result}")

        user_id = app.user_data.get('id')
        if not user_id:
            print("User ID не найден в app.user_data")
            return

        UrlRequest(
            f"{app.api_url}/users/{user_id}/main_info",
            req_headers={"Authorization": f"Bearer {app.token}"},
            on_success=on_success,
            on_error=on_error,
            method="GET"
        )

