from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from pathlib import Path

Builder.load_file(str(Path(__file__).parent / 'load_dialog.kv'))


class LoadDialog(BoxLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LoadDialog, self).__init__(**kwargs)
