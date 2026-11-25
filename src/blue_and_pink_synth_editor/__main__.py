if __name__ == '__main__':
    from multiprocessing import set_start_method, freeze_support
    freeze_support()

    set_start_method('spawn')
    from src.blue_and_pink_synth_editor.BlueAndPinkSynthEditorApp import BlueAndPinkSynthEditorApp
    try:
        BlueAndPinkSynthEditorApp().run()
    except KeyboardInterrupt:
        print("Blue and Pink Synth Editor is stopping...")
