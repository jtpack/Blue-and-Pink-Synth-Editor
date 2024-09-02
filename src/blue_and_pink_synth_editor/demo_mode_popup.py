from kivy.uix.boxlayout import BoxLayout


class DemoModePopup(BoxLayout):
    # TODO: Remove this if it isn't needed.
    def dismiss_popup(self):
        self.parent_popup.dismiss()

    