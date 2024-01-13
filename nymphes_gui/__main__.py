import logging
from nymphes_gui.NymphesGuiApp import NymphesGuiApp


def main():
    NymphesGuiApp(log_level=logging.DEBUG).run()


if __name__ == '__main__':
    main()
