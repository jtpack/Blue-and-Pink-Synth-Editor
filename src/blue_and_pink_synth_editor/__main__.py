from multiprocessing import set_start_method, freeze_support
from blue_and_pink_synth_editor.BlueAndPinkSynthEditorApp import BlueAndPinkSynthEditorApp


def main():
    freeze_support()
    set_start_method('spawn')
    try:
        BlueAndPinkSynthEditorApp().run()
    except KeyboardInterrupt:
        print("Blue and Pink Synth Editor is stopping...")


if __name__ == '__main__':
    main()
