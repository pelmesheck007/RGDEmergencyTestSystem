import json

from kivy.network.urlrequest import UrlRequest
from kivy.properties import ListProperty, DictProperty, NumericProperty, Clock, StringProperty
from kivy.uix.togglebutton import ToggleButton
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

from mobile.screens.base_screen import BaseScreen


class TestTakingScreen(BaseScreen):
    questions = ListProperty([])
    current_index = NumericProperty(0)
    selected_answers = DictProperty({})
    test_type = StringProperty("standard")  # "standard" или "scenario"
    selected_test_id = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time_limit = None
        self.remaining_time = None


    def on_pre_enter(self):
        self.remaining_time_label = self.ids.timer_label

        if self.test_type == "standard":
            self.ids.next_button.opacity = 1
            self.ids.next_button.disabled = False
            self.load_normal_test()
        else:
            self.ids.next_button.opacity = 0
            self.ids.next_button.disabled = True
            self.start_scenario()

        if self.selected_test_id:
            self.load_test_data()

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
        if self.current_task_id not in self.selected_answers:
            from kivymd.toast import toast
            toast("Пожалуйста, выберите ответ перед продолжением")
            return

            # Перейдем к следующему вопросу, если он есть
        if self.current_index + 1 < len(self.questions):
            self.current_index += 1
            self.display_question(self.current_index)
        else:
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
                MDFlatButton(text="Закрыть", on_release=lambda x: self.go_to_tests_screen),
                MDFlatButton(text="На главную", on_release=self.go_to_main_screen)
            ],
        )
        self.results_dialog.open()

    def update_timer(self, dt):
        self.remaining_time -= 1

        if self.remaining_time_label:
            self.remaining_time_label.text = f"Осталось времени: {self.remaining_time} сек."

        if self.remaining_time <= 0:
            Clock.unschedule(self.update_timer)
            self.finish_test_due_to_timeout()

    def go_to_main_screen(self, *args):
        self.results_dialog.dismiss()
        self.manager.current = "main"
        self.results_dialog.dismiss()

    def go_to_tests_screen(self, *args):
        self.results_dialog.dismiss()
        self.manager.current = "tests"
        self.results_dialog.dismiss()

    def load_normal_test(self):
        self.load_test_questions()  # твой существующий метод

    def load_scenario_test(self):
        headers = {
            'Authorization': f'Bearer {self.app.token}',
            'Content-Type': 'application/json'
        }
        # Получаем первый шаг сценария
        UrlRequest(
            f"{self.app.api_url}/scenario-tests/{self.app.current_test_id}/steps",
            req_headers=headers,
            on_success=self.on_scenario_steps_loaded,
            on_error=self.on_load_error,
            on_failure=self.on_load_error,
            timeout=10
        )

    def on_scenario_steps_loaded(self, req, result):
        # result — список шагов сценария
        if not isinstance(result, list) or len(result) == 0:
            from kivymd.toast import toast
            toast("Не удалось загрузить шаги сценария")
            return
        self.scenario_steps = result
        self.current_index = 0
        self.display_scenario_step(self.current_index)

    def display_scenario_step(self, index):
        step = self.scenario_steps[index]
        self.current_task_id = step["id"]

        self.ids.question_label.text = step.get("text", "Нет текста шага")
        self.ids.answers_box.clear_widgets()

        for choice in step.get("choices", []):
            btn = ToggleButton(
                text=choice["choice_text"],
                group="answers",
                allow_no_selection=False,
                size_hint_y=None,
                height="40dp"
            )
            btn.bind(on_press=lambda btn_instance, c_id=choice["id"]: self.select_scenario_choice(c_id))
            self.ids.answers_box.add_widget(btn)

    def select_scenario_choice(self, choice_id):
        # Сохраняем выбор для текущего шага
        self.selected_answers[self.current_task_id] = [choice_id]

        # Переход к следующему шагу
        if self.current_index + 1 < len(self.scenario_steps):
            self.current_index += 1
            self.display_scenario_step(self.current_index)
        else:
            # Конец сценария — отправляем результат
            self.submit_scenario_result()

    def submit_scenario_result(self):
        headers = {"Authorization": f"Bearer {self.app.token}", "Content-Type": "application/json"}

        data = {
            "scenario_id": self.app.current_test_id,
            "user_id": self.app.user_id,
            "answers": [
                {
                    "step_id": step_id,
                    "choice_ids": choice_ids
                }
                for step_id, choice_ids in self.selected_answers.items()
            ]
        }

        UrlRequest(
            f"{self.app.api_url}/scenario-tests/{self.app.current_test_id}/log",
            req_body=json.dumps(data),
            req_headers=headers,
            on_success=self.on_submit_success,
            on_error=self.on_submit_error,
            method='POST'
        )

    def load_test_data(self):
        # В зависимости от типа загружаем тест с разного эндпоинта
        if self.test_type == "standard":
            url = f"{self.app.api_url}/tests/{self.selected_test_id}"
        else:
            url = f"{self.app.api_url}/scenario-tests/{self.selected_test_id}"

        headers = {}

        UrlRequest(
            url,
            on_success=self.on_test_data_loaded,
            on_error=self.on_test_data_error,
            on_failure=self.on_test_data_error,
            req_headers=headers,
            timeout=10
        )

    def on_test_data_error(self, req, error):
        from kivymd.toast import toast
        toast(f"Ошибка загрузки теста: {error}")

    def start_test(self):
        # Запуск теста, в зависимости от типа можно показывать разный интерфейс
        if self.test_type == "standard":
            # логика старта стандартного теста
            print("Старт стандартного теста")
        else:
            # логика старта сценарного теста
            print("Старт сценарного теста")

    def start_scenario(self):
        headers = {'Authorization': f'Bearer {self.app.token}'}
        UrlRequest(
            f"{self.app.api_url}/scenario-tests/{self.app.current_test_id}/start",
            req_headers=headers,
            on_success=self.on_scenario_step_loaded,
            on_error=self.on_load_error,
            on_failure=self.on_load_error
        )

    def on_scenario_step_loaded(self, req, result):
        self.current_step = result
        self.display_scenario_step_data(result)
        self.start_timer_if_needed()


    def display_scenario_step_data(self, step):
        self.ids.question_label.text = step["text"]
        self.ids.answers_box.clear_widgets()
        for choice in step.get("choices", []):
            btn = ToggleButton(
                text=choice["choice_text"],
                group="answers",
                allow_no_selection=False,
                size_hint_y=None,
                height="40dp"
            )
            btn.bind(on_press=lambda btn_inst, c=choice: self.make_choice(step["id"], c["id"]))
            self.ids.answers_box.add_widget(btn)

    def make_choice(self, step_id, choice_id):
        data = {
            "step_id": step_id,
            "choice_id": choice_id,
            "user_id": self.app.user_id,
            "time_taken": 0
        }
        headers = {'Authorization': f'Bearer {self.app.token}', 'Content-Type': 'application/json'}
        UrlRequest(
            f"{self.app.api_url}/scenario-tests/{self.app.current_test_id}/step",
            req_body=json.dumps(data),
            req_headers=headers,
            on_success=self.on_choice_response,
            on_error=self.on_load_error,
            on_failure=self.on_load_error,
            method="POST"
        )

    def on_choice_response(self, req, result):
        print("Ответ от сервера на выбор:", result)

        if result.get("end"):
            self.show_scenario_result_dialog(result)
        else:
            next_step = result.get("next_step")
            if next_step:
                self.current_step = next_step
                self.display_scenario_step_data(next_step)
            else:
                print("❗ Нет next_step в ответе. Сценарий завис.")
                from kivymd.toast import toast
                toast("Сценарий не может продолжиться: сервер не прислал следующий шаг.")


    def show_scenario_result_dialog(self, result):
        next_step = result.get("next_step")

        if next_step:
            final_text = next_step.get("text", "")
        else:
            final_text = result.get("message", "Сценарий завершён.")

        self.results_dialog = MDDialog(
            title="Результаты сценария",
            text=final_text,
            size_hint=(0.8, None),
            height="250dp",
            buttons=[
                MDFlatButton(text="Закрыть", on_release=lambda x: self.go_to_tests_screen()),
                MDFlatButton(text="На главную", on_release=self.go_to_main_screen)
            ],
        )
        self.results_dialog.open()

    def finish_test_due_to_timeout(self):
        print("Время вышло. Отправка результатов...")

        if self.test_type == "standard":
            self.submit_test_result()
        elif self.test_type == "scenario":
            self.submit_scenario_result()

    def start_timer_if_needed(self):
        if not isinstance(self.time_limit, (int, float)) or self.time_limit <= 0:
            print("Таймер не запущен: время не указано или нулевое.")
            return

        self.remaining_time = self.time_limit
        Clock.schedule_interval(self.update_timer, 1)

    def on_test_data_loaded(self, req, result):
        print(f"Тест загружен ({self.test_type}):", result)
        self.time_limit = result.get("time_limit", 0)
        self.test_name = result.get("test_name", "")
        self.start_timer_if_needed()
