import logging
from pathlib import Path
import os
import threading
import configparser
import netifaces
import platform
import subprocess
import glob

from kivy.config import Config
Config.read(str(Path(__file__).resolve().parent / 'app_config.ini'))

from kivy.app import App
import kivy
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.core.window import Window
from kivy.lang.builder import Builder

from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.osc_message_builder import OscMessageBuilder

from kivy.logger import Logger, LOG_LEVELS
Logger.setLevel(LOG_LEVELS["debug"])

from nymphes_midi.NymphesPreset import NymphesPreset
from src.blue_and_pink_synth_editor.nymphes_osc_process import NymphesOscProcess

from src.blue_and_pink_synth_editor.ui_controls.load_dialog import LoadDialog
from src.blue_and_pink_synth_editor.ui_controls.save_dialog import SaveDialog, SavePopup
from src.blue_and_pink_synth_editor.ui_controls.error_dialog import ErrorDialog
from src.blue_and_pink_synth_editor.ui_controls import chords_screen
from src.blue_and_pink_synth_editor.ui_controls import value_control
from src.blue_and_pink_synth_editor.ui_controls import synth_editor_value_controls
from src.blue_and_pink_synth_editor.ui_controls import left_bar
from src.blue_and_pink_synth_editor.ui_controls import top_bar
from src.blue_and_pink_synth_editor.ui_controls import params_grid_mod_cell
from src.blue_and_pink_synth_editor.ui_controls import params_grid_non_mod_cell
from src.blue_and_pink_synth_editor.ui_controls import params_grid_lfo_config_cell
from src.blue_and_pink_synth_editor.ui_controls import settings_screen
from src.blue_and_pink_synth_editor.ui_controls import bottom_bar
from src.blue_and_pink_synth_editor.ui_controls.demo_mode_popup import DemoModePopup
from src.activation_code_verifier.code_verifier import load_activation_code_from_file, verify_activation_code, data_from_activation_code, load_public_key_from_file

Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)

#
# Make sure that activation_code_enabled.py file exists.
# The file is not a part of the git repository
# so that open-source users automatically don't
# need to have an activation code to use the app.
# However, those who do want to enable
# activation code-checking, demo-mode and other
# related features can do so by setting
# the return value in this file to True
#

activation_code_checking_file_path = Path(__file__).parent / 'activation_code_enabled.py'
if not activation_code_checking_file_path.exists():
    print(f'activation_code_enabled.py does not exist at {activation_code_checking_file_path}')
    # Create the file and populate it with its only function
    activation_code_checking_file_contents = """def activation_code_checking_enabled():
    return False
    """
    try:
        with open(activation_code_checking_file_path, 'w') as file:
            file.write(activation_code_checking_file_contents)
            print(f'Created activation_code_enabled.py file at {activation_code_checking_file_path}')

    except Exception as e:
        print(f'Failed to create activation_code_enabled.py file at {activation_code_checking_file_path}')

# Now import it
from src.blue_and_pink_synth_editor.activation_code_enabled import activation_code_checking_enabled

kivy.require('2.1.0')

app_version_string = 'v0.3.1-beta_dev'


