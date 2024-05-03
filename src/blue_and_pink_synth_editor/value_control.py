from kivy.properties import NumericProperty, StringProperty, ObjectProperty, BooleanProperty, ListProperty
from kivy.uix.textinput import TextInput, CutBuffer
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.core.window import Window
import re

class ValueControl(TextInput):
    value = NumericProperty(0)
    external_value = NumericProperty(0)
    min_value = NumericProperty(0)
    max_value = NumericProperty(127)
    fine_mode = BooleanProperty(False)
    coarse_increment = NumericProperty(1)
    fine_increment = NumericProperty(0.1)
    enable_float_value = BooleanProperty(False)
    value_changed_callback = ObjectProperty(None)
    float_value_decimal_places = NumericProperty(1)
    invert_mouse_wheel = BooleanProperty(False)
    base_font_size = NumericProperty(30)
    mouseover_magnification_amount = NumericProperty(1.08)
    enable_float_drag = BooleanProperty(True)
    mouse_inside_bounds = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bind(external_value=self.on_external_value)
        self.bind(focus=self.on_focus)
        self.bind(on_text_validate=self.on_enter_key)
        Window.bind(mouse_pos=self.on_mouseover)

        self._drag_start_pos = 0.0
        self._drag_value = 0.0

        self.multiline = False
        self.readonly = False
        self.background_color = (0, 0, 0, 0)
        self.font_size = self.base_font_size
        self._update_text()

    #
    # Limit text input to numbers and decimal point
    #

    pat = re.compile('[^0-9.-]')

    def insert_text(self, substring, from_undo=False):
        """
        Only allow numeric characters and decimal point
        """

        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join(
                re.sub(pat, '', s)
                for s in substring.split('.', 1)
            )
        return super().insert_text(s, from_undo=from_undo)

    def on_external_value(self, _, value):
        #
        # The value of the external_value property has changed
        #

        # Clamp the value to the min/max value range
        value = self.clamped_value(value)

        # Store the new value
        self.value = value

        # Update text
        self._update_text()

    def set_value(self, value):
        """
        Set the value property and then call the value_changed_callback
        if the value has actually changed.
        """
        # Store the previous value
        prev_value = self.value

        # Clamp the new value to the min/max range
        value = self.clamped_value(value)

        # Store the new value
        self.value = value

        # Update text
        self._update_text()

        # Call the value_changed_callback, if the value has changed
        if self.enable_float_value:
            value_changed = not self.float_equals(
                prev_value,
                self.value,
                self.float_value_decimal_places
            )
        else:
            value_changed = prev_value != self.value

        if value_changed and self.value_changed_callback is not None:
            self.value_changed_callback(self.value)

    def clamped_value(self, value):
        # Clamp value to min/max range
        if value < self.min_value:
            value = self.min_value

        elif value > self.max_value:
            value = self.max_value

        return value

    def on_focus(self, _, value):
        if value:
            #
            # Focus has been gained, which means
            # that text editing has started
            #
            pass

        else:
            #
            # Focus has been lost, which means
            # that text editing has ended
            #

            # Get the new value
            value = self._text_to_value(self.text)

            # Store it
            if value is not None:
                self.set_value(value)
            else:
                # Invalid text was entered.
                # Restore the original value text.
                self._update_text()

    def on_enter_key(self, _):
        """
        The Enter key has been pressed while editing the text
        """
        # Get the new value
        value = self._text_to_value(self.text)

        # Store it
        if value is not None:
            self.set_value(value)
        else:
            # Invalid text was entered.
            # Restore the original value text.
            self._update_text()

    def _text_to_value(self, text):
        """
        Convert the supplied text string into a
        value using current configuration settings.
        Return None if conversion is not possible.
        """

        if self.enable_float_value:
            try:
                # Convert text to a number
                value = float(text)

                # Clamp to min/max range
                value = self.clamped_value(value)

                # Return it
                return value

            except ValueError:
                return None

        else:
            try:
                # Convert text to a number
                value = int(text)

                # Clamp to min/max range
                value = self.clamped_value(value)

                # Return it
                return value

            except ValueError:
                return None

    def _update_text(self):
        """
        Convert the current value to a string and set the text with it
        """
        self.text = f'{round(self.value, self.float_value_decimal_places):.{self.float_value_decimal_places}f}'


    @staticmethod
    def float_equals(first_value, second_value, num_decimals):
        """
        Uses a limited amount of precision to determine
        whether the supplied float values are equal
        :param first_value:
        :param second_value:
        :param num_decimals: int
        :return: True if the two values are equal. False if not.
        """
        v1 = int(round(first_value, num_decimals) * pow(10, num_decimals))
        v2 = int(round(second_value, num_decimals) * pow(10, num_decimals))
        return v1 == v2

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            if self.focus:
                self.focus = False
            return False

        if self.collide_point(*touch.pos):
            # Store the starting y position of the touch
            # in case it becomes a mouse drag
            self._drag_start_pos = float(touch.pos[1])

            # Store the current value as well
            self._drag_value = self.value

            #
            # Don't let the parent TextInput class start editing
            # on the first click
            #
            if super().on_touch_down(touch):
                if self.focus:
                    self.focus = False

            #
            # Handle mouse wheel
            #
            if 'button' in touch.profile and touch.button.startswith('scroll'):
                scroll_type = touch.button[6:]
                if scroll_type == 'down':
                    if self.invert_mouse_wheel:
                        self.increment_value()
                    else:
                        self.decrement_value()

                elif scroll_type == 'up':
                    if self.invert_mouse_wheel:
                        self.decrement_value()
                    else:
                        self.increment_value()

            return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return

        # Get the current Y position
        curr_pos = float(touch.pos[1])

        # Calculate the distance from the starting drag position
        curr_drag_distance = (self._drag_start_pos - curr_pos) * -1

        # Store the new drag start position
        self._drag_start_pos = float(touch.pos[1])

        # Calculate how much the value should change
        #
        distance_for_full_value_range = 500.0
        if self.fine_mode:
            distance_for_full_value_range *= 10.0

        drag_amount = (curr_drag_distance / distance_for_full_value_range) * (abs(self.max_value - self.min_value))

        # Apply the amount and store the new fractional value
        # to be used during further dragging, even if float
        # value is not currently enabled.
        self._drag_value += drag_amount

        # Apply the new value
        if self.enable_float_drag:
            self.set_value(self._drag_value)
        else:
            self.set_value(int(round(self._drag_value, 0)))

    def on_double_tap(self):
        #
        # A double-click has occurred. Start editing.
        #
        self.start_editing()

    def start_editing(self):
        """
        Start editing by setting focus and then selecting all text.
        """
        def work_func(_):
            self.focus = True
            self.select_all()

        Clock.schedule_once(lambda dt: work_func(dt), 0)

    def get_mouse_drag_increment(self, drag_distance):
        return drag_distance * (1 / 3)

    def increment_value(self):
        self.set_value(self.value + (self.fine_increment if self.fine_mode else self.coarse_increment))

    def decrement_value(self):
        self.set_value(self.value - (self.fine_increment if self.fine_mode else self.coarse_increment))

    def on_mouseover(self, _, pos):
        if self.collide_point(*pos):
            # The mouse has entered the control
            self.mouse_inside_bounds = True

        else:
            if self.mouse_inside_bounds:
                # The mouse has exited
                self.mouse_inside_bounds = False


class DiscreteValuesControl(ValueControl):
    """
    A control which can be set only to specific values.
    Internally it uses a mapping of the values to integers.
    """
    values_list = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.coarse_increment = 1
        self.fine_increment = 1
        self.enable_float_drag = False
        self.enable_float_value = False
        self.float_value_decimal_places = 0

        self.bind(values_list=self.on_values_list)

    def _update_text(self):
        """
        Convert the current value to a string and set the text with it
        """
        if 0 <= self.value < len(self.values_list):
            self.text = str(self.values_list[self.value])

        else:
            self.text = str(self.value)

    def on_values_list(self, _, value):
        # A new values list has been supplied.
        # Update max value to the length of the list minus 1
        self.max_value = len(self.values_list) - 1

        if self.value >= len(self.values_list):
            self.value = len(self.values_list) - 1

            self._update_text()



