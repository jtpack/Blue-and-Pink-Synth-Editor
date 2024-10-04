from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from pathlib import Path
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.core.window import Window
import webbrowser

Builder.load_file(str(Path(__file__).parent / 'demo_mode_popup.kv'))


class DemoModePopup(BoxLayout):
    pass


class WebsiteButtonLabel(ButtonBehavior, Label):
    hovered = BooleanProperty(False)
    border_point = (0, 0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)
        Window.bind(on_dropfile=self._on_file_drop)

    def on_mouse_pos(self, *args):
        pos = args[1]
        inside = self.collide_point(*self.to_widget(*pos))
        if self.hovered != inside:
            self.hovered = inside
            if inside:
                self.on_enter()
            else:
                self.on_leave()

    def on_enter(self):
        Window.set_system_cursor('hand')

    def on_leave(self):
        Window.set_system_cursor('arrow')

    def button_clicked(self):
        webbrowser.open('https://www.scottlumsden.com')

    def _on_file_drop(self, window, file_path):
        file_path_string = file_path.decode('utf-8')
        print(f'_on_file_drop: {file_path_string}')

    def on_dismiss(self):
        print('unbinding')
        Window.unbind(on_dropfile=self._on_file_drop)