from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.lang.builder import Builder
from .misc_widgets import HoverButton
from pathlib import Path

Builder.load_file(str(Path(__file__).parent / 'chords_screen.kv'))
 

class ChordsMainControlsBox(BoxLayout):
    screen_name = StringProperty('')
    corner_radius = NumericProperty(0)


class ChordParamsGridCell(ButtonBehavior, BoxLayout):
    screen_name = StringProperty('')
    section_name = StringProperty('')
    title = StringProperty('')
    param_name = StringProperty('')
    value_prop = NumericProperty(0)
    corner_radius = NumericProperty(0)
    value_color_string = StringProperty('#06070FFF')
    background_color_string = StringProperty('#438EFFFF')


class ChordSectionTitleLabel(HoverButton):
    this_chord_active = BooleanProperty(False)


