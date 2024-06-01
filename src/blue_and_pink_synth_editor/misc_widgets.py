from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, DictProperty, BooleanProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.logger import Logger


class ParamsGridModCell(BoxLayout):
    screen_name = StringProperty('')
    section_name = StringProperty('')
    title = StringProperty('')
    param_name = StringProperty('')
    param_name_color_string = StringProperty('#ECBFEBFF')
    value_color_string = StringProperty('#06070FFF')
    background_color_string = StringProperty('#438EFFFF')
    mod_amount_line_background_color_string = StringProperty('#000000FF')

    value_prop = NumericProperty(0)
    lfo2_prop = NumericProperty(0)
    mod_wheel_prop = NumericProperty(0)
    velocity_prop = NumericProperty(0)
    aftertouch_prop = NumericProperty(0)
    corner_radius = NumericProperty(0)


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


class ParamsGridLfoConfigCell(BoxLayout):
    screen_name = StringProperty('')
    section_name = StringProperty('')
    type_prop = NumericProperty(0)
    key_sync_prop = NumericProperty(0)
    corner_radius = NumericProperty(0)
    param_name_color_string = StringProperty('#ECBFEBFF')
    value_color_string = StringProperty('#06070FFF')
    background_color_string = StringProperty('#438EFFFF')


class ModAmountLine(ButtonBehavior, Widget):
    midi_val = NumericProperty(0) # This is 0 to 127
    color_hex = StringProperty('#FFFFFFFF')
    screen_name = StringProperty('')
    section_name = StringProperty('')
    param_name = StringProperty('')
    mod_type = StringProperty('')
    drag_start_pos = NumericProperty(0)
    background_color_string = StringProperty('#72777BFF')
    mouse_pressed = BooleanProperty(False)
    mouse_inside_bounds = BooleanProperty(False)
    fine_mode_decimal_places = NumericProperty(1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouseover)

    def on_mouseover(self, _, pos):
        if not self.disabled:
            if App.get_running_app().curr_screen_name == self.screen_name:
                if self.collide_point(*pos):
                    if not self.mouse_inside_bounds:
                        self.mouse_inside_bounds = True
                        self.on_mouse_enter()

                else:
                    if self.mouse_inside_bounds:
                        self.mouse_inside_bounds = False
                        self.on_mouse_exit()

    def on_mouse_enter(self):
        App.get_running_app().on_mouse_entered_param_control(f'{self.param_name}.{self.mod_type}')

    def on_mouse_exit(self):
        App.get_running_app().on_mouse_exited_param_control(f'{self.param_name}.{self.mod_type}')

    def handle_touch(self, device, button):
        #
        # Mouse Wheel
        #
        if not self.disabled:
            if device == 'mouse':
                if button == 'scrollup':
                    direction = -1 if App.get_running_app().invert_mouse_wheel else 1

                    if App.get_running_app().fine_mode:
                        # Use the minimum increment defined by
                        # NymphesPreset's float precision property
                        increment = float(direction) / pow(10, self.fine_mode_decimal_places)

                    else:
                        # We are not in fine mode, so increment by 1
                        increment = int(direction)

                    # Increment the property
                    App.get_running_app().increment_prop_value_for_param_name(f'{self.param_name}.{self.mod_type}', increment)

                elif button == 'scrolldown':
                    direction = 1 if App.get_running_app().invert_mouse_wheel else -1

                    if App.get_running_app().fine_mode:
                        # Use the minimum decrement defined by
                        # NymphesPreset's float precision property
                        increment = float(direction) / pow(10, self.fine_mode_decimal_places)

                    else:
                        # We are not in fine mode, so decrement by 1
                        increment = int(direction)

                    # Increment the property
                    App.get_running_app().increment_prop_value_for_param_name(f'{self.param_name}.{self.mod_type}', increment)

            else:
                Logger.debug(f'{self.param_name} {device} {button}')

    def on_touch_down(self, touch):
        #
        # This is called when the mouse is clicked
        #
        if not self.disabled:
            if self.collide_point(*touch.pos) and touch.button == 'left':
                touch.grab(self)

                # Store the starting y position of the touch
                self.drag_start_pos = int(touch.pos[1])

                # The mouse is pressed
                self.mouse_pressed = True

                # Inform the app that a drag has started
                App.get_running_app().set_curr_mouse_dragging_param_name(f'{self.param_name}.{self.mod_type}')

                return True
            return super(ModAmountLine, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        #
        # This is called when the mouse drags
        #
        if not self.disabled:
            if touch.grab_current == self:
                # Get the current y position
                curr_pos = int(touch.pos[1])

                # Calculate the distance from the starting drag position
                curr_drag_distance = (self.drag_start_pos - curr_pos) * -1

                # Scale the drag distance and use as the increment
                if App.get_running_app().fine_mode:
                    # Use the minimum increment defined by
                    # NymphesPreset's float precision property
                    increment = round(curr_drag_distance * 0.05, self.fine_mode_decimal_places)

                else:
                    increment = int(round(curr_drag_distance * 0.5))

                # Increment the property's value
                App.get_running_app().increment_prop_value_for_param_name(f'{self.param_name}.{self.mod_type}', increment)

                # Reset the drag start position to the current position
                self.drag_start_pos = curr_pos

                return True

            return super(ModAmountLine, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if not self.disabled:
            if touch.grab_current == self:
                touch.ungrab(self)

                # The mouse is no longer pressed
                self.mouse_pressed = False

                # Inform the app that a drag has ended
                App.get_running_app().set_curr_mouse_dragging_param_name('')

                return True
            return super(ModAmountLine, self).on_touch_up(touch)


class HoverButton(ButtonBehavior, Label):
    screen_name = StringProperty('')
    mouse_inside_bounds = BooleanProperty(False)
    tooltip_text = StringProperty('')
    base_font_size = NumericProperty(20)
    mouse_pressed = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouseover)

    def on_mouseover(self, _, pos):
        if self.disabled or App.get_running_app().curr_screen_name != self.screen_name:
            return

        if self.collide_point(*pos):
            if not self.mouse_inside_bounds:
                self.on_mouse_enter()

        else:
            if self.mouse_inside_bounds:
                self.on_mouse_exit()

    def on_mouse_enter(self):
        self.mouse_inside_bounds = True

        Window.set_system_cursor('hand')

        if self.tooltip_text != '':
            App.get_running_app().status_bar_text = self.tooltip_text

    def on_mouse_exit(self):
        self.mouse_inside_bounds = False
        self.mouse_pressed = False

        Window.set_system_cursor('arrow')

        if self.tooltip_text != '':
            App.get_running_app().status_bar_text = ''

    def on_touch_down(self, touch):
        #
        # This is called when the mouse is clicked
        #
        if not self.disabled and self.collide_point(*touch.pos) and touch.button == 'left':
            super().on_touch_down(touch)
            self.mouse_pressed = True
            return True

        else:
            return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        #
        # This is called when the mouse is released
        #

        if not self.disabled and touch.button == 'left':
            super().on_touch_up(touch)
            self.mouse_pressed = False

            if self.collide_point(*touch.pos):
                Logger.info(f'on_touch_up: {self.text}')
                return True

            else:
                return False

        else:
            return super().on_touch_up(touch)


class HoverSpinner(Spinner):
    screen_name = StringProperty('')
    mouse_inside_bounds = BooleanProperty(False)
    tooltip_text = StringProperty('')
    base_font_size = NumericProperty(20)
    mouse_pressed = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouseover)

    def on_mouseover(self, _, pos):
        if self.disabled or App.get_running_app().curr_screen_name != self.screen_name:
            return

        if self.collide_point(*pos):
            if not self.mouse_inside_bounds:
                self.on_mouse_enter()

        else:
            if self.mouse_inside_bounds:
                self.on_mouse_exit()

    def on_mouse_enter(self):
        self.mouse_inside_bounds = True

        Window.set_system_cursor('hand')

        if self.tooltip_text != '':
            App.get_running_app().status_bar_text = self.tooltip_text

    def on_mouse_exit(self):
        self.mouse_inside_bounds = False
        self.mouse_pressed = False

        Window.set_system_cursor('arrow')

        if self.tooltip_text != '':
            App.get_running_app().status_bar_text = ''

    def on_touch_down(self, touch):
        #
        # This is called when the mouse is clicked
        #
        if self.collide_point(*touch.pos) and touch.button == 'left':
            super().on_touch_down(touch)
            self.mouse_pressed = True
            return True

        else:
            return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        #
        # This is called when the mouse is released
        #

        if touch.button == 'left':
            super().on_touch_up(touch)
            self.mouse_pressed = False

            if self.collide_point(*touch.pos):
                Logger.info(f'on_touch_up: {self.text}')
                return True

            else:
                return False

        else:
            return super().on_touch_up(touch)


