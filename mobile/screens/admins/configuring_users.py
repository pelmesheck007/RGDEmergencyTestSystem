# mobile/screens/users/configuring_users_screen.py
import json

from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout

from mobile.screens.base_screen import BaseScreen
from kivymd.uix.list import TwoLineRightIconListItem, IconRightWidget
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
from kivy.network.urlrequest import UrlRequest
from kivy.properties import ListProperty, DictProperty, StringProperty
from kivymd.uix.menu import MDDropdownMenu


class ConfiguringUsersScreen(BaseScreen):
    users = ListProperty([])

    def on_screen_enter(self):
        self.screen_title = "Управление пользователями"
        self.load_users()

    def load_users(self):
        headers = self._auth_headers()
        UrlRequest(
            f"{self.app.api_url}/users/",
            on_success=self.on_users_loaded,
            on_error=self.on_load_error,
            on_failure=self.on_load_error,
            req_headers=headers
        )

    def on_users_loaded(self, req, result):
        self.users = result
        self.display_users()

    def display_users(self):
        self.ids.content.clear_widgets()
        for user in self.users:
            item = TwoLineRightIconListItem(
                text=user.get("full_name") or user.get("username"),
                secondary_text=f"{user.get('email')} ({user.get('role')})",
                on_release=lambda x, u=user: self.show_edit_user_dialog(u)
            )
            delete_icon = IconRightWidget(icon="delete", on_release=lambda x, u=user: self.confirm_delete_user(u))
            item.add_widget(delete_icon)
            self.ids.content.add_widget(item)

    def confirm_delete_user(self, user):
        self.dialog = MDDialog(
            title="Удаление пользователя",
            text=f"Удалить пользователя {user['username']}?",
            buttons=[
                MDFlatButton(text="ОТМЕНА", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="УДАЛИТЬ", text_color=self.app.rjd_dark_red,
                             on_release=lambda x: self.delete_user(user))
            ]
        )
        self.dialog.open()

    def delete_user(self, user):
        self.dialog.dismiss()
        headers = self._auth_headers()
        UrlRequest(
            f"{self.app.api_url}/users/{user['id']}",
            req_headers=headers,
            method="DELETE",
            on_success=lambda req, res: self.on_user_deleted(user),
            on_error=lambda req, err: toast("Ошибка удаления"),
            on_failure=lambda req, res: toast("Удаление не удалось")
        )

    def on_user_deleted(self, user):
        toast(f"Пользователь {user['username']} удалён")
        self.load_users()

    def show_edit_user_dialog(self, user):
        self.edit_user_dialog = MDDialog(
            title=f"Редактировать: {user['username']}",
            type="custom",
            content_cls=EditUserContent(user=user),
            buttons=[
                MDFlatButton(text="ОТМЕНА", on_release=lambda x: self.edit_user_dialog.dismiss()),
                MDFlatButton(text="СОХРАНИТЬ", on_release=lambda x: self.save_user_changes(user))
            ]
        )
        self.edit_user_dialog.open()

    def save_user_changes(self, user):
        content = self.edit_user_dialog.content_cls
        headers = self._auth_headers()
        print(f"Saving role: {content.selected_role}")
        body = {
            "full_name": content.ids.full_name.text,
            "role": content.selected_role,
            "email": content.ids.email.text,
        }

        UrlRequest(
            f"{self.app.api_url}/users/{user['id']}",
            req_headers=headers,
            req_body=json.dumps(body),
            method="PUT",
            on_success=lambda req, res: (toast("Сохранено"), self.load_users()),
            on_error=lambda req, err: toast("Ошибка сохранения"),
            on_failure=lambda req, res: toast("Не удалось сохранить")
        )
        self.edit_user_dialog.dismiss()

    def _auth_headers(self):
        return {
            'Authorization': f'Bearer {self.app.token}',
            'Content-Type': 'application/json'
        }

    def on_load_error(self, *args):
        toast("Ошибка загрузки пользователей")

    def on_enter(self):
        self.load_users()




Builder.load_string('''
<EditUserContent>:
    orientation: 'vertical'
    spacing: "16dp"
    padding: "24dp"
    size_hint_y: None
    height: self.minimum_height

    MDTextField:
        id: full_name
        hint_text: "ФИО"
        text: root.user.get("full_name", "")
        mode: "rectangle"

    MDTextField:
        id: email
        hint_text: "Email"
        text: root.user.get("email", "")
        mode: "rectangle"

    MDRaisedButton:
        id: role_button
        text: root.user.get("role", "").capitalize() if root.user.get("role") else "Выбрать роль"
        size_hint: None, None
        size: dp(200), dp(48)
        pos_hint: {"center_x": .5}
        on_release: root.menu.open()
''')

class EditUserContent(MDBoxLayout):
    user = DictProperty({})
    selected_role = StringProperty("")

    def __init__(self, user, **kwargs):
        self.user = user
        super().__init__(**kwargs)
        self.selected_role = user.get("role", "").lower() if user.get("role") else ""
        self._init_menu()
        self.ids.role_button.text = self.selected_role.capitalize() if self.selected_role else "Выбрать роль"

    def _init_menu(self):
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": role.capitalize(),
                "on_release": lambda x=role: self.set_role(x),
            }
            for role in ["admin", "student", "teacher"]
        ]

        self.menu = MDDropdownMenu(
            caller=self.ids.role_button,
            items=menu_items,
            width_mult=4,
        )

    def set_role(self, role_text):
        self.selected_role = role_text.lower()
        self.ids.role_button.text = role_text
        self.menu.dismiss()
        print(f"Role selected: {self.selected_role}")


