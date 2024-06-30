from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout


class ErrorDialog(BoxLayout):
    ok = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ErrorDialog, self).__init__(**kwargs)
        self._keyboard = None

    def _keyboard_closed(self):
        Logger.debug('ErrorDialog Keyboard Closed')
        if self._keyboard is not None:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard.unbind(on_key_up=self._on_key_up)
            self._keyboard.release()
            self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        Logger.debug(f'ErrorDialog on_key_down: {keyboard}, {keycode}, {text}, {modifiers}')

    def _on_key_up(self, keyboard, keycode):
        Logger.debug(f'ErrorDialog on_key_up: {keyboard}, {keycode}')

        # Handle Enter and Escape keys
        # This is the same as clicking the OK button
        enter_keycode = 13
        numpad_enter_keycode = 271
        escape_keycode = 27
        if keycode[0] in [escape_keycode, enter_keycode, numpad_enter_keycode]:
            App.get_running_app().dismiss_popup()

    def _unbind_keyboard(self):
        Logger.debug('ErrorDialog: _unbind_keyboard')
        if self._keyboard is not None:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard.unbind(on_key_up=self._on_key_up)
            self._keyboard.release()
            self._keyboard = None
