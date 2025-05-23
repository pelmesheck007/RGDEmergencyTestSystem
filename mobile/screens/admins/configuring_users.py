from screens.base_screen import BaseScreen
from kivymd.uix.label import MDLabel

class ConfiguringUsersScreen(BaseScreen):
    def on_screen_enter(self):
        self.screen_title = "Управление пользователями"
        if not hasattr(self, 'initialized'):
            self.ids.content.add_widget(
                MDLabel(
                    text="Экран управления пользователями",
                    halign="center",
                    theme_text_color="Primary",
                    font_style="H4"
                )
            )
            self.initialized = True