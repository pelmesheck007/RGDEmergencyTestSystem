import json

from kivy.uix.screenmanager import Screen
from kivy.network.urlrequest import UrlRequest
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem, TwoLineRightIconListItem, IconRightWidget, OneLineAvatarIconListItem, \
    OneLineRightIconListItem
from kivymd.toast import toast
from kivy.app import App
from kivymd.uix.selectioncontrol import MDCheckbox

from mobile.screens.base_screen import BaseScreen
from mobile.screens.widgets.menu.main_menu import RoleMenu


class GroupsScreen(BaseScreen):
    screen_title = "Учебные группы"

    def on_pre_enter(self):
        super().on_pre_enter()

        app = App.get_running_app()
        role = getattr(app, "user_data", {}).get("role", "").lower()

        self.user_role = role
        self.is_admin = role == "admin"
        self.is_teacher = role == "teacher"
        self.is_student = role == "student"
        self.can_edit_group = self.is_admin or self.is_teacher
        self.can_assign_test = self.is_admin or self.is_teacher
        self.can_create_group = self.is_admin or self.is_teacher

        self.setup_top_bar_buttons()
        self.load_groups()

    def setup_top_bar_buttons(self):
        top_bar = self.ids.menu_button
        top_bar.right_action_items = []  # Очистим на всякий случай

        if self.can_create_group:
            top_bar.right_action_items = [["plus", lambda x: setattr(self.manager, 'current', 'create_group')]]

    def load_groups(self):
        self.ids.groups_box.clear_widgets()
        headers = {
            "Authorization": f"Bearer {App.get_running_app().token}",
            "Content-Type": "application/json"
        }

        UrlRequest(
            url=f"{App.get_running_app().api_url}/groups/",
            req_headers=headers,
            on_success=self.on_success,
            on_error=self.on_error,
            method='GET'
        )

    def on_success(self, req, result):
        self.groups = result  # сохраняем для повторного использования
        app = App.get_running_app()
        role = getattr(app, "user_data", {}).get("role", "").lower()

        for group in result:
            item = TwoLineRightIconListItem(
                text=group["name"],
                on_release=lambda x, g=group: self.open_group(g)
            )

            if role in ["admin", "teacher"]:
                edit_icon = IconRightWidget(
                    icon="pencil",
                    on_release=lambda x, g=group: self.edit_group(g)
                )
                delete_icon = IconRightWidget(
                    icon="delete",
                    on_release=lambda x, g=group: self.confirm_delete_group(g)
                )
                item.add_widget(edit_icon)
                item.add_widget(delete_icon)

            self.ids.groups_box.add_widget(item)

    def edit_group(self, group):
        App.get_running_app().current_group = group
        self.manager.current = "edit_group"

    def open_group(self, group):
        App.get_running_app().current_group = group
        self.show_assigned_tests_dialog(group)


    def on_error(self, req, error):
        toast("Ошибка загрузки групп")

    def open_menu(self):
        role = getattr(App.get_running_app(), "user_data", {}).get("role", None)
        if role:
            RoleMenu(self.ids["menu_button"], role).open()
        else:
            self.show_error("Роль пользователя не определена.")

    def confirm_unassign_test(self, test_id):
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton

        def unassign(*args):
            self.unassign_test(test_id)
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title="Удаление теста",
            text="Вы уверены, что хотите удалить этот тест?",
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="Удалить", on_release=unassign),
            ],
        )
        self.dialog.open()

    def delete_group(self, group):
        self.dialog.dismiss()
        headers = {
            "Authorization": f"Bearer {App.get_running_app().token}",
            "Content-Type": "application/json"
        }

        UrlRequest(
            url=f"{App.get_running_app().api_url}/groups/{group['id']}",
            req_headers=headers,
            method='DELETE',
            on_success=lambda req, res: self.on_group_deleted(group),
            on_error=self.on_delete_error
        )

    def on_group_deleted(self, group):
        toast(f"Группа '{group['name']}' удалена")
        self.load_groups()

    def on_delete_error(self, req, error):
        toast("Ошибка при удалении группы")






    def load_all_tests(self):
        headers = {
            "Authorization": f"Bearer {App.get_running_app().token}",
            "Content-Type": "application/json"
        }
        # Запрос всех тестов (или по каким-то фильтрам)
        UrlRequest(
            url=f"{App.get_running_app().api_url}/tests/",
            req_headers=headers,
            on_success=self.on_all_tests_loaded,
            on_error=lambda *args: toast("Ошибка загрузки тестов"),
            method='GET'
        )

    def on_all_tests_loaded(self, req, result):
        self.all_tests = result  # список всех тестов
        self.show_assign_dialog()

    def show_assign_dialog(self):
        group = App.get_running_app().current_group

        # Формируем список с чекбоксами, выбранные - уже назначенные
        self.test_items = []
        assigned_test_ids = {t['id'] for t in self.assigned_tests}

        items = []
        for test in self.all_tests:
            item = OneLineAvatarIconListItem(text=test['test_name'])
            item.test_id = test['id']
            checkbox = MDCheckbox(
                size_hint=(None, None),
                size=("48dp", "48dp"),
                active=test['id'] in assigned_test_ids
            )
            checkbox.bind(active=self.on_checkbox_active)
            item.add_widget(checkbox)
            items.append(item)
            self.test_items.append((item, checkbox))

        self.dialog = MDDialog(
            title=f"Назначить тесты группе '{group['name']}'",
            type="custom",
            content_cls=MDBoxLayout(
                orientation='vertical',
                spacing="12dp",
                size_hint_y=None,
                height="400dp",
                children=items
            ),
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="Сохранить", on_release=self.save_assigned_tests)
            ]
        )
        self.dialog.open()

    def on_checkbox_active(self, checkbox, value):
        # Можно обработать сразу, если нужно
        pass

    def save_assigned_tests(self, *args):
        self.dialog.dismiss()
        group = App.get_running_app().current_group

        selected_tests = [
            item.test_id for item, checkbox in self.test_items if checkbox.active
        ]

        headers = {
            "Authorization": f"Bearer {App.get_running_app().token}",
            "Content-Type": "application/json"
        }

        data = {
            "test_ids": selected_tests
        }

        # Запрос для обновления назначенных тестов — предполагается POST или PUT
        UrlRequest(
            url=f"{App.get_running_app().api_url}/groups/{group['id']}/assigned_tests",
            req_headers=headers,
            req_body=json.dumps(data),
            method="POST",
            on_success=lambda *args: toast("Назначения обновлены"),
            on_error=lambda *args: toast("Ошибка обновления назначений"),
        )

    from kivymd.uix.boxlayout import MDBoxLayout

    def show_assigned_tests_dialog(self, group):
        self.current_group_id = group["id"]

        # Создаем контейнер для списка назначенных тестов с вертикальным расположением и отступами
        self.assigned_tests_box = MDBoxLayout(
            orientation='vertical',
            spacing="8dp",
            padding="16dp",
            size_hint_y=None
        )
        self.assigned_tests_box.bind(minimum_height=self.assigned_tests_box.setter("height"))
        scroll = ScrollView(size_hint=(1, None), size=("400dp", "400dp"))
        scroll.add_widget(self.assigned_tests_box)

        buttons = [
            MDFlatButton(text="Закрыть", on_release=lambda x: self.dialog.dismiss())
        ]

        if self.can_assign_test:
            buttons.append(MDRaisedButton(text="Добавить", on_release=self.show_add_test_dialog))

        self.dialog = MDDialog(
            title=f"Назначенные тесты: {group['name']}",
            type="custom",
            content_cls=scroll,
            buttons=buttons,
        )
        self.dialog.open()

        # Загружаем и отображаем назначенные тесты для выбранной группы
        self.load_assigned_tests(group["id"])

    def load_assigned_tests(self, group_id):
        headers = {
            "Authorization": f"Bearer {App.get_running_app().token}",
            "Content-Type": "application/json"
        }

        UrlRequest(
            url=f"{App.get_running_app().api_url}/groups/{group_id}/assigned_tests",
            req_headers=headers,
            method='GET',
            on_success=self.on_assigned_tests_loaded,
            on_error=lambda *a: toast("Ошибка загрузки тестов")
        )

    def on_assigned_tests_loaded(self, req, result):
        self.assigned_tests_box.clear_widgets()

        if not result:
            self.assigned_tests_box.add_widget(
                OneLineListItem(text="Нет назначенных тестов")
            )
            return

        app = App.get_running_app()
        role = getattr(app, "user_data", {}).get("role", "").lower()

        for test in result:
            item = OneLineRightIconListItem(text=test["test_name"])

            if role in ["admin", "teacher"]:
                delete_icon = IconRightWidget(
                    icon="delete",
                    on_release=lambda x, t_id=test["id"]: self.confirm_unassign_test(t_id)
                )
                item.add_widget(delete_icon)

            self.assigned_tests_box.add_widget(item)

    def show_add_test_dialog(self, *args):
        app = App.get_running_app()
        url = f"{App.get_running_app().api_url}/tests/"

        def on_success(req, result):
            # Создаём контейнер с фиксированной высотой
            menu_layout = MDBoxLayout(
                orientation="vertical",
                spacing="8dp",
                padding="8dp",
                size_hint_y=None
            )
            menu_layout.bind(minimum_height=menu_layout.setter("height"))

            # Оборачиваем в ScrollView с фиксированной высотой
            scroll = ScrollView(
                size_hint=(1, None),
                height="300dp"  # <= обязательно: иначе ничего не будет видно!
            )
            scroll.add_widget(menu_layout)

            for test in result:
                def on_select(_, test_id=test["id"]):
                    self.assign_test_and_close(test_id)
                    self.add_test_dialog.dismiss()

                item = OneLineListItem(text=test["test_name"])
                item.bind(on_release=on_select)
                menu_layout.add_widget(item)

            self.add_test_dialog = MDDialog(
                title="Выберите тест",
                type="custom",
                content_cls=scroll,
                buttons=[
                    MDFlatButton(text="Отмена", on_release=lambda x: self.add_test_dialog.dismiss())
                ]
            )
            self.add_test_dialog.open()

            print("Полученные тесты:", result)

        def on_error(*args):
            print("Ошибка загрузки тестов:", args)

        UrlRequest(url, on_success=on_success, on_error=on_error)

    def assign_test_and_close(self, test_id):
        app = App.get_running_app()
        group_id = self.current_group_id
        if not group_id:
            toast("Группа не выбрана")
            return

        headers = {
            "Authorization": f"Bearer {app.token}",
            "Content-Type": "application/json"
        }

        data = json.dumps({"test_id": test_id})

        def on_success(req, result):
            toast("Тест назначен")
            self.add_test_dialog.dismiss()
            self.load_assigned_tests(group_id)

        def on_error(req, error):
            toast("Ошибка назначения теста")

        UrlRequest(
            url=f"{App.get_running_app().api_url}/groups/{group_id}/assigned_tests",
            req_headers=headers,
            req_body=data,
            method="POST",
            on_success=on_success,
            on_error=on_error
        )

    def unassign_test(self, test_id):
        app = App.get_running_app()
        url = f"{App.get_running_app().api_url}/groups/{self.current_group_id}/assigned_tests/{test_id}"

        def on_success(req, result):
            self.load_assigned_tests(self.current_group_id)

        UrlRequest(url, method="DELETE", on_success=on_success)

