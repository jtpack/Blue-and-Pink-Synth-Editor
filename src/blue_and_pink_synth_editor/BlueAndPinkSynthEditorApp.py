import logging
from pathlib import Path
import os
import threading
import configparser
import netifaces
import platform
import subprocess

from kivy.config import Config
Config.read(str(Path(__file__).resolve().parent / 'app_config.ini'))

from kivy.app import App
import kivy
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, DictProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.factory import Factory
from kivy.core.window import Window
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner, SpinnerOption

from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.osc_message_builder import OscMessageBuilder

from kivy.logger import Logger, LOG_LEVELS
Logger.setLevel(LOG_LEVELS["info"])

from nymphes_midi.NymphesPreset import NymphesPreset
from .nymphes_osc_process import NymphesOscProcess

kivy.require('2.1.0')

app_version_string = 'v0.2.3-beta'


class BlueAndPinkSynthEditorApp(App):
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

    detected_midi_input_names_for_gui = ListProperty([])
    midi_inputs_spinner_curr_value = StringProperty('Not Connected')

    detected_midi_output_names_for_gui = ListProperty([])
    midi_outputs_spinner_curr_value = StringProperty('Not Connected')

    status_bar_text = StringProperty('NYMPHES NOT CONNECTED')
    error_text = StringProperty('')
    error_detail_text = StringProperty('')

    unsaved_preset_changes = BooleanProperty(False)

    curr_mouse_hover_param_name = StringProperty('')
    curr_mouse_dragging_param_name = StringProperty('')
    curr_screen_name = StringProperty('dashboard')

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

    invert_mouse_wheel = BooleanProperty(True)

    # Window dimensions
    #
    curr_width = NumericProperty(800)
    curr_height = NumericProperty(480)

    def __init__(self, **kwargs):
        super(BlueAndPinkSynthEditorApp, self).__init__(**kwargs)

        # Set the app title
        self.title = f'Blue and Pink Synth Editor {app_version_string}'

        #
        # Keyboard Stuff
        #

        # Bind keyboard events
        self._bind_keyboard_events()

        # Keep track of currently held modifier keys
        self._shift_key_pressed = False
        self._caps_lock_key_on = False
        self._meta_key_pressed = False
        self._alt_key_pressed = False

        # Choose the fine mode modifier key based on the
        # current operating system
        #
        os_name = platform.system()
        Logger.info(f'Operating system is {os_name}')

        if os_name == 'Windows':
            self.fine_mode_modifier_key = 'shift'
        elif os_name == 'Darwin':
            self.fine_mode_modifier_key = 'meta'
        elif os_name == 'Linux':
            self.fine_mode_modifier_key = 'shift'
        else:
            self.fine_mode_modifier_key = 'shift'

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
        self._curr_preset_slot_bank_and_number = (None, None)

        #
        # Presets Spinner Stuff
        #

        values = ['init']
        values.extend(
            [f'{kind} {bank}{num}' for kind in ['USER', 'FACTORY'] for bank in ['A', 'B', 'C', 'D', 'E', 'F', 'G']
             for num in [1, 2, 3, 4, 5, 6, 7]])
        self.presets_spinner_values = values

        self._curr_presets_spinner_index = 0

        #
        # Preset File Dialog
        #

        self._popup = None

        #
        # Create directories to hold app data, like presets
        # and config files.
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

        # Create a config file if one doesn't exist
        if not Path(self._config_file_path).exists():
            self._create_config_file(self._config_file_path)

        # Load contents of config file
        self._load_config_file(self._config_file_path)

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
        content = LoadDialog(load=self.on_file_load_dialog, cancel=self._dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.bind(on_open=self._on_popup_open)
        self._popup.bind(on_dismiss=self._on_popup_dismiss)
        self._popup.open()

    def show_save_dialog(self):
        content = SaveDialog(
            save=self.on_file_save_dialog,
            cancel=self._dismiss_popup,
            default_filename=self._curr_preset_file_path.name if self._curr_preset_file_path is not None else ''
        )
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.bind(on_open=self._on_popup_open)
        self._popup.bind(on_dismiss=self._on_popup_dismiss)
        self._popup.open()

    def show_error_dialog_on_main_thread(self, error_string, error_detail_string):
        def work_func(_, error_text, error_detail_text):
            self.error_text = error_text
            self.error_detail_text = error_detail_text
            self.show_error_dialog()

        Clock.schedule_once(lambda dt: work_func(dt, error_string, error_detail_string), 0)

    def show_error_dialog(self):
        content = ErrorDialog(ok=self._dismiss_popup)
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

    def on_file_load_dialog(self, path=None, filepaths=[]):
        # Close the file load dialog
        self._dismiss_popup()

        # Re-bind keyboard events
        self._bind_keyboard_events()

        if len(filepaths) > 0:
            Logger.debug(f'load path: {path}, filename: {filepaths}')

            # Send message to nymphes controller to load the preset file
            self.send_nymphes_osc('/load_file', filepaths[0])

    def on_file_save_dialog(self, directory_path, filepath):
        # Close the dialogue
        self._dismiss_popup()

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
                self._set_prop_value_for_param_name(param_name, new_val)

        else:
            # Apply the increment amount and round using the precision
            # specified in NymphesPreset
            new_val = round(curr_val + amount, NymphesPreset.float_precision_num_decimals)

            # Keep within the min and max value range
            if new_val < min_val:
                new_val = min_val

            if new_val > max_val:
                new_val = max_val

            # Set the property's value only if the new value is different
            # than the current value
            if not self.float_equals(curr_val, new_val, NymphesPreset.float_precision_num_decimals):
                self._set_prop_value_for_param_name(param_name, new_val)

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

    def on_mouse_entered_param_control(self, param_name):
        # When the mouse enters a parameter control and Nymphes
        # is connected, display the name and value in the status
        # bar.
        if self.nymphes_connected:
            if self.curr_mouse_dragging_param_name == '':
                # Change the mouse cursor to a hand indicate that
                # this is a control
                Window.set_system_cursor('hand')

                # Store the name of the parameter
                self.curr_mouse_hover_param_name = param_name

                # Get the value and type for the parameter
                value = self._get_prop_value_for_param_name(param_name)
                param_type = NymphesPreset.type_for_param_name(param_name)

                if param_type == float:
                    value_string = format(round(value, NymphesPreset.float_precision_num_decimals), f'.{NymphesPreset.float_precision_num_decimals}f')

                elif param_type == int:
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

    def increment_mod_wheel(self, amount):
        new_val = self.mod_wheel + int(amount)
        if new_val > 127:
            new_val = 127
        elif new_val < 0:
            new_val = 0

        if new_val != self.mod_wheel:
            # Update the property
            self.mod_wheel = new_val

            # Send the new value to Nymphes
            self.send_nymphes_osc(
                '/mod_wheel',
                new_val
            )

    def increment_aftertouch(self, amount):
        new_val = self.aftertouch + int(amount)
        if new_val > 127:
            new_val = 127
        elif new_val < 0:
            new_val = 0

        if new_val != self.aftertouch:
            # Update the property
            self.aftertouch = new_val

            # Send the new value to Nymphes
            self.send_nymphes_osc(
                '/aftertouch',
                new_val
            )

    def on_nymphes_midi_channel_spinner(self, new_val):
        # The spinner's values are strings, so
        # convert new_val to an int
        midi_channel = int(new_val)

        if midi_channel != self.nymphes_midi_channel:
            Logger.info(f'Changing Nymphes MIDI channel to {midi_channel}')

            # Send a message to nymphes-osc to change the channel
            self.send_nymphes_osc(
                '/set_nymphes_midi_channel',
                midi_channel
            )

    def set_curr_screen_name(self, screen_name):
        self.curr_screen_name = screen_name

    def set_curr_mouse_dragging_param_name(self, param_name):
        self.curr_mouse_dragging_param_name = param_name

    def _get_prop_value_for_param_name(self, param_name):
        # Convert the parameter name to the name
        # of our corresponding property
        property_name = param_name.replace('.', '_')

        # Get the property's current value
        return getattr(self, property_name)

    def _set_prop_value_for_param_name(self, param_name, value):
        # Update our property for this parameter name
        setattr(self, param_name.replace('.', '_'), value)

        # Set status bar text
        #
        param_type = NymphesPreset.type_for_param_name(param_name)
        if param_type == float:
            value_string = format(round(value, NymphesPreset.float_precision_num_decimals),
                                  f'.{NymphesPreset.float_precision_num_decimals}f')
        elif param_type == int:
            value_string = str(value)

        self._set_prop_value_on_main_thread('status_bar_text', f'{param_name}: {value_string}')

        # Send an OSC message for this parameter with the new value
        self.send_nymphes_osc(f'/{param_name.replace(".", "/")}', value)

    def _bind_keyboard_events(self):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self.root)
        self._keyboard.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)

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
            'nymphes midi channel': self.nymphes_midi_channel
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
            
            self._set_prop_value_on_main_thread('nymphes_input_name', input_port)
            self._set_prop_value_on_main_thread('nymphes_output_name', output_port)

            # Update app state
            self.nymphes_connected = True

            # Status message
            self._set_prop_value_on_main_thread('status_bar_text', 'NYMPHES CONNECTED')

        elif address == '/nymphes_disconnected':
            #
            # nymphes_midi is no longer connected to a Nymphes synthesizer
            #

            Logger.info(f'Received from nymphes-osc: {address}')

            # Update app state
            self.nymphes_connected = False
            self._nymphes_input_port = None
            self._nymphes_output_port = None

            self._set_prop_value_on_main_thread('status_bar_text', 'NYMPHES NOT CONNECTED')
            self._set_prop_value_on_main_thread('nymphes_input_name', 'Not Connected')
            self._set_prop_value_on_main_thread('nymphes_output_name', 'Not Connected')

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

            # Update the current preset type
            self.curr_preset_type = 'preset_slot'

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
            self.curr_preset_type = 'file'

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
            self.curr_preset_type = 'init'

            # Reset current preset slot info
            self._curr_preset_slot_type = None
            self._curr_preset_slot_bank_and_number = None

            # Reset the unsaved changes flag
            self._set_prop_value_on_main_thread('unsaved_preset_changes', False)

            # Update the presets spinner
            # Select the init option
            self.presets_spinner_text = 'init'
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

            # Update the current preset type
            self.curr_preset_type = 'file'

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
            self._set_presets_spinner_file_option_on_main_thread(self._curr_preset_file_path.name)

            # Status bar message
            msg = f'SAVED {filepath.name} PRESET FILE'
            self._set_prop_value_on_main_thread('status_bar_text', msg)

        elif address == '/saved_preset_to_file':
            #
            # A Nymphes preset slot has been saved to a file
            #

            # Get the preset info
            filepath = str(args[0])
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

        elif address == '/osc/legato/value':
            Logger.debug(f'Received from nymphes-osc: {address}: {args[0]}')
            val = int(args[0])
            self._set_prop_value_on_main_thread('osc_legato_value', val)

        elif address == '/osc/voice_mode/value':
            Logger.debug(f'Received from nymphes-osc: {address}: {args[0]}')

            voice_mode = int(args[0])

            # Store the new voice mode as an int
            self.osc_voice_mode_value = voice_mode

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
                    value = round(args[0], NymphesPreset.float_precision_num_decimals)

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

    def _on_popup_open(self, popup_instance):
        # Bind keyboard events for the popup
        popup_instance.content._keyboard = Window.request_keyboard(popup_instance.content._keyboard_closed,
                                                                   popup_instance)
        popup_instance.content._keyboard.bind(
            on_key_down=popup_instance.content._on_key_down,
            on_key_up=popup_instance.content._on_key_up
        )

    def _dismiss_popup(self):
        self._popup.dismiss()

    def _on_popup_dismiss(self, popup_instance):
        # Unbind keyboard events from the popup
        if popup_instance.content._keyboard is not None:
            popup_instance.content._keyboard.unbind(on_key_down=popup_instance.content._on_key_down)
            popup_instance.content._keyboard.unbind(on_key_up=popup_instance.content._on_key_up)
            popup_instance.content._keyboard = None

        # Rebind keyboard events for the app itself
        self._bind_keyboard_events()

    def _keyboard_closed(self):
        Logger.debug('Keyboard Closed')
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard.unbind(on_key_up=self._on_key_up)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        Logger.debug(f'on_key_down: {keyboard}, {keycode}, {text}, {modifiers}')

        # Check for either of the shift keys
        left_shift_key_code = 304
        right_shift_key_code = 303
        if keycode in [left_shift_key_code, right_shift_key_code] or 'shift' in modifiers:
            Logger.debug('Shift key pressed')
            self._shift_key_pressed = True

            if self.fine_mode_modifier_key == 'shift':
                # Enable fine mode
                Logger.debug('Fine Mode Enabled')
                self.fine_mode = True

        # Check for the meta key (CMD on macOS)
        left_meta_key_code = 309
        right_meta_key_code = 1073742055
        if keycode in [left_meta_key_code, right_meta_key_code] or 'meta' in modifiers:
            Logger.debug('meta key pressed')
            self._meta_key_pressed = True

            if self.fine_mode_modifier_key == 'meta':
                # Enable fine mode
                Logger.debug('Fine Mode Enabled')
                self.fine_mode = True

        # Check for the Alt key (Alt/Option on macOS)
        left_alt_key_code = 308
        right_alt_key_code = 307
        if keycode in [left_alt_key_code, right_alt_key_code] or 'alt' in modifiers:
            Logger.debug('alt key pressed')
            self._alt_key_pressed = True

            if self.fine_mode_modifier_key == 'alt':
                # Enable fine mode
                Logger.debug('Fine Mode Enabled')
                self.fine_mode = True

    def _on_key_up(self, keyboard, keycode):
        Logger.debug(f'on_key_up: {keyboard}, {keycode}')

        # Check for either of the shift keys
        left_shift_key_code = 304
        right_shift_key_code = 303
        if keycode[0] in [left_shift_key_code, right_shift_key_code]:
            Logger.debug('Shift key released')
            self._shift_key_pressed = False

            if self.fine_mode_modifier_key == 'shift':
                # Disable fine mode
                Logger.debug('Fine Mode Disabled')
                self.fine_mode = False

        # Check for the meta key (CMD on macOS)
        left_meta_key_code = 309
        right_meta_key_code = 1073742055
        if keycode[0] in [left_meta_key_code, right_meta_key_code]:
            Logger.debug('meta key released')
            self._meta_key_pressed = False

            if self.fine_mode_modifier_key == 'meta':
                # Disable fine mode
                Logger.debug('Fine Mode Disabled')
                self.fine_mode = False

        # Check for the Alt key (Alt/Option on macOS)
        left_alt_key_code = 308
        right_alt_key_code = 307
        if keycode[0] in [left_alt_key_code, right_alt_key_code]:
            Logger.debug('alt key released')
            self._alt_key_pressed = False

            if self.fine_mode_modifier_key == 'alt':
                # Disable fine mode
                Logger.debug('Fine Mode Disabled')
                self.fine_mode = False

        # File Open
        if keycode[1] == 'o' and self._meta_key_pressed:
            # Show the file load dialog
            self.show_load_dialog()

        # File Save / Save As
        if keycode[1] == 's' and self._meta_key_pressed and self._alt_key_pressed:
            #
            # Save As
            #

            # Show the file save dialog
            self.show_save_dialog()

        elif keycode[1] == 's' and self._meta_key_pressed:
            #
            # Save
            #

            if self.curr_preset_type == 'file':
                # A file is currently loaded. Update it.
                self.update_current_preset_file()

            else:
                # Show the file save dialog
                self.show_save_dialog()

    def _on_window_resize(self, instance, width, height):
        #
        # The window has just been resized.
        # We want to maintain a constant aspect ratio.
        #

        # Get the scaling of the window
        scaling = instance.dpi / 96

        # Determine how much the window size has changed
        #
        width_diff = width - self.curr_width
        height_diff = height - self.curr_height

        Logger.debug(f'on_window_resize: new size: {width} x {height}, prev size: {self.curr_width} x {self.curr_height}, diff: {width_diff} x {height_diff}, scaling: {scaling}')

        if self._just_resized_window:
            # Skip this resize callback, as it wasn't generated
            # by the user
            # Logger.debug('Skipping this resize as it was triggered by us setting the window size')
            self._just_resized_window = False
            return

        #
        # Handle weird situation where resizing on a display with
        # scaling greater than 1 generates a second callback at
        # window size multiplied by the scaling
        #

        if scaling > 1:
            if width == self.curr_width * scaling and height == self.curr_height * scaling:
                # Logger.debug(f'Skipping errant callback related to window scaling')
                return

        #
        # Adjust the size of the window to maintain our
        # desired aspect ratio
        #

        if width_diff == 0 and height_diff == 0:
            # For some reason we can get a window resize notification
            # with the same size that it already is
            # Logger.debug(f'The window is already this size. Skipping...')
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

                # Logger.debug(f'Resizing based on height to {new_width}, {height}')

                # Resize the window, but use scaling
                Window.size = (new_width / scaling, height / scaling)

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
                # Logger.debug(f'Resizing based on width to {width}, {new_height}')

                # Resize the window, using the scaling
                Window.size = (width / scaling, new_height / scaling)

    def _set_presets_spinner_file_option_on_main_thread(self, option_text):
        """
        Replace the first item in the self.presets_spinner_values ListProperty
        with new_text and update the spinner text, but do it on the Main thread.
        If a file has just been loaded or saved for the first time, then insert
        the option at the beginning of the list and then select it.
        This is needed if the change occurs in response to an OSC message on a
        background thread.
        :param new_text: str
        :return:
        """
        def work_func(_, new_text):
            if len(self.presets_spinner_values) == 99:
                # No file has previously been loaded or saved,
                # so we need to insert the new value at the
                # beginning of the list
                self.presets_spinner_values.insert(0, new_text)

            else:
                # There is already a spot at the beginning of
                # the list for filename
                self.presets_spinner_values[0] = new_text

            # Update the preset spinner text
            self.presets_spinner_text = self.presets_spinner_values[0]
            self._curr_presets_spinner_index = 0

        Clock.schedule_once(lambda dt: work_func(dt, option_text), 0)
        
    def _set_prop_value_on_main_thread(self, prop_name, value):
        def work_func(_, _prop_name, _value):
            setattr(self, _prop_name, _value)
            
        Clock.schedule_once(lambda dt: work_func(dt, prop_name, value), 0)

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
        Opens a new native filebrowser (Finder on macOS, Windows Explorer on Windows)
        showing the presets folder.
        """
        subprocess.call(['open', '-R', self._presets_directory_path])

    def open_logs_folder_in_native_file_browser(self):
        """
        Opens a new native filebrowser (Finder on macOS, Windows Explorer on Windows)
        showing the kivy logs folder.
        """
        subprocess.call(['open', '-R', Path(os.path.expanduser('~/.kivy/logs/'))])

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

class ValueControl(ButtonBehavior, Label):
    screen_name = StringProperty('')
    section_name = StringProperty('')
    param_name = StringProperty('')
    drag_start_pos = NumericProperty(0)
    text_color_string = StringProperty('#06070FFF')
    mouse_pressed = BooleanProperty(False)
    mouse_inside_bounds = BooleanProperty(False)
    base_font_size = NumericProperty(20)

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
        if App.get_running_app().curr_mouse_dragging_param_name == '':
            self.mouse_inside_bounds = True
            App.get_running_app().on_mouse_entered_param_control(self.param_name)

    def on_mouse_exit(self):
        App.get_running_app().on_mouse_exited_param_control(self.param_name)
        self.mouse_inside_bounds = False

    def on_touch_down(self, touch):
        #
        # This is called when the mouse is clicked
        #
        if not self.disabled:
            if self.collide_point(*touch.pos) and touch.button == 'left':
                touch.grab(self)

                # Store the starting y position of the touch
                self.drag_start_pos = int(touch.pos[1])

                # The mouse is pressed
                self.mouse_pressed = True

                # Inform the app that a drag has started
                App.get_running_app().set_curr_mouse_dragging_param_name(self.param_name)

                return True

            return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if not self.disabled:
            if touch.grab_current == self:
                touch.ungrab(self)

                # Inform the app that a drag has ended
                App.get_running_app().set_curr_mouse_dragging_param_name('')

                # The mouse is no longer pressed
                self.mouse_pressed = False

                return True

            return super().on_touch_up(touch)

    def handle_touch(self, device, button):
        #
        # Mouse Wheel
        #
        if self.disabled:
            return

        if device == 'mouse' and button in ['scrollup', 'scrolldown']:
            # Determine direction
            direction = 1 if button == 'scrollup' else -1

            # Apply mouse wheel inversion, if enabled
            if App.get_running_app().invert_mouse_wheel:
                direction *= -1

            # Determine the increment
            #
            increment = self.get_mouse_wheel_increment()
            if isinstance(increment, float):
                increment *= float(direction)
            else:
                increment *= direction

            # Increment the property
            App.get_running_app().increment_prop_value_for_param_name(self.param_name, increment)

    def on_touch_move(self, touch):
        #
        # This is called when the mouse drags
        #
        if not self.disabled:
            if touch.grab_current == self:
                # Get the current y position
                curr_pos = int(touch.pos[1])

                # Calculate the distance from the starting drag position
                curr_drag_distance = (self.drag_start_pos - curr_pos) * -1

                # Scale the drag distance and use as the increment
                increment = self.get_mouse_drag_increment(curr_drag_distance)

                # Increment the property's value
                App.get_running_app().increment_prop_value_for_param_name(self.param_name, increment)

                # Reset the drag start position to the current position
                self.drag_start_pos = curr_pos

                return True

            return super().on_touch_move(touch)

    def get_mouse_wheel_increment(self):
        return 1

    def get_mouse_drag_increment(self, drag_distance):
        return int(round(drag_distance * (1 / 3)))

class FloatParamValueLabel(ValueControl):
    def get_mouse_wheel_increment(self):
        if App.get_running_app().fine_mode:
            # We are in fine mode, so use the minimum increment defined by
            # NymphesPreset's float precision property
            return 1.0 / pow(10, NymphesPreset.float_precision_num_decimals)

        else:
            return 1

    def get_mouse_drag_increment(self, drag_distance):
        if App.get_running_app().fine_mode:
            return round(drag_distance * 0.05, NymphesPreset.float_precision_num_decimals)

        else:
            return int(round(drag_distance * (1 / 3)))

class IntParamValueLabel(ValueControl):
    def get_mouse_drag_increment(self, drag_distance):
        return int(round(drag_distance * 0.2))

class ChordParamValueLabel(ValueControl):
    def get_mouse_drag_increment(self, drag_distance):
        return int(round(drag_distance * 0.2))

class ParamsGridModCell(BoxLayout):
    screen_name = StringProperty('')
    section_name = StringProperty('')
    title = StringProperty('')
    screen_name = StringProperty('')
    param_name = StringProperty('')
    param_name_color_string = StringProperty('#ECBFEBFF')
    value_color_string = StringProperty('#06070FFF')
    background_color_string = StringProperty('#438EFFFF')
    mod_amount_line_background_color_string = StringProperty('#000000FF')

    value_prop = NumericProperty(0)
    lfo2_prop = NumericProperty(0)
    mod_wheel_prop = NumericProperty(0)
    velocity_prop = NumericProperty(0)
    aftertouch_prop = NumericProperty(0)
    corner_radius = NumericProperty(0)


class ParamsGridNonModCell(ButtonBehavior, BoxLayout):
    screen_name = StringProperty('')
    section_name = StringProperty('')
    title = StringProperty('')
    param_name = StringProperty('')
    value_prop = NumericProperty(0)
    corner_radius = NumericProperty(0)
    value_color_string = StringProperty('#06070FFF')
    background_color_string = StringProperty('#438EFFFF')
    param_name_color_string = StringProperty('#ECBFEBFF')


class ParamsGridLfoConfigCell(ButtonBehavior, BoxLayout):
    screen_name = StringProperty('')
    section_name = StringProperty('')
    type_prop = NumericProperty(0)
    key_sync_prop = NumericProperty(0)
    corner_radius = NumericProperty(0)
    param_name_color_string = StringProperty('#ECBFEBFF')
    value_color_string = StringProperty('#06070FFF')
    background_color_string = StringProperty('#438EFFFF')


class ParamsGridPlaceholderCell(Widget):
    pass


class LoadDialog(BoxLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LoadDialog, self).__init__(**kwargs)
        self._keyboard = None

    def _keyboard_closed(self):
        Logger.debug('LoadDialog Keyboard Closed')
        if self._keyboard is not None:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard.unbind(on_key_up=self._on_key_up)
            self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        Logger.debug(f'LoadDialog on_key_down: {keyboard}, {keycode}, {text}, {modifiers}')

    def _on_key_up(self, keyboard, keycode):
        Logger.debug(f'LoadDialog on_key_up: {keyboard}, {keycode}')

        # Handle Enter Key
        # This is the same as clicking the OK button
        enter_keycode = 13
        numpad_enter_keycode = 271

        if keycode[0] in [enter_keycode, numpad_enter_keycode]:
            self.load(self.ids.filechooser.path, self.ids.filechooser.selection)

        # Handle escape key
        # This is the same as clicking the Cancel button
        escape_keycode = 27
        if keycode[0] in [escape_keycode]:
            App.get_running_app()._dismiss_popup()


class SaveDialog(BoxLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    default_filename = StringProperty('')
    
    def __init__(self, **kwargs):
        super(SaveDialog, self).__init__(**kwargs)
        self._keyboard = None

    def _keyboard_closed(self):
        Logger.debug('SaveDialog Keyboard Closed')
        # if self._keyboard is not None:
        #     self._keyboard.unbind(on_key_down=self._on_key_down)
        #     self._keyboard.unbind(on_key_up=self._on_key_up)
        #     self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        Logger.debug(f'SaveDialog on_key_down: {keyboard}, {keycode}, {text}, {modifiers}')

    def _on_key_up(self, keyboard, keycode):
        Logger.debug(f'SaveDialog on_key_up: {keyboard}, {keycode}')

        # Handle Enter Key
        # This is the same as clicking the OK button
        enter_keycode = 13
        numpad_enter_keycode = 271

        if keycode[0] in [enter_keycode, numpad_enter_keycode]:
            self.save(self.ids.filechooser.path, self.ids.filechooser.path + '/' + self.ids.text_input.text)

        # Handle escape key
        # This is the same as clicking the Cancel button
        escape_keycode = 27
        if keycode[0] in [escape_keycode]:
            App.get_running_app()._dismiss_popup()


Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)


class ModAmountLine(ButtonBehavior, Widget):
    midi_val = NumericProperty(0) # This is 0 to 127
    color_hex = StringProperty('#FFFFFFFF')
    screen_name = StringProperty('')
    section_name = StringProperty('')
    param_name = StringProperty('')
    mod_type = StringProperty('')
    drag_start_pos = NumericProperty(0)
    background_color_string = StringProperty('#72777BFF')
    mouse_pressed = BooleanProperty(False)
    mouse_inside_bounds = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouseover)

    def on_mouseover(self, _, pos):
        if App.get_running_app().curr_screen_name == self.screen_name:
            if self.collide_point(*pos):
                if not self.mouse_inside_bounds:
                    self.mouse_inside_bounds = True
                    self.on_mouse_enter()

            else:
                if self.mouse_inside_bounds:
                    self.mouse_inside_bounds = False
                    self.on_mouse_exit()

    def on_mouse_enter(self):
        App.get_running_app().on_mouse_entered_param_control(f'{self.param_name}.{self.mod_type}')

    def on_mouse_exit(self):
        App.get_running_app().on_mouse_exited_param_control(f'{self.param_name}.{self.mod_type}')

    def handle_touch(self, device, button):
        #
        # Mouse Wheel
        #
        if not self.disabled:
            if device == 'mouse':
                if button == 'scrollup':
                    direction = -1 if App.get_running_app().invert_mouse_wheel else 1

                    if App.get_running_app().fine_mode:
                        # Use the minimum increment defined by
                        # NymphesPreset's float precision property
                        increment = float(direction) / pow(10, NymphesPreset.float_precision_num_decimals)

                    else:
                        # We are not in fine mode, so increment by 1
                        increment = int(direction)

                    # Increment the property
                    App.get_running_app().increment_prop_value_for_param_name(f'{self.param_name}.{self.mod_type}', increment)

                elif button == 'scrolldown':
                    direction = 1 if App.get_running_app().invert_mouse_wheel else -1

                    if App.get_running_app().fine_mode:
                        # Use the minimum decrement defined by
                        # NymphesPreset's float precision property
                        increment = float(direction) / pow(10, NymphesPreset.float_precision_num_decimals)

                    else:
                        # We are not in fine mode, so decrement by 1
                        increment = int(direction)

                    # Increment the property
                    App.get_running_app().increment_prop_value_for_param_name(f'{self.param_name}.{self.mod_type}', increment)

            else:
                Logger.debug(f'{self.param_name} {device} {button}')

    def on_touch_down(self, touch):
        #
        # This is called when the mouse is clicked
        #
        if not self.disabled:
            if self.collide_point(*touch.pos) and touch.button == 'left':
                touch.grab(self)

                # Store the starting y position of the touch
                self.drag_start_pos = int(touch.pos[1])

                # The mouse is pressed
                self.mouse_pressed = True

                # Inform the app that a drag has started
                App.get_running_app().set_curr_mouse_dragging_param_name(f'{self.param_name}.{self.mod_type}')

                return True
            return super(ModAmountLine, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        #
        # This is called when the mouse drags
        #
        if not self.disabled:
            if touch.grab_current == self:
                # Get the current y position
                curr_pos = int(touch.pos[1])

                # Calculate the distance from the starting drag position
                curr_drag_distance = (self.drag_start_pos - curr_pos) * -1

                # Scale the drag distance and use as the increment
                if App.get_running_app().fine_mode:
                    # Use the minimum increment defined by
                    # NymphesPreset's float precision property
                    increment = round(curr_drag_distance * 0.05, NymphesPreset.float_precision_num_decimals)

                else:
                    increment = int(round(curr_drag_distance * 0.5))

                # Increment the property's value
                App.get_running_app().increment_prop_value_for_param_name(f'{self.param_name}.{self.mod_type}', increment)

                # Reset the drag start position to the current position
                self.drag_start_pos = curr_pos

                return True

            return super(ModAmountLine, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if not self.disabled:
            if touch.grab_current == self:
                touch.ungrab(self)

                # The mouse is no longer pressed
                self.mouse_pressed = False

                # Inform the app that a drag has ended
                App.get_running_app().set_curr_mouse_dragging_param_name('')

                return True
            return super(ModAmountLine, self).on_touch_up(touch)


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
        App.get_running_app().status_bar_text = self.tooltip_text

    def on_mouse_exit(self):
        self.mouse_inside_bounds = False
        self.mouse_pressed = False
        App.get_running_app().status_bar_text = ''
        Window.set_system_cursor('arrow')

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
                Logger.info(f'on_touch_up: {self.text}')
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
        App.get_running_app().status_bar_text = self.tooltip_text

    def on_mouse_exit(self):
        self.mouse_inside_bounds = False
        self.mouse_pressed = False
        App.get_running_app().status_bar_text = ''
        Window.set_system_cursor('arrow')

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
                Logger.info(f'on_touch_up: {self.text}')
                return True

            else:
                return False

        else:
            return super().on_touch_up(touch)


class VoiceModeButton(HoverButton):
    voice_mode_name = StringProperty('')


class SectionRelativeLayout(RelativeLayout):
    corner_radius = NumericProperty(12)
    section_name = StringProperty('')


class ModAmountsBox(BoxLayout):
    screen_name = StringProperty('')
    param_name = StringProperty('')
    lfo2_prop = NumericProperty(0)
    mod_wheel_prop = NumericProperty(0)
    velocity_prop = NumericProperty(0)
    aftertouch_prop = NumericProperty(0)
    mod_amount_line_background_color_string = StringProperty('#000000FF')


class MainControlsBox(BoxLayout):
    screen_name = StringProperty('')
    corner_radius = NumericProperty(0)


class ChordsMainControlsBox(BoxLayout):
    screen_name = StringProperty('')
    corner_radius = NumericProperty(0)


class MainSettingsGrid(GridLayout):
    corner_radius = NumericProperty(0)


class SettingsSubBox(BoxLayout):
    corner_radius = NumericProperty(0)


class VoiceModeBox(BoxLayout):
    num_voice_modes = NumericProperty(6)
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')


class LegatoBox(BoxLayout):
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')


class ChordsButtonBox(BoxLayout):
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')


class FineModeBox(BoxLayout):
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')


class LeftBar(BoxLayout):
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')


class TopBar(BoxLayout):
    screen_name = StringProperty('')
    corner_radius = NumericProperty(0)


class BottomBar(BoxLayout):
    screen_name = StringProperty('')
    corner_radius = NumericProperty(0)


class SettingsTopBar(BoxLayout):
    screen_name = StringProperty('')
    corner_radius = NumericProperty(0)


class ChordsTopBar(BoxLayout):
    screen_name = StringProperty('')
    corner_radius = NumericProperty(0)


class ChordsMainControlsBox(BoxLayout):
    corner_radius = NumericProperty(0)


class ControlSectionsGrid(GridLayout):
    corner_radius = NumericProperty(0)


class ControlSection(BoxLayout):
    corner_radius = NumericProperty(0)
    screen_name = StringProperty('')


class ChordsControlSectionsGrid(GridLayout):
    corner_radius = NumericProperty(0)


class SectionTitleLabel(ButtonBehavior, Label):
    pass


class ParamsGrid(GridLayout):
    corner_radius = NumericProperty(0)


class ParamsGridCell(BoxLayout):
    corner_radius = NumericProperty(0)
    param_title = StringProperty('')
    value_prop = ObjectProperty()


class ParamNameLabel(Label):
    text_color_string = StringProperty('#ECBFEBFF')


class MidiInputPortsGrid(GridLayout):
    midi_ports = ListProperty([])

    def __init__(self, **kwargs):
        super(MidiInputPortsGrid, self).__init__(**kwargs)
        self.cols = 2
        self.bind(midi_ports=self.update_grid)

    def update_grid(self, instance, value):
        # Remove all old rows
        self.clear_widgets()

        # Create a row for each entry in midi_ports
        for port_name in self.midi_ports:
            # Add the label
            self.add_widget(MidiPortLabel(text=port_name))

            # Add a checkbox
            self.add_widget(MidiInputPortCheckBox(port_name=port_name))
            
class MidiOutputPortsGrid(GridLayout):
    midi_ports = ListProperty([])

    def __init__(self, **kwargs):
        super(MidiOutputPortsGrid, self).__init__(**kwargs)
        self.cols = 2
        self.bind(midi_ports=self.update_grid)

    def update_grid(self, instance, value):
        # Remove all old rows
        self.clear_widgets()

        # Create a row for each entry in midi_ports
        for port_name in self.midi_ports:
            # Add the label
            self.add_widget(MidiPortLabel(text=port_name))

            # Add a checkbox
            self.add_widget(MidiOutputPortCheckBox(port_name=port_name))


class MidiPortLabel(Label):
    pass


class MidiInputPortCheckBox(CheckBox):
    port_name = StringProperty('')


class MidiOutputPortCheckBox(CheckBox):
    port_name = StringProperty('')


class ModWheelValueLabel(ButtonBehavior, Label):
    screen_name = StringProperty('')
    drag_start_pos = NumericProperty(0)
    text_color_string = StringProperty('#06070FFF')
    param_name = StringProperty('mod_wheel')
    mouse_pressed = BooleanProperty(False)
    mouse_inside_bounds = BooleanProperty(False)
    tooltip_text = StringProperty('')
    base_font_size = NumericProperty(20)

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
        if App.get_running_app().curr_mouse_dragging_param_name == '':
            self.mouse_inside_bounds = True
            App.get_running_app().status_bar_text = self.tooltip_text
            Window.set_system_cursor('hand')

    def on_mouse_exit(self):
        self.mouse_inside_bounds = False
        App.get_running_app().status_bar_text = ''
        Window.set_system_cursor('arrow')

    def handle_touch(self, device, button):
        #
        # Mouse Wheel
        #
        if not self.disabled:
            if device == 'mouse':
                if button == 'scrollup':
                    increment = -1 if App.get_running_app().invert_mouse_wheel else 1

                    # Increment the property
                    App.get_running_app().increment_mod_wheel(increment)

                elif button == 'scrolldown':
                    increment = 1 if App.get_running_app().invert_mouse_wheel else -1

                    # Increment the property
                    App.get_running_app().increment_mod_wheel(increment)

            else:
                Logger.debug(f'mod_wheel {device} {button}')

    def on_touch_down(self, touch):
        #
        # This is called when the mouse is clicked
        #
        if not self.disabled:
            if self.collide_point(*touch.pos) and touch.button == 'left':
                touch.grab(self)

                # Store the starting y position of the touch
                self.drag_start_pos = int(touch.pos[1])

                # The mouse is pressed
                self.mouse_pressed = True

                # Inform the app that a drag has started
                App.get_running_app().set_curr_mouse_dragging_param_name(self.param_name)

                return True

            return super(ModWheelValueLabel, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        #
        # This is called when the mouse drags
        #
        if not self.disabled:
            if touch.grab_current == self:
                # Get the current y position
                curr_pos = int(touch.pos[1])

                # Calculate the distance from the starting drag position
                curr_drag_distance = (self.drag_start_pos - curr_pos) * -1

                # Scale the drag distance and use as the increment
                increment = int(round(curr_drag_distance * 0.2))

                # Increment the property's value
                App.get_running_app().increment_mod_wheel(increment)

                # Reset the drag start position to the current position
                self.drag_start_pos = curr_pos

                return True

            return super(ModWheelValueLabel, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if not self.disabled:
            if touch.grab_current == self:
                touch.ungrab(self)

                # Inform the app that a drag has ended
                App.get_running_app().set_curr_mouse_dragging_param_name('')

                # The mouse is no longer pressed
                self.mouse_pressed = False

                return True

            return super(ModWheelValueLabel, self).on_touch_up(touch)
        

class AftertouchValueLabel(ButtonBehavior, Label):
    screen_name = StringProperty('')
    drag_start_pos = NumericProperty(0)
    text_color_string = StringProperty('#06070FFF')
    param_name = StringProperty('aftertouch')
    mouse_pressed = BooleanProperty(False)
    mouse_inside_bounds = BooleanProperty(False)
    tooltip_text = StringProperty('')
    base_font_size = NumericProperty(20)

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
        if App.get_running_app().curr_mouse_dragging_param_name == '':
            self.mouse_inside_bounds = True
            App.get_running_app().status_bar_text = self.tooltip_text
            Window.set_system_cursor('hand')

    def on_mouse_exit(self):
        self.mouse_inside_bounds = False
        App.get_running_app().status_bar_text = ''
        Window.set_system_cursor('arrow')

    def handle_touch(self, device, button):
        #
        # Mouse Wheel
        #
        if not self.disabled:
            if device == 'mouse':
                if button == 'scrollup':
                    increment = -1 if App.get_running_app().invert_mouse_wheel else 1

                    # Increment the property
                    App.get_running_app().increment_aftertouch(increment)

                elif button == 'scrolldown':
                    increment = 1 if App.get_running_app().invert_mouse_wheel else -1

                    # Increment the property
                    App.get_running_app().increment_aftertouch(increment)

            else:
                Logger.debug(f'aftertouch {device} {button}')

    def on_touch_down(self, touch):
        #
        # This is called when the mouse is clicked
        #
        if not self.disabled:
            if self.collide_point(*touch.pos) and touch.button == 'left':
                touch.grab(self)

                # Store the starting y position of the touch
                self.drag_start_pos = int(touch.pos[1])

                # The mouse is pressed
                self.mouse_pressed = True

                # Inform the app that a drag has started
                App.get_running_app().set_curr_mouse_dragging_param_name(self.param_name)

                return True

            return super(AftertouchValueLabel, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        #
        # This is called when the mouse drags
        #
        if not self.disabled:
            if touch.grab_current == self:
                # Get the current y position
                curr_pos = int(touch.pos[1])

                # Calculate the distance from the starting drag position
                curr_drag_distance = (self.drag_start_pos - curr_pos) * -1

                # Scale the drag distance and use as the increment
                increment = int(round(curr_drag_distance * 0.2))

                # Increment the property's value
                App.get_running_app().increment_aftertouch(increment)

                # Reset the drag start position to the current position
                self.drag_start_pos = curr_pos

                return True

            return super(AftertouchValueLabel, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if not self.disabled:
            if touch.grab_current == self:
                touch.ungrab(self)

                # Inform the app that a drag has ended
                App.get_running_app().set_curr_mouse_dragging_param_name('')

                # The mouse is no longer pressed
                self.mouse_pressed = False

                return True

            return super(AftertouchValueLabel, self).on_touch_up(touch)


class ChordParamsGrid(GridLayout):
    corner_radius = NumericProperty(0)


class ChordParamsGridCell(ButtonBehavior, BoxLayout):
    screen_name = StringProperty('')
    section_name = StringProperty('')
    title = StringProperty('')
    param_name = StringProperty('')
    value_prop = NumericProperty(0)
    corner_radius = NumericProperty(0)
    value_color_string = StringProperty('#06070FFF')
    background_color_string = StringProperty('#438EFFFF')
    
    

class ChordSectionTitleLabel(HoverButton):
    this_chord_active = BooleanProperty(False)


class ErrorDialog(BoxLayout):
    ok = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(ErrorDialog, self).__init__(**kwargs)
        self._keyboard = None

    def _keyboard_closed(self):
        Logger.debug('ErrorDialog Keyboard Closed')
        if self._keyboard is not None:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard.unbind(on_key_up=self._on_key_up)
            self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        Logger.debug(f'ErrorDialog on_key_down: {keyboard}, {keycode}, {text}, {modifiers}')

    def _on_key_up(self, keyboard, keycode):
        Logger.debug(f'ErrorDialog on_key_up: {keyboard}, {keycode}')

        # Handle Enter and Escape keys
        # This is the same as clicking the OK button
        enter_keycode = 13
        numpad_enter_keycode = 271
        escape_keycode = 27
        if keycode[0] in [escape_keycode, enter_keycode, numpad_enter_keycode]:
            App.get_running_app()._dismiss_popup()
    