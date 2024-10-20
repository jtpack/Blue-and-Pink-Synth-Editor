from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.lang.builder import Builder
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from pathlib import Path

Builder.load_file(str(Path(__file__).parent / 'settings_screen.kv'))

class MidiInputPortsGrid(GridLayout):
    midi_ports = ListProperty([])

    def __init__(self, **kwargs):
        super(MidiInputPortsGrid, self).__init__(**kwargs)
        self.cols = 2
        self.bind(midi_ports=self.update_grid)

    def update_grid(self, instance, value):
        # Remove all old rows
        self.clear_widgets()

        # Create a row for each entry in midi_ports
        for port_name in self.midi_ports:
            # Add the label
            self.add_widget(MidiPortLabel(text=port_name))

            # Add a checkbox
            self.add_widget(MidiInputPortCheckBox(port_name=port_name))


class MidiOutputPortsGrid(GridLayout):
    midi_ports = ListProperty([])

    def __init__(self, **kwargs):
        super(MidiOutputPortsGrid, self).__init__(**kwargs)
        self.cols = 2
        self.bind(midi_ports=self.update_grid)

    def update_grid(self, instance, value):
        # Remove all old rows
        self.clear_widgets()

        # Create a row for each entry in midi_ports
        for port_name in self.midi_ports:
            # Add the label
            self.add_widget(MidiPortLabel(text=port_name))

            # Add a checkbox
            self.add_widget(MidiOutputPortCheckBox(port_name=port_name))


class MidiPortLabel(Label):
    pass


class MidiInputPortCheckBox(CheckBox):
    port_name = StringProperty('')


class MidiOutputPortCheckBox(CheckBox):
    port_name = StringProperty('')
