from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.lang.builder import Builder
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.app import App
from pathlib import Path

Builder.load_file(str(Path(__file__).parent / 'params_grid_mod_cell.kv'))


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


class ModAmountsBox(BoxLayout):
    screen_name = StringProperty('')
    param_name = StringProperty('')
    lfo2_prop = NumericProperty(0)
    mod_wheel_prop = NumericProperty(0)
    velocity_prop = NumericProperty(0)
    aftertouch_prop = NumericProperty(0)
    mod_amount_line_background_color_string = StringProperty('#000000FF')


class SectionScreenParamsGridModCell(BoxLayout):
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


class SectionScreenModAmountsBox(BoxLayout):
    screen_name = StringProperty('')
    param_name = StringProperty('')
    lfo2_prop = NumericProperty(0)
    mod_wheel_prop = NumericProperty(0)
    velocity_prop = NumericProperty(0)
    aftertouch_prop = NumericProperty(0)
    mod_amount_line_background_color_string = StringProperty('#000000FF')


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
