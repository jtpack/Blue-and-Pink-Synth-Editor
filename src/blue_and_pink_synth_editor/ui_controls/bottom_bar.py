from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.lang.builder import Builder
from pathlib import Path

Builder.load_file(str(Path(__file__).parent / 'bottom_bar.kv'))


class BottomBar(BoxLayout):
    screen_name = StringProperty('')
    corner_radius = NumericProperty(0)
