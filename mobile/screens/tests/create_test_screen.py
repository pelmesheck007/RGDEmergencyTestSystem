from kivy.app import App
from kivy.properties import StringProperty, Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.network.urlrequest import UrlRequest
from kivymd.toast import toast
from kivymd.uix.bottomsheet import MDListBottomSheet
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem, OneLineAvatarListItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField
import json

from mobile.screens.base_screen import BaseScreen


class TaskForm(MDBoxLayout):
    def __init__(self, task_number=1, total_tasks=1, **kwargs):
        super().__init__(**kwargs)
        self.task_type = "text"
        self.ids.title_label.text = f"Задание {task_number} ({task_number} из {total_tasks})"
        self.ids.options_count_field.height = 0
        self.ids.options_count_field.opacity = 0
        self.user_data = None
        self.user_id = None



    def open_task_type_menu(self):
        bottom_sheet = MDListBottomSheet()

        types = [
            {"text": "Текст", "type": "text"},
            {"text": "Множественный выбор", "type": "checkbox"},
        ]

        for item in types:
            bottom_sheet.add_item(
                item["text"],
                lambda x, t=item["type"]: self.on_task_type_change(t),
                icon="format-text" if item["type"] == "text" else "checkbox-marked-circle-outline"
            )

        bottom_sheet.open()

    def on_task_type_change(self, selected_type):
        self.task_type = selected_type
        self.ids.type_button.text = f"Тип: {selected_type}"
        self.ids.options_container.clear_widgets()

        if selected_type == "checkbox":
            self.ids.options_count_field.height = 48
            self.ids.options_count_field.opacity = 1
        else:
            self.ids.options_count_field.height = 0
            self.ids.options_count_field.opacity = 0

    def update_options(self, *args):
        try:
            count = int(self.ids.options_count_field.text)
            if count <= 0:
                raise ValueError
        except ValueError:
            toast("Введите положительное число вариантов")
            return

        self.ids.options_container.clear_widgets()

        for i in range(count):
            row = BoxLayout(orientation="horizontal", spacing="10dp",
                          size_hint_y=None, height="48dp")

            checkbox = MDCheckbox(
                size_hint_x=0.15,
                active=False
            )

            option_field = MDTextField(
                hint_text=f"Вариант {i + 1}",
                size_hint_x=0.85,
                multiline=False
            )

            row.add_widget(checkbox)
            row.add_widget(option_field)
            self.ids.options_container.add_widget(row)

    def get_task_data(self):
        question = self.ids.question_field.text.strip()
        if not question:
            return None

        options = []
        correct_answers = []

        if self.task_type == "checkbox":
            for row in self.ids.options_container.children:
                checkbox, option_field = row.children[::-1]  # Разворачиваем список
                option_text = option_field.text.strip()
                if option_text:
                    options.append(option_text)
                    if checkbox.active:
                        correct_answers.append(option_text)

        return {
            "question": question,
            "task_type": self.task_type,
            "options": options if self.task_type == "checkbox" else [],
            "correct_answers": correct_answers,
        }

    def go_back(self):
        self.manager.current = "tests"  # Название экрана со списком тестов (или задач)


