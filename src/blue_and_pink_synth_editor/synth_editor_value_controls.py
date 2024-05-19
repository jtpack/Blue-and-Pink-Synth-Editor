from value_control import ValueControl, DiscreteValuesControl
from kivy.properties import StringProperty
from kivy.app import App


class SynthEditorValueControl(ValueControl):
    """
    A ValueControl subclass which provides functionality specific to the
    Blue and Pink Synth Editor app
    """
    screen_name = StringProperty('')
    section_name = StringProperty('')
    param_name = StringProperty('')
    text_color_string = StringProperty('#06070FFF')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.min_value = 0.0
        self.max_value = 127.0

        self.bind(mouse_inside_bounds=self.on_mouse_inside_bounds)

        self.value_changed_callback = (lambda val: App.get_running_app().set_prop_value_for_param_name(self.param_name, self.value))
        self.invert_mouse_wheel = App.get_running_app().invert_mouse_wheel


    def on_mouse_inside_bounds(self, _, inside):
        if App.get_running_app().curr_screen_name == self.screen_name:
            if inside:
                App.get_running_app().on_mouse_entered_param_control(f'{self.param_name}')
            else:
                App.get_running_app().on_mouse_exited_param_control(f'{self.param_name}')

    def on_touch_down(self, touch):
        #
        # This is called when the mouse is clicked
        #
        if not self.disabled and self.collide_point(*touch.pos) and touch.button == 'left':
            # Inform the app that a drag has started
            App.get_running_app().set_curr_mouse_dragging_param_name(self.param_name)
            super().on_touch_down(touch)
            return True
        else:
            super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if not self.disabled and App.get_running_app().curr_mouse_dragging_param_name == self.param_name:
            # Inform the app that a drag has ended
            App.get_running_app().set_curr_mouse_dragging_param_name('')
            super().on_touch_up(touch)
            return True
        else:
            return super().on_touch_up(touch)

    def start_editing(self):
        App.get_running_app().set_curr_keyboard_editing_param_name(self.param_name)
        super().start_editing()

    def _unbind_keyboard(self):
        super()._unbind_keyboard()
        App.get_running_app().set_curr_keyboard_editing_param_name('')


class FloatValueControl(SynthEditorValueControl):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.min_value = 0.0
        self.max_value = 127.0

        self.fine_mode = App.get_running_app().fine_mode
        self.enable_float_drag = App.get_running_app().fine_mode
        self.float_value_decimal_places = App.get_running_app().fine_mode_decimal_places


class ChordValueControl(SynthEditorValueControl):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.min_value = -127
        self.max_value = 127
        self.float_value_decimal_places = 0
        self.enable_float_drag = False
        self.enable_float_value = False
        self.fine_mode = False

        self._update_text()


class MidiIntValueControl(SynthEditorValueControl):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.min_value = 0
        self.max_value = 127
        self.float_value_decimal_places = 0
        self.enable_float_drag = False
        self.enable_float_value = False
        self.fine_mode = False

        self._update_text()


class ModWheelValueControl(MidiIntValueControl):
    def on_mouse_inside_bounds(self, _, inside):
        if App.get_running_app().curr_screen_name == self.screen_name:
            if inside:
                App.get_running_app().on_mouse_entered_param_control(
                    param_name=f'{self.param_name}',
                    tooltip_text='SEND MOD WHEEL AMOUNT TO NYMPHES'
                )
            else:
                App.get_running_app().on_mouse_exited_param_control(f'{self.param_name}')


class AftertouchValueControl(MidiIntValueControl):
    def on_mouse_inside_bounds(self, _, inside):
        if App.get_running_app().curr_screen_name == self.screen_name:
            if inside:
                App.get_running_app().on_mouse_entered_param_control(
                    param_name=f'{self.param_name}',
                    tooltip_text='SEND AFTERTOUCH AMOUNT TO NYMPHES'
                )
            else:
                App.get_running_app().on_mouse_exited_param_control(f'{self.param_name}')

class SynthEditorDiscreteValuesControl(DiscreteValuesControl):
    """
    A ValueControl subclass which provides functionality specific to the
    Blue and Pink Synth Editor app
    """
    screen_name = StringProperty('')
    section_name = StringProperty('')
    param_name = StringProperty('')
    text_color_string = StringProperty('#06070FFF')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bind(mouse_inside_bounds=self.on_mouse_inside_bounds)

    def on_mouse_inside_bounds(self, _, inside):
        if App.get_running_app().curr_screen_name == self.screen_name:
            if inside:
                App.get_running_app().on_mouse_entered_param_control(self.param_name)
            else:
                App.get_running_app().on_mouse_exited_param_control(self.param_name)

    def on_touch_down(self, touch):
        #
        # This is called when the mouse is clicked
        #
        if not self.disabled and self.collide_point(*touch.pos) and touch.button == 'left':
            # Inform the app that a drag has started
            App.get_running_app().set_curr_mouse_dragging_param_name(self.param_name)
            super().on_touch_down(touch)
            return True
        else:
            super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if not self.disabled and App.get_running_app().curr_mouse_dragging_param_name == self.param_name:
            # Inform the app that a drag has ended
            App.get_running_app().set_curr_mouse_dragging_param_name('')
            super().on_touch_up(touch)
            return True
        else:
            return super().on_touch_up(touch)


class LfoTypeValueControl(SynthEditorDiscreteValuesControl):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.values_list = ['BPM', 'LOW', 'HIGH', 'TRACK']


class LfoSyncValueControl(SynthEditorDiscreteValuesControl):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.values_list = ['OFF', 'ON']