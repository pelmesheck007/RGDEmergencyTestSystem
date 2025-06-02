import json

from kivy.network.urlrequest import UrlRequest
from kivy.properties import ListProperty, DictProperty, NumericProperty
from kivy.uix.togglebutton import ToggleButton

from mobile.screens.base_screen import BaseScreen


class TestTakingScreen(BaseScreen):
    questions = ListProperty([])
    current_index = NumericProperty(0)
    selected_answers = DictProperty({})

    def on_pre_enter(self):
        self.load_test_questions()


    def on_questions_loaded(self, req, result):
        self.questions = result
        self.display_question(0)

    def select_answer(self, answer_id):
        self.selected_answers[self.current_task_id] = [answer_id]

    def submit_test_result(self):
        headers = {"Authorization": f"Bearer {self.app.token}", "Content-Type": "application/json"}

        data = {
            "test_id": self.app.current_test_id,
            "student_id": self.app.user_id,
            "answers": [
                {
                    "task_id": task_id,
                    "selected_variable_ids": selected_ids,
                    "string_answer": None,  # если текстовый
                    "time_spent": 20  # пример
                }
                for task_id, selected_ids in self.selected_answers.items()
            ]
        }

        UrlRequest(
            f"{self.app.api_url}/answers/",
            req_body=json.dumps(data),
            req_headers=headers,
            on_success=self.on_submit_success,
            on_error=self.on_submit_error,
            method='POST'
        )

    def display_question(self, index):
        question = self.questions[index]
        task = question["task"]
        task_id = task["id"]
        self.current_task_id = task_id  # ⬅ сохраняем текущий task_id

        self.ids.question_label.text = task["question"]
        self.ids.answers_box.clear_widgets()

        for answer in question["variable_answers"]:
            btn = ToggleButton(
                text=answer["string_answer"],
                group="answers",
                allow_no_selection=False,
                size_hint_y=None,
                height="40dp"
            )
            btn.bind(on_press=lambda btn_instance, a_id=answer["id"]: self.select_answer(a_id))
            self.ids.answers_box.add_widget(btn)

    def on_submit_success(self, req, result):
        print("Ответ успешно отправлен:", result)
        self.manager.current = "results"  # или другая страница

    def on_submit_error(self, req, error):
        print("Ошибка отправки:", error)
        self.ids.error_label.text = "Не удалось отправить ответы. Проверьте соединение."


    def on_load_error(self, request, error):
        """Обработка ошибки при загрузке данных теста"""
        from kivymd.toast import toast
        error_msg = str(error) if error else "Ошибка загрузки теста"
        toast(f"Ошибка: {error_msg}")
        print(f"[Ошибка загрузки теста] {error_msg}")

    def load_test_questions(self):
        from kivy.network.urlrequest import UrlRequest

        headers = {
            'Authorization': f'Bearer {self.app.token}',
            'Content-Type': 'application/json'
        }

        UrlRequest(
            f"{self.app.api_url}/tests/{self.app.current_test_id}/questions/",
            req_headers=headers,
            on_success=self.on_questions_loaded,
            on_error=self.on_load_error,
            on_failure=self.on_load_error,
            timeout=10
        )
