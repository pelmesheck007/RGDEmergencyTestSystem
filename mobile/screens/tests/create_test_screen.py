from kivy.app import App
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.uix.screenmanager import Screen
from kivy.network.urlrequest import UrlRequest
from kivymd.toast import toast
import json

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu

class TaskForm(MDBoxLayout):
    question = StringProperty("")
    task_type = StringProperty("text")
    options_count = NumericProperty(0)
    options = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "8dp"

        self.question_field = MDTextField(hint_text="Вопрос", multiline=True, size_hint_y=None, height="80dp")
        self.add_widget(self.question_field)

        types = ["text", "short_answer", "radio", "checkbox"]
        menu_items = [
            {"text": t, "on_release": lambda x=t: self.set_task_type(x)} for t in types
        ]
        self.task_type_button_caller = MDFlatButton(text="Тип: текст", on_release=self.open_task_type_menu)
        self.add_widget(self.task_type_button_caller)

        self.task_type_menu = MDDropdownMenu(
            caller=self.task_type_button_caller,
            items=menu_items,
            width_mult=4,
        )

        self.options_count_field = MDTextField(
            hint_text="Количество вариантов (для радио/чекбоксов)",
            input_filter="int",
            on_text_validate=self.update_options,
            size_hint_y=None,
            height=0
        )
        self.add_widget(self.options_count_field)

        self.options_container = MDBoxLayout(orientation="vertical", spacing="4dp", size_hint_y=None)
        self.options_container.bind(minimum_height=self.options_container.setter('height'))
        self.add_widget(self.options_container)

    def open_task_type_menu(self, *args):
        self.task_type_menu.open()

    def set_task_type(self, task_type):
        self.task_type = task_type
        self.task_type_button_caller.text = f"Тип: {task_type}"
        self.task_type_menu.dismiss()
        self.update_ui()

    def update_ui(self):
        if self.task_type in ("radio", "checkbox"):
            self.options_count_field.height = "40dp"
            self.options_count_field.size_hint_y = None
        else:
            self.options_count_field.height = 0
            self.options_count_field.size_hint_y = None
            self.options_container.clear_widgets()

    def update_options(self, *args):
        try:
            count = int(self.options_count_field.text)
        except:
            count = 0
        self.options_container.clear_widgets()
        for i in range(count):
            option_field = MDTextField(hint_text=f"Вариант {i+1}", size_hint_y=None, height="40dp")
            self.options_container.add_widget(option_field)

