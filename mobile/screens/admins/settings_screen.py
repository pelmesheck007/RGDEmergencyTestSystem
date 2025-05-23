from screens.base_screen import BaseScreen
from kivymd.uix.label import MDLabel

class SettingsScreen(BaseScreen):
    def on_enter(self):
        self.screen_title = "Настройки системы"
        if not hasattr(self, 'initialized'):
            self.ids.content.add_widget(
                MDLabel(
                    text="Экран настроек системы",
                    halign="center",
                    theme_text_color="Primary",
                    font_style="H4"
                )
            )
            self.initialized = True