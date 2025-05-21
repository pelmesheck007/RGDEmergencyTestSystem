from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

# Устанавливаем размер окна
Window.size = (360, 640)

KV = '''
MDFloatLayout:
    md_bg_color: app.rjd_light_red

    MDCard:
        size_hint: .85, .6
        pos_hint: {"center_x": .5, "center_y": .5}
        elevation: 8
        padding: 25
        spacing: 25
        orientation: "vertical"
        md_bg_color: app.rjd_white

        Image:
            source: "rjd_logo.png"  # Замените на путь к логотипу
            size_hint: (None, None)
            size: "150dp", "50dp"
            pos_hint: {"center_x": .5}

        MDLabel:
            text: "Вход в систему"
            font_style: "H5"
            halign: "center"
            size_hint_y: None
            height: self.texture_size[1]
            theme_text_color: "Custom"
            text_color: app.rjd_dark_red

        MDTextField:
            id: login
            hint_text: "Табельный номер"
            size_hint_x: .9
            pos_hint: {"center_x": .5}
            icon_left: "account"
            line_color_normal: app.rjd_dark_red
            line_color_focus: app.rjd_dark_red

        MDTextField:
            id: password
            hint_text: "Пароль"
            size_hint_x: .9
            pos_hint: {"center_x": .5}
            icon_left: "key"
            password: True
            line_color_normal: app.rjd_dark_red
            line_color_focus: app.rjd_dark_red

        MDRaisedButton:
            text: "ВОЙТИ"
            size_hint_x: .9
            pos_hint: {"center_x": .5}
            md_bg_color: app.rjd_dark_red
            on_release: app.try_login()
            font_style: "Button"
            bold: True

        MDBoxLayout:
            size_hint_y: None
            height: self.minimum_height
            spacing: 10

            MDTextButton:
                text: "Забыли пароль?"
                theme_text_color: "Custom"
                text_color: app.rjd_dark_red
                on_release: app.forgot_password()

            Widget:
                size_hint_x: None
                width: 20

            MDTextButton:
                text: "Регистрация"
                theme_text_color: "Custom"
                text_color: app.rjd_dark_red
                on_release: app.go_to_register()
'''


class RZDLoginApp(MDApp):
    # Фирменные цвета РЖД
    rjd_dark_red = get_color_from_hex("#CC0000")  # Темно-красный
    rjd_light_red = get_color_from_hex("#FFEBEE")  # Светло-красный (фон)
    rjd_white = get_color_from_hex("#FFFFFF")  # Белый

    def build(self):
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.theme_style = "Light"
        return Builder.load_string(KV)

    def try_login(self):
        login = self.root.ids.login.text
        password = self.root.ids.password.text
        print(f"Попытка входа: {login}")
        # Здесь должна быть логика авторизации

    def forgot_password(self):
        print("Восстановление пароля")

    def go_to_register(self):
        print("Переход к регистрации")


if __name__ == "__main__":
    RZDLoginApp().run()