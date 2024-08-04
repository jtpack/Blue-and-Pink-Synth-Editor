from kivy.properties import NumericProperty, StringProperty, ObjectProperty, BooleanProperty, ListProperty
from kivy.uix.textinput import TextInput, CutBuffer
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.core.window import Window
import re


class ValueControl(TextInput):
    """
    This is a numeric value control that allows users to
    adjust the value by mouse dragging up and down,
    using the mouse scroll wheel to increment/decrement
    or typing in the desired value.

    It is also possible to simply increment/decrement
    the value using coarse or fine increment amounts.

    min_value, max_value and coarse_increment are all integers.
    fine_increment is a float.
    value will be an integer if fine_mode if False.
    It will be a float if fine_mode is True.

    min_value must be lower than max_value. An Exception will be
    raised if min_value or max_value are set in a way that violates
    this rule.

    If value is manually set to a float value (by typing the value),
    then it will temporarily be a float even if fine_mode is not True.
    However, dragging or incrementing the value will cause the value
    to jump to the next coarse integer value, and then continue to
    use the coarse increment values after that.

    If the min and max values are both >= 0, or are both <= 0
    (ie: 0 to 127 or -127 to 0),
    then the values accessible by incrementing/decrementing
    will start at the min value and step by the increment
    amount until reaching the max value. If the max value
    is not a multiple of the increment amount, then it is
    included in the list as the final value.

    If the min and max values cross 0 (ie: a range of -127 to 127),
    then the values accessible via incrementing/decrementing will
    be generated symmetrically around 0 (ie: for a range of
    -12 to 12 with increment amount 5: -12, -10, -5, 0, 5, 10, 12)
    """
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
    currently_dragging = BooleanProperty(False)
    coarse_increment_values_list = ListProperty([])
    drag_distance_for_full_value_range = NumericProperty(500.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bind(external_value=self.on_external_value)
        self.bind(focus=self.on_focus)
        self.bind(on_text_validate=self.on_enter_key)
        Window.bind(mouse_pos=self.on_mouseover)
        self.bind(on_min_value=self.on_min_value)
        self.bind(on_max_value=self.on_max_value)
        self.bind(on_coarse_increment=self.on_coarse_increment)

        self._drag_start_pos = 0.0
        self._drag_value = 0.0

        self.multiline = False
        self.readonly = False
        self.background_color = (0, 0, 0, 0)
        self.font_size = self.base_font_size
        self._update_text()

    # Limit text input to numbers and decimal point
    #

    pat = re.compile('[^0-9.-]')

    def on_kv_post(self, base_widget):
        self._update_coarse_increment_values_list()

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
        if self.float_value_decimal_places == 0:
            self.text = str(int(self.value))
        else:
            self.text = f'{round(self.value, self.float_value_decimal_places):.{self.float_value_decimal_places}f}'

    def _update_coarse_increment_values_list(self):
        """
        Recalculate the coarse increment values list based
        on min and max values and increment amount.

        If the min and max values are both >= 0, or are both <= 0
        (ie: 0 to 127 or -127 to 0),
        then the values accessible by incrementing/decrementing
        will start at the min value and step by the increment
        amount until reaching the max value. If the max value
        is not a multiple of the increment amount, then it is
        included in the list as the final value.

        If the min and max values cross 0 (ie: a range of -127 to 127),
        then the values accessible via incrementing/decrementing will
        be generated symmetrically around 0 (ie: for a range of
        -12 to 12 with increment amount 5: -12, -10, -5, 0, 5, 10, 12)
        """
        if (self.min_value <= 0 and self.max_value <= 0) or (self.min_value >= 0 and self.max_value >= 0):
            #
            # Min and max values are on the same side of zero, so our values list
            # is a simple list starting at the min value and ending with the max
            # value.
            #

            values_list = [x for x in range(self.min_value, self.max_value, self.coarse_increment)]

            # Make sure max value is in the list
            if self.max_value not in values_list:
                values_list.append(self.max_value)

            # Store the list
            self.coarse_increment_values_list = values_list

        else:
            #
            # The min and max values are on either side of zero, so we
            # need to create the two halves to they are symmetrical
            # around zero.
            #

            #
            # Create the positive and negative portions of the list separately
            #

            positive_values_list = [x for x in range(0, self.max_value, self.coarse_increment)]
            if self.max_value not in positive_values_list:
                positive_values_list.append(self.max_value)

            negative_values_list = sorted([-x for x in range(0, self.min_value * -1, self.coarse_increment)])
            if self.min_value not in negative_values_list:
                negative_values_list.append(self.min_value)
                negative_values_list.sort()

            combined_values_list = sorted(set(positive_values_list + negative_values_list))

            # Store the list
            self.coarse_increment_values_list = combined_values_list

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
        #
        # Handle Mouse Clicks
        #
        if self.disabled:
            return False

        if not self.collide_point(*touch.pos) and touch.button == 'left':
            if self.focus:
                self.focus = False
            return False

        if self.collide_point(*touch.pos) and touch.button == 'left':
            #
            # Don't let TextInput parent class start editing on the first click
            #
            if super().on_touch_down(touch):
                if self.focus:
                    self.focus = False

            # Grab the touch
            if touch.grab_current != self:
                touch.grab(self)

            # Store the starting y position of the touch
            # in case it becomes a mouse drag
            self._drag_start_pos = float(touch.pos[1])

            # Store the current value as well
            self._drag_value = self.value

            return True

        #
        # Handle mouse wheel
        #
        if self.collide_point(*touch.pos) and 'button' in touch.profile and touch.button.startswith('scroll'):
            # If editing was occurring and
            # a scroll has now happened, cancel
            # focus
            if self.focus:
                self.focus = False

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

        # If we get here then let the textinput
        # handle the touch
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return

        if not self.currently_dragging:
            self.currently_dragging = True

        # If editing was occurring and
        # a drag has now happened, cancel
        # focus
        if self.focus:
            self.focus = False

        # Get the current Y position
        curr_pos = float(touch.pos[1])

        # Calculate the distance from the starting drag position
        curr_drag_distance = (self._drag_start_pos - curr_pos) * -1

        # Store the new drag start position
        self._drag_start_pos = float(touch.pos[1])

        # Calculate how much the value should change
        #
        drag_amount = (curr_drag_distance / self.drag_distance_for_full_value_range) * (abs(self.max_value - self.min_value))

        if self.fine_mode:
            drag_amount *= 0.05

        self._drag_value += drag_amount

        # Apply the new value
        if self.enable_float_drag:
            self.set_value(self._drag_value)
        else:
            self.set_value(int(round(self._drag_value + drag_amount, 0)))

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            if self.currently_dragging:
                self.currently_dragging = False

            touch.ungrab(self)
            return True

        else:
            return False

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
            #super(ValueControl, self)._bind_keyboard()

        Clock.schedule_once(lambda dt: work_func(dt), 0)

    def get_mouse_drag_increment(self, drag_distance):
        return drag_distance * (1 / 3)

    def increment_value(self):
        if self.fine_mode:
            self.set_value(self.value + self.fine_increment)

        else:
            # Find the next value in the coarse increment values list
            for val in self.coarse_increment_values_list:
                if val > self.value:
                    self.set_value(val)
                    break

    def decrement_value(self):
        if self.fine_mode:
            self.set_value(self.value - self.fine_increment)

        else:
            # Find the prev value in the coarse increment values list
            for val in sorted(self.coarse_increment_values_list, reverse=True):
                if val < self.value:
                    self.set_value(val)
                    break

    def on_mouseover(self, _, pos):
        if not self.disabled:
            if self.collide_point(*pos):
                # The mouse has entered the control
                self.mouse_inside_bounds = True

            else:
                if self.mouse_inside_bounds:
                    # The mouse has exited
                    self.mouse_inside_bounds = False

    def _bind_keyboard(self):
        # Do not actually bind the keyboard until
        # editing starts
        pass

    def _unbind_keyboard(self):
        super()._unbind_keyboard()

    def on_min_value(self, _, __):
        # Ensure min_value is an integer
        self.min_value = int(self.min_value)

        # Ensure min_value is not equal to or greater
        # than max_value
        if self.min_value >= self.max_value:
            raise Exception(f'min_value must be smaller than max_value')

        # Update the coarse increment values list
        self._update_coarse_increment_values_list()

    def on_max_value(self, _, __):
        # Ensure max_value is an integer
        self.max_value = int(self.max_value)

        # Ensure max_value is not equal to or smaller
        # than min_value
        if self.max_value <= self.min_value:
            raise Exception(f'max_value must be greater than min_value')

        # Update the coarse increment values list
        self._update_coarse_increment_values_list()
        
    def on_coarse_increment(self, _, __):
        # Ensure the increment is an integer
        self.coarse_increment = int(self.coarse_increment)

        # Update the coarse increment values list
        self._update_coarse_increment_values_list()


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

    def start_editing(self):
        def work_func(_):
            # Replace the text value with its numeric value
            self.text = str(int(self.value))

            # Let superclass handle the rest
            super(DiscreteValuesControl, self).start_editing()

        Clock.schedule_once(lambda dt: work_func(dt), 0)
