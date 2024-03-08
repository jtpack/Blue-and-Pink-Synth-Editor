
if __name__ == '__main__':
    from src.nymphes_gui.NymphesGuiApp import NymphesGuiApp
    from multiprocessing import set_start_method, freeze_support
    freeze_support()
    set_start_method('spawn')
    NymphesGuiApp().run()
