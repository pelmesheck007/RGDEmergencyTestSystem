from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from base_screen import BaseScreen


class ProfileScreen(BaseScreen):
    def build_content(self):
        self.screen_title = "Профиль пользователя"
        self.show_back_button = True
        self.show_menu_button = True

        content = self.ids.content_box
        content.add_widget(MDLabel(
            text=f"Добро пожаловать, {self.app.user_data.get('username', '')}",
            halign="center",
            font_style="H5"
        ))

        content.add_widget(MDRaisedButton(
            text="Редактировать профиль",
            pos_hint={"center_x": 0.5},
            on_release=self.edit_profile
        ))

    def edit_profile(self, *args):
        self.navigate_to('edit_profile')

    def on_refresh(self):
        """Вызывается при каждом открытии экрана"""
        self.ids.content_box.clear_widgets()
        self.build_content()