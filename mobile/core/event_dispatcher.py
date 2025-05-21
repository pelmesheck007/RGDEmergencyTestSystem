# core/event_dispatcher.py
from kivy.event import EventDispatcher


class EventDispatcher(EventDispatcher):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def show_message(self, message):
        print(f"Message: {message}")

    def show_error(self, error):
        print(f"Error: {error}")


# Создаем глобальный экземпляр
event_dispatcher = EventDispatcher()