class VoiceModeButton(HoverButton):
    voice_mode_name = StringProperty('')


class ModAmountsBox(BoxLayout):
    screen_name = StringProperty('')
    param_name = StringProperty('')
    lfo2_prop = NumericProperty(0)
    mod_wheel_prop = NumericProperty(0)
    velocity_prop = NumericProperty(0)
    aftertouch_prop = NumericProperty(0)
    mod_amount_line_background_color_string = StringProperty('#000000FF')


class MainControlsBox(BoxLayout):
    screen_name = StringProperty('')
    corner_radius = NumericProperty(0)


class ChordsMainControlsBox(BoxLayout):
    screen_name = StringProperty('')
    corner_radius = NumericProperty(0)


class MainSettingsGrid(GridLayout):
    corner_radius = NumericProperty(0)


class SettingsSubBox(BoxLayout):
    corner_radius = NumericProperty(0)


class VoiceModeBox(BoxLayout):
    num_voice_modes = NumericProperty(6)
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')


class LegatoBox(BoxLayout):
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')


class ChordsButtonBox(BoxLayout):
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')


class FineModeBox(BoxLayout):
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')


class LeftBar(BoxLayout):
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')


class TopBar(BoxLayout):
    screen_name = StringProperty('')
    corner_radius = NumericProperty(0)


class BottomBar(BoxLayout):
    screen_name = StringProperty('')
    corner_radius = NumericProperty(0)


class SettingsTopBar(BoxLayout):
    screen_name = StringProperty('')
    corner_radius = NumericProperty(0)


class ChordsTopBar(BoxLayout):
    screen_name = StringProperty('')
    corner_radius = NumericProperty(0)


class ControlSectionsGrid(GridLayout):
    corner_radius = NumericProperty(0)


class ControlSection(BoxLayout):
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')
    param_name_color_string = StringProperty('#ECBFEB')


class ChordsControlSectionsGrid(GridLayout):
    corner_radius = NumericProperty(0)


class SectionTitleLabel(ButtonBehavior, Label):
    pass


class ParamsGrid(GridLayout):
    corner_radius = NumericProperty(0)


class ParamNameLabel(Label):
    text_color_string = StringProperty('#ECBFEBFF')


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


class ChordParamsGrid(GridLayout):
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
