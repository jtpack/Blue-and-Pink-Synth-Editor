from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout


class LoadDialog(BoxLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LoadDialog, self).__init__(**kwargs)
        self._keyboard = None

    def _unbind_keyboard(self):
        Logger.debug('LoadDialog: _unbind_keyboard')
        if self._keyboard is not None:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard.unbind(on_key_up=self._on_key_up)
            self._keyboard.release()
            self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        Logger.debug(f'LoadDialog on_key_down: {keyboard}, {keycode}, {text}, {modifiers}')

    def _on_key_up(self, keyboard, keycode):
        Logger.debug(f'LoadDialog on_key_up: {keyboard}, {keycode}')

        # Handle Enter Key
        # This is the same as clicking the OK button
        enter_keycode = 13
        numpad_enter_keycode = 271

        if keycode[0] in [enter_keycode, numpad_enter_keycode]:
            self.load(self.ids.filechooser.path, self.ids.filechooser.selection)

        # Handle escape key
        # This is the same as clicking the Cancel button
        escape_keycode = 27
        if keycode[0] in [escape_keycode]:
            App.get_running_app().dismiss_popup()