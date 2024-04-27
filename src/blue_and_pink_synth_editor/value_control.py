from kivy.properties import NumericProperty, StringProperty, ObjectProperty, BooleanProperty
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
import re

class ValueControl(TextInput):
    screen_name = StringProperty('')
    section_name = StringProperty('')
    param_name = StringProperty('')
    min_value = NumericProperty(0)
    max_value = NumericProperty(127)
    fine_mode = BooleanProperty(False)
    setter_function = ObjectProperty(None)
    drag_start_pos = NumericProperty(0)
    text_color_string = StringProperty('#06070FFF')
    mouse_pressed = BooleanProperty(False)
    mouse_inside_bounds = BooleanProperty(False)
    base_font_size = NumericProperty(20)
    curr_state = StringProperty('idle')
    mouse_status = StringProperty('idle')

    pat = re.compile('[^0-9]')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline = False
        self.readonly = False
        self.background_color = (0, 0, 0, 0)
        #Window.bind(mouse_pos=self.on_mouseover)
        self.bind(focus=self.on_focus)
        #self.bind(on_text_validate=self.on_enter_key)
        self.bind(disabled=self.on_disabled)
        self.bind(fine_mode=self.on_fine_mode)
        self.bind(mouse_status=self.on_mouse_status)

        self._prev_text = self.text

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

    def on_disabled(self, _, value):
        self.curr_state = 'disabled' if value else 'idle'

    def on_mouse_status(self, _, value):
        print(f'mouse_status: {self.mouse_status}')

        match self.mouse_status:
            case 'clicked':
                pass


    # def on_mouseover(self, _, pos):
    #     if self.collide_point(*pos):
    #         #
    #         # The mouse is inside the control's bounds
    #         #
    #         if self.curr_state == 'idle':
    #             self.curr_state = 'mouse_entered'
    #
    #     else:
    #         #
    #         # The mouse is outside the control's bounds
    #         #
    #         if self.curr_state == 'mouse_over':
    #             self.curr_state = 'mouse_exited'

    def on_touch_down(self, touch):
        #
        # This is called when the mouse is clicked
        #
        if self.mouse_status == 'editing':
            return super().on_touch_down(touch)

        else:

            if not self.disabled and self.collide_point(*touch.pos) and touch.button == 'left':
                #
                # We were idle, the left mouse button has been clicked, and it was inside our bounds
                #
                touch.grab(self)
                self.mouse_status = 'pressed'
                super().on_touch_down(touch)
                return True
            #
            #     super().on_touch_down(touch)
            #
            #
            #     # Store the starting y position of the touch
            #     self.drag_start_pos = int(touch.pos[1])
            #
            #     # The mouse is pressed
            #     self.curr_state = 'mouse_click_started'
            #
            #     # Inform the app that a drag has started
            #     App.get_running_app().set_curr_mouse_dragging_param_name(self.param_name)
            #
            #     return True
            #
            else:
                return super().on_touch_down(touch)
    #
    def on_touch_move(self, touch):
        #
        # This is called when the mouse drags
        #

        if self.mouse_status == 'editing':
            return super().on_touch_move(touch)

        else:
            if touch.grab_current == self:
                #super().on_touch_move(touch)
                self.mouse_status = 'dragging'
                return True
    #
    #         # The mouse is dragging
    #         if self.curr_state == 'mouse_click_started':
    #             self.curr_state = 'mouse_dragging'
    #
    #         # Get the current y position
    #         curr_pos = int(touch.pos[1])
    #
    #         # Calculate the distance from the starting drag position
    #         curr_drag_distance = (self.drag_start_pos - curr_pos) * -1
    #
    #         # Scale the drag distance and use as the increment
    #         increment = self.get_mouse_drag_increment(curr_drag_distance)
    #
    #         # Increment the property's value
    #         App.get_running_app().increment_prop_value_for_param_name(self.param_name, increment)
    #
    #         # Reset the drag start position to the current position
    #         self.drag_start_pos = curr_pos
    #
    #         return True
    #
    #     else:
    #         return super().on_touch_move(touch)
    #
    def on_touch_up(self, touch):
        if self.mouse_status == 'editing':
            return super().on_touch_up(touch)

        else:

            if touch.grab_current == self:
                touch.ungrab(self)
                if self.mouse_status == 'dragging':
                    self.mouse_status = 'idle'
                elif self.mouse_status == 'pressed':
                    super().on_touch_up(touch)
                    self.mouse_status = 'clicked'

                #super().on_touch_up(touch)
                return True



    #
    #         if self.curr_state == 'mouse_dragging':
    #             #
    #             # We are no longer dragging
    #             #
    #
    #             App.get_running_app().set_curr_mouse_dragging_param_name('')
    #             self.curr_state = 'idle'
    #
    #             print('drag ended')
    #
    #         elif self.curr_state == 'mouse_click_started':
    #             #
    #             # The mouse has been released after a click,
    #             # but not a drag
    #             #
    #
    #             self.curr_state = 'idle'
    #             print('mouse click ended')
    #
    #         return True
    #
    #     else:
    #         return super().on_touch_up(touch)
    #
    # def handle_touch(self, device, button):
    #     #
    #     # Mouse Wheel
    #     #
    #     if self.disabled:
    #         return False
    #
    #     if device == 'mouse' and button in ['scrollup', 'scrolldown']:
    #         # Determine direction
    #         direction = 1 if button == 'scrollup' else -1
    #
    #         # Apply mouse wheel inversion, if enabled
    #         if App.get_running_app().invert_mouse_wheel:
    #             direction *= -1
    #
    #         # Determine the increment
    #         #
    #         increment = self.get_mouse_wheel_increment()
    #         if isinstance(increment, float):
    #             increment *= float(direction)
    #         else:
    #             increment *= direction
    #
    #         # Increment the property
    #         App.get_running_app().increment_prop_value_for_param_name(self.param_name, increment)

    def get_mouse_wheel_increment(self):
        return 1

    def get_mouse_drag_increment(self, drag_distance):
        return int(round(drag_distance * (1 / 3)))

    def on_focus(self, instance, value):
        if value:
            #
            # Editing has started
            #

            # Store the previous text value, in
            # case we need to restore it when
            # editing ends because an invalid
            # value has been entered.
            self._prev_text = self.text

            print(f'prev_text: {self._prev_text}')
            self.mouse_status = 'editing'

        if not value:
            #
            # Focus has been lost, which means
            # that editing has just ended.
            #

            # Get the new text converted to a
            # number
            new_value = self._get_value()

            if new_value is not None:
                print(f'New Value: {new_value}')

            else:
                print('New value was None')

            if self.mouse_status == 'editing':
                self.mouse_status = 'idle'
    #
    # def on_enter_key(self, instance):
    #     #
    #     # The Enter key has been pressed.
    #     #
    #
    #     # Get the new text converted to a
    #     # number
    #     new_value = self._get_value()
    #
    #     if new_value is not None:
    #         print(f'New Value: {new_value}')
    #
    #     else:
    #         print('New value was None')
    #
    def on_double_tap(self):
        # Start editing
        self.focus = True

    def _get_value(self):
        # Convert our current text into a number
        try:
            return int(self.text)

        except ValueError:
            return None

    def on_fine_mode(self, _, value):
        print(f'on_fine_mode: {value}')
