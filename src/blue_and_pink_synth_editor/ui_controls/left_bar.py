from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.lang.builder import Builder
from pathlib import Path

Builder.load_file(str(Path(__file__).parent / 'left_bar.kv'))


class LeftBar(BoxLayout):
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')
