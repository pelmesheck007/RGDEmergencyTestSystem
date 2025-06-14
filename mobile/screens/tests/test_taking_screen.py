import json

from kivy.network.urlrequest import UrlRequest
from kivy.properties import ListProperty, DictProperty, NumericProperty, Clock
from kivy.uix.togglebutton import ToggleButton
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from mobile.screens.base_screen import BaseScreen


class TestTakingScreen(BaseScreen):
    questions = ListProperty([])
    current_index = NumericProperty(0)
    selected_answers = DictProperty({})

    def on_pre_enter(self):
        self.load_test_questions()
        self.remaining_time_label = self.ids.timer_label

    def on_questions_loaded(self, req, result):
        print("DEBUG: Ответ от сервера:", result)

        if not isinstance(result, dict):
            print("Ошибка: ожидается словарь, но получен:", type(result))
            return

        self.questions = result.get("questions", [])
        self.passing_score = result.get("passing_score", 0)
        self.time_limit = result.get("time_limit", 0)
        self.test_name = result.get("test_name", "")
        self.max_score = result.get("max_score", len(self.questions))

        self.current_index = 0
        self.display_question(self.current_index)
        self.start_timer_if_needed()

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


    def on_submit_success(self, req, result):
        print("Ответ успешно отправлен:", result)
        self.show_results_dialog(result)

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


    def go_to_next_question(self):
        # Проверим, выбрал ли пользователь ответ на текущий вопрос
        if self.current_task_id not in self.selected_answers:
            from kivymd.toast import toast
            toast("Пожалуйста, выберите ответ перед продолжением")
            return

        # Перейдем к следующему вопросу, если он есть
        if self.current_index + 1 < len(self.questions):
            self.current_index += 1
            self.display_question(self.current_index)
        else:
            # Последний вопрос — отправляем результаты
            self.submit_test_result()

    def display_question(self, index):
        question = self.questions[index]
        task_id = question["id"]
        self.current_task_id = task_id

        self.ids.question_label.text = question["question"]
        self.ids.answers_box.clear_widgets()

        for answer in question.get("answers", []):
            btn = ToggleButton(
                text=answer["text"],
                group="answers",
                allow_no_selection=False,
                size_hint_y=None,
                height="40dp"
            )
            btn.bind(on_press=lambda btn_instance, a_id=answer["id"]: self.select_answer(a_id))
            self.ids.answers_box.add_widget(btn)

        selected = self.selected_answers.get(task_id, [])
        if selected:
            for btn in self.ids.answers_box.children:
                if btn.text == next((a["text"] for a in question["answers"] if a["id"] == selected[0]), None):
                    btn.state = 'down'

    def show_results_dialog(self, result):
        score = result.get("score", 0)
        max_score = self.max_score
        passing_score = self.passing_score
        percent = (score / max_score * 100) if max_score else 0
        passed = percent >= passing_score

        text = (
            f"Результаты:\n\n"
            f"Ваш балл: {score} из {max_score}\n"
            f"Процент: {percent:.1f}%\n"
            f"Минимум для зачета: {passing_score}%\n\n"
            f"{'ЗАЧЕТ' if passed else 'НЕЗАЧЕТ'}"
        )

        self.results_dialog = MDDialog(
            title="Результаты теста",
            text=text,
            size_hint=(0.8, None),
            height="250dp",
            buttons=[
                MDFlatButton(text="Закрыть", on_release=lambda x: self.results_dialog.dismiss()),
                MDFlatButton(text="На главную", on_release=self.go_to_main_screen)
            ],
        )
        self.results_dialog.open()

    def start_timer_if_needed(self):
        self.remaining_time = self.time_limit  # time_limit должна быть установлена заранее
        if self.remaining_time > 0:
            Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        self.remaining_time -= 1
        print(f"Осталось времени: {self.remaining_time} сек.")

        # Можно обновить UI: например, Label с оставшимся временем
        if self.remaining_time_label:
            self.remaining_time_label.text = f"Осталось времени: {self.remaining_time} сек."

        if self.remaining_time <= 0:
            Clock.unschedule(self.update_timer)
            self.finish_test_due_to_timeout()

    def finish_test_due_to_timeout(self):
        # Здесь логика автосдачи
        print("Время вышло. Отправка результатов...")
        self.submit_test_result()

    def go_to_main_screen(self, *args):
        self.results_dialog.dismiss()
        self.manager.current = "main"