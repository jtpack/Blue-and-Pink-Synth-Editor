from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.lang.builder import Builder
from pathlib import Path

# Import the kv file with the same name as this file
parent_directory = Path(__file__).resolve().parent
this_file_name = Path(__file__).stem
Builder.load_file(str(parent_directory / f'{this_file_name}.kv'))


class SaveDialog(BoxLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    default_filename = StringProperty('')

    def __init__(self, **kwargs):
        super(SaveDialog, self).__init__(**kwargs)

class SavePopup(Popup):
    def on_open(self):
        def select_all_delayed(_):
            self.content.text_input.select_all()

        # Start editing the text input
        self.content.text_input.focus = True

        # Make it select all the text
        Clock.schedule_once(lambda dt: select_all_delayed(dt), 0)
