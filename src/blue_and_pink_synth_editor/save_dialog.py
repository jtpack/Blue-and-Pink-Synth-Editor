from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout


class SaveDialog(BoxLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    default_filename = StringProperty('')

    def __init__(self, **kwargs):
        super(SaveDialog, self).__init__(**kwargs)
        self._keyboard = None

    def _unbind_keyboard(self):
        # Do not actually unbind the keyboard
        # because we want to activate the OK
        # action when the user presses the Enter
        # key and cancel when they press the
        # Escape key.
        pass

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        Logger.debug(f'SaveDialog on_key_down: {keyboard}, {keycode}, {text}, {modifiers}')

    def _on_key_up(self, keyboard, keycode):
        Logger.debug(f'SaveDialog on_key_up: {keyboard}, {keycode}')

        # Handle Enter Key
        # This is the same as clicking the OK button
        enter_keycode = 13
        numpad_enter_keycode = 271

        if keycode[0] in [enter_keycode, numpad_enter_keycode]:
            self.save(self.ids.filechooser.path, self.ids.filechooser.path + '/' + self.ids.text_input.text)

        # Handle escape key
        # This is the same as clicking the Cancel button
        escape_keycode = 27
        if keycode[0] in [escape_keycode]:
            App.get_running_app().dismiss_popup()