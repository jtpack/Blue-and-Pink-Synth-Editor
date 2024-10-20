from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.lang.builder import Builder
from pathlib import Path

Builder.load_file(str(Path(__file__).parent / 'params_grid_lfo_config_cell.kv'))


class ParamsGridLfoConfigCell(BoxLayout):
    screen_name = StringProperty('')
    section_name = StringProperty('')
    type_prop = NumericProperty(0)
    key_sync_prop = NumericProperty(0)
    corner_radius = NumericProperty(0)
    param_name_color_string = StringProperty('#ECBFEBFF')
    value_color_string = StringProperty('#06070FFF')
    background_color_string = StringProperty('#438EFFFF')