class CreateTestScreen(Screen):
    def on_pre_enter(self):
        self.menu = None  # Инициализация меню
        test_id = None

    def create_test(self):
        if not hasattr(self, 'selected_theme_id'):
            toast("Пожалуйста, выберите тему из списка.")
            return

        test_data = {
            "test_name": self.ids.test_name.text,
            "description": self.ids.description.text,
            "time_limit": int(self.ids.time_limit.text or 0),
            "passing_score": int(self.ids.passing_score.text or 0),
            "theme_id": self.selected_theme_id,
            "attempts_limit": int(self.ids.attempts_limit.text or 0)
        }

        app = App.get_running_app()
        headers = {
            "Authorization": f"Bearer {app.token}",
            "Content-Type": "application/json"
        }

        print("Отправляемые данные:", json.dumps(test_data, indent=2))

        UrlRequest(
            url=f"{app.api_url}/tests/",
            req_body=json.dumps(test_data),
            req_headers=headers,
            on_success=self.on_success,
            on_error=self.on_error,
            method='POST'
        )


    def on_error(self, req, error):
        toast(f"Ошибка создания теста: {error}")

    def open_theme_menu(self):
        app = App.get_running_app()
        self.ids.theme_loader.active = True
        UrlRequest(
            url=f"{app.api_url}/themes/",
            req_headers={"Authorization": f"Bearer {app.token}"},
            on_success=self.on_themes_loaded,
            on_error=self.on_error
        )

    def set_theme(self, theme_obj):
        self.ids.theme.text = theme_obj["title"]
        self.selected_theme_id = theme_obj["id"]
        if hasattr(self, 'menu'):
            self.menu.dismiss()

    def open_add_theme_dialog(self):
        self.dialog = MDDialog(
            title="Новая тема",
            type="custom",
            content_cls=MDTextField(hint_text="Название темы"),
            buttons=[
                MDFlatButton(text="ОТМЕНА", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="СОХРАНИТЬ", on_release=self.create_theme),
            ],
        )
        self.dialog.open()

    def create_theme(self, *args):
        theme_title = self.dialog.content_cls.text
        self.dialog.dismiss()
        app = App.get_running_app()
        UrlRequest(
            url=f"{app.api_url}/themes/",
            req_headers={
                "Authorization": f"Bearer {app.token}",
                "Content-Type": "application/json"
            },
            req_body=json.dumps({"title": theme_title}),
            on_success=lambda req, result: self.after_theme_created(result),
            on_error=lambda req, err: toast("Ошибка создания темы"),
            method="POST",
        )

    def after_theme_created(self, new_theme):
        toast("Тема добавлена")
        self.selected_theme_id = new_theme["id"]
        self.ids.theme.text = new_theme["title"]
        self.open_theme_menu()  # Обновить список

    def on_themes_loaded(self, request, result):
        menu_items = []
        for theme in result:
            menu_items.append({
                "text": theme["title"],
                "on_release": lambda x=theme: self.set_theme(x)
            })

        self.ids.theme_loader.active = False

        self.menu = MDDropdownMenu(
            caller=self.ids.theme,
            items=menu_items,
            width_mult=4,
        )
        self.menu.open()

    def create_test_and_load_tasks_ui(self):
        # Сначала создать тест на сервере
        self.create_test()

        # Очистить контейнер заданий (на всякий случай)
        self.ids.tasks_container.clear_widgets()

    def on_success(self, req, result):
        toast("Тест успешно создан!")
        self.test_id = result["id"]

        self.manager.current = "create_test"  # можно оставить
        self.ids.tasks_container.clear_widgets()

        self.create_task_forms()

    def create_task_forms(self):

        container = self.ids.tasks_container
        container.clear_widgets()
        try:
            num = int(self.ids.num_tasks.text)
            if num <= 0:
                raise ValueError
        except:
            toast("Введите корректное число заданий")
            return
        for i in range(num):
            task_form = TaskForm()
            container.add_widget(task_form)
        # Добавим кнопку для отправки заданий
        from kivymd.uix.button import MDRaisedButton
        btn = MDRaisedButton(
            text="Сохранить задания",
            pos_hint={"center_x": 0.5},
            on_release=self.send_tasks_to_server
        )
        container.add_widget(btn)

    def send_tasks_to_server(self, *args):
        if not self.test_id:
            toast("Сначала создайте тест")
            return

        tasks_data = []
        for task_form in self.ids.tasks_container.children:
            # Пропускаем кнопку в конце (если это кнопка)
            if not isinstance(task_form, TaskForm):
                continue

            question = task_form.question_field.text.strip()
            task_type = task_form.task_type
            options = []
            if task_type in ("radio", "checkbox"):
                for option_field in task_form.options_container.children:
                    opt_text = option_field.text.strip()
                    if opt_text:
                        options.append(opt_text)

            if not question:
                toast("Заполните все вопросы")
                return

            task_obj = {
                "question": question,
                "task_type": task_type,
                "options": options,
            }
            tasks_data.append(task_obj)

        if not tasks_data:
            toast("Добавьте задания")
            return

        app = App.get_running_app()
        headers = {
            "Authorization": f"Bearer {app.token}",
            "Content-Type": "application/json"
        }

        body = {
            "test_id": self.test_id,
            "tasks": tasks_data
        }

        print("Отправляем задания:", json.dumps(body, indent=2))

        UrlRequest(
            url=f"{app.api_url}/tasks/",
            req_body=json.dumps(body),
            req_headers=headers,
            on_success=lambda req, result: toast("Задания успешно сохранены!"),
            on_error=lambda req, err: toast(f"Ошибка при сохранении заданий: {err}"),
            method="POST",
        )

