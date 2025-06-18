import json

from kivy.uix.screenmanager import Screen
from kivy.network.urlrequest import UrlRequest
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem, TwoLineRightIconListItem, IconRightWidget, OneLineAvatarIconListItem
from kivymd.toast import toast
from kivy.app import App
from kivymd.uix.selectioncontrol import MDCheckbox

from mobile.screens.base_screen import BaseScreen
from mobile.screens.widgets.menu.main_menu import RoleMenu


class GroupsScreen(BaseScreen):
    screen_title = "Учебные группы"

    def on_pre_enter(self):
        self.load_groups()

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
        for group in result:
            item = TwoLineRightIconListItem(
                text=group["name"],
                secondary_text=f"ID: {group['id']}",
                on_release=lambda x, g=group: self.open_group(g)
            )

            delete_icon = IconRightWidget(
                icon="delete",
                on_release=lambda x, g=group: self.confirm_delete_group(g)
            )
            edit_icon = IconRightWidget(
                icon="pencil",
                on_release=lambda x, g=group: self.edit_group(g)
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

    def confirm_delete_group(self, group):
        self.dialog = MDDialog(
            title="Удалить группу?",
            text=f"Вы уверены, что хотите удалить группу '{group['name']}'?",
            buttons=[
                MDFlatButton(text="Отмена", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="Удалить", on_release=lambda x: self.delete_group(group)),
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

        self.dialog = MDDialog(
            title=f"Назначенные тесты: {group['name']}",
            type="custom",
            content_cls=scroll,
            buttons=[
                MDFlatButton(text="Закрыть", on_release=lambda x: self.dialog.dismiss()),
                # MDRaisedButton(text="Добавить", on_release=self.show_add_test_dialog),
            ],
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

        for test in result:
            item = OneLineListItem(text=test["test_name"])
            self.assigned_tests_box.add_widget(item)
