from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen
from pathlib import Path

# Import the kv file with the same name as this file
parent_directory = Path(__file__).resolve().parent
this_file_name = Path(__file__).stem
Builder.load_file(str(parent_directory / f'{this_file_name}.kv'))


class FileLoadScreen(Screen):
    pass


class FileLoadScreenTopBar(BoxLayout):
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')

# class FileLoadMainControlsBox(BoxLayout):
#     screen_name = StringProperty('')
#     corner_radius = NumericProperty(0)