class CreateTestScreen(BaseScreen):
    selected_theme_name = StringProperty("Выберите тему *")
    selected_theme_id = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_dialog = None
        self.test_id = None
        self.selected_theme_id = ""
        self.selected_theme_name = "Выберите тему *"
        self.themes = []
        self.user_id = None

    def go_back(self):
        self.manager.current = "tests"

    def show_tasks_section(self):
        self.ids.test_form_box.opacity = 0
        self.ids.test_form_box.disabled = True
        self.ids.test_form_box.size_hint_y = None
        self.ids.test_form_box.height = 0

        self.ids.tasks_section.opacity = 1
        self.ids.tasks_section.disabled = False
        self.ids.tasks_section.size_hint_y = None
        self.ids.tasks_section.height = self.ids.tasks_section.minimum_height


    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.app = App.get_running_app()  # Получаем ссылку на приложение

        self.selected_theme_id = ""
        self.selected_theme_name = "Выберите тему *"
        self.ids.theme.text = self.selected_theme_name

        if hasattr(self.app, 'user_data') and self.app.user_data:
            print("Пользователь:", self.app.user_data.get("full_name", "Неизвестно"))
            self.user_id = self.app.user_data['id']

    def show_task_creation_ui(self):
        self.ids.test_form_box.disabled = True
        self.ids.test_form_box.opacity = 0.3  # Приглушение
        self.ids.tasks_section.disabled = False
        self.ids.tasks_section.opacity = 1  # Сделать видимым
        self.create_task_forms()

    def create_test(self):
        if not hasattr(self, 'selected_theme_id') or not self.selected_theme_id:
            toast("Выберите тему теста")
            return

        try:
            test_data = {
                "test_name": self.ids.test_name.text.strip(),
                "description": self.ids.description.text.strip(),
                "time_limit": int(self.ids.time_limit.text or 0),
                "passing_score": int(self.ids.passing_score.text or 0),
                "theme_id": self.selected_theme_id,
                "attempts_limit": int(self.ids.attempts_limit.text or 0)
            }
        except ValueError:
            toast("Проверьте числовые поля")
            return

        if not test_data["test_name"]:
            toast("Введите название теста")
            return

        app = App.get_running_app()
        headers = {
            "Authorization": f"Bearer {app.token}",
            "Content-Type": "application/json"
        }

        UrlRequest(
            url=f"{app.api_url}/tests/",
            req_body=json.dumps(test_data),
            req_headers=headers,
            on_success=self.on_test_created,
            on_error=self.on_error,
            method='POST'
        )

    def on_test_created(self, req, result):
        self.test_id = result["id"]
        toast("Тест создан! Добавьте задания")
        self.show_task_creation_ui()
        #self.show_tasks_section()

    def show_test_form(self):
        self.ids.test_form_box.disabled = False
        self.ids.test_form_box.opacity = 1  # Полная видимость
        self.ids.tasks_section.disabled = True
        self.ids.tasks_section.opacity = 0  # Скрыть задания

    def create_task_forms(self):
        try:
            num_tasks = int(self.ids.num_tasks.text)
            if num_tasks <= 0:
                raise ValueError
        except ValueError:
            toast("Введите корректное число заданий")
            return

        self.ids.tasks_container.clear_widgets()

        for i in range(num_tasks):
            task_form = TaskForm(task_number=i + 1, total_tasks=num_tasks)
            self.ids.tasks_container.add_widget(task_form)

        # Добавляем кнопки управления
        buttons_box = BoxLayout(size_hint_y=None, height="80dp", spacing="10dp")

        back_btn = MDRaisedButton(
            text="Назад к тесту",
            on_release=lambda x: self.show_test_form()
        )

        save_btn = MDRaisedButton(
            text="Сохранить задания",
            on_release=lambda x: self.send_tasks_to_server()
        )

        add_btn = MDRaisedButton(
            text="+ Добавить задание",
            on_release=lambda x: self.add_single_task()
        )

        buttons_box.add_widget(back_btn)
        buttons_box.add_widget(save_btn)
        buttons_box.add_widget(add_btn)

        self.ids.tasks_container.add_widget(buttons_box)

    def add_single_task(self):
        current_forms = len([w for w in self.ids.tasks_container.children if isinstance(w, TaskForm)])
        new_form = TaskForm(task_number=current_forms + 1, total_tasks=current_forms + 1)
        self.ids.tasks_container.add_widget(new_form, index=0)  # Добавляем в начало
        self.update_task_numbers()

    def update_task_numbers(self):
        forms = [w for w in self.ids.tasks_container.children if isinstance(w, TaskForm)]
        for i, form in enumerate(reversed(forms), 1):
            form.ids.title_label.text = f"Задание {i} ({i} из {len(forms)})"

    def send_tasks_to_server(self, *args):
        if not self.test_id:
            toast("Сначала создайте тест")
            return

        # Маппинг типов взаимодействия
        INTERACTION_TYPES = {
            "text": 1,
            "checkbox": 2,
            "multiple_choice": 2
        }

        # Маппинг уровней сложности
        DIFFICULTY_LEVELS = {
            "easy": 1,
            "medium": 2,
            "hard": 3
        }

        tasks_data = []
        for widget in self.ids.tasks_container.children:
            if isinstance(widget, TaskForm):
                task_data = widget.get_task_data()
                if not task_data:
                    toast("Заполните все вопросы")
                    return

                if task_data["task_type"] == "checkbox" and not task_data["options"]:
                    toast("Добавьте варианты ответа для всех заданий")
                    return

                # Преобразуем данные в формат сервера
                validated_data = {
                    "question": task_data["question"],
                    "interaction_type": INTERACTION_TYPES.get(task_data["task_type"], 1),
                    "time_limit": 60,
                    "difficulty_level": DIFFICULTY_LEVELS.get("easy", 1),
                    "theme": self.selected_theme_id,
                    #"count_variables": len(task_data.get("options", []))
                }

                if task_data["task_type"] == "checkbox":
                    validated_data["variable_answers"] = [
                        {
                            "string_answer": opt,
                            "truthful": opt in task_data["correct_answers"],
                            "order_number": i
                        } for i, opt in enumerate(task_data["options"])
                    ]

                tasks_data.append(validated_data)

        if not tasks_data:
            toast("Добавьте хотя бы одно задание")
            return

        app = App.get_running_app()
        headers = {
            "Authorization": f"Bearer {app.token}",
            "Content-Type": "application/json"
        }

        body = {
            "test_id": str(self.test_id),
            "creator_id": self.user_id,
            "tasks": tasks_data
        }

        print("Отправляемые данные:", json.dumps(body, indent=2, ensure_ascii=False))

        UrlRequest(
            url=f"{app.api_url}/tasks/",
            req_body=json.dumps(body, ensure_ascii=False).encode('utf-8'),
            req_headers=headers,
            on_success=lambda req, res: self.on_tasks_created(),
            on_failure=lambda req, err: toast(f"Ошибка сервера: {err}"),
            on_error=lambda req, err: toast(f"Сетевая ошибка: {err}"),
            method="POST"
        )

    def on_tasks_created(self):
        try:
            toast("Задания сохранены!")
            tests_screen = self.manager.get_screen("tests")
            if hasattr(tests_screen, 'on_pre_enter'):
                tests_screen.on_pre_enter()
            #self.manager.current = "tests"

            return True
        except Exception as e:
            Logger.error(f"TasksScreen: Error saving tasks - {str(e)}")
            toast("Ошибка при сохранении заданий!")
            return False

    def get_task_data(self):
        question = self.ids.question_field.text.strip()
        if not question:
            return None

        options = []
        correct_answers = []

        if self.task_type == "checkbox":
            for row in self.ids.options_container.children:
                checkbox, option_field = row.children[::-1]  # Разворачиваем список
                option_text = option_field.text.strip()
                if option_text:
                    options.append(option_text)
                    if checkbox.active:
                        correct_answers.append(option_text)

        return {
            "question": question,
            "task_type": self.task_type,
            "options": options if self.task_type == "checkbox" else [],
            "correct_answers": correct_answers,
            "difficulty": "easy"
        }

    def open_theme_menu(self):
        app = App.get_running_app()
        self.ids.theme_loader.active = True

        from kivymd.uix.list import OneLineListItem

        def on_themes_loaded(req, result):
            self.ids.theme_loader.active = False

            if not result or not isinstance(result, list):
                toast("Нет доступных тем или ошибка формата данных")
                return

            print("Полученные темы с сервера:", result)

            self.themes = result  # Сохраняем список тем

            bottom_sheet = MDListBottomSheet()

            for theme in self.themes:
                title = theme.get("title")
                if not title:
                    continue

                bottom_sheet.add_item(
                    title,
                    lambda x, t=theme: self.set_selected_theme(t),
                    icon="format-list-bulleted"  # или любой другой иконкой
                )

            bottom_sheet.open()

        UrlRequest(
            url=f"{app.api_url}/themes/",
            req_headers={"Authorization": f"Bearer {app.token}"},
            on_success=on_themes_loaded,
            on_failure=lambda req, err: toast(f"Ошибка загрузки тем: {err}"),
            on_error=lambda req, err: toast(f"Ошибка сети: {err}")
        )

    def set_selected_theme(self, theme):
        self.selected_theme_id = theme['id']
        self.ids.theme.text = theme.get('title', 'Без названия')
        if hasattr(self, 'theme_dialog') and self.theme_dialog:
            self.theme_dialog.dismiss()


    def set_theme_and_close(self, theme_obj, dialog):
        self.selected_theme_id = theme_obj["id"]
        self.ids.theme.text = theme_obj["title"]
        dialog.dismiss()

    def set_theme(self, theme_obj):
        self.selected_theme_id = theme_obj["id"]
        self.ids.theme.text = theme_obj["title"]
        if hasattr(self, 'menu') and self.menu:
            self.menu.dismiss()

    def open_add_theme_dialog(self):
        self.dialog = MDDialog(
            title="Новая тема",
            type="custom",
            content_cls=MDTextField(hint_text="Название темы"),
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="Создать", on_release=self.create_theme),
            ],
        )
        self.dialog.open()

    def create_theme(self, *args):
        theme_title = self.dialog.content_cls.text.strip()
        self.dialog.dismiss()

        if not theme_title:
            toast("Введите название темы")
            return

        app = App.get_running_app()
        UrlRequest(
            url=f"{app.api_url}/themes/",
            req_headers={
                "Authorization": f"Bearer {app.token}",
                "Content-Type": "application/json"
            },
            req_body=json.dumps({"title": theme_title}),
            on_success=lambda req, res: self.after_theme_created(res),
            on_error=lambda req, err: toast("Ошибка создания темы"),
            method="POST"
        )

    def after_theme_created(self, new_theme):
        self.selected_theme_id = new_theme["id"]
        self.ids.theme.text = new_theme["title"]
        toast("Тема создана")
        self.open_theme_menu()  # Обновляем меню

    def on_error(self, req, error):
        toast(f"Ошибка: {error}")
        self.ids.test_form_box.disabled = False
        #Animation(opacity=0.3, duration=0.3, t='out_quad').start(self.ids.test_form_box)