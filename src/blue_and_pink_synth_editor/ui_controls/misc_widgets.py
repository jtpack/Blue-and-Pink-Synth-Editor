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
import webbrowser


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
                return True

            else:
                return False

        else:
            return super().on_touch_up(touch)


class VoiceModeButton(HoverButton):
    voice_mode_name = StringProperty('')


class LegatoBox(BoxLayout):
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')


class BackButtonBox(BoxLayout):
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')


class FineModeBox(BoxLayout):
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')


class ControlSection(BoxLayout):
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')
    param_name_color_string = StringProperty('#ECBFEB')


class SectionTitleLabel(ButtonBehavior, Label):
    pass


class ParamsGrid(GridLayout):
    corner_radius = NumericProperty(0)


class ParamNameLabel(ButtonBehavior, Label):
    text_color_string = StringProperty('#ECBFEBFF')


class WebsiteButtonLabel(ButtonBehavior, Label):
    hovered = BooleanProperty(False)
    border_point = (0, 0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

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
