from kivy.uix.screenmanager import ScreenManager

class SafeScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_safe_transition')

    def safe_transition(self, screen_name):
        try:
            self.current = screen_name
        except Exception as e:
            self.dispatch('on_safe_transition', e)
            self.current = screen_name  # Повторная попытка