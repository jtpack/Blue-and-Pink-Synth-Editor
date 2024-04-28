from kivy.properties import NumericProperty, StringProperty, ObjectProperty, BooleanProperty
from kivy.uix.textinput import TextInput
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
    magnification_amount = NumericProperty(1.08)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False
        self.readonly = False
        self.background_color = (0, 0, 0, 0)

        self.bind(external_value=self.on_external_value)
        self.bind(focus=self.on_focus)
        self.bind(on_text_validate=self.on_enter_key)



    #
    # Limit text input to numbers and decimal point
    #

    pat = re.compile('[^0-9]')

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
        if not self.enable_float_value:
            self.text = str(int(self.value))
        else:
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