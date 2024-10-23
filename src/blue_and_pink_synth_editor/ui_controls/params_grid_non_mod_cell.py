from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.lang.builder import Builder
from pathlib import Path

# Import the kv file with the same name as this file
parent_directory = Path(__file__).resolve().parent
this_file_name = Path(__file__).stem
Builder.load_file(str(parent_directory / f'{this_file_name}.kv'))


class ParamsGridNonModCell(BoxLayout):
    screen_name = StringProperty('')
    section_name = StringProperty('')
    title = StringProperty('')
    param_name = StringProperty('')
    value_prop = NumericProperty(0)
    corner_radius = NumericProperty(0)
    value_color_string = StringProperty('#06070FFF')
    background_color_string = StringProperty('#438EFFFF')
    param_name_color_string = StringProperty('#ECBFEBFF')