class BlueAndPinkSynthEditorApp(App):
    # Disable the built-in kivy settings editor normally activated
    # by pressing F1 key.
    def open_settings(self, *args):
        pass

    nymphes_connected = BooleanProperty(False)
    nymphes_midi_channel = NumericProperty(1)
    midi_feedback_suppression_enabled = BooleanProperty(False)

    mod_wheel = NumericProperty(0)
    velocity = NumericProperty(0)
    aftertouch = NumericProperty(0)
    sustain_pedal = BooleanProperty(False)

    detected_midi_input_names_for_gui = ListProperty([])
    detected_midi_output_names_for_gui = ListProperty([])

    connected_midi_input_names_for_gui = ListProperty([])
    connected_midi_output_names_for_gui = ListProperty([])

    nymphes_input_spinner_names = ListProperty(['Not Connected'])
    nymphes_output_spinner_names = ListProperty(['Not Connected'])

    nymphes_input_name = StringProperty('Not Connected')
    nymphes_output_name = StringProperty('Not Connected')

    presets_spinner_text = StringProperty('PRESET')
    presets_spinner_values = ListProperty()

    # This is used to track what kind of preset is currently loaded.
    # Valid values: 'init', 'file', 'preset_slot'
    curr_preset_type = StringProperty('')

    midi_inputs_spinner_curr_value = StringProperty('Not Connected')
    midi_outputs_spinner_curr_value = StringProperty('Not Connected')

    status_bar_text = StringProperty('NYMPHES NOT CONNECTED')
    error_text = StringProperty('')
    error_detail_text = StringProperty('')

    unsaved_preset_changes = BooleanProperty(False)

    curr_mouse_hover_param_name = StringProperty('')
    curr_mouse_dragging_param_name = StringProperty('')
    curr_keyboard_editing_param_name = StringProperty('')
    curr_screen_name = StringProperty('main')
    prev_screen_name = StringProperty('main')

    #
    # Nymphes Parameters
    #

    osc_wave_value = NumericProperty(0.0)
    osc_wave_lfo2 = NumericProperty(0.0)
    osc_wave_mod_wheel = NumericProperty(0.0)
    osc_wave_velocity = NumericProperty(0.0)
    osc_wave_aftertouch = NumericProperty(0.0)

    osc_pulsewidth_value = NumericProperty(0.0)
    osc_pulsewidth_lfo2 = NumericProperty(0.0)
    osc_pulsewidth_mod_wheel = NumericProperty(0.0)
    osc_pulsewidth_velocity = NumericProperty(0.0)
    osc_pulsewidth_aftertouch = NumericProperty(0.0)

    osc_voice_mode_value = NumericProperty(0)
    osc_legato_value = NumericProperty(0)

    mix_osc_value = NumericProperty(0.0)
    mix_osc_lfo2 = NumericProperty(0.0)
    mix_osc_mod_wheel = NumericProperty(0.0)
    mix_osc_velocity = NumericProperty(0.0)
    mix_osc_aftertouch = NumericProperty(0.0)

    mix_sub_value = NumericProperty(0.0)
    mix_sub_lfo2 = NumericProperty(0.0)
    mix_sub_mod_wheel = NumericProperty(0.0)
    mix_sub_velocity = NumericProperty(0.0)
    mix_sub_aftertouch = NumericProperty(0.0)

    mix_noise_value = NumericProperty(0.0)
    mix_noise_lfo2 = NumericProperty(0.0)
    mix_noise_mod_wheel = NumericProperty(0.0)
    mix_noise_velocity = NumericProperty(0.0)
    mix_noise_aftertouch = NumericProperty(0.0)

    mix_level_value = NumericProperty(0.0)

    pitch_glide_value = NumericProperty(0.0)
    pitch_glide_lfo2 = NumericProperty(0.0)
    pitch_glide_mod_wheel = NumericProperty(0.0)
    pitch_glide_velocity = NumericProperty(0.0)
    pitch_glide_aftertouch = NumericProperty(0.0)

    pitch_detune_value = NumericProperty(0.0)
    pitch_detune_lfo2 = NumericProperty(0.0)
    pitch_detune_mod_wheel = NumericProperty(0.0)
    pitch_detune_velocity = NumericProperty(0.0)
    pitch_detune_aftertouch = NumericProperty(0.0)

    pitch_chord_value = NumericProperty(0.0)
    pitch_chord_lfo2 = NumericProperty(0.0)
    pitch_chord_mod_wheel = NumericProperty(0.0)
    pitch_chord_velocity = NumericProperty(0.0)
    pitch_chord_aftertouch = NumericProperty(0.0)

    pitch_eg_value = NumericProperty(0.0)
    pitch_eg_lfo2 = NumericProperty(0.0)
    pitch_eg_mod_wheel = NumericProperty(0.0)
    pitch_eg_velocity = NumericProperty(0.0)
    pitch_eg_aftertouch = NumericProperty(0.0)

    pitch_lfo1_value = NumericProperty(0.0)
    pitch_lfo1_lfo2 = NumericProperty(0.0)
    pitch_lfo1_mod_wheel = NumericProperty(0.0)
    pitch_lfo1_velocity = NumericProperty(0.0)
    pitch_lfo1_aftertouch = NumericProperty(0.0)

    lpf_cutoff_value = NumericProperty(0.0)
    lpf_cutoff_lfo2 = NumericProperty(0.0)
    lpf_cutoff_mod_wheel = NumericProperty(0.0)
    lpf_cutoff_velocity = NumericProperty(0.0)
    lpf_cutoff_aftertouch = NumericProperty(0.0)

    lpf_resonance_value = NumericProperty(0.0)
    lpf_resonance_lfo2 = NumericProperty(0.0)
    lpf_resonance_mod_wheel = NumericProperty(0.0)
    lpf_resonance_velocity = NumericProperty(0.0)
    lpf_resonance_aftertouch = NumericProperty(0.0)

    lpf_tracking_value = NumericProperty(0.0)
    lpf_tracking_lfo2 = NumericProperty(0.0)
    lpf_tracking_mod_wheel = NumericProperty(0.0)
    lpf_tracking_velocity = NumericProperty(0.0)
    lpf_tracking_aftertouch = NumericProperty(0.0)

    lpf_eg_value = NumericProperty(0.0)
    lpf_eg_lfo2 = NumericProperty(0.0)
    lpf_eg_mod_wheel = NumericProperty(0.0)
    lpf_eg_velocity = NumericProperty(0.0)
    lpf_eg_aftertouch = NumericProperty(0.0)

    lpf_lfo1_value = NumericProperty(0.0)
    lpf_lfo1_lfo2 = NumericProperty(0.0)
    lpf_lfo1_mod_wheel = NumericProperty(0.0)
    lpf_lfo1_velocity = NumericProperty(0.0)
    lpf_lfo1_aftertouch = NumericProperty(0.0)

    hpf_cutoff_value = NumericProperty(0.0)
    hpf_cutoff_lfo2 = NumericProperty(0.0)
    hpf_cutoff_mod_wheel = NumericProperty(0.0)
    hpf_cutoff_velocity = NumericProperty(0.0)
    hpf_cutoff_aftertouch = NumericProperty(0.0)

    filter_eg_attack_value = NumericProperty(0.0)
    filter_eg_attack_lfo2 = NumericProperty(0.0)
    filter_eg_attack_mod_wheel = NumericProperty(0.0)
    filter_eg_attack_velocity = NumericProperty(0.0)
    filter_eg_attack_aftertouch = NumericProperty(0.0)

    filter_eg_decay_value = NumericProperty(0.0)
    filter_eg_decay_lfo2 = NumericProperty(0.0)
    filter_eg_decay_mod_wheel = NumericProperty(0.0)
    filter_eg_decay_velocity = NumericProperty(0.0)
    filter_eg_decay_aftertouch = NumericProperty(0.0)

    filter_eg_sustain_value = NumericProperty(0.0)
    filter_eg_sustain_lfo2 = NumericProperty(0.0)
    filter_eg_sustain_mod_wheel = NumericProperty(0.0)
    filter_eg_sustain_velocity = NumericProperty(0.0)
    filter_eg_sustain_aftertouch = NumericProperty(0.0)

    filter_eg_release_value = NumericProperty(0.0)
    filter_eg_release_lfo2 = NumericProperty(0.0)
    filter_eg_release_mod_wheel = NumericProperty(0.0)
    filter_eg_release_velocity = NumericProperty(0.0)
    filter_eg_release_aftertouch = NumericProperty(0.0)

    amp_eg_attack_value = NumericProperty(0.0)
    amp_eg_attack_lfo2 = NumericProperty(0.0)
    amp_eg_attack_mod_wheel = NumericProperty(0.0)
    amp_eg_attack_velocity = NumericProperty(0.0)
    amp_eg_attack_aftertouch = NumericProperty(0.0)

    amp_eg_decay_value = NumericProperty(0.0)
    amp_eg_decay_lfo2 = NumericProperty(0.0)
    amp_eg_decay_mod_wheel = NumericProperty(0.0)
    amp_eg_decay_velocity = NumericProperty(0.0)
    amp_eg_decay_aftertouch = NumericProperty(0.0)

    amp_eg_sustain_value = NumericProperty(0.0)
    amp_eg_sustain_lfo2 = NumericProperty(0.0)
    amp_eg_sustain_mod_wheel = NumericProperty(0.0)
    amp_eg_sustain_velocity = NumericProperty(0.0)
    amp_eg_sustain_aftertouch = NumericProperty(0.0)

    amp_eg_release_value = NumericProperty(0.0)
    amp_eg_release_lfo2 = NumericProperty(0.0)
    amp_eg_release_mod_wheel = NumericProperty(0.0)
    amp_eg_release_velocity = NumericProperty(0.0)
    amp_eg_release_aftertouch = NumericProperty(0.0)

    lfo1_rate_value = NumericProperty(0.0)
    lfo1_rate_lfo2 = NumericProperty(0.0)
    lfo1_rate_mod_wheel = NumericProperty(0.0)
    lfo1_rate_velocity = NumericProperty(0.0)
    lfo1_rate_aftertouch = NumericProperty(0.0)

    lfo1_wave_value = NumericProperty(0.0)
    lfo1_wave_lfo2 = NumericProperty(0.0)
    lfo1_wave_mod_wheel = NumericProperty(0.0)
    lfo1_wave_velocity = NumericProperty(0.0)
    lfo1_wave_aftertouch = NumericProperty(0.0)

    lfo1_delay_value = NumericProperty(0.0)
    lfo1_delay_lfo2 = NumericProperty(0.0)
    lfo1_delay_mod_wheel = NumericProperty(0.0)
    lfo1_delay_velocity = NumericProperty(0.0)
    lfo1_delay_aftertouch = NumericProperty(0.0)

    lfo1_fade_value = NumericProperty(0.0)
    lfo1_fade_lfo2 = NumericProperty(0.0)
    lfo1_fade_mod_wheel = NumericProperty(0.0)
    lfo1_fade_velocity = NumericProperty(0.0)
    lfo1_fade_aftertouch = NumericProperty(0.0)

    lfo1_type_value = NumericProperty(0)
    lfo1_key_sync_value = NumericProperty(0)

    lfo2_rate_value = NumericProperty(0.0)
    lfo2_rate_lfo2 = NumericProperty(0.0)
    lfo2_rate_mod_wheel = NumericProperty(0.0)
    lfo2_rate_velocity = NumericProperty(0.0)
    lfo2_rate_aftertouch = NumericProperty(0.0)

    lfo2_wave_value = NumericProperty(0.0)
    lfo2_wave_lfo2 = NumericProperty(0.0)
    lfo2_wave_mod_wheel = NumericProperty(0.0)
    lfo2_wave_velocity = NumericProperty(0.0)
    lfo2_wave_aftertouch = NumericProperty(0.0)

    lfo2_delay_value = NumericProperty(0.0)
    lfo2_delay_lfo2 = NumericProperty(0.0)
    lfo2_delay_mod_wheel = NumericProperty(0.0)
    lfo2_delay_velocity = NumericProperty(0.0)
    lfo2_delay_aftertouch = NumericProperty(0.0)

    lfo2_fade_value = NumericProperty(0.0)
    lfo2_fade_lfo2 = NumericProperty(0.0)
    lfo2_fade_mod_wheel = NumericProperty(0.0)
    lfo2_fade_velocity = NumericProperty(0.0)
    lfo2_fade_aftertouch = NumericProperty(0.0)

    lfo2_type_value = NumericProperty(0)
    lfo2_key_sync_value = NumericProperty(0)

    reverb_size_value = NumericProperty(0.0)
    reverb_size_lfo2 = NumericProperty(0.0)
    reverb_size_mod_wheel = NumericProperty(0.0)
    reverb_size_velocity = NumericProperty(0.0)
    reverb_size_aftertouch = NumericProperty(0.0)

    reverb_decay_value = NumericProperty(0.0)
    reverb_decay_lfo2 = NumericProperty(0.0)
    reverb_decay_mod_wheel = NumericProperty(0.0)
    reverb_decay_velocity = NumericProperty(0.0)
    reverb_decay_aftertouch = NumericProperty(0.0)

    reverb_filter_value = NumericProperty(0.0)
    reverb_filter_lfo2 = NumericProperty(0.0)
    reverb_filter_mod_wheel = NumericProperty(0.0)
    reverb_filter_velocity = NumericProperty(0.0)
    reverb_filter_aftertouch = NumericProperty(0.0)

    reverb_mix_value = NumericProperty(0.0)
    reverb_mix_lfo2 = NumericProperty(0.0)
    reverb_mix_mod_wheel = NumericProperty(0.0)
    reverb_mix_velocity = NumericProperty(0.0)
    reverb_mix_aftertouch = NumericProperty(0.0)

    chord_0_root_value = NumericProperty(0)
    chord_0_semi_1_value = NumericProperty(0)
    chord_0_semi_2_value = NumericProperty(0)
    chord_0_semi_3_value = NumericProperty(0)
    chord_0_semi_4_value = NumericProperty(0)
    chord_0_semi_5_value = NumericProperty(0)

    chord_1_root_value = NumericProperty(0)
    chord_1_semi_1_value = NumericProperty(0)
    chord_1_semi_2_value = NumericProperty(0)
    chord_1_semi_3_value = NumericProperty(0)
    chord_1_semi_4_value = NumericProperty(0)
    chord_1_semi_5_value = NumericProperty(0)

    chord_2_root_value = NumericProperty(0)
    chord_2_semi_1_value = NumericProperty(0)
    chord_2_semi_2_value = NumericProperty(0)
    chord_2_semi_3_value = NumericProperty(0)
    chord_2_semi_4_value = NumericProperty(0)
    chord_2_semi_5_value = NumericProperty(0)

    chord_3_root_value = NumericProperty(0)
    chord_3_semi_1_value = NumericProperty(0)
    chord_3_semi_2_value = NumericProperty(0)
    chord_3_semi_3_value = NumericProperty(0)
    chord_3_semi_4_value = NumericProperty(0)
    chord_3_semi_5_value = NumericProperty(0)

    chord_4_root_value = NumericProperty(0)
    chord_4_semi_1_value = NumericProperty(0)
    chord_4_semi_2_value = NumericProperty(0)
    chord_4_semi_3_value = NumericProperty(0)
    chord_4_semi_4_value = NumericProperty(0)
    chord_4_semi_5_value = NumericProperty(0)

    chord_5_root_value = NumericProperty(0)
    chord_5_semi_1_value = NumericProperty(0)
    chord_5_semi_2_value = NumericProperty(0)
    chord_5_semi_3_value = NumericProperty(0)
    chord_5_semi_4_value = NumericProperty(0)
    chord_5_semi_5_value = NumericProperty(0)

    chord_6_root_value = NumericProperty(0)
    chord_6_semi_1_value = NumericProperty(0)
    chord_6_semi_2_value = NumericProperty(0)
    chord_6_semi_3_value = NumericProperty(0)
    chord_6_semi_4_value = NumericProperty(0)
    chord_6_semi_5_value = NumericProperty(0)

    chord_7_root_value = NumericProperty(0)
    chord_7_semi_1_value = NumericProperty(0)
    chord_7_semi_2_value = NumericProperty(0)
    chord_7_semi_3_value = NumericProperty(0)
    chord_7_semi_4_value = NumericProperty(0)
    chord_7_semi_5_value = NumericProperty(0)

    voice_mode_name = StringProperty('POLY')
    mod_source = NumericProperty(0)

    # If True then increment float value parameters using
    # float values.
    fine_mode = BooleanProperty(False)
    fine_mode_decimal_places = NumericProperty(NymphesPreset.float_precision_num_decimals)

    invert_mouse_wheel = BooleanProperty(True)

    # Window dimensions
    #
    curr_width = NumericProperty(800)
    curr_height = NumericProperty(480)
    curr_scaling = NumericProperty(1)

    # App Activation
    #
    demo_mode = BooleanProperty(False)
    if activation_code_checking_enabled():
        demo_mode = True

    user_name = StringProperty('')
    user_email = StringProperty('')
    license_type = StringProperty('')
    expiration_date = StringProperty('')

    def __init__(self, **kwargs):
        super(BlueAndPinkSynthEditorApp, self).__init__(**kwargs)

        # Set the app icon
        self.icon = str(Path(__file__).resolve().parent / 'icon.png')

        #
        # Window Aspect Ratio Control
        #

        self.aspect_ratio = 800 / 480
        Window.bind(on_resize=self._on_window_resize)
        self._just_resized_window = False

        #
        # OSC communication with nymphes-osc
        #

        self._nymphes_osc_child_process = None
        self._connected_to_nymphes_osc = False

        # OSC Server that listens for OSC messages from nymphes-osc
        # child process
        self._nymphes_osc_listener = None
        self._nymphes_osc_listener_host = None
        self._nymphes_osc_listener_port = None
        self._nymphes_osc_listener_thread = None
        self._nymphes_osc_listener_dispatcher = Dispatcher()

        # OSC Client that sends OSC messages to nymphes-osc
        # child process
        self._nymphes_osc_sender = None
        self._nymphes_osc_sender_host = None
        self._nymphes_osc_sender_port = None

        #
        # Nymphes Synthesizer State
        #

        # Names of Connected Nymphes MIDI Ports
        self._nymphes_input_port = None
        self._nymphes_output_port = None

        # Names of detected Nymphes MIDI ports
        self._detected_nymphes_midi_inputs = []
        self._detected_nymphes_midi_outputs = []

        # Names of Detected MIDI Ports
        self._detected_midi_inputs = []
        self._detected_midi_outputs = []

        # Names of Connected MIDI Ports
        self._connected_midi_inputs = []
        self._connected_midi_outputs = []

        # If a preset file was loaded, or we have saved a preset file,
        # then this will be a Path object
        self._curr_preset_file_path = None

        # Once a preset has been loaded, this will be
        # either 'user' or 'factory'
        self._curr_preset_slot_type = None

        # Once a preset has been loaded, this will contain
        # the bank name ('A' to 'G') and preset number (1 to 7)
        self._curr_preset_slot_bank_and_number = None, None

        #
        # Presets Spinner Stuff
        #

        values = ['init']
        values.extend(
            [f'{kind} {bank}{num}' for kind in ['USER', 'FACTORY'] for bank in ['A', 'B', 'C', 'D', 'E', 'F', 'G']
             for num in [1, 2, 3, 4, 5, 6, 7]])
        self.presets_spinner_values = values

        self._curr_presets_spinner_index = 0

        self._popup = None

        #
        # Preset File Dialog
        #

        #
        # Create directories to hold app data, like presets
        # config files and activate code file.
        # The location varies with platform. On macOS, we
        # create a folder inside /Applications, and then
        # both the app bundle and the presets folder go
        # into it. The app's config files go into a folder
        # inside ~/Library/Application Support/
        # On other platforms, we create a directory in the
        # user's home folder and put both the presets folder
        # and config files inside.
        #

        os_name = platform.system()

        if os_name == 'Darwin':
            # Create the app data folder. On macOS, the app bundle is also installed
            # in this folder by the pkg installer.
            #
            self._app_data_folder_path = Path(os.path.expanduser('~')) / 'Library/Application Support/Blue and Pink Synth Editor'
            if not self._app_data_folder_path.exists():
                try:
                    self._app_data_folder_path.mkdir()
                    Logger.info(f'Created app data folder at {self._app_data_folder_path}')

                except Exception as e:
                    Logger.critical(f'Failed to create app data folder at {self._app_data_folder_path} ({e})')

            # Create the presets folder
            #
            self._presets_directory_path = self._app_data_folder_path / 'presets'
            if not self._presets_directory_path.exists():
                try:
                    self._presets_directory_path.mkdir()
                    Logger.info(f'Created presets folder at {self._presets_directory_path}')

                except Exception as e:
                    Logger.critical(f'Failed to create presets folder at {self._presets_directory_path} ({e})')

            # Store the path to the config file
            self._config_file_path = self._app_data_folder_path / 'config.txt'

        else:
            # Create the app data folder
            #
            self._app_data_folder_path = Path.home() / 'Blue and Pink Synth Editor Data'
            if not self._app_data_folder_path.exists():
                try:
                    self._app_data_folder_path.mkdir()
                    Logger.info(f'Created app data folder at {self._app_data_folder_path}')

                except Exception as e:
                    Logger.critical(f'Failed to create app data folder at {self._app_data_folder_path} ({e})')

            # Create the presets folder
            #
            self._presets_directory_path = self._app_data_folder_path / 'presets'
            if not self._presets_directory_path.exists():
                try:
                    self._presets_directory_path.mkdir()
                    Logger.info(f'Created presets folder at {self._presets_directory_path}')

                except Exception as e:
                    Logger.critical(f'Failed to create presets folder at {self._presets_directory_path} ({e})')

            # Create the path for the config file
            self._config_file_path = self._app_data_folder_path / 'config.txt'

        # Path to init preset
        self._init_preset_file_path = self._presets_directory_path / 'init.txt'

        # Create a config file if one doesn't exist
        if not Path(self._config_file_path).exists():
            self._create_config_file(self._config_file_path)

        # Load contents of config file
        self._load_config_file(self._config_file_path)

        #
        # Activation Code Verification
        #
        self._activation_code_file_path = self._app_data_folder_path / 'activation_code.txt'
        self._public_key_path = Path(__file__).parent / 'BlueAndPinkSynthEditorLicenseKey_public.pem'

        if activation_code_checking_enabled():
            #
            # Activation code checking is enabled
            #
            Logger.info('Activation code checking is enabled')

            if not self._activation_code_file_path.exists():
                # No activation code file exists.
                # Run the app in demo mode.
                self.demo_mode = True
                Logger.info(f'No activation code file found at {self._activation_code_file_path}')
                Logger.info('Running in Demo Mode')

            else:
                #
                # Load the activation code file and check whether it is valid.
                #
                try:
                    # Load the public key
                    public_key = load_public_key_from_file(self._public_key_path)
                    activation_code = load_activation_code_from_file(self._activation_code_file_path)
                    self.demo_mode = not verify_activation_code(activation_code, public_key)
                    if not self.demo_mode:
                        Logger.info(f'Valid activation code file found at {self._activation_code_file_path}')

                        # Get user info from file
                        user_info = data_from_activation_code(activation_code)
                        self.user_name = user_info['display_name']
                        self.user_email = user_info['email']
                        self.license_type = user_info['license_type']
                        self.expiration_date = user_info['expiration_date'] if user_info['expiration_date'] is not None else 'None'

                        Logger.info('Registered User Info:')
                        Logger.info(f'Name: {self.user_name}')
                        Logger.info(f'Email: {self.user_email}')
                        Logger.info(f'License Type: {self.license_type}')
                        Logger.info(f'Expiration Date: {self.expiration_date}')

                    else:
                        Logger.warning(f'Invalid activation code file found at {self._activation_code_file_path}')
                        Logger.info('Running in Demo Mode')

                except Exception as e:
                    self.demo_mode = True
                    Logger.warning(f'Failed to validate activation code file found at {self._activation_code_file_path} ({e})')
                    Logger.info('Running in Demo Mode')

            # Set the app title
            #
            if not self.demo_mode:
                self.title = f'Blue and Pink Synth Editor {app_version_string} - Registered to {self.user_name}'
            else:
                self.title = f'Blue and Pink Synth Editor {app_version_string} (DEMO MODE)'

        else:
            #
            # Activation code checking is not enabled
            #
            print(f'Activation code checking is not enabled')
            self.demo_mode = False

            # Set the app title
            self.title = f'Blue and Pink Synth Editor {app_version_string}'

        # Bind file drop onto window
        Window.bind(on_drop_file=self._on_file_drop)

    def on_start(self):
        # Store the current window size
        self.curr_width = Window.width
        self.curr_height = Window.height

        Logger.debug(f'Window size: {self.curr_width}, {self.curr_height}')

        # Start the nymphes_osc child process
        self._start_nymphes_osc_child_process()

        #
        # Start OSC Communication
        #

        self._nymphes_osc_sender = SimpleUDPClient(self._nymphes_osc_sender_host, self._nymphes_osc_sender_port)
        self._start_nymphes_osc_listener()

        #
        # Map Incoming OSC Messages
        #
        self._nymphes_osc_listener_dispatcher.map('*', self._on_nymphes_osc_message)

        #
        # Show Demo Mode Popup if we are in Demo Mode
        #
        if self.demo_mode:
            self._show_demo_mode_popup()

    def on_stop(self):
        """
        The app is about to close.
        :return:
        """
        Logger.info('on_stop')

        # Stop the OSC server
        self._stop_nymphes_osc_listener()

        # Stop the nymphes_osc child process
        self._stop_nymphes_osc_child_process()

        # Save the config file
        self._save_config_file(self._config_file_path)

    def set_voice_mode_by_name(self, voice_mode_name):
        """
        Used to set the voice mode by name instead of using a number.
        Possible names are:
        POLY
        UNI-A
        UNI-B
        TRI
        DUO
        MONO
        """

        if voice_mode_name == 'POLY':
            voice_mode_int = 0

        elif voice_mode_name == 'UNI-A':
            voice_mode_int = 1

        elif voice_mode_name == 'UNI-B':
            voice_mode_int = 2

        elif voice_mode_name == 'TRI':
            voice_mode_int = 3

        elif voice_mode_name == 'DUO':
            voice_mode_int = 4

        elif voice_mode_name == 'MONO':
            voice_mode_int = 5

        else:
            raise Exception(f'Invalid voice mode string: {voice_mode_name}')

        # Update the current voice mode
        self.voice_mode_name = voice_mode_name

        # Status bar text
        self._set_prop_value_on_main_thread('status_bar_text', f'osc.voice_mode.value: {voice_mode_int}')

        # Send the command to the Nymphes
        self.send_nymphes_osc('/osc/voice_mode/value', voice_mode_int)

    def set_legato(self, val):
        """
        val is an int. 0 for off, 127 for on.
        """

        # Update the property
        self.osc_legato_value = val

        # Status bar text
        self._set_prop_value_on_main_thread('status_bar_text', f'osc.legato.value: {val}')

        # Send the command to the Nymphes
        self.send_nymphes_osc('/osc/legato/value', val)

    def set_fine_mode(self, enable_fine_mode):
        # Update the property
        self.fine_mode = enable_fine_mode

    def load_preset_by_index(self, preset_index):
        """
        Load the Nymphes preset at preset_index.
        Raises an Exception if preset_index is invalid.
        """
        if preset_index < 0 or preset_index > 97:
            raise Exception(f'Invalid preset_index: {preset_index}')

        # Parse preset_index into preset type, bank and number
        preset_info = BlueAndPinkSynthEditorApp.parse_preset_index(preset_index)

        # Load the preset
        self.load_preset(preset_info['bank_name'],
                         preset_info['preset_num'],
                         preset_info['preset_type'])

    def load_preset(self, bank_name, preset_num, preset_type):
        self.send_nymphes_osc(
            '/load_preset',
            preset_type,
            bank_name,
            preset_num
        )

    def show_load_dialog(self):
        content = LoadDialog(load=self.on_file_load_dialog, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save_dialog(self):
        if self.curr_preset_type == 'init':
            default_filename = 'new_preset.txt'
        elif self.curr_preset_type == 'file' and self._curr_preset_file_path.name == 'init.txt':
            default_filename = 'new_preset.txt'
        elif self.curr_preset_type == 'preset_slot':
            default_filename = f'{self._curr_preset_slot_type.upper()} {self._curr_preset_slot_bank_and_number[0]}{self._curr_preset_slot_bank_and_number[1]}.txt'
        elif self.curr_preset_type == 'file':
            default_filename = self._curr_preset_file_path.name
        else:
            default_filename = ''

        content = SaveDialog(
            save=self.on_file_save_dialog,
            cancel=self.dismiss_popup,
            default_filename=default_filename
        )
        self._popup = SavePopup(title="Save file", content=content,
                                size_hint=(0.9, 0.9))
        self._popup.open()

    def show_error_dialog_on_main_thread(self, error_string, error_detail_string):
        def work_func(_, error_text, error_detail_text):
            self.error_text = error_text
            self.error_detail_text = error_detail_text
            self.show_error_dialog()

        Clock.schedule_once(lambda dt: work_func(dt, error_string, error_detail_string), 0)

    def show_error_dialog(self):
        content = ErrorDialog(ok=self.dismiss_popup)
        self._popup = Popup(title="ERROR", content=content,
                            size_hint=(0.5, 0.5))
        self._popup.bind(on_open=self._on_popup_open)
        self._popup.bind(on_dismiss=self._on_popup_dismiss)
        self._popup.open()

    def update_current_preset(self):
        """
        If a preset of any kind has been loaded, then update
        it by writing the current settings to the same file
        or memory slot.
        """
        if self.curr_preset_type == 'init':
            #
            # The most-recently loaded preset was the init
            # preset, which is the file init.txt
            #

            # Write the current settings to the init file
            self.send_nymphes_osc(
                '/save_to_file',
                str(self._curr_preset_file_path)
            )

        elif self.curr_preset_type == 'file':
            #
            # The most-recently loaded preset was a file.
            #

            # Write the current settings to the file
            self.send_nymphes_osc(
                '/save_to_file',
                str(self._curr_preset_file_path)
            )

        elif self.curr_preset_type == 'preset_slot':
            #
            # The most-recently loaded preset was a memory
            # slot.
            #

            # Write the current settings to the slot
            self.send_nymphes_osc(
                '/save_to_preset',
                self._curr_preset_slot_type,
                self._curr_preset_slot_bank_and_number[0],
                self._curr_preset_slot_bank_and_number[1]
            )

    def on_file_load_dialog(self, path, filepaths):
        # Close the file load dialog
        self.dismiss_popup()

        if len(filepaths) > 0:
            Logger.debug(f'load path: {path}, filename: {filepaths}')

            if Path(filepaths[0]).name == 'init.txt':
                # This is the init file. Don't load it as a regular
                # preset file. Load it as init.
                self.send_nymphes_osc('/load_init_file')

            else:
                # Send message to nymphes controller to load the preset file
                self.send_nymphes_osc('/load_file', filepaths[0])

    def on_file_save_dialog(self, directory_path, filepath):
        # Close the dialogue
        self.dismiss_popup()

        # Get the filename by removing all occurrences of the
        # directory path (with a trailing slash added)
        filename = filepath.replace(directory_path + '/', '')

        if filename != '':
            # Make sure that the filename has a .txt file extension
            if '.txt' not in filename.lower():
                filename += '.txt'

            # Reconstruct the full path
            filepath = directory_path + '/' + filename

            Logger.info(f'Saving preset to {filepath}')

            # Send message to nymphes controller to load the preset file
            self.send_nymphes_osc('/save_to_file', filepath)

    def presets_spinner_text_changed(self, spinner_index, spinner_text):
        if self._curr_presets_spinner_index != spinner_index:
            # Store the new index
            self._curr_presets_spinner_index = spinner_index

            if len(self.presets_spinner_values) == 99:
                #
                # No file has been loaded or saved, so the first
                # item in the list is the init file.
                #
                if spinner_index == 0:
                    # Load the init preset file
                    self.send_nymphes_osc('/load_init_file')

                else:
                    # This is a preset slot
                    self.load_preset_by_index(spinner_index - 1)

            else:
                #
                # A file has been loaded or saved, so the first item
                # in the list is the filename, and the second item is
                # the init file.
                #
                if spinner_index == 0:
                    # Reload the most recent preset file.
                    self.send_nymphes_osc('/load_file', str(self._curr_preset_file_path))

                elif spinner_index == 1:
                    # Load the init preset file
                    self.send_nymphes_osc('/load_init_file')

                else:
                    # This is a preset slot
                    self.load_preset_by_index(spinner_index - 2)

    def load_next_preset(self):

        if len(self.presets_spinner_values) == 99:
            #
            # No file has been loaded or saved, so the first
            # item in the list is the init file.
            #

            if self._curr_presets_spinner_index + 1 > 98:
                # Wrap around to the beginning of the list
                self._curr_presets_spinner_index = 0

                # Load the init preset file
                self.send_nymphes_osc('/load_init_file')

            else:
                # Load the next preset slot
                self._curr_presets_spinner_index += 1
                self.load_preset_by_index(self._curr_presets_spinner_index - 1)

        else:
            #
            # A file has been loaded or saved, so the first item
            # in the list is the filename, and the second item is
            # the init file.
            #

            if self._curr_presets_spinner_index + 1 >= len(self.presets_spinner_values):
                # Wrap around to the beginning of the list
                self._curr_presets_spinner_index = 0

                # Reload the most recent preset file
                self.send_nymphes_osc('/load_file', str(self._curr_preset_file_path))

            elif self._curr_presets_spinner_index + 1 == 1:
                # Load the init preset file
                self._curr_presets_spinner_index = 1
                self.send_nymphes_osc('/load_init_file')

            else:
                # Load the next preset slot
                self._curr_presets_spinner_index += 1
                self.load_preset_by_index(self._curr_presets_spinner_index - 2)

    def load_prev_preset(self):
        if len(self.presets_spinner_values) == 99:
            #
            # No file has been loaded or saved, so the first
            # item in the list is the init file.
            #
            if self._curr_presets_spinner_index - 1 == 0:
                # Load the init preset file
                self._curr_presets_spinner_index = 0
                self.send_nymphes_osc('/load_init_file')

            elif self._curr_presets_spinner_index - 1 < 0:
                # Wrap around to the end of the list
                self._curr_presets_spinner_index = 98
                self.load_preset_by_index(97)

            else:
                # Load the previous preset
                self._curr_presets_spinner_index -= 1
                self.load_preset_by_index(self._curr_presets_spinner_index - 1)

        else:
            #
            # A file has been loaded or saved, so the first item
            # in the list is the filename, and the second item is
            # the init file.
            #
            if self._curr_presets_spinner_index - 1 == 1:
                # Load the init preset file
                self._curr_presets_spinner_index = 1
                self.send_nymphes_osc('/load_init_file')

            elif self._curr_presets_spinner_index - 1 == 0:
                # Reload the most recent preset file
                self._curr_presets_spinner_index = 0
                self.send_nymphes_osc('/load_file', str(self._curr_preset_file_path))

            elif self._curr_presets_spinner_index - 1 < 0:
                # Wrap around to the end of the list
                self._curr_presets_spinner_index = 99
                self.load_preset_by_index(self._curr_presets_spinner_index - 2)

            else:
                # Load the previous preset
                self._curr_presets_spinner_index = self._curr_presets_spinner_index - 1
                self.load_preset_by_index(self._curr_presets_spinner_index - 2)

    def increment_prop_value_for_param_name(self, param_name, amount):
        # Convert the parameter name to the name
        # of our corresponding property
        property_name = param_name.replace('.', '_')

        # Get the property's current value
        curr_val = getattr(self, property_name)

        # Get the parameter type (int or float), and its minimum
        # and maximum values
        param_type = NymphesPreset.type_for_param_name(param_name)
        min_val = NymphesPreset.min_val_for_param_name(param_name)
        max_val = NymphesPreset.max_val_for_param_name(param_name)

        if not self.fine_mode or param_type == int:
            # Apply the increment amount, then round with zero
            # decimal places and convert to int
            new_val = int(round(curr_val + amount))

            # Keep within the min and max value range
            if new_val < min_val:
                new_val = int(min_val)

            if new_val > max_val:
                new_val = int(max_val)

            # Set the property's value only if the new value is different
            # than the current value
            if new_val != curr_val:
                self.set_prop_value_for_param_name(param_name, new_val)

        else:
            # Apply the increment amount and round using the precision
            # specified in NymphesPreset
            new_val = round(curr_val + amount, self.fine_mode_decimal_places)

            # Keep within the min and max value range
            if new_val < min_val:
                new_val = min_val

            if new_val > max_val:
                new_val = max_val

            # Set the property's value only if the new value is different
            # than the current value
            if not self.float_equals(curr_val, new_val, self.fine_mode_decimal_places):
                self.set_prop_value_for_param_name(param_name, new_val)

    def reload(self):
        """
        Reloads the current preset
        :return:
        """
        if self.curr_preset_type == 'file' and self._curr_preset_file_path is not None:
            self.send_nymphes_osc('/load_file', str(self._curr_preset_file_path))

        elif self.curr_preset_type == 'init':
            self.send_nymphes_osc('/load_init_file')

        elif self.curr_preset_type == 'preset_slot':
            # Get the index of the last preset slot that was loaded
            preset_slot_index = self.index_from_preset_info(
                bank_name=self._curr_preset_slot_bank_and_number[0],
                preset_num=self._curr_preset_slot_bank_and_number[1],
                preset_type=self._curr_preset_slot_type
            )

            # Load the preset
            self.load_preset_by_index(preset_slot_index)

    def update_current_preset_file(self):
        """
        Save the current settings to the currently-loaded or saved
        preset file, updating it.
        """
        if self.curr_preset_type == 'file' and self._curr_preset_file_path is not None:
            Logger.info(f'Updating preset file at {self._curr_preset_file_path}')
            self.send_nymphes_osc('/save_to_file', str(self._curr_preset_file_path))

    def midi_input_port_checkbox_toggled(self, port_name, active):
        if active:
            if port_name not in self._connected_midi_inputs:
                # Connect to this MIDI input
                self.send_nymphes_osc(
                    '/connect_midi_input',
                    port_name
                )

        else:
            if port_name in self._connected_midi_inputs:
                # Disconnect from this MIDI input
                self.send_nymphes_osc(
                    '/disconnect_midi_input',
                    port_name
                )

    def midi_output_port_checkbox_toggled(self, port_name, active):
        if active:
            if port_name not in self._connected_midi_outputs:
                # Connect to this MIDI output
                self.send_nymphes_osc(
                    '/connect_midi_output',
                    port_name
                )

        else:
            if port_name in self._connected_midi_outputs:
                # Disconnect from this MIDI output
                self.send_nymphes_osc(
                    '/disconnect_midi_output',
                    port_name
                )

    def nymphes_input_spinner_text_changed(self, new_text):
        if new_text != self.nymphes_input_name:
            #
            # A new selection has been made by the user
            #

            # Store the new selection
            self.nymphes_input_name = new_text

            # Try connecting if we have both input and output names
            #
            if self.nymphes_input_name != 'Not Connected' and self.nymphes_output_name != 'Not Connected':
                self.send_nymphes_osc(
                    '/connect_nymphes',
                    self.nymphes_input_name,
                    self.nymphes_output_name
                )

            else:
                if self.nymphes_connected:
                    self.send_nymphes_osc('/disconnect_nymphes')

    def nymphes_output_spinner_text_changed(self, new_text):
        if new_text != self.nymphes_output_name:
            #
            # A new selection has been made by the user
            #

            # Store the new selection
            self.nymphes_output_name = new_text

            # Try connecting if we have both input and output names
            #
            if self.nymphes_input_name != 'Not Connected' and self.nymphes_output_name != 'Not Connected':
                self.send_nymphes_osc(
                    '/connect_nymphes',
                    self.nymphes_input_name,
                    self.nymphes_output_name
                )

            else:
                if self.nymphes_connected:
                    self.send_nymphes_osc('/disconnect_nymphes')

    def on_mouse_entered_param_control(self, param_name, tooltip_text=None):
        # When the mouse enters a parameter control and Nymphes
        # is connected, display the name and value in the status
        # bar, or display the control's tooltip_text if provided.
        #
        if self.curr_mouse_dragging_param_name == '':
            # Change the mouse cursor to a hand indicate that
            # this is a control
            Window.set_system_cursor('hand')

            # Store the name of the parameter
            self.curr_mouse_hover_param_name = param_name

            if tooltip_text is not None:
                self._set_prop_value_on_main_thread('status_bar_text', tooltip_text)

            else:
                # Get the value and type for the parameter
                value = self.get_prop_value_for_param_name(param_name)

                if param_name in ['mod_wheel', 'aftertouch']:
                    #
                    # This is performance parameter, not a Nymphes preset parameter.
                    #
                    value_string = str(value)

                else:
                    #
                    # This should be a Nymphes preset parameter.
                    #
                    param_type = NymphesPreset.type_for_param_name(param_name)

                    if param_type == float:
                        value_string = format(round(value, self.fine_mode_decimal_places), f'.{self.fine_mode_decimal_places}f')

                    else:
                        value_string = str(value)

                self._set_prop_value_on_main_thread('status_bar_text', f'{param_name}: {value_string}')

    def on_mouse_exited_param_control(self, param_name):
        # When Nymphes is connected and the mouse exits a parameter
        # control, blank the status bar
        #
        if self.curr_mouse_dragging_param_name == '':
            if self.curr_mouse_hover_param_name != '' and param_name == self.curr_mouse_hover_param_name:
                # Set the mouse cursor back to an arrow
                Window.set_system_cursor('arrow')

                # Reset the hover param name
                self.curr_mouse_hover_param_name = ''

                if self.nymphes_connected:
                    # Reset the status message to blank
                    self._set_prop_value_on_main_thread('status_bar_text', '')

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

    def set_nymphes_midi_channel(self, midi_channel):
        """
        Set the MIDI channel used for communication with
        Nymphes.
        This is an int, with a range of 1 to 16
        """
        # Make sure midi_channel is an int
        midi_channel = int(midi_channel)

        if midi_channel != self.nymphes_midi_channel:
            Logger.info(f'Changing Nymphes MIDI channel to {midi_channel}')

            # Send a message to nymphes-osc to change the channel
            self.send_nymphes_osc(
                '/set_nymphes_midi_channel',
                midi_channel
            )

    def set_curr_screen_name(self, screen_name):
        # Store the previous screen name
        self.prev_screen_name = self.curr_screen_name

        # Store the new screen name
        self.curr_screen_name = screen_name

    def set_curr_mouse_dragging_param_name(self, param_name):
        self.curr_mouse_dragging_param_name = param_name

    def set_curr_keyboard_editing_param_name(self, param_name):
        self.curr_keyboard_editing_param_name = param_name

    def get_prop_value_for_param_name(self, param_name):
        # Convert the parameter name to the name
        # of our corresponding property
        property_name = param_name.replace('.', '_')

        # Get the property's current value
        return getattr(self, property_name)

    def set_prop_value_for_param_name(self, param_name, value):
        # Update our property for this parameter name
        setattr(self, param_name.replace('.', '_'), value)

        # Set status bar text
        #
        if param_name in ['mod_wheel', 'aftertouch']:
            #
            # This is performance parameter, not a Nymphes preset parameter.
            #
            pass
        else:
            # This must be a Nymphes preset parameter.
            param_type = NymphesPreset.type_for_param_name(param_name)
            if param_type == float:
                value_string = format(round(value, self.fine_mode_decimal_places),
                                      f'.{self.fine_mode_decimal_places}f')
            else:
                value_string = str(value)

            self._set_prop_value_on_main_thread('status_bar_text', f'{param_name}: {value_string}')

        #
        # Send an OSC message for this parameter with the new value
        #

        # Send the value as an int if it is equivalent to an int
        if not abs(value - int(value)) > 0.0:
            value = int(value)

        self.send_nymphes_osc(
            f'/{param_name.replace(".", "/")}',
            value
        )

    def min_val_for_param_name(self, param_name):
        return NymphesPreset.min_val_for_param_name(param_name)

    def max_val_for_param_name(self, param_name):
        return NymphesPreset.max_val_for_param_name(param_name)

    def _load_config_file(self, filepath):
        """
        Load the contents of the specified config txt file.
        :param filepath: str or Path
        :return:
        """
        Logger.info(f'Loading settings from config file at {filepath}...')

        config = configparser.ConfigParser()
        config.read(filepath)

        #
        # Nymphes OSC Communication
        #

        self._nymphes_osc_sender_host = config['NYMPHES_OSC']['sender host']
        self._nymphes_osc_sender_port = int(config['NYMPHES_OSC']['sender port'])

        if config.has_option('NYMPHES_OSC', 'listener host'):
            #
            # Listener host has been specified in config.txt
            #

            self._nymphes_osc_listener_host = config['NYMPHES_OSC']['listener host']
            Logger.info(
                f'[NYMPHES_OSC][listener_host]: {self._nymphes_osc_listener_host}')

        else:
            #
            # Listener host is not specified.
            # Try to automatically determine the local ip address
            #

            in_host = self._get_local_ip_address()
            self._nymphes_osc_listener_host = in_host
            Logger.info(f'[NYMPHES_OSC][listener_host] not specified. Will use detected local ip address: {in_host}')

        self._nymphes_osc_listener_port = int(config['NYMPHES_OSC']['listener port'])

        #
        # Nymphes MIDI Channel
        #

        if config.has_option('MIDI', 'nymphes midi channel'):
            try:
                self.nymphes_midi_channel = int(config['MIDI']['nymphes midi channel'])
                Logger.info(f'[MIDI][nymphes midi channel]: {self.nymphes_midi_channel}')

            except Exception as e:
                # Something went wrong retrieving and converting the MIDI
                # channel

                # Use MIDI channel 1
                self.nymphes_midi_channel = 1

                Logger.warning(
                    f'[MIDI][nymphes midi channel] was invalid. Using channel {self.nymphes_midi_channel}: {e}')

        else:
            # Use MIDI channel 1
            self.nymphes_midi_channel = 1

            Logger.warning(
                f'[MIDI][nymphes midi channel] not specified. Using channel {self.nymphes_midi_channel}')

        #
        # GUI
        #

        if config.has_option('GUI', 'invert mouse wheel'):
            raw_value = config['GUI']['invert mouse wheel']

            if raw_value in ['0', '1']:
                self.invert_mouse_wheel = True if raw_value == '1' else False
                Logger.info(f'[GUI][invert mouse wheel]: {self.invert_mouse_wheel}')

            else:
                Logger.warning(f"[GUI][invert mouse wheel] was invalid: {raw_value}. Using {self.invert_mouse_wheel}")

    def _reload_config_file(self):
        Logger.info(f'Reloading config file at {self._config_file_path}')
        self._load_config_file(self._config_file_path)

    def _create_config_file(self, filepath):
        config = configparser.ConfigParser()

        # OSC Communication with Nymphes-OSC App
        config['NYMPHES_OSC'] = {
            'sender host': '127.0.0.1',
            'sender port': '1236',
            'listener host': '127.0.0.1',
            'listener port': '1237'}

        # Nymphes MIDI Channel
        config['MIDI'] = {
            'nymphes midi channel': '1'
        }

        # GUI
        config['GUI'] = {
            'invert mouse wheel': '0'
        }

        # Write to a new config file
        try:
            with open(filepath, 'w') as config_file:
                config.write(config_file)

            Logger.info(f'Created config file at {filepath}')

        except Exception as e:
            Logger.critical(f'Failed to create config file at {filepath}: ({e})')

    def _save_config_file(self, filepath):
        config = configparser.ConfigParser()

        # OSC Communication with Nymphes-OSC App
        config['NYMPHES_OSC'] = {
            'sender host': self._nymphes_osc_sender_host,
            'sender port': self._nymphes_osc_sender_port,
            'listener host': self._nymphes_osc_listener_host,
            'listener port': self._nymphes_osc_listener_port}

        # Nymphes MIDI Channel
        config['MIDI'] = {
            'nymphes midi channel': str(self.nymphes_midi_channel)
        }

        # GUI
        config['GUI'] = {
            'invert mouse wheel': '1' if self.invert_mouse_wheel else '0'
        }

        # Write to the config file
        try:
            with open(filepath, 'w') as config_file:
                config.write(config_file)

            Logger.info(f'Wrote to config file at {filepath}')

        except Exception as e:
            Logger.critical(f'Failed to write to config file at {filepath} ({e})')

    @staticmethod
    def _get_local_ip_address():
        """
        Return the local IP address as a string.
        If no address other than 127.0.0.1 can be found, then
        return '127.0.0.1'
        :return: str
        """
        # Get a list of all network interfaces
        interfaces = netifaces.interfaces()

        for iface in interfaces:
            try:
                # Get the addresses associated with the interface
                addresses = netifaces.ifaddresses(iface)

                # Extract the IPv4 addresses (if available)
                if netifaces.AF_INET in addresses:
                    ip_info = addresses[netifaces.AF_INET][0]
                    ip_address = ip_info['addr']
                    if ip_address != '127.0.0.1':
                        return ip_address

            except Exception as e:
                Logger.critical(f'Failed to detect local IP address ({e})')

                # Default to localhost
                return '127.0.0.1'

        # If we get here, then no IP Address other than 127.0.0.1 was found
        return '127.0.0.1'

    def _start_nymphes_osc_listener(self):
        """
        Start an OSC server that listens for OSC messages from nymphes-osc
        on a background thread
        :return:
        """
        self._nymphes_osc_listener = BlockingOSCUDPServer(
            (self._nymphes_osc_listener_host, self._nymphes_osc_listener_port),
            self._nymphes_osc_listener_dispatcher
        )
        self._nymphes_osc_listener_thread = threading.Thread(target=self._nymphes_osc_listener.serve_forever)
        self._nymphes_osc_listener_thread.start()

        Logger.info(
            f'Started listener for nymphes-osc at: {self._nymphes_osc_listener_host}:{self._nymphes_osc_listener_port}')

    def _stop_nymphes_osc_listener(self):
        """
        Shut down the OSC server that listens for OSC messages from nymphes-osc
        :return:
        """
        if self._nymphes_osc_listener is not None:
            self._nymphes_osc_listener.shutdown()
            self._nymphes_osc_listener.server_close()
            self._nymphes_osc_listener = None
            self._nymphes_osc_listener_thread.join()
            self._nymphes_osc_listener_thread = None
            Logger.info('Stopped nymphes-osc listener')

    def _register_as_nymphes_osc_client(self):
        """
        Register as a client with nymphes-osc by sending it a
        /register_client OSC message
        :return:
        """

        # To connect to the nymphes_osc server, we need
        # to send it a /register_host OSC message
        # with the port we are listening on.
        Logger.info(
            f'Registering as client with nymphes-osc server at {self._nymphes_osc_sender_host}:{self._nymphes_osc_sender_port}...')
        self.send_nymphes_osc('/register_client', self._nymphes_osc_listener_port)

    def send_nymphes_osc(self, address, *args):
        """
        Send an OSC message to nymphes_osc
        :param address: The osc address including the forward slash ie: /register_host
        :param args: A variable number arguments. Types will be automatically detected
        :return:
        """
        msg = OscMessageBuilder(address=address)
        for arg in args:
            msg.add_arg(arg)
        msg = msg.build()
        self._nymphes_osc_sender.send(msg)

        Logger.info(f'Sent to nymphes-osc: {address}, {[str(arg) for arg in args]}')

    def _on_nymphes_osc_message(self, address, *args):
        """
        An OSC message has been received from nymphes-osc
        :param address: str
        :param args: A list of arguments
        :return:
        """
        # App Status Messages
        #
        if address == '/client_registered':
            # Get the hostname and port
            #
            host_name = str(args[0])
            port = int(args[1])

            Logger.info(f'Received from nymphes-osc: {address}: {host_name}:{port}')

            # We are connected to nymphes_osc
            self._connected_to_nymphes_osc = True

        elif address == '/client_unregistered':
            # Get the hostname and port
            #
            host_name = str(args[0])
            port = int(args[1])

            Logger.info(f'Received from nymphes-osc: {address}: {host_name}:{port}')

            # We are no longer connected to nymphes-osc
            self._connected_to_nymphes_osc = False

        elif address == '/presets_directory_path':
            # Get the path
            path = Path(args[0])

            Logger.info(f'Received from nymphes-osc: {address}: {path}')

            # Store it
            self._presets_directory_path = str(path)

        elif address == '/nymphes_midi_input_detected':
            #
            # A Nymphes MIDI input port has been detected
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'Received from nymphes-osc: {address}: {port_name}')

            # Add it to our list of detected Nymphes MIDI input ports
            if port_name not in self._detected_nymphes_midi_inputs:
                self._detected_nymphes_midi_inputs.append(port_name)
                self._add_name_to_nymphes_input_spinner_on_main_thread(port_name)

            # Try automatically connecting to the first Nymphes if we
            # now have both an input and output port
            if not self.nymphes_connected:
                if len(self._detected_nymphes_midi_inputs) > 0 and len(self._detected_nymphes_midi_outputs) > 0:
                    Logger.info('Attempting to automatically connect to the first detected Nymphes')
                    self.send_nymphes_osc(
                        '/connect_nymphes',
                        self._detected_nymphes_midi_inputs[0],
                        self._detected_nymphes_midi_outputs[0]
                    )

        elif address == '/nymphes_midi_input_no_longer_detected':
            #
            # A previously-detected Nymphes MIDI input port is no longer found
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'Received from nymphes-osc: {address}: {port_name}')

            # Remove it from our list of detected Nymphes MIDI input ports
            if port_name in self._detected_nymphes_midi_inputs:
                self._detected_nymphes_midi_inputs.remove(port_name)
                self._remove_name_from_nymphes_input_spinner_on_main_thread(port_name)

        elif address == '/nymphes_midi_output_detected':
            #
            # A Nymphes MIDI output port has been detected
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'Received from nymphes-osc: {address}: {port_name}')

            # Add it to our list of detected Nymphes MIDI output ports
            if port_name not in self._detected_nymphes_midi_outputs:
                self._detected_nymphes_midi_outputs.append(port_name)
                self._add_name_to_nymphes_output_spinner_on_main_thread(port_name)

            # Try automatically connecting to the first Nymphes if we
            # now have both an input and output port
            if not self.nymphes_connected:
                if len(self._detected_nymphes_midi_inputs) > 0 and len(self._detected_nymphes_midi_outputs) > 0:
                    Logger.info('Attempting to automatically connect to the first detected Nymphes')
                    self.send_nymphes_osc(
                        '/connect_nymphes',
                        self._detected_nymphes_midi_inputs[0],
                        self._detected_nymphes_midi_outputs[0]
                    )

        elif address == '/nymphes_midi_output_no_longer_detected':
            #
            # A previously-detected Nymphes MIDI output port is no longer found
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'Received from nymphes-osc: {address}: {port_name}')

            # Remove it from our list of detected Nymphes MIDI output ports
            if port_name in self._detected_nymphes_midi_outputs:
                self._detected_nymphes_midi_outputs.remove(port_name)
                self._remove_name_from_nymphes_output_spinner_on_main_thread(port_name)

        elif address == '/nymphes_connected':
            #
            # nymphes_midi has connected to a Nymphes synthesizer
            #
            input_port = str(args[0])
            output_port = str(args[1])

            Logger.info(f'Received from nymphes-osc: {address}: input_port: {input_port}, output_port: {output_port}')

            # Get the names of the MIDI input and output ports
            self._nymphes_input_port = input_port
            self._nymphes_output_port = output_port

            self._set_prop_value_on_main_thread('nymphes_connected', True)
            self._set_prop_value_on_main_thread('nymphes_input_name', input_port)
            self._set_prop_value_on_main_thread('nymphes_output_name', output_port)

            # Status message
            self._set_prop_value_on_main_thread('status_bar_text', 'NYMPHES CONNECTED')

        elif address == '/nymphes_disconnected':
            #
            # nymphes_midi is no longer connected to a Nymphes synthesizer
            #

            Logger.info(f'Received from nymphes-osc: {address}')

            # Update app state
            self._nymphes_input_port = None
            self._nymphes_output_port = None

            self._set_prop_value_on_main_thread('nymphes_connected', False)
            self._set_prop_value_on_main_thread('nymphes_input_name', 'Not Connected')
            self._set_prop_value_on_main_thread('nymphes_output_name', 'Not Connected')

            # Status message
            self._set_prop_value_on_main_thread('status_bar_text', 'NYMPHES NOT CONNECTED')

            # Set the system cursor to an arrow, just in case it was a hand
            # when Nymphes disconnected
            self.set_system_cursor_on_main_thread('arrow')

        elif address == '/loaded_preset':
            #
            # The Nymphes synthesizer has just loaded a preset
            #
            preset_slot_type = str(args[0])
            preset_slot_bank_and_number = str(args[1]), int(args[2])

            Logger.info(
                f'{address}: {preset_slot_type} {preset_slot_bank_and_number[0]}{preset_slot_bank_and_number[1]}')

            # Reset the unsaved changes flag
            self._set_prop_value_on_main_thread('unsaved_preset_changes', False)

            # Update the current preset type property
            self._set_prop_value_on_main_thread('curr_preset_type', 'preset_slot')

            # Store preset slot info
            self._curr_preset_slot_type = preset_slot_type
            self._curr_preset_slot_bank_and_number = preset_slot_bank_and_number

            # Get the index of the loaded preset
            preset_slot_index = BlueAndPinkSynthEditorApp.index_from_preset_info(
                bank_name=self._curr_preset_slot_bank_and_number[0],
                preset_num=self._curr_preset_slot_bank_and_number[1],
                preset_type=self._curr_preset_slot_type
            )

            # Calculate the index within the presets spinner options
            preset_slot_start_index = 1 if len(self.presets_spinner_values) == 99 else 2
            self._curr_presets_spinner_index = preset_slot_start_index + preset_slot_index

            # Update the preset spinner's text
            if self.presets_spinner_text != self.presets_spinner_values[self._curr_presets_spinner_index]:
                self.presets_spinner_text = self.presets_spinner_values[self._curr_presets_spinner_index]

            # Status bar message
            self._set_prop_value_on_main_thread('status_bar_text',
                                                f'LOADED {preset_slot_type.upper()} PRESET {preset_slot_bank_and_number[0]}{preset_slot_bank_and_number[1]}')

        elif address == '/loaded_preset_dump_from_midi_input_port':
            port_name = str(args[0])
            preset_slot_type = str(args[0])
            preset_slot_bank_and_number = str(args[1]), int(args[2])

            Logger.info(
                f'{address}: {port_name}: {preset_slot_type} {preset_slot_bank_and_number[0]}{preset_slot_bank_and_number[1]}')

            # Reset the unsaved changes flag
            self._set_prop_value_on_main_thread('unsaved_preset_changes', False)

            self._curr_preset_slot_type = preset_slot_type
            self._curr_preset_slot_bank_and_number = preset_slot_bank_and_number

            # Status bar message
            msg = f'LOADED PRESET DUMP {preset_slot_type.upper()} {preset_slot_bank_and_number[0]}{preset_slot_bank_and_number[1]} FROM MIDI INPUT PORT {port_name}'
            self._set_prop_value_on_main_thread('status_bar_text', msg)

        elif address == '/loaded_file':
            #
            # A preset file was loaded
            #
            filepath = Path(args[0])

            Logger.info(f'Received from nymphes-osc: {address}: {filepath}')

            # Update the current preset type
            self._set_prop_value_on_main_thread('curr_preset_type', 'file')

            # Store the path to the file
            self._curr_preset_file_path = filepath

            # Reset current preset slot info
            self._curr_preset_slot_type = None
            self._curr_preset_slot_bank_and_number = None

            # Reset the unsaved changes flag
            self._set_prop_value_on_main_thread('unsaved_preset_changes', False)

            # Update the presets spinner.
            # This also sets the spinner's current text
            # and updates self._curr_presets_spinner_index.
            self._set_presets_spinner_file_option_on_main_thread(self._curr_preset_file_path.stem)

            # Status bar message
            msg = f'LOADED {filepath.name}'
            self._set_prop_value_on_main_thread('status_bar_text', msg)

        elif address == '/loaded_init_file':
            #
            # The init preset file was loaded
            #

            # Get the path to the init preset file
            filepath = Path(args[0])

            Logger.info(f'Received from nymphes-osc: {address}: {filepath}')

            # Store the path
            self._curr_preset_file_path = filepath

            # Update the current preset type
            self._set_prop_value_on_main_thread('curr_preset_type', 'init')

            # Reset current preset slot info
            self._curr_preset_slot_type = None
            self._curr_preset_slot_bank_and_number = None

            # Reset the unsaved changes flag
            self._set_prop_value_on_main_thread('unsaved_preset_changes', False)

            # Update the presets spinner
            # Select the init option
            self._set_prop_value_on_main_thread('presets_spinner_text', 'init')
            self._curr_presets_spinner_index = 0 if len(self.presets_spinner_values) == 99 else 1

            # Status bar message
            msg = f'LOADED INIT PRESET (init.txt)'
            self._set_prop_value_on_main_thread('status_bar_text', msg)

        elif address == '/saved_to_file':
            #
            # The current settings have been saved to a preset file
            #
            filepath = Path(args[0])

            Logger.info(f'Received from nymphes-osc: {address}: {filepath}')

            if filepath.name != 'init.txt':
                # Update the current preset type
                self._set_prop_value_on_main_thread('curr_preset_type', 'file')

                # Store the path to the file
                self._curr_preset_file_path = filepath

                # Update the presets spinner.
                # This also sets the spinner's current text
                # and updates self._curr_presets_spinner_index.
                self._set_presets_spinner_file_option_on_main_thread(self._curr_preset_file_path.name)

                # Status bar message
                msg = f'SAVED {filepath.name} PRESET FILE'
                self._set_prop_value_on_main_thread('status_bar_text', msg)

            else:
                # The init file was overwritten.
                # Treat this as if init was loaded/saved rather
                # than a regular preset file

                # Update the current preset type
                self._set_prop_value_on_main_thread('curr_preset_type', 'init')

                # Store the path to the file
                self._curr_preset_file_path = filepath

                # Update the presets spinner
                # Sending it None removes the file option and selects the first entry (init)
                self._set_presets_spinner_file_option_on_main_thread(None)

                # Status bar message
                msg = f'UPDATED INIT PRESET (init.txt)'
                self._set_prop_value_on_main_thread('status_bar_text', msg)

            # Reset current preset slot info
            self._curr_preset_slot_type = None
            self._curr_preset_slot_bank_and_number = None

            # Reset the unsaved changes flag
            self._set_prop_value_on_main_thread('unsaved_preset_changes', False)

        elif address == '/saved_preset_to_file':
            #
            # A Nymphes preset slot has been saved to a file
            #

            # Get the preset info
            filepath = Path(str(args[0]))
            preset_type = str(args[1])
            bank_name = str(args[2])
            preset_number = int(args[3])

            Logger.info(f'Received from nymphes-osc: {address}: {filepath} {preset_type} {bank_name}{preset_number}')

            # Status bar message
            msg = f'SAVED PRESET {preset_type.upper()} {bank_name}{preset_number} TO FILE {filepath.name}'
            self._set_prop_value_on_main_thread('status_bar_text', msg)

        elif address == '/loaded_file_to_preset':
            #
            # A preset file has been loaded into one of Nymphes'
            # preset slots
            #

            # Get the preset info
            filepath = Path(args[0])
            preset_type = str(args[1])
            bank_name = str(args[2])
            preset_number = int(args[3])

            Logger.info(f'Received from nymphes-osc: {address}: {filepath} {preset_type} {bank_name}{preset_number}')

            # Status bar message
            msg = f'LOADED PRESET FILE {filepath.name} TO SLOT {preset_type.upper()} {bank_name}{preset_number}'
            self._set_prop_value_on_main_thread('status_bar_text', msg)

        elif address == '/saved_to_preset':
            #
            # The current settings have been saved into one of
            # Nymphes' preset slots. We will not make the preset
            # active however, because Nymphes has not actually
            # loaded the new preset.
            #

            # Get the preset info
            preset_type = str(args[0])
            bank_name = str(args[1])
            preset_number = int(args[2])

            Logger.info(f'Received from nymphes-osc: {address}: {preset_type} {bank_name}{preset_number}')

            # Status bar message
            msg = f'SAVED TO PRESET SLOT {preset_type.upper()} {bank_name}{preset_number}'
            self._set_prop_value_on_main_thread('status_bar_text', msg)

        elif address == '/requested_preset_dump':
            #
            # A full preset dump has been requested
            #
            Logger.info(f'Received from nymphes-osc: {address}:')

            # Status bar message
            msg = f'REQUESTED PRESET DUMP...'
            self._set_prop_value_on_main_thread('status_bar_text', msg)

        elif address == '/received_preset_dump_from_nymphes':
            #
            # A single preset has been received from Nymphes
            # as a persistent import type SYSEX message
            #

            # Get the preset info
            preset_type = str(args[0])
            bank_name = str(args[1])
            preset_number = int(args[2])

            Logger.info(f'Received from nymphes-osc: {address}: {preset_type} {bank_name}{preset_number}')

            # Status bar message
            msg = f'RECEIVED {preset_type.upper()} {bank_name}{preset_number} PRESET SYSEX DUMP'
            self._set_prop_value_on_main_thread('status_bar_text', msg)

        elif address == '/saved_preset_dump_from_midi_input_port_to_preset':
            #
            # A preset was received via SYSEX from a MIDI input port and written
            # to a Nymphes preset slot
            #

            # Get the port name
            port_name = str(args[0])

            # Get the preset info
            preset_type = str(args[1])
            bank_name = str(args[2])
            preset_number = int(args[3])

            Logger.info(f'Received from nymphes-osc: {address}: {port_name} {preset_type} {bank_name}{preset_number}')

            # Status bar message
            msg = f'SAVED PRESET DUMP FROM MIDI INPUT {port_name} TO SLOT {preset_type.upper()} {bank_name}{preset_number}'
            self._set_prop_value_on_main_thread('status_bar_text', msg)

        elif address == '/unsaved_changes':
            #
            # Parameter values have changed since the current preset
            # was loaded or saved.
            #
            Logger.info(address)
            self._set_prop_value_on_main_thread('unsaved_preset_changes', True)

        elif address == '/midi_input_detected':
            #
            # A MIDI input port has been detected
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'Received from nymphes-osc: {address}: {port_name}')

            # Add it to our list of detected MIDI input ports
            if port_name not in self._detected_midi_inputs:
                self._detected_midi_inputs.append(port_name)
                self._add_midi_input_name_on_main_thread(port_name)
                self._add_name_to_nymphes_input_spinner_on_main_thread(port_name)

        elif address == '/midi_input_no_longer_detected':
            #
            # A previously-detected MIDI input port is no longer found
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'Received from nymphes-osc: {address}: {port_name}')

            # Remove it from our list of detected MIDI input ports
            if port_name in self._detected_midi_inputs:
                self._detected_midi_inputs.remove(port_name)
                self._remove_midi_input_name_on_main_thread(port_name)
                self._remove_name_from_nymphes_input_spinner_on_main_thread(port_name)

        elif address == '/midi_input_connected':
            #
            # A MIDI input port has been connected
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'Received from nymphes-osc: {address}: {port_name}')

            # Add it to our list of connected MIDI input ports
            if port_name not in self._connected_midi_inputs:
                self._connected_midi_inputs.append(port_name)
                self._add_connected_midi_input_name_on_main_thread(port_name)

        elif address == '/midi_input_disconnected':
            #
            # A previously-connected MIDI input port has been disconnected
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'Received from nymphes-osc: {address}: {port_name}')

            # Remove it from our list of connected MIDI input ports
            if port_name in self._connected_midi_inputs:
                self._connected_midi_inputs.remove(port_name)
                self._remove_connected_midi_input_name_on_main_thread(port_name)

        elif address == '/midi_output_detected':
            #
            # A MIDI output port has been detected
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'Received from nymphes-osc: {address}: {port_name}')

            # Add it to our list of detected MIDI output ports
            if port_name not in self._detected_midi_outputs:
                self._detected_midi_outputs.append(port_name)
                self._add_midi_output_name_on_main_thread(port_name)
                self._add_name_to_nymphes_output_spinner_on_main_thread(port_name)

        elif address == '/midi_output_no_longer_detected':
            #
            # A previously-detected MIDI output port is no longer found
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'Received from nymphes-osc: {address}: {port_name}')

            # Remove it from our list of detected MIDI output ports
            if port_name in self._detected_midi_outputs:
                self._detected_midi_outputs.remove(port_name)
                self._remove_midi_output_name_on_main_thread(port_name)
                self._remove_name_from_nymphes_output_spinner_on_main_thread(port_name)

        elif address == '/midi_output_connected':
            #
            # A MIDI output port has been connected
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'Received from nymphes-osc: {address}: {port_name}')

            # Add it to our list of connected MIDI output ports
            if port_name not in self._connected_midi_outputs:
                self._connected_midi_outputs.append(port_name)
                self._add_connected_midi_output_name_on_main_thread(port_name)

        elif address == '/midi_output_disconnected':
            #
            # A previously-connected MIDI output port has been disconnected
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'Received from nymphes-osc: {address}: {port_name}')

            # Remove it from our list of connected MIDI output ports
            if port_name in self._connected_midi_outputs:
                self._connected_midi_outputs.remove(port_name)
                self._remove_connected_midi_output_name_on_main_thread(port_name)

        elif address == '/mod_wheel':
            val = int(args[0])
            Logger.debug(f'Received from nymphes-osc: {address}: {val}')
            self._set_prop_value_on_main_thread('mod_wheel', val)

        elif address == '/velocity':
            val = int(args[0])
            Logger.debug(f'Received from nymphes-osc: {address}: {val}')
            self._set_prop_value_on_main_thread('velocity', val)

        elif address == '/aftertouch':
            val = int(args[0])
            Logger.debug(f'Received from nymphes-osc: {address}: {val}')
            self._set_prop_value_on_main_thread('aftertouch', val)

        elif address == '/poly_aftertouch':
            channel = int(args[0])
            val = int(args[1])
            Logger.debug(f'Received from nymphes-osc: {address}: {channel}, {val}')
            self._set_prop_value_on_main_thread('aftertouch', val)

        elif address == '/sustain_pedal':
            val = bool(args[0])
            Logger.debug(f'Received from nymphes-osc: {address}: {val}')
            self._set_prop_value_on_main_thread('sustain_pedal', val)

        elif address == '/nymphes_midi_channel_changed':
            midi_channel = int(args[0])
            Logger.info(f'Received from nymphes-osc: {address}: {midi_channel}')

            # Store the new MIDI channel
            self._set_prop_value_on_main_thread('nymphes_midi_channel', midi_channel)

            # Save the config file
            self._save_config_file(self._config_file_path)

        elif address == '/midi_feedback_suppression_enabled':
            Logger.info(f'Received from nymphes-osc: {address}')

            # Store the value
            self._set_prop_value_on_main_thread('midi_feedback_suppression_enabled', True)

        elif address == '/midi_feedback_suppression_disabled':
            Logger.info(f'Received from nymphes-osc: {address}')

            # Store the value
            self._set_prop_value_on_main_thread('midi_feedback_suppression_enabled', False)

        elif address == '/status':
            Logger.info(f'Received from nymphes-osc: {address}: {args[0]}')
            self._set_prop_value_on_main_thread('status_bar_text', f'status: {args[0]}')

        elif address == '/error':
            Logger.info(f'Received from nymphes-osc: {address}: {args[0]}, {args[1]}')
            self.show_error_dialog_on_main_thread(args[0], args[1])

        elif address == '/midi_feedback_detected':
            Logger.info(f'Received from nymphes-osc: {address}')

        elif address == '/osc/legato/value':
            Logger.debug(f'Received from nymphes-osc: {address}: {args[0]}')
            val = int(args[0])
            self._set_prop_value_on_main_thread('osc_legato_value', val)

        elif address == '/osc/voice_mode/value':
            Logger.debug(f'Received from nymphes-osc: {address}: {args[0]}')

            voice_mode = int(args[0])

            # Store the new voice mode as an int
            self._set_prop_value_on_main_thread('osc_voice_mode_value', voice_mode)

            # Get the name of the voice mode
            if voice_mode == 0:
                voice_mode_name = 'POLY'

            elif voice_mode == 1:
                voice_mode_name = 'UNI-A'

            elif voice_mode == 2:
                voice_mode_name = 'UNI-B'

            elif voice_mode == 3:
                voice_mode_name = 'TRI'

            elif voice_mode == 4:
                voice_mode_name = 'DUO'

            elif voice_mode == 5:
                voice_mode_name = 'MONO'

            else:
                # This is an unsupported voice mode value
                Logger.warning(f'Invalid voice mode value: {voice_mode}')
                return

            # Update the voice mode name property
            # used by the UI
            self._set_prop_value_on_main_thread('voice_mode_name', voice_mode_name)

        else:
            # This could be a Nymphes parameter message

            # Convert to a parameter name by skipping the
            # first slash and replacing all other slashes
            # with periods
            param_name = address[1:].replace('/', '.')

            if param_name in NymphesPreset.all_param_names():
                #
                # This is a valid parameter name.
                #

                # Convert the value based on its type
                if NymphesPreset.type_for_param_name(param_name) == float:
                    #
                    # This is a float value parameter.
                    #
                    value = round(args[0], self.fine_mode_decimal_places)

                else:
                    #
                    # This is an integer value
                    #
                    value = int(args[0])

                Logger.debug(f'Received from nymphes-osc: {address}: {args[0]}')

                # Set our property for this parameter
                self._set_prop_value_on_main_thread(param_name.replace('.', '_'), value)

            else:
                # This is an unrecognized OSC message
                Logger.warning(f'Received unhandled OSC message: {address}')

    def _start_nymphes_osc_child_process(self):
        """
        Start the nymphes_osc child process, which handles all
        communication with the Nymphes synthesizer and with
        which we communicate with via OSC.
        :return:
        """
        try:
            self._nymphes_osc_child_process = NymphesOscProcess(
                server_host=self._nymphes_osc_sender_host,
                server_port=self._nymphes_osc_sender_port,
                client_host=self._nymphes_osc_listener_host,
                client_port=self._nymphes_osc_listener_port,
                nymphes_midi_channel=self.nymphes_midi_channel,
                osc_log_level=logging.INFO,
                midi_log_level=logging.INFO,
                presets_directory_path=self._presets_directory_path
            )

            self._nymphes_osc_child_process.start()

            Logger.info('Started the nymphes_osc child process')

        except Exception as e:
            Logger.critical(f'Failed to start the nymphes_osc child process: {e}')

    def _stop_nymphes_osc_child_process(self):
        """
        Stop the nymphes_osc child process if it is running
        :return:
        """
        if self._nymphes_osc_child_process is not None:
            self._nymphes_osc_child_process.kill()
            self._nymphes_osc_child_process.join()
            self._nymphes_osc_child_process = None

            Logger.info('Stopped the nymphes_osc child process')

    def dismiss_popup(self):
        self._popup.dismiss()

    def _on_window_resize(self, instance, width, height):
        #
        # The window has just been resized.
        # We want to maintain a constant aspect ratio.
        #

        # Get the scaling of the window
        new_scaling = instance.dpi / 96
        if self.curr_scaling != new_scaling:
            Logger.debug(f'Scaling changed: was {self.curr_scaling}, now is {new_scaling}')
            self.curr_scaling = new_scaling

        # Scale the width and height
        width /= self.curr_scaling
        height /= self.curr_scaling

        # Determine how much the window size has changed
        #
        width_diff = width - self.curr_width
        height_diff = height - self.curr_height

        self.curr_width = width
        self.curr_height = height

        Logger.debug(f'on_window_resize: new size: {width} x {height}, prev size: {self.curr_width} x {self.curr_height}, diff: {width_diff} x {height_diff}, scaling: {self.curr_scaling}')

        if self._just_resized_window:
            # Skip this resize callback, as it wasn't generated
            # by the user
            Logger.debug('Skipping this resize as it was triggered by us setting the window size')
            self._just_resized_window = False
            return

        #
        # Handle weird situation where resizing on a display with
        # scaling greater than 1 generates a second callback at
        # window size multiplied by the scaling
        #

        if self.curr_scaling > 1:
            if width == self.curr_width and height == self.curr_height:
                Logger.debug(f'Skipping errant callback related to window scaling')

                return

        #
        # Adjust the size of the window to maintain our
        # desired aspect ratio
        #

        if width_diff == 0 and height_diff == 0:
            # For some reason we can get a window resize notification
            # with the same size that it already is
            Logger.debug(f'The window is already this size. Skipping...')
            return

        else:

            if abs(height_diff) > abs(width_diff):
                #
                # The height changed more than the width,
                # so we will achieve our desired aspect
                # ratio by adjusting the width.
                #

                # Calculate the new width
                new_width = int(round(height * self.aspect_ratio))

                # Store the new window size, ignoring scaling
                self.curr_width = new_width
                self.curr_height = height

                # Skip the next callback, as it will be generated by us
                # and not the user
                self._just_resized_window = True

                Logger.debug(f'Resizing based on height to {new_width}, {height}')

                # Resize the window, but use scaling
                Window.size = (new_width, height)

            else:
                #
                # Resize the window by adjusting the height
                #

                # Calculate the new height
                new_height = int(round(width / self.aspect_ratio))

                # Store the new window size, ignoring scaling
                self.curr_width = width
                self.curr_height = new_height

                # Skip the next callback, as it will be generated by us
                # and not the user
                self._just_resized_window = True
                Logger.debug(f'Resizing based on width to {width}, {new_height}')

                # Resize the window, using the scaling
                Window.size = (width, new_height)

    def _set_presets_spinner_file_option_on_main_thread(self, option_text):
        """
        Replace the first item in the self.presets_spinner_values ListProperty
        with new_text and update the spinner text, but do it on the Main thread.
        If a file has just been loaded or saved for the first time, then insert
        the option at the beginning of the list and then select it.
        If option_text is None, then remove the file option from the list.
        This is needed if the change occurs in response to an OSC message on a
        background thread.
        :param option_text: str
        :return:
        """
        def work_func(_, new_text):
            if new_text is None:
                # We need to remove the file option from the list
                if len(self.presets_spinner_values) != 99:
                    self.presets_spinner_values.pop(0)

                # Select the first entry
                self.presets_spinner_text = self.presets_spinner_values[0]
                self._curr_presets_spinner_index = 0
            else:
                # new_text is not None, so we are setting the file
                # option or adding it if it doesn't exist
                if len(self.presets_spinner_values) == 99:
                    # No file has previously been loaded or saved,
                    # so we need to insert the new filename at the
                    # beginning of the list
                    self.presets_spinner_values.insert(0, new_text)

                else:
                    # There is already a spot at the beginning of
                    # the list for the filename
                    self.presets_spinner_values[0] = new_text

                # Update the preset spinner text
                self.presets_spinner_text = self.presets_spinner_values[0]
                self._curr_presets_spinner_index = 0

        Clock.schedule_once(lambda dt: work_func(dt, option_text), 0)

    def _set_prop_value_on_main_thread(self, prop_name, value):
        def work_func(_, _prop_name, _value):
            setattr(self, _prop_name, _value)
            setattr(self, _prop_name, _value)

        Clock.schedule_once(lambda dt: work_func(dt, prop_name, value), 0)

    @staticmethod
    def set_system_cursor_on_main_thread(cursor_name):
        def work_func(_, _cursor_name):
            Window.set_system_cursor(_cursor_name)

        Clock.schedule_once(lambda dt: work_func(dt, cursor_name), 0)

    def set_invert_mouse_wheel(self, value):
        self.invert_mouse_wheel = value

        # Save the config file
        self._save_config_file(self._config_file_path)

    def _add_name_to_nymphes_input_spinner_on_main_thread(self, port_name):
        def work_func(_, new_port_name):
            # Add the port name to the list used by the
            # Nymphes input ports spinner
            self.nymphes_input_spinner_names.append(new_port_name)
            self.nymphes_input_spinner_names = [self.nymphes_input_spinner_names[0]] + sorted(
                self.nymphes_input_spinner_names[1:])

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

    def _remove_name_from_nymphes_input_spinner_on_main_thread(self, port_name):
        def work_func(_, new_port_name):
            # Remove it from the Nymphes input spinner list as well
            if new_port_name in self.nymphes_input_spinner_names:
                self.nymphes_input_spinner_names.remove(new_port_name)

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

    def _add_name_to_nymphes_output_spinner_on_main_thread(self, port_name):
        def work_func(_, new_port_name):
            # Add the port name to the list used by the
            # Nymphes output ports spinner
            self.nymphes_output_spinner_names.append(new_port_name)
            self.nymphes_output_spinner_names = [self.nymphes_output_spinner_names[0]] + sorted(
                self.nymphes_output_spinner_names[1:])

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

    def _remove_name_from_nymphes_output_spinner_on_main_thread(self, port_name):
        def work_func(_, new_port_name):
            # Remove it from the Nymphes output spinner list as well
            if new_port_name in self.nymphes_output_spinner_names:
                self.nymphes_output_spinner_names.remove(new_port_name)

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

    def _add_midi_input_name_on_main_thread(self, port_name):
        def work_func(_, new_port_name):
            # Add the port name to the list of detected
            # MIDI controller input ports
            self.detected_midi_input_names_for_gui.append(new_port_name)
            self.detected_midi_input_names_for_gui.sort()

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

    def _remove_midi_input_name_on_main_thread(self, port_name):
        def work_func(_, new_port_name):
            if new_port_name in self.detected_midi_input_names_for_gui:
                self.detected_midi_input_names_for_gui.remove(new_port_name)

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

    def _add_midi_output_name_on_main_thread(self, port_name):
        def work_func(_, new_port_name):
            self.detected_midi_output_names_for_gui.append(new_port_name)
            self.detected_midi_output_names_for_gui.sort()

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

    def _remove_midi_output_name_on_main_thread(self, port_name):
        def work_func(_, new_port_name):
            if new_port_name in self.detected_midi_output_names_for_gui:
                self.detected_midi_output_names_for_gui.remove(new_port_name)

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

    def _add_connected_midi_input_name_on_main_thread(self, port_name):
        def work_func(_, new_port_name):
            self.connected_midi_input_names_for_gui.append(new_port_name)
            self.connected_midi_input_names_for_gui.sort()

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

    def _remove_connected_midi_input_name_on_main_thread(self, port_name):
        def work_func(_, new_port_name):
            if new_port_name in self.connected_midi_input_names_for_gui:
                self.connected_midi_input_names_for_gui.remove(new_port_name)

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

    def _add_connected_midi_output_name_on_main_thread(self, port_name):
        def work_func(_, new_port_name):
            self.connected_midi_output_names_for_gui.append(new_port_name)
            self.connected_midi_output_names_for_gui.sort()

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

    def _remove_connected_midi_output_name_on_main_thread(self, port_name):
        def work_func(_, new_port_name):
            if new_port_name in self.connected_midi_output_names_for_gui:
                self.connected_midi_output_names_for_gui.remove(new_port_name)

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

    @staticmethod
    def parse_preset_index(preset_index):
        """
        Parse the supplied preset spinner index into bank, preset number
        and type.
        Return a dict containing the parsed values.
        """
        bank_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        preset_nums = [1, 2, 3, 4, 5, 6, 7]
        preset_types = ['user', 'factory']

        bank_name = bank_names[int((preset_index % 49) / 7)]
        preset_num = preset_nums[int((preset_index % 49) % 7)]
        preset_type = preset_types[int(preset_index / 49)]

        return {'bank_name': bank_name,
                'preset_num': preset_num,
                'preset_type': preset_type}

    @staticmethod
    def index_from_preset_info(bank_name, preset_num, preset_type):
        """
        Calculates and returns the preset index for the supplied preset
        bank_name, preset_num and preset_type.
        Raises an Exception if any of the arguments are invalid.
        Return type: int
        """
        bank_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        preset_nums = [1, 2, 3, 4, 5, 6, 7]
        preset_types = ['user', 'factory']

        if bank_name not in bank_names:
            raise Exception(f'Invalid bank_name: {bank_name}')

        if preset_num not in preset_nums:
            raise Exception(f'Invalid preset_num: {preset_num}')

        if preset_type not in preset_types:
            raise Exception(f'Invalid preset_type: {preset_type}')

        index = 0
        index += preset_num - 1
        index += bank_names.index(bank_name) * 7
        index += preset_types.index(preset_type) * 49

        return index

    @staticmethod
    def string_for_lfo_type(lfo_type_int):
        """
        LFO Type has four discrete values, from 0 to 3, and
        each has a name. Return the name as a string.
        Raises an Exception if lfo_type_int is less than 0
        or greater than 3.
        """
        if lfo_type_int < 0 or lfo_type_int > 3:
            raise Exception(f'lfo_type_int must be between 0 and 3: {lfo_type_int}')

        if lfo_type_int == 0:
            return 'BPM'

        elif lfo_type_int == 1:
            return 'LOW'

        elif lfo_type_int == 2:
            return 'HIGH'

        elif lfo_type_int == 3:
            return 'TRACK'

    def open_presets_folder_in_native_file_browser(self):
        """
        Opens a new native filebrowser (Finder on macOS)
        showing the presets folder.
        """
        #
        # In order to make open -R show the contents of a directory,
        # we need to provide a path to a file inside the directory.
        # Otherwise it opens the parent folder of the directory instead.
        # We will use the init.txt preset file because we know that
        # it exists.
        #

        subprocess.call(['open', '-R', self._init_preset_file_path])

    def open_logs_folder_in_native_file_browser(self):
        """
        Opens a new native filebrowser (Finder on macOS)
        showing the kivy logs folder.
        """
        #
        # In order to make open -R show the contents of a directory,
        # we need to provide a path to a file inside the directory.
        # Otherwise it opens the parent folder of the directory instead.
        # We will select the most recently created log file in the directory.
        #

        # Check whether the logs directory contains any files
        logs_dir_path = Path(os.path.expanduser('~/.kivy/logs/'))
        log_files = glob.glob(os.path.join(logs_dir_path, '*'))

        if not log_files:
            # The directory is empty.
            # Open the directory itself, which will cause Finder
            # to show the directory inside its parent directory.
            subprocess.call(['open', '-R', logs_dir_path])

        else:
            # The directory contains files.
            # Open the most recent one, which will cause
            # Finder to show the contents of the folder
            # and select the file.
            most_recent_file = max(log_files, key=os.path.getctime)
            subprocess.call(['open', '-R', most_recent_file])

    def activate_chord_number(self, chord_number):
        """
        Send /pitch/chord/value to Nymphes to activate one
        of the chords.
        chord_number should be an int, from 0 to 7.
        """
        if chord_number == 0:
            chord_val = 0

        elif chord_number == 1:
            chord_val = 10

        elif chord_number == 2:
            chord_val = 28

        elif chord_number == 3:
            chord_val = 46

        elif chord_number == 4:
            chord_val = 64

        elif chord_number == 5:
            chord_val = 82

        elif chord_number == 6:
            chord_val = 100

        elif chord_number == 7:
            chord_val = 118

        else:
            raise Exception(f'Invalid chord number: {chord_number}. Should be between 0 and 7')

        # Send to Nymphes
        self.send_nymphes_osc('/pitch/chord/value', chord_val)

        # Update our property
        self._set_prop_value_on_main_thread('pitch_chord_value', chord_val)

        self._set_prop_value_on_main_thread('status_bar_text', f'pitch.chord.value: {chord_val}')

    def _on_file_drop(self, window, file_path, x, y):
        # file_path is bytes. Convert to string
        file_path = str(file_path)

        # Remove leading "b'" and trailing "'"
        file_path = file_path[2:-1]

        Logger.info(f'_on_file_drop: {file_path}')

        self.send_nymphes_osc('/load_file', file_path)

    @staticmethod
    def string_for_lfo_key_sync(lfo_key_sync):
        """
        LFO Key Sync has two discrete values, 0 and 1,
        representing ON and OFF. Return these as strings.
        Raises an Exception if lfo_key_sync is less than 0
        or greater than 1.
        """
        if lfo_key_sync < 0 or lfo_key_sync > 1:
            raise Exception(f'lfo_key_sync must be between 0 and 1: {lfo_key_sync}')

        return 'ON' if lfo_key_sync == 1 else 'OFF'

    def control_section_selected(self, name):
        """
        A control section has been selected by tapping its title
        """
        print(name)

    def control_selected(self, name):
        """
        A control has been selected by tapping its title
        """
        print(name)

    def _show_demo_mode_popup(self):
        content = DemoModePopup()

        self._popup = Popup(title='DEMO MODE',
                            content=content,
                            size_hint=(0.6, 0.6))

        self._popup.open()
