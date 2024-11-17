from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen
from pathlib import Path

# Import the kv file with the same name as this file
parent_directory = Path(__file__).resolve().parent
this_file_name = Path(__file__).stem
Builder.load_file(str(parent_directory / f'{this_file_name}.kv'))


class PresetSaveScreen(Screen):
    pass


class PresetSaveScreenTopBar(BoxLayout):\
    screen_name = StringProperty('')


class PresetSaveSlotChooser(BoxLayout):
    preset_type = StringProperty('')
    preset_bank = StringProperty('')
    preset_number = StringProperty('')
