from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from pathlib import Path

# Import the kv file with the same name as this file
parent_directory = Path(__file__).resolve().parent
this_file_name = Path(__file__).stem
Builder.load_file(str(parent_directory / f'{this_file_name}.kv'))


class DemoModeScreen(BoxLayout):
    pass
