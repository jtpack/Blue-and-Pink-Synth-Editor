from src.nymphes_gui.NymphesGuiApp import NymphesGuiApp
from multiprocessing import set_start_method, freeze_support


def main():
    NymphesGuiApp().run()


if __name__ == '__main__':
    set_start_method('spawn')
    freeze_support()
    main()
