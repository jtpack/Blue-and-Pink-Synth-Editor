from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from pathlib import Path

Builder.load_file(str(Path(__file__).parent / 'demo_mode_popup.kv'))


class DemoModePopup(BoxLayout):
    pass
