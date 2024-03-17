import logging
from pathlib import Path
import os

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
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.osc_message_builder import OscMessageBuilder
import threading
import configparser

import netifaces
# import logging
# from logging.handlers import RotatingFileHandler
from kivy.logger import Logger, LOG_LEVELS
Logger.setLevel(LOG_LEVELS["debug"])
from nymphes_midi.NymphesPreset import NymphesPreset
import platform
from .nymphes_osc_process import NymphesOscProcess


kivy.require('2.1.0')

app_version_string = 'v0.1.4-beta_dev'

def presets_spinner_values_list():
    """
    Returns a list of text values for the presets spinner to show.
    """
    values = ['init']
    values.extend([f'{kind} {bank}{num}' for kind in ['USER', 'FACTORY'] for bank in ['A', 'B', 'C', 'D', 'E', 'F', 'G']
                   for num in [1, 2, 3, 4, 5, 6, 7]])
    return values


class BlueAndPinkSynthEditorApp(App):
    #
    # App Status Parameters
    #

    nymphes_connected = BooleanProperty(False)
    nymphes_midi_channel = NumericProperty(1)
    mod_wheel = NumericProperty(0)
    velocity = NumericProperty(0)
    aftertouch = NumericProperty(0)

    detected_midi_input_names_for_gui = ListProperty([])
    detected_midi_output_names_for_gui = ListProperty([])

    connected_midi_input_names_for_gui = ListProperty([])
    connected_midi_output_names_for_gui = ListProperty([])

    nymphes_input_spinner_names = ListProperty(['Not Connected'])
    nymphes_output_spinner_names = ListProperty(['Not Connected'])

    nymphes_input_name = StringProperty('Not Connected')
    nymphes_output_name = StringProperty('Not Connected')

    presets_spinner_text = StringProperty('PRESET')
    presets_spinner_values = ListProperty(presets_spinner_values_list())

    # This is used to track what is currently loaded.
    # Valid values: 'init', 'file', 'preset_slot'
    curr_preset_type = StringProperty('')

    selected_section = StringProperty('')
    detected_midi_input_names_for_gui = ListProperty([])
    midi_inputs_spinner_curr_value = StringProperty('Not Connected')
    
    detected_midi_output_names_for_gui = ListProperty([])
    midi_outputs_spinner_curr_value = StringProperty('Not Connected')

    status_bar_text = StringProperty('NYMPHES NOT CONNECTED')

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

    osc_voice_mode_value = NumericProperty(0.0)
    osc_legato_value = NumericProperty(0.0)

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

    chord_8_root_value = NumericProperty(0)
    chord_8_semi_1_value = NumericProperty(0)
    chord_8_semi_2_value = NumericProperty(0)
    chord_8_semi_3_value = NumericProperty(0)
    chord_8_semi_4_value = NumericProperty(0)
    chord_8_semi_5_value = NumericProperty(0)

    voice_mode_name = StringProperty('POLY')
    legato = BooleanProperty(False)
    mod_source = NumericProperty(0)
    main_level = DictProperty({'value': 0})

    #
    # Preset File Handling
    #

    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)

    # If True then increment float value parameters using
    # float values.
    float_mode = BooleanProperty(False)

    invert_mouse_wheel = BooleanProperty(True)

    curr_width = NumericProperty(800)
    curr_height = NumericProperty(480)

    def __init__(self, **kwargs):
        super(BlueAndPinkSynthEditorApp, self).__init__(**kwargs)

        # Set the app title
        self.title = f'Blue and Pink Synth Editor {app_version_string}'

        # Bind keyboard events
        self._bind_keyboard_events()

        # Keep track of currently held modifier keys
        self._shift_key_pressed = False
        self._caps_lock_key_on = False
        self._meta_key_pressed = False
        self._alt_key_pressed = False

        # Choose the float mode modifier key based on the
        # current operating system
        os_name = platform.system()
        Logger.info(f'Operating system is {os_name}')

        if os_name == 'Windows':
            self.float_mode_modifier_key = 'shift'
        elif os_name == 'Darwin':
            self.float_mode_modifier_key = 'meta'
        elif os_name == 'Linux':
            self.float_mode_modifier_key = 'shift'
        else:
            self.float_mode_modifier_key = 'shift'

        # Get notified when the window resizes so we can maintain
        # aspect ratio
        self.aspect_ratio = 800 / 480
        Window.bind(on_resize=self._on_window_resize)
        self._just_resized_window = False

        #
        # Encoder Properties
        #
        self._connected_to_encoders = False

        self._encoder_osc_incoming_host = None
        self._encoder_osc_incoming_port = None
        self._encoder_osc_outgoing_host = None
        self._encoder_osc_outgoing_port = None

        self._encoder_osc_client = None
        self._encoder_osc_server = None
        self._encoder_osc_server_thread = None
        self._encoder_osc_dispatcher = Dispatcher()

        #
        # nymphes-osc properties
        #
        self._nymphes_osc_child_process = None

        self._nymphes_osc_incoming_host = None
        self._nymphes_osc_incoming_port = None
        self._nymphes_osc_outgoing_host = None
        self._nymphes_osc_outgoing_port = None

        self._nymphes_osc_client = None
        self._nymphes_osc_server = None
        self._nymphes_osc_server_thread = None
        self._nymphes_osc_dispatcher = Dispatcher()

        self._connected_to_nymphes_osc = False

        #
        # Nymphes Synthesizer State
        #

        # The MIDI channel used when communicating with Nymphes.
        # This is non-zero-referenced, so 1 is channel 1.
        self._nymphes_midi_channel = 1

        self._sustain_pedal = 0
        self._legato = False

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

        # TODO: Remove this
        # Once a preset has been loaded, this will be
        # either 'user' or 'factory'
        self._curr_preset_slot_type = None

        # TODO: Remove this
        # Once a preset has been loaded, this will contain
        # the bank name ('A' to 'G') and preset number (1 to 7)
        self._curr_preset_slot_bank_and_number = (None, None)

        # Used for Presets Spinner
        self._curr_presets_spinner_index = 0

        #
        # Preset File Handling
        #
        self._popup = None

        #
        # Prep data folder and get Configuration From config.txt
        #

        # Set path to data folder
        self._data_folder_path = Path(os.path.expanduser('~')) / 'BlueAndPinkSynthEditor_data/'

        # Make sure it exists
        if not self._data_folder_path.exists():
            try:
                self._data_folder_path.mkdir()
                Logger.info(f'Created data folder at {self._data_folder_path}')

            except Exception as e:
                Logger.critical(f'Failed to create data folder at {self._data_folder_path} ({e})')

        # Path for presets folder
        self._presets_directory_path = self._data_folder_path / 'presets'
        if not self._presets_directory_path.exists():
            try:
                self._presets_directory_path.mkdir()
                Logger.info(f'Created presets folder at {self._presets_directory_path}')

            except Exception as e:
                Logger.critical(f'Failed to create presets folder at {self._presets_directory_path} ({e})')

        # Path to config file
        self._config_file_path = self._data_folder_path / 'config.txt'

        # Create a config file if one doesn't exist
        if not Path(self._config_file_path).exists():
            self._create_config_file(self._config_file_path)

        # Load contents of config file
        self._load_config_file(self._config_file_path)

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

        self._nymphes_osc_client = SimpleUDPClient(self._nymphes_osc_outgoing_host, self._nymphes_osc_outgoing_port)
        self._start_nymphes_osc_server()

        try:
            self._encoder_osc_client = SimpleUDPClient(self._encoder_osc_outgoing_host, self._encoder_osc_outgoing_port)
        except Exception as e:
            Logger.warning(f'Failed to create Encoders OSC client ({e})')

        self._start_encoder_osc_server()

        #
        # Map Incoming OSC Messages
        #
        self._nymphes_osc_dispatcher.map('*', self._on_nymphes_osc_message)
        self._encoder_osc_dispatcher.map('*', self._on_encoder_osc_message)

        #
        # Register as client with Encoders device
        #
        self._register_as_encoders_osc_client()

        # Select the oscillator section at the start
        #self.select_section('oscillator_top_row')

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
        self.set_status_bar_text_on_main_thread(f'osc.voice_mode.value: {voice_mode_int}')

        # Send the command to the Nymphes
        self._send_nymphes_osc('/osc/voice_mode/value', voice_mode_int)

    def set_legato(self, enable_legato):
        """
        enable_legato should be a bool
        """

        # Update the property
        self.legato = enable_legato

        # Status bar text
        self.set_status_bar_text_on_main_thread(f'osc.legato.value: {1 if enable_legato else 0}')

        # Send the command to the Nymphes
        self._send_nymphes_osc('/osc/legato/value', 1 if enable_legato else 0)

    def set_float_mode(self, enable_float_mode):
        # Update the property
        self.float_mode = enable_float_mode

    def _load_config_file(self, filepath):
        """
        Load the contents of the specified config txt file.
        :param filepath: str or Path
        :return:
        """
        config = configparser.ConfigParser()
        config.read(filepath)

        #
        # Nymphes OSC Communication
        #

        self._nymphes_osc_outgoing_host = config['NYMPHES_OSC']['outgoing host']
        self._nymphes_osc_outgoing_port = int(config['NYMPHES_OSC']['outgoing port'])

        if config.has_option('NYMPHES_OSC', 'incoming host'):
            #
            # Incoming hostname has been specified in config.txt
            #

            self._nymphes_osc_incoming_host = config['NYMPHES_OSC']['incoming host']
            Logger.info(f'Using incoming host from config file for Nymphes OSC communication: {self._nymphes_osc_incoming_host}')

        else:
            #
            # Incoming host is not specified.
            # Try to automatically determine the local ip address
            #

            in_host = self._get_local_ip_address()
            self._nymphes_osc_incoming_host = in_host
            Logger.info(f'Using detected local ip address for NYMPHES_OSC communication: {in_host}')

        self._nymphes_osc_incoming_port = int(config['NYMPHES_OSC']['incoming port'])

        #
        # Encoder OSC Communication
        #

        self._encoder_osc_outgoing_host = config['ENCODER_OSC']['outgoing host']
        self._encoder_osc_outgoing_port = int(config['ENCODER_OSC']['outgoing port'])

        if config.has_option('ENCODER_OSC', 'incoming host'):
            #
            # Incoming hostname has been specified in config.txt
            #

            self._encoder_osc_incoming_host = config['ENCODER_OSC']['incoming host']
            Logger.info(f'Using incoming host from config file for Encoder OSC communication: {self._encoder_osc_incoming_host}')

        else:
            #
            # Incoming host is not specified.
            # Try to automatically determine the local ip address
            #

            in_host = self._get_local_ip_address()
            self._encoder_osc_incoming_host = in_host
            Logger.info(f'Using detected local ip address for Encoder OSC communication: {in_host}')

        self._encoder_osc_incoming_port = int(config['ENCODER_OSC']['incoming port'])

    def _reload_config_file(self):
        Logger.info(f'Reloading config file at {self._config_file_path}')
        self._load_config_file(self._config_file_path)

    def _create_config_file(self, filepath):
        config = configparser.ConfigParser()

        # OSC Communication with Nymphes-OSC App
        config['NYMPHES_OSC'] = {
            'outgoing host': '127.0.0.1',
            'outgoing port': '1236',
            'incoming host': '127.0.0.1',
            'incoming port': '1237'}

        # OSC Communication with Encoder App
        config['ENCODER_OSC'] = {
            'outgoing host': 'nymphes-encoders-0001',
            'outgoing port': '5000',
            'incoming port': '5001'}

        # Write to a new config file
        try:
            with open(filepath, 'w') as config_file:
                config.write(config_file)

            Logger.info(f'Created config file at {filepath}')

        except Exception as e:
            Logger.critical(f'Failed to create config file at {filepath} ({e})')

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

    def _start_nymphes_osc_server(self):
        """
        Start an OSC server on a background thread for communication
        with nymphes-osc
        :return:
        """
        self._nymphes_osc_server = BlockingOSCUDPServer(
            (self._nymphes_osc_incoming_host, self._nymphes_osc_incoming_port),
            self._nymphes_osc_dispatcher
        )
        self._nymphes_osc_server_thread = threading.Thread(target=self._nymphes_osc_server.serve_forever)
        self._nymphes_osc_server_thread.start()

        Logger.info(f'Started OSC Server: Listening for nymphes-osc at {self._nymphes_osc_incoming_host}:{self._nymphes_osc_incoming_port}')

    def _stop_nymphes_osc_server(self):
        """
        Shut down the OSC server used for communication with nymphes-osc
        :return:
        """
        if self._nymphes_osc_server is not None:
            self._nymphes_osc_server.shutdown()
            self._nymphes_osc_server.server_close()
            self._nymphes_osc_server = None
            self._nymphes_osc_server_thread.join()
            self._nymphes_osc_server_thread = None
            Logger.info('Stopped OSC Server: No longer listening for nymphes-osc')

    def _start_encoder_osc_server(self):
        """
        Start an OSC server on a background thread for communication
        with the Encoders device
        :return:
        """
        self._encoder_osc_server = BlockingOSCUDPServer(
            (self._encoder_osc_incoming_host, self._encoder_osc_incoming_port),
            self._encoder_osc_dispatcher
        )
        self._encoder_osc_server_thread = threading.Thread(target=self._encoder_osc_server.serve_forever)
        self._encoder_osc_server_thread.start()

        Logger.info(f'Started OSC Server: Listening for encoders at {self._encoder_osc_incoming_host}:{self._encoder_osc_incoming_port}')

    def _stop_encoder_osc_server(self):
        """
        Shut down the OSC server used for communication with the Encoders device
        :return:
        """
        if self._encoder_osc_server is not None:
            self._encoder_osc_server.shutdown()
            self._encoder_osc_server.server_close()
            self._encoder_osc_server = None
            self._encoder_osc_server_thread.join()
            self._encoder_osc_server_thread = None
            Logger.info('Stopped OSC Server: No longer listening for encoders')

    def _register_as_nymphes_osc_client(self):
        """
        Register as a client with nymphes-osc by sending it a
        /register_client OSC message
        :return:
        """

        # To connect to the nymphes_osc server, we need
        # to send it a /register_host OSC message
        # with the port we are listening on.
        Logger.info(f'Registering as client with nymphes-osc server at {self._nymphes_osc_outgoing_host}:{self._nymphes_osc_outgoing_port}...')
        self._send_nymphes_osc('/register_client', self._nymphes_osc_incoming_port)

    def _register_as_encoders_osc_client(self):
        """
        Register as a client with the Encoders device by sending it a
        /register_client OSC message
        :return:
        """
        if self._encoder_osc_client is not None:
            Logger.info(f'Registering as client with Encoders server at {self._encoder_osc_outgoing_host}:{self._encoder_osc_outgoing_port}...')
            self._send_encoder_osc('/register_client', self._encoder_osc_incoming_port)

    def _send_nymphes_osc(self, address, *args):
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
        self._nymphes_osc_client.send(msg)

        Logger.debug(f'send_nymphes_osc: {address}, {[str(arg) for arg in args]}')

    def _send_encoder_osc(self, address, *args):
        """
        Send an OSC message to the Encoders device
        :param address: The osc address including the forward slash ie: /register_host
        :param args: A variable number arguments. Types will be automatically detected
        :return:
        """
        if self._encoder_osc_client is not None:
            msg = OscMessageBuilder(address=address)
            for arg in args:
                msg.add_arg(arg)
            msg = msg.build()
            self._encoder_osc_client.send(msg)

            Logger.debug(f'send_encoder_osc: {address}, {[str(arg) + " " for arg in args]}')

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

            Logger.info(f'{address}: {host_name}:{port}')

            # We are connected to nymphes_osc
            self._connected_to_nymphes_osc = True

        elif address == '/client_unregistered':
            # Get the hostname and port
            #
            host_name = str(args[0])
            port = int(args[1])

            Logger.info(f'{address}: {host_name}:{port}')

            # We are no longer connected to nymphes-osc
            self._connected_to_nymphes_osc = False

        elif address == '/presets_directory_path':
            # Get the path
            path = Path(args[0])

            Logger.info(f'{address}: {path}')

            # Store it
            self._presets_directory_path = str(path)

        elif address == '/nymphes_midi_input_detected':
            #
            # A Nymphes MIDI input port has been detected
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'{address}: {port_name}')

            # Add it to our list of detected Nymphes MIDI input ports
            if port_name not in self._detected_nymphes_midi_inputs:
                self._detected_nymphes_midi_inputs.append(port_name)
                self.add_name_to_nymphes_input_spinner_on_main_thread(port_name)

            # Try automatically connecting to the first Nymphes if we
            # now have both an input and output port
            if not self.nymphes_connected:
                if len(self._detected_nymphes_midi_inputs) > 0 and len(self._detected_nymphes_midi_outputs) > 0:
                    Logger.info('Attempting to automatically connect to the first detected Nymphes')
                    self._send_nymphes_osc(
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

            Logger.info(f'{address}: {port_name}')

            # Remove it from our list of detected Nymphes MIDI input ports
            if port_name in self._detected_nymphes_midi_inputs:
                self._detected_nymphes_midi_inputs.remove(port_name)
                self.remove_name_from_nymphes_input_spinner_on_main_thread(port_name)
            
        elif address == '/nymphes_midi_output_detected':
            #
            # A Nymphes MIDI output port has been detected
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'{address}: {port_name}')

            # Add it to our list of detected Nymphes MIDI output ports
            if port_name not in self._detected_nymphes_midi_outputs:
                self._detected_nymphes_midi_outputs.append(port_name)
                self.add_name_to_nymphes_output_spinner_on_main_thread(port_name)

            # Try automatically connecting to the first Nymphes if we
            # now have both an input and output port
            if not self.nymphes_connected:
                if len(self._detected_nymphes_midi_inputs) > 0 and len(self._detected_nymphes_midi_outputs) > 0:
                    Logger.info('Attempting to automatically connect to the first detected Nymphes')
                    self._send_nymphes_osc(
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

            Logger.info(f'{address}: {port_name}')

            # Remove it from our list of detected Nymphes MIDI output ports
            if port_name in self._detected_nymphes_midi_outputs:
                self._detected_nymphes_midi_outputs.remove(port_name)
                self.remove_name_from_nymphes_output_spinner_on_main_thread(port_name)

        elif address == '/nymphes_connected':
            #
            # nymphes_midi has connected to a Nymphes synthesizer
            #
            input_port = str(args[0])
            output_port = str(args[1])

            Logger.info(f'{address}: input_port: {input_port}, output_port: {output_port}')

            # Get the names of the MIDI input and output ports
            self._nymphes_input_port = input_port
            self._nymphes_output_port = output_port
            
            self.set_nymphes_input_name_on_main_thread(input_port)
            self.set_nymphes_output_name_on_main_thread(output_port)

            # Update app state
            self.nymphes_connected = True

            # Status message
            self.set_status_bar_text_on_main_thread('NYMPHES CONNECTED')

        elif address == '/nymphes_disconnected':
            #
            # nymphes_midi is no longer connected to a Nymphes synthesizer
            #

            Logger.info(f'{address}')

            # Update app state
            self.nymphes_connected = False
            self._nymphes_input_port = None
            self._nymphes_output_port = None

            # Status message
            self.set_status_bar_text_on_main_thread('NYMPHES NOT CONNECTED')

            self.set_nymphes_input_name_on_main_thread('Not Connected')
            self.set_nymphes_output_name_on_main_thread('Not Connected')

        elif address == '/loaded_preset':
            #
            # The Nymphes synthesizer has just loaded a preset
            #
            preset_slot_type = str(args[0])
            preset_slot_bank_and_number = str(args[1]), int(args[2])

            Logger.info(f'{address}: {preset_slot_type} {preset_slot_bank_and_number[0]}{preset_slot_bank_and_number[1]}')

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
            self.set_status_bar_text_on_main_thread(f'LOADED {preset_slot_type.upper()} PRESET {preset_slot_bank_and_number[0]}{preset_slot_bank_and_number[1]}')

        elif address == '/loaded_preset_dump_from_midi_input_port':
            port_name = str(args[0])
            preset_slot_type = str(args[0])
            preset_slot_bank_and_number = str(args[1]), int(args[2])

            Logger.info(f'{address}: {port_name}: {preset_slot_type} {preset_slot_bank_and_number[0]}{preset_slot_bank_and_number[1]}')

            self._curr_preset_slot_type = preset_slot_type
            self._curr_preset_slot_bank_and_number = preset_slot_bank_and_number

            # Status bar message
            msg = f'LOADED PRESET DUMP {preset_slot_type.upper()} {preset_slot_bank_and_number[0]}{preset_slot_bank_and_number[1]} FROM MIDI INPUT PORT {port_name}'
            self.set_status_bar_text_on_main_thread(msg)

        elif address == '/loaded_file':
            #
            # A preset file was loaded
            #
            filepath = Path(args[0])

            Logger.info(f'{address}: {filepath}')

            # Update the current preset type
            self.curr_preset_type = 'file'

            # Store the path to the file
            self._curr_preset_file_path = filepath

            # Reset current preset slot info
            self._curr_preset_slot_type = None
            self._curr_preset_slot_bank_and_number = None

            # Update the presets spinner.
            # This also sets the spinner's current text
            # and updates self._curr_presets_spinner_index.
            self._set_presets_spinner_file_option_on_main_thread(self._curr_preset_file_path.stem)

            # Status bar message
            msg = f'LOADED {filepath.stem} PRESET FILE '
            self.set_status_bar_text_on_main_thread(msg)

        elif address == '/loaded_init_file':
            #
            # The init preset file was loaded
            #

            Logger.info(f'{address}: {str(args[0])}')

            # Update the current preset type
            self.curr_preset_type = 'init'

            # Reset current preset slot info
            self._curr_preset_slot_type = None
            self._curr_preset_slot_bank_and_number = None

            # Update the presets spinner
            # Select the init option
            self.presets_spinner_text = 'init'
            self._curr_presets_spinner_index = 0 if len(self.presets_spinner_values) == 99 else 1

            # Status bar message
            msg = f'LOADED INIT PRESET'
            self.set_status_bar_text_on_main_thread(msg)

        elif address == '/saved_to_file':
            #
            # The current settings have been saved to a preset file
            #
            filepath = Path(args[0])

            Logger.info(f'{address}: {filepath}')

            # Update the current preset type
            self.curr_preset_type = 'file'

            # Store the path to the file
            self._curr_preset_file_path = filepath

            # Reset current preset slot info
            self._curr_preset_slot_type = None
            self._curr_preset_slot_bank_and_number = None

            # Update the presets spinner.
            # This also sets the spinner's current text
            # and updates self._curr_presets_spinner_index.
            self._set_presets_spinner_file_option_on_main_thread(self._curr_preset_file_path.stem)

            # Status bar message
            msg = f'SAVED {filepath.stem} PRESET FILE'
            self.set_status_bar_text_on_main_thread(msg)

        elif address == '/saved_preset_to_file':
            #
            # A Nymphes preset slot has been saved to a file
            #

            # Get the preset info
            filepath = str(args[0])
            preset_type = str(args[1])
            bank_name = str(args[2])
            preset_number = int(args[3])

            Logger.info(f'{address}: {filepath} {preset_type} {bank_name}{preset_number}')

            # Status bar message
            msg = f'SAVED PRESET {preset_type.upper()} {bank_name}{preset_number} TO FILE {filepath.stem}'
            self.set_status_bar_text_on_main_thread(msg)

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

            Logger.info(f'{address}: {filepath} {preset_type} {bank_name}{preset_number}')

            # Status bar message
            msg = f'LOADED PRESET FILE {filepath.stem} TO SLOT {preset_type.upper()} {bank_name}{preset_number}'
            self.set_status_bar_text_on_main_thread(msg)

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

            Logger.info(f'{address}: {preset_type} {bank_name}{preset_number}')

            # Status bar message
            msg = f'SAVED TO PRESET SLOT {preset_type.upper()} {bank_name}{preset_number}'
            self.set_status_bar_text_on_main_thread(msg)

        elif address == '/requested_preset_dump':
            #
            # A full preset dump has been requested
            #
            Logger.info(f'{address}:')

            # Status bar message
            msg = f'REQUESTED PRESET DUMP...'
            self.set_status_bar_text_on_main_thread(msg)

        elif address == '/received_preset_dump_from_nymphes':
            #
            # A single preset has been received from Nymphes
            # as a persistent import type SYSEX message
            #

            # Get the preset info
            preset_type = str(args[0])
            bank_name = str(args[1])
            preset_number = int(args[2])

            Logger.info(f'{address}: {preset_type} {bank_name}{preset_number}')

            # Status bar message
            msg = f'RECEIVED {preset_type.upper()} {bank_name}{preset_number} PRESET SYSEX DUMP'
            self.set_status_bar_text_on_main_thread(msg)

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

            Logger.info(f'{address}: {port_name} {preset_type} {bank_name}{preset_number}')

            # Status bar message
            msg = f'SAVED PRESET DUMP FROM MIDI INPUT {port_name} TO SLOT {preset_type.upper()} {bank_name}{preset_number}'
            self.set_status_bar_text_on_main_thread(msg)

        elif address == '/midi_input_detected':
            #
            # A MIDI input port has been detected
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'{address}: {port_name}')

            # Add it to our list of detected MIDI input ports
            if port_name not in self._detected_midi_inputs:
                self._detected_midi_inputs.append(port_name)
                self.add_midi_input_name_on_main_thread(port_name)
                self.add_name_to_nymphes_input_spinner_on_main_thread(port_name)

        elif address == '/midi_input_no_longer_detected':
            #
            # A previously-detected MIDI input port is no longer found
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'{address}: {port_name}')

            # Remove it from our list of detected MIDI input ports
            if port_name in self._detected_midi_inputs:
                self._detected_midi_inputs.remove(port_name)
                self.remove_midi_input_name_on_main_thread(port_name)
                self.remove_name_from_nymphes_input_spinner_on_main_thread(port_name)

        elif address == '/midi_input_connected':
            #
            # A MIDI input port has been connected
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'{address}: {port_name}')

            # Add it to our list of connected MIDI input ports
            if port_name not in self._connected_midi_inputs:
                self._connected_midi_inputs.append(port_name)
                self.add_connected_midi_input_name_on_main_thread(port_name)

        elif address == '/midi_input_disconnected':
            #
            # A previously-connected MIDI input port has been disconnected
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'{address}: {port_name}')

            # Remove it from our list of connected MIDI input ports
            if port_name in self._connected_midi_inputs:
                self._connected_midi_inputs.remove(port_name)
                self.remove_connected_midi_input_name_on_main_thread(port_name)

        elif address == '/midi_output_detected':
            #
            # A MIDI output port has been detected
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'{address}: {port_name}')

            # Add it to our list of detected MIDI output ports
            if port_name not in self._detected_midi_outputs:
                self._detected_midi_outputs.append(port_name)
                self.add_midi_output_name_on_main_thread(port_name)
                self.add_name_to_nymphes_output_spinner_on_main_thread(port_name)

        elif address == '/midi_output_no_longer_detected':
            #
            # A previously-detected MIDI output port is no longer found
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'{address}: {port_name}')

            # Remove it from our list of detected MIDI output ports
            if port_name in self._detected_midi_outputs:
                self._detected_midi_outputs.remove(port_name)
                self.remove_midi_output_name_on_main_thread(port_name)
                self.remove_name_from_nymphes_output_spinner_on_main_thread(port_name)

        elif address == '/midi_output_connected':
            #
            # A MIDI output port has been connected
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'{address}: {port_name}')

            # Add it to our list of connected MIDI output ports
            if port_name not in self._connected_midi_outputs:
                self._connected_midi_outputs.append(port_name)
                self.add_connected_midi_output_name_on_main_thread(port_name)

        elif address == '/midi_output_disconnected':
            #
            # A previously-connected MIDI output port has been disconnected
            #

            # Get the name of the port
            port_name = str(args[0])

            Logger.info(f'{address}: {port_name}')

            # Remove it from our list of connected MIDI output ports
            if port_name in self._connected_midi_outputs:
                self._connected_midi_outputs.remove(port_name)
                self.remove_connected_midi_output_name_on_main_thread(port_name)

        elif address == '/mod_wheel':
            val = int(args[0])
            Logger.debug(f'{address}: {val}')

            self.set_mod_wheel_on_main_thread(val)

        elif address == '/velocity':
            val = int(args[0])
            Logger.debug(f'{address}: {val}')

            self.set_velocity_on_main_thread(val)

        elif address == '/aftertouch':
            val = int(args[0])
            Logger.debug(f'{address}: {val}')

            self.set_aftertouch_on_main_thread(val)

        elif address == '/sustain_pedal':
            val = int(args[0])
            Logger.debug(f'{address}: {val}')

            self._sustain_pedal = val

        elif address == '/nymphes_midi_channel_changed':
            midi_channel = int(args[0])
            Logger.debug(f'{address}: {midi_channel}')

            self._nymphes_midi_channel = midi_channel

        elif address == '/status':
            Logger.info(f'{address}: {args[0]}')

        elif address == '/legato':
            val = bool(args[0])
            Logger.debug(f'{address}: {val}')

            self._legato = val

        elif address == '/osc/voice_mode/value':
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
            self.voice_mode_name = voice_mode_name

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

                Logger.debug(f'Received param name {param_name}: {args[0]}')

                # Set our property for this parameter
                setattr(self, param_name.replace('.', '_'), value)

            else:
                # This is an unrecognized OSC message
                Logger.warning(f'Received unhandled OSC message: {address}')

    def _on_encoder_osc_message(self, address, *args):
        """
        An OSC message has been received from the Encoders device
        :param address: str
        :param args: A list of arguments
        :return:
        """
        Logger.debug(f'Received OSC Message from Encoders device: {address}, {[str(arg) + " " for arg in args]}')

        # App Status Messages
        #
        if address == '/client_registered':
            # Get the hostname and port
            #
            host_name = str(args[0])
            port = int(args[1])

            # We are connected to the Encoder device
            self._connected_to_encoders = True

            Logger.info(f'{address}: {host_name}:{port}')

        elif address == '/client_unregistered':
            # Get the hostname and port
            #
            host_name = str(args[0])
            port = int(args[1])

            # We are no longer connected to the Encoders device
            self._connected_to_encoders = False

            Logger.info(f'{address}: {host_name}:{port}')

    def _start_nymphes_osc_child_process(self):
        """
        Start the nymphes_osc child process, which handles all
        communication with the Nymphes synthesizer and with
        which we communicate with via OSC.
        :return:
        """
        try:
            Logger.info('Starting nymphes-osc child process...')
            self._nymphes_osc_child_process = NymphesOscProcess(
                server_host=self._nymphes_osc_outgoing_host,
                server_port=self._nymphes_osc_outgoing_port,
                client_host=self._nymphes_osc_incoming_host,
                client_port=self._nymphes_osc_incoming_port,
                nymphes_midi_channel=self._nymphes_midi_channel,
                osc_log_level=logging.WARNING,
                midi_log_level=logging.WARNING,
                presets_directory_path=self._presets_directory_path
            )

            self._nymphes_osc_child_process.start()


            #
            #
            # arguments = [
            #     '--server_host', self._nymphes_osc_outgoing_host,
            #     '--server_port', str(self._nymphes_osc_outgoing_port),
            #     '--client_host', self._nymphes_osc_incoming_host,
            #     '--client_port', str(self._nymphes_osc_incoming_port),
            #     '--midi_channel', str(self._nymphes_midi_channel),
            #     '--osc_log_level', 'info',
            #     '--midi_log_level', 'info',
            #     '--presets_directory_path', self._presets_directory_path
            # ]
            # nymphes_osc_path = str(Path(__file__).resolve().parent.parent.parent / 'nymphes-osc')
            # command = [nymphes_osc_path] + arguments
            # self._nymphes_osc_child_process = subprocess.Popen(
            #     command,
            #     text=True
            # )

            Logger.info('Started the nymphes_osc child process')

        except Exception as e:
            Logger.critical(f'Failed to start the nymphes_osc child process ({e})')

    def _stop_nymphes_osc_child_process(self):
        """
        Stop the nymphes_osc child process if it is running
        :return:
        """
        Logger.info('Stopping the nymphes_osc child process...')
        if self._nymphes_osc_child_process is not None:
            self._nymphes_osc_child_process.kill()
            self._nymphes_osc_child_process.join()
            self._nymphes_osc_child_process = None

    def on_stop(self):
        """
        The app is about to close.
        :return:
        """
        Logger.info('on_stop')

        # Stop the OSC servers
        self._stop_nymphes_osc_server()
        self._stop_encoder_osc_server()

        # Stop the nymphes_osc child process
        self._stop_nymphes_osc_child_process()

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

    #
    # Nymphes Internal Memory Preset Handling
    #

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
        self._send_nymphes_osc(
            '/load_preset',
            preset_type,
            bank_name,
            preset_num
        )

    #
    # Preset File Handling
    #

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load_dialog(self):
        content = LoadDialog(load=self.on_file_load_dialog, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.bind(on_open=self._on_popup_open)
        self._popup.bind(on_dismiss=self._on_popup_dismiss)
        self._popup.open()

    def show_save_dialog(self):
        content = SaveDialog(
            save=self.on_file_save_dialog,
            cancel=self.dismiss_popup,
            default_filename=self._curr_preset_file_path.stem if self._curr_preset_file_path is not None else ''
        )
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.bind(on_open=self._on_popup_open)
        self._popup.bind(on_dismiss=self._on_popup_dismiss)
        self._popup.open()

    def on_file_load_dialog(self, path=None, filepaths=[]):
        # Close the file load dialog
        self.dismiss_popup()

        # Re-bind keyboard events
        self._bind_keyboard_events()

        if len(filepaths) > 0:
            Logger.debug(f'load path: {path}, filename: {filepaths}')

            # Send message to nymphes controller to load the preset file
            self._send_nymphes_osc('/load_file', filepaths[0])

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
            self._send_nymphes_osc('/save_to_file', filepath)

    def presets_spinner_text_changed(self, spinner_index, spinner_text):
        Logger.debug(f'presets_spinner_text_changed: {spinner_index}, {spinner_text}')
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
                    self._send_nymphes_osc('/load_init_file')

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
                    self._send_nymphes_osc('/load_file', str(self._curr_preset_file_path))

                elif spinner_index == 1:
                    # Load the init preset file
                    self._send_nymphes_osc('/load_init_file')

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
                self._send_nymphes_osc('/load_init_file')

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

            if self._curr_presets_spinner_index + 1 >= len(presets_spinner_values_list()):
                # Wrap around to the beginning of the list
                self._curr_presets_spinner_index = 0

                # Reload the most recent preset file
                self._send_nymphes_osc('/load_file', str(self._curr_preset_file_path))

            elif self._curr_presets_spinner_index + 1 == 1:
                # Load the init preset file
                self._curr_presets_spinner_index = 1
                self._send_nymphes_osc('/load_init_file')

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
                self._send_nymphes_osc('/load_init_file')

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
                self._send_nymphes_osc('/load_init_file')

            elif self._curr_presets_spinner_index - 1 == 0:
                # Reload the most recent preset file
                self._curr_presets_spinner_index = 0
                self._send_nymphes_osc('/load_file', str(self._curr_preset_file_path))

            elif self._curr_presets_spinner_index - 1 < 0:
                # Wrap around to the end of the list
                self._curr_presets_spinner_index = 99
                self.load_preset_by_index(self._curr_presets_spinner_index - 2)

            else:
                # Load the previous preset
                self._curr_presets_spinner_index = self._curr_presets_spinner_index - 1
                self.load_preset_by_index(self._curr_presets_spinner_index - 2)

    def on_encoder_osc_message(self, address, *args):
        """
        An OSC message has been received from the encoders.
        :param address: str
        :param args: A list of arguments
        :return:
        """
        if address == '/client_registered':
            # We have just successfully registered as the encoders'
            # client.
            self._connected_to_encoders = True
            Logger.info("Connected to Encoders")

        elif address == '/client_removed':
            # We are no longer the encoders' client
            self._connected_to_encoders = False
            Logger.info("Disconnected from Encoders")

        elif address == '/encoder_pos':
            # An encoder's position has been sent
            num = args[0]
            val = args[1]

            self.on_encoder_pos(num, val)

        elif address == '/encoder_button_short_press_ended':
            num = args[0]
            self.on_encoder_button_short_press_ended(num)

        elif address == '/encoder_button_long_press_started':
            num = args[0]
            self.on_encoder_button_long_press_started(num)

        elif address == '/encoder_button_released':
            pass

        else:
            Logger.warning(f'Received unrecognized OSC Message: {address}')

    def select_section(self, section_name):
        if section_name == 'oscillator_top_row':
            self.encoder_display_names = [
                'PW',
                'GLIDE',
                'DETUNE',
                'CHORD',
                'EG'
            ]

            encoder_property_names = [
                'osc_pulsewidth',
                'pitch_glide',
                'pitch_detune',
                'pitch_chord',
                'pitch_env_depth'
            ]

            self._encoder_property_osc_addresses = [
                '/osc/pulsewidth',
                '/pitch/glide',
                '/pitch/detune',
                '/pitch/chord',
                '/pitch/env_depth'
            ]

        elif section_name == 'oscillator_bottom_row':
            self.encoder_display_names = [
                'WAVE',
                'LEVEL',
                'SUB',
                'NOISE',
                'LFO'
            ]

            encoder_property_names = [
                'osc_wave',
                'mix_osc',
                'mix_sub',
                'mix_noise',
                'pitch_lfo1'
            ]

            self._encoder_property_osc_addresses = [
                '/osc/wave',
                '/mix/osc',
                '/mix/sub',
                '/mix/noise',
                '/pitch/lfo1'
            ]

        elif section_name == 'filter_top_row':
            self.encoder_display_names = [
                'CUTOFF',
                'RESONANCE',
                'TRACKING',
                'EG',
                'LFO'
            ]

            encoder_property_names = [
                'lpf_cutoff',
                'lpf_resonance',
                'lpf_tracking',
                'lpf_env_depth',
                'lpf_lfo1'
            ]

            self._encoder_property_osc_addresses = [
                '/lpf/cutoff',
                '/lpf/resonance',
                '/lpf/tracking',
                '/lpf/env_depth',
                '/lpf/lfo1'
            ]

        elif section_name == 'filter_bottom_row':
            self.encoder_display_names = [
                'HPF',
                '',
                '',
                '',
                ''
            ]

            encoder_property_names = [
                'hpf_cutoff',
                None,
                None,
                None,
                None
            ]

            self._encoder_property_osc_addresses = [
                '/hpf/cutoff',
                None,
                None,
                None,
                None
            ]

        elif section_name == 'amp':
            self.encoder_display_names = [
                'ATTACK',
                'DECAY',
                'SUSTAIN',
                'RELEASE',
                'MAIN'
            ]

            encoder_property_names = [
                'amp_attack',
                'amp_decay',
                'amp_sustain',
                'amp_release',
                'main_level'
            ]

            self._encoder_property_osc_addresses = [
                '/amp/attack',
                '/amp/decay',
                '/amp/sustain',
                '/amp/release',
                '/amp/level'
            ]

        elif section_name == 'pitch_filter_env':
            self.encoder_display_names = [
                'ATTACK',
                'DECAY',
                'SUSTAIN',
                'RELEASE',
                ''
            ]

            encoder_property_names = [
                'pitch_filter_env_attack',
                'pitch_filter_env_decay',
                'pitch_filter_env_sustain',
                'pitch_filter_env_release',
                None
            ]

            self._encoder_property_osc_addresses = [
                '/pitch_filter_env/attack',
                '/pitch_filter_env/decay',
                '/pitch_filter_env/sustain',
                '/pitch_filter_env/release',
                None
            ]

        elif section_name == 'lfo1':
            self.encoder_display_names = [
                'RATE',
                'WAVE',
                'DELAY',
                'FADE',
                'CONFIG'
            ]

            encoder_property_names = [
                'lfo1_rate',
                'lfo1_wave',
                'lfo1_delay',
                'lfo1_fade',
                'lfo1_config'
            ]

            self._encoder_property_osc_addresses = [
                '/lfo1/rate',
                '/lfo1/wave',
                '/lfo1/delay',
                '/lfo1/fade',
                '/lfo1'
            ]

        elif section_name == 'lfo2':
            self.encoder_display_names = [
                'RATE',
                'WAVE',
                'DELAY',
                'FADE',
                'CONFIG'
            ]

            encoder_property_names = [
                'lfo2_rate',
                'lfo2_wave',
                'lfo2_delay',
                'lfo2_fade',
                'lfo2_config'
            ]

            self._encoder_property_osc_addresses = [
                '/lfo2/rate',
                '/lfo2/wave',
                '/lfo2/delay',
                '/lfo2/fade',
                '/lfo2'
            ]

        elif section_name == 'reverb':
            self.encoder_display_names = [
                'SIZE',
                'DECAY',
                'FILTER',
                'MIX',
                ''
            ]

            encoder_property_names = [
                'reverb_size',
                'reverb_decay',
                'reverb_filter',
                'reverb_mix',
                None
            ]

            self._encoder_property_osc_addresses = [
                '/reverb/size',
                '/reverb/decay',
                '/reverb/filter',
                '/reverb/mix',
                None
            ]

        else:
            raise Exception(f'Unknown section name: {section_name}')

        # Store the name of the newly-selected section
        self.selected_section = section_name

        # # Implement the encoder configuration
        # for encoder_num in range(self.num_param_encoders):
        #
        #     # Remove any previous property binding for this encoder
        #     if self._encoder_bindings[encoder_num]['property_name'] is not None:
        #         self.unbind(**{
        #             self._encoder_bindings[encoder_num]['property_name']: self._encoder_bindings[encoder_num][
        #                 'function']})
        #         self._encoder_bindings[encoder_num]['property_name'] = None
        #         self._encoder_bindings[encoder_num]['function'] = None
        #
        #     # Get the new property name for the encoder
        #     prop_name = encoder_property_names[encoder_num]
        #
        #     if prop_name is None:
        #         # Clear the encoder displays
        #         self.encoder_display_names[encoder_num] = ''
        #         self.encoder_display_types[encoder_num] = ''
        #         self.encoder_display_values[encoder_num] = ''
        #
        #     else:
        #         prop_dict = getattr(self, prop_name)
        #         prop_keys = list(prop_dict.keys())
        #
        #         # Reset the selected dict key for the property
        #         self._encoder_property_dict_key[encoder_num] = prop_keys[0]
        #
        #         # Update the encoder's value type and value displays
        #         #
        #         key = self._encoder_property_dict_key[encoder_num]
        #         if key == 'key_sync':
        #             # Key Sync has two discrete values, displayed as strings.
        #             #
        #
        #             # Set the encoder's value type display
        #             self.encoder_display_types[encoder_num] = 'KEY SYNC'
        #
        #             # Get the current value for Key Sync
        #             key_sync_int = prop_dict[key]
        #
        #             # Get the string representation
        #             key_sync_string = self.string_for_lfo_key_sync(key_sync_int)
        #
        #             # Set the encoder's value display
        #             self.encoder_display_values[encoder_num] = key_sync_string
        #
        #         elif key == 'type':
        #             # LFO Type has four discrete values, displayed as strings
        #             #
        #
        #             # Set the encoder's value type display
        #             self.encoder_display_types[encoder_num] = 'TYPE'
        #
        #             # Get the current value for LFO Type
        #             lfo_type_int = prop_dict[key]
        #
        #             # Get its string representation
        #             lfo_type_string = self.string_for_lfo_type(lfo_type_int)
        #
        #             # Set the encoder's value display
        #             self.encoder_display_values[encoder_num] = lfo_type_string
        #
        #         else:
        #             # This is just a numerical value.
        #             #
        #             self.encoder_display_types[encoder_num] = key.upper()
        #             self.encoder_display_values[encoder_num] = str(prop_dict[key])
        #
        #         # Bind a callback to the property so the encoder
        #         # displays update whenever the property changes
        #         if prop_name is not None:
        #             bound_func = lambda _, prop_dict, encoder_num=encoder_num, prop_name=prop_name: self._encoder_bound_property_changed(encoder_num, prop_name, prop_dict)
        #             self.bind(**{prop_name: bound_func})
        #
        #             # Store new binding info
        #             self._encoder_bindings[encoder_num]['property_name'] = prop_name
        #             self._encoder_bindings[encoder_num]['function'] = bound_func
        #
        #     # Update encoder LED color
        #     self.update_encoder_led_color(encoder_num)

    def label_clicked(self, param_name):
        Logger.debug(f'label_clicked: {param_name}')

    def label_touched(self, label, param_name):
        Logger.debug(f'label_touched: {label}, {param_name}')

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
        param_type = NymphesPreset.type_for_param_name(param_name)
        if param_type == float:
            value_string = format(round(value, NymphesPreset.float_precision_num_decimals),
                                  f'.{NymphesPreset.float_precision_num_decimals}f')
        elif param_type == int:
            value_string = str(value)

        self.set_status_bar_text_on_main_thread(f'{param_name}: {value_string}')

        # Send an OSC message for this parameter with the new value
        self._send_nymphes_osc(f'/{param_name.replace(".", "/")}', value)

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

        if not self.float_mode or param_type == int:
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
            new_val = round(curr_val + amount, NymphesPreset.float_precision_num_decimals)

            # Keep within the min and max value range
            if new_val < min_val:
                new_val = min_val

            if new_val > max_val:
                new_val = max_val

            # Set the property's value only if the new value is different
            # than the current value
            if not self.float_equals(curr_val, new_val, NymphesPreset.float_precision_num_decimals):
                self.set_prop_value_for_param_name(param_name, new_val)

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

            if self.float_mode_modifier_key == 'shift':
                # Enable float mode
                Logger.debug('Float Mode Enabled')
                self.float_mode = True

        # Check for the meta key (CMD on macOS)
        left_meta_key_code = 309
        right_meta_key_code = 1073742055
        if keycode in [left_meta_key_code, right_meta_key_code] or 'meta' in modifiers:
            Logger.debug('meta key pressed')
            self._meta_key_pressed = True

            if self.float_mode_modifier_key == 'meta':
                # Enable float mode
                Logger.debug('Float Mode Enabled')
                self.float_mode = True

        # Check for the Alt key (Alt/Option on macOS)
        left_alt_key_code = 308
        right_alt_key_code = 307
        if keycode in [left_alt_key_code, right_alt_key_code] or 'alt' in modifiers:
            Logger.debug('alt key pressed')
            self._alt_key_pressed = True

            if self.float_mode_modifier_key == 'alt':
                # Enable float mode
                Logger.debug('Float Mode Enabled')
                self.float_mode = True

    def _on_key_up(self, keyboard, keycode):
        Logger.debug(f'on_key_up: {keyboard}, {keycode}')

        # Check for either of the shift keys
        left_shift_key_code = 304
        right_shift_key_code = 303
        if keycode[0] in [left_shift_key_code, right_shift_key_code]:
            Logger.debug('Shift key released')
            self._shift_key_pressed = False

            if self.float_mode_modifier_key == 'shift':
                # Disable float mode
                Logger.debug('Float Mode Disabled')
                self.float_mode = False

        # Check for the meta key (CMD on macOS)
        left_meta_key_code = 309
        right_meta_key_code = 1073742055
        if keycode[0] in [left_meta_key_code, right_meta_key_code]:
            Logger.debug('meta key released')
            self._meta_key_pressed = False

            if self.float_mode_modifier_key == 'meta':
                # Disable float mode
                Logger.debug('Float Mode Disabled')
                self.float_mode = False

        # Check for the Alt key (Alt/Option on macOS)
        left_alt_key_code = 308
        right_alt_key_code = 307
        if keycode[0] in [left_alt_key_code, right_alt_key_code]:
            Logger.debug('alt key released')
            self._alt_key_pressed = False

            if self.float_mode_modifier_key == 'alt':
                # Disable float mode
                Logger.debug('Float Mode Disabled')
                self.float_mode = False

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

        # Logger.debug(f'on_window_resize: new size: {width} x {height}, prev size: {self.curr_width} x {self.curr_height}, diff: {width_diff} x {height_diff}, scaling: {scaling}')

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

        Clock.schedule_once(lambda dt: work_func(dt, option_text), 0)

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

    def reload(self):
        """
        Reloads the current preset
        :return:
        """
        if self.curr_preset_type == 'file' and self._curr_preset_file_path is not None:
            self._send_nymphes_osc('/load_file', str(self._curr_preset_file_path))

        elif self.curr_preset_type == 'init':
            self._send_nymphes_osc('/load_init_file')

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
            self._send_nymphes_osc('/save_to_file', str(self._curr_preset_file_path))

    def _bind_keyboard_events(self):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self.root)
        self._keyboard.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)

    def _on_popup_open(self, popup_instance):
        # Bind keyboard events for the popup
        popup_instance.content._keyboard = Window.request_keyboard(popup_instance.content._keyboard_closed, popup_instance)
        popup_instance.content._keyboard.bind(
            on_key_down=popup_instance.content._on_key_down,
            on_key_up=popup_instance.content._on_key_up
        )

    def _on_popup_dismiss(self, popup_instance):
        # Unbind keyboard events from the popup
        if popup_instance.content._keyboard is not None:
            popup_instance.content._keyboard.unbind(on_key_down=popup_instance.content._on_key_down)
            popup_instance.content._keyboard.unbind(on_key_up=popup_instance.content._on_key_up)
            popup_instance.content._keyboard = None

        # Rebind keyboard events for the app itself
        self._bind_keyboard_events()

    def set_nymphes_input_name_on_main_thread(self, port_name):
        Logger.debug(f'set_nymphes_input_name_on_main_thread: {port_name}')

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

        def work_func(_, new_port_name):
            self.nymphes_input_name = new_port_name
            
    def set_nymphes_output_name_on_main_thread(self, port_name):
        Logger.debug(f'set_nymphes_output_name_on_main_thread: {port_name}')

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

        def work_func(_, new_port_name):
            self.nymphes_output_name = new_port_name

    def add_name_to_nymphes_input_spinner_on_main_thread(self, port_name):
        Logger.debug(f'add_nymphes_input_name_on_main_thread: {port_name}')

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

        def work_func(_, new_port_name):
            # Add the port name to the list used by the
            # Nymphes input ports spinner
            self.nymphes_input_spinner_names.append(new_port_name)
            self.nymphes_input_spinner_names = [self.nymphes_input_spinner_names[0]] + sorted(self.nymphes_input_spinner_names[1:])

    def remove_name_from_nymphes_input_spinner_on_main_thread(self, port_name):
        Logger.debug(f'remove_nymphes_input_name_on_main_thread: {port_name}')

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

        def work_func(_, new_port_name):
            # Remove it from the Nymphes input spinner list as well
            if new_port_name in self.nymphes_input_spinner_names:
                self.nymphes_input_spinner_names.remove(new_port_name)
                
    def add_name_to_nymphes_output_spinner_on_main_thread(self, port_name):
        Logger.debug(f'add_nymphes_output_name_on_main_thread: {port_name}')

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

        def work_func(_, new_port_name):
            # Add the port name to the list used by the
            # Nymphes output ports spinner
            self.nymphes_output_spinner_names.append(new_port_name)
            self.nymphes_output_spinner_names = [self.nymphes_output_spinner_names[0]] + sorted(self.nymphes_output_spinner_names[1:])

    def remove_name_from_nymphes_output_spinner_on_main_thread(self, port_name):
        Logger.debug(f'remove_nymphes_output_name_on_main_thread: {port_name}')

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

        def work_func(_, new_port_name):
            # Remove it from the Nymphes output spinner list as well
            if new_port_name in self.nymphes_output_spinner_names:
                self.nymphes_output_spinner_names.remove(new_port_name)

    def add_midi_input_name_on_main_thread(self, port_name):
        Logger.debug(f'add_midi_input_name_on_main_thread: {port_name}')

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

        def work_func(_, new_port_name):
            # Add the port name to the list of detected
            # MIDI controller input ports
            self.detected_midi_input_names_for_gui.append(new_port_name)
            self.detected_midi_input_names_for_gui.sort()

    def remove_midi_input_name_on_main_thread(self, port_name):
        Logger.debug(f'remove_midi_input_name_on_main_thread: {port_name}')

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

        def work_func(_, new_port_name):
            if new_port_name in self.detected_midi_input_names_for_gui:
                self.detected_midi_input_names_for_gui.remove(new_port_name)

    def add_midi_output_name_on_main_thread(self, port_name):
        Logger.debug(f'add_midi_output_name_on_main_thread: {port_name}')

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

        def work_func(_, new_port_name):
            self.detected_midi_output_names_for_gui.append(new_port_name)
            self.detected_midi_output_names_for_gui.sort()

    def remove_midi_output_name_on_main_thread(self, port_name):
        Logger.debug(f'remove_midi_output_name_on_main_thread: {port_name}')

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

        def work_func(_, new_port_name):
            if new_port_name in self.detected_midi_output_names_for_gui:
                self.detected_midi_output_names_for_gui.remove(new_port_name)

    def add_connected_midi_input_name_on_main_thread(self, port_name):
        Logger.debug(f'add_connected_midi_input_name_on_main_thread: {port_name}')

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

        def work_func(_, new_port_name):
            self.connected_midi_input_names_for_gui.append(new_port_name)
            self.connected_midi_input_names_for_gui.sort()

    def remove_connected_midi_input_name_on_main_thread(self, port_name):
        Logger.debug(f'remove_connected_midi_input_name_on_main_thread: {port_name}')

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

        def work_func(_, new_port_name):
            if new_port_name in self.connected_midi_input_names_for_gui:
                self.connected_midi_input_names_for_gui.remove(new_port_name)
                
    def add_connected_midi_output_name_on_main_thread(self, port_name):
        Logger.debug(f'add_connected_midi_output_name_on_main_thread: {port_name}')

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

        def work_func(_, new_port_name):
            self.connected_midi_output_names_for_gui.append(new_port_name)
            self.connected_midi_output_names_for_gui.sort()

    def remove_connected_midi_output_name_on_main_thread(self, port_name):
        Logger.debug(f'remove_connected_midi_output_name_on_main_thread: {port_name}')

        Clock.schedule_once(lambda dt: work_func(dt, port_name), 0)

        def work_func(_, new_port_name):
            if new_port_name in self.connected_midi_output_names_for_gui:
                self.connected_midi_output_names_for_gui.remove(new_port_name)

    def set_status_bar_text_on_main_thread(self, status_text):
        Clock.schedule_once(lambda dt: work_func(dt, status_text), 0)

        def work_func(_, new_status_text):
            self.status_bar_text = new_status_text

    def set_mod_wheel_on_main_thread(self, val):
        Clock.schedule_once(lambda dt: work_func(dt, val), 0)

        def work_func(_, value):
            self.mod_wheel = value
            
    def set_velocity_on_main_thread(self, val):
        Clock.schedule_once(lambda dt: work_func(dt, val), 0)

        def work_func(_, value):
            self.velocity = value
        
    def set_aftertouch_on_main_thread(self, val):
        Clock.schedule_once(lambda dt: work_func(dt, val), 0)

        def work_func(_, value):
            self.aftertouch = value

    def midi_input_port_checkbox_toggled(self, port_name, active):
        Logger.debug(f'midi_input_port_checkbox_toggled: {port_name}, {active}')

        if active:
            if port_name not in self._connected_midi_inputs:
                # Connect to this MIDI input
                self._send_nymphes_osc(
                    '/connect_midi_input',
                    port_name
                )

        else:
            if port_name in self._connected_midi_inputs:
                # Disconnect from this MIDI input
                self._send_nymphes_osc(
                    '/disconnect_midi_input',
                    port_name
                )

    def midi_output_port_checkbox_toggled(self, port_name, active):
        Logger.debug(f'midi_output_port_checkbox_toggled: {port_name}, {active}')

        if active:
            if port_name not in self._connected_midi_outputs:
                # Connect to this MIDI output
                self._send_nymphes_osc(
                    '/connect_midi_output',
                    port_name
                )

        else:
            if port_name in self._connected_midi_outputs:
                # Disconnect from this MIDI output
                self._send_nymphes_osc(
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
                self._send_nymphes_osc(
                    '/connect_nymphes',
                    self.nymphes_input_name,
                    self.nymphes_output_name
                )

            else:
                if self.nymphes_connected:
                    self._send_nymphes_osc('/disconnect_nymphes')
                    
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
                self._send_nymphes_osc(
                    '/connect_nymphes',
                    self.nymphes_output_name,
                    self.nymphes_output_name
                )

            else:
                if self.nymphes_connected:
                    self._send_nymphes_osc('/disconnect_nymphes')

    def on_mouse_entered_param_control(self, param_name):
        # When the mouse enters a parameter control and Nymphes
        # is connected, display the name and value in the status
        # bar.

        if self.nymphes_connected:
            # Get the value and type for the parameter
            value = self.get_prop_value_for_param_name(param_name)
            param_type = NymphesPreset.type_for_param_name(param_name)

            if param_type == float:
                value_string = format(round(value, NymphesPreset.float_precision_num_decimals), f'.{NymphesPreset.float_precision_num_decimals}f')

            elif param_type == int:
                value_string = str(value)

            self.set_status_bar_text_on_main_thread(f'{param_name}: {value_string}')

    def on_mouse_exited_param_control(self, param_name):
        # When Nymphes is connected and the mouse exits a parameter
        # control, blank the status bar
        #

        if self.nymphes_connected:
            # Reset the status message to blank
            self.set_status_bar_text_on_main_thread('')

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
        print(f'increment_mod_wheel: {amount}')

        new_val = self.mod_wheel + int(amount)
        if new_val > 127:
            new_val = 127
        elif new_val < 0:
            new_val = 0

        if new_val != self.mod_wheel:
            # Update the property
            self.mod_wheel = new_val

            # Send the new value to Nymphes
            self._send_nymphes_osc(
                '/mod_wheel',
                new_val
            )

    def increment_aftertouch(self, amount):
        print(f'increment_aftertouch: {amount}')

        new_val = self.aftertouch + int(amount)
        if new_val > 127:
            new_val = 127
        elif new_val < 0:
            new_val = 0

        if new_val != self.aftertouch:
            # Update the property
            self.aftertouch = new_val

            # Send the new value to Nymphes
            self._send_nymphes_osc(
                '/aftertouch',
                new_val
            )


class FloatParamValueLabel(ButtonBehavior, Label):
    section_name = StringProperty('')
    param_name = StringProperty('')
    drag_start_pos = NumericProperty(0)
    text_color_string = StringProperty('#06070FFF')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouseover)

        self.mouse_inside_bounds = False

    def on_mouseover(self, _, pos):
        if self.collide_point(*pos):
            if not self.mouse_inside_bounds:
                self.mouse_inside_bounds = True
                self.on_mouse_enter()

        else:
            if self.mouse_inside_bounds:
                self.mouse_inside_bounds = False
                self.on_mouse_exit()

    def on_mouse_enter(self):
        App.get_running_app().on_mouse_entered_param_control(f'{self.param_name}.value')

    def on_mouse_exit(self):
        App.get_running_app().on_mouse_exited_param_control(f'{self.param_name}.value')


    def handle_touch(self, device, button):
        #
        # Mouse Wheel
        #
        if not self.disabled:
            if device == 'mouse':
                if button == 'scrollup':
                    direction = -1 if App.get_running_app().invert_mouse_wheel else 1

                    if App.get_running_app().float_mode:
                        # We are in float mode, so use the minimum increment defined by
                        # NymphesPreset's float precision property
                        increment = float(direction) / pow(10, NymphesPreset.float_precision_num_decimals)

                    else:
                        increment = int(direction)

                    # Increment the property
                    App.get_running_app().increment_prop_value_for_param_name(self.param_name + '.value', increment)

                elif button == 'scrolldown':
                    direction = 1 if App.get_running_app().invert_mouse_wheel else -1

                    if App.get_running_app().float_mode:
                        # We are in float mode, so use the minimum decrement defined by
                        # NymphesPreset's float precision property
                        increment = float(direction) / pow(10, NymphesPreset.float_precision_num_decimals)

                    else:
                        increment = int(direction)

                    # Increment the property
                    App.get_running_app().increment_prop_value_for_param_name(self.param_name + '.value', increment)

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

                return True

            return super(FloatParamValueLabel, self).on_touch_down(touch)

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
                if App.get_running_app().float_mode:
                    # Use the minimum increment defined by
                    # NymphesPreset's float precision property
                    increment = round(curr_drag_distance * 0.05, NymphesPreset.float_precision_num_decimals)

                else:
                    increment = int(round(curr_drag_distance * (1/3)))

                # Increment the property's value
                App.get_running_app().increment_prop_value_for_param_name(self.param_name + '.value', increment)

                # Reset the drag start position to the current position
                self.drag_start_pos = curr_pos

                return True

            return super(FloatParamValueLabel, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if not self.disabled:
            if touch.grab_current == self:
                touch.ungrab(self)
                return True
            return super(FloatParamValueLabel, self).on_touch_up(touch)


class IntParamValueLabel(ButtonBehavior, Label):
    section_name = StringProperty('')
    param_name = StringProperty('')
    drag_start_pos = NumericProperty(0)
    text_color_string = StringProperty('#06070FFF')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouseover)

        self.mouse_inside_bounds = False

    def on_mouseover(self, _, pos):
        if self.collide_point(*pos):
            if not self.mouse_inside_bounds:
                self.mouse_inside_bounds = True
                self.on_mouse_enter()

        else:
            if self.mouse_inside_bounds:
                self.mouse_inside_bounds = False
                self.on_mouse_exit()

    def on_mouse_enter(self):
        App.get_running_app().on_mouse_entered_param_control(f'{self.param_name}.value')

    def on_mouse_exit(self):
        App.get_running_app().on_mouse_exited_param_control(f'{self.param_name}.value')

    def handle_touch(self, device, button):
        #
        # Mouse Wheel
        #
        if not self.disabled:
            if device == 'mouse':
                if button == 'scrollup':
                    increment = -1 if App.get_running_app().invert_mouse_wheel else 1

                    # Increment the property
                    App.get_running_app().increment_prop_value_for_param_name(self.param_name + '.value', increment)

                elif button == 'scrolldown':
                    increment = 1 if App.get_running_app().invert_mouse_wheel else -1

                    # Increment the property
                    App.get_running_app().increment_prop_value_for_param_name(self.param_name + '.value', increment)

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

                return True
            return super(IntParamValueLabel, self).on_touch_down(touch)

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
                App.get_running_app().increment_prop_value_for_param_name(self.param_name + '.value', increment)

                # Reset the drag start position to the current position
                self.drag_start_pos = curr_pos

                return True

            return super(IntParamValueLabel, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if not self.disabled:
            if touch.grab_current == self:
                touch.ungrab(self)
                return True
            return super(IntParamValueLabel, self).on_touch_up(touch)

    

class ParamsGridModCell(BoxLayout):
    section_name = StringProperty('')
    title = StringProperty('')
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
    section_name = StringProperty('')
    title = StringProperty('')
    param_name = StringProperty('')
    value_prop = NumericProperty(0)
    corner_radius = NumericProperty(0)
    value_color_string = StringProperty('#06070FFF')
    background_color_string = StringProperty('#438EFFFF')
    param_name_color_string = StringProperty('#ECBFEBFF')


class ParamsGridLfoConfigCell(ButtonBehavior, BoxLayout):
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
            App.get_running_app().dismiss_popup()


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
            App.get_running_app().dismiss_popup()


Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)


class ModAmountLine(ButtonBehavior, Widget):
    midi_val = NumericProperty(0) # This is 0 to 127
    color_hex = StringProperty('#FFFFFFFF')
    section_name = StringProperty('')
    param_name = StringProperty('')
    mod_type = StringProperty('')
    drag_start_pos = NumericProperty(0)
    background_color_string = StringProperty('#72777BFF')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouseover)

        self.mouse_inside_bounds = False

    def on_mouseover(self, _, pos):
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
        App.get_running_app().on_mouse_exited_param_control(self.param_name)

    def handle_touch(self, device, button):
        #
        # Mouse Wheel
        #
        if not self.disabled:
            if device == 'mouse':
                if button == 'scrollup':
                    direction = -1 if App.get_running_app().invert_mouse_wheel else 1

                    if App.get_running_app().float_mode:
                        # Use the minimum increment defined by
                        # NymphesPreset's float precision property
                        increment = float(direction) / pow(10, NymphesPreset.float_precision_num_decimals)

                    else:
                        # We are not in float mode, so increment by 1
                        increment = int(direction)

                    # Increment the property
                    App.get_running_app().increment_prop_value_for_param_name(f'{self.param_name}.{self.mod_type}', increment)

                elif button == 'scrolldown':
                    direction = 1 if App.get_running_app().invert_mouse_wheel else -1

                    if App.get_running_app().float_mode:
                        # Use the minimum decrement defined by
                        # NymphesPreset's float precision property
                        increment = float(direction) / pow(10, NymphesPreset.float_precision_num_decimals)

                    else:
                        # We are not in float mode, so decrement by 1
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
                if App.get_running_app().float_mode:
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
                return True
            return super(ModAmountLine, self).on_touch_up(touch)


class VoiceModeButton(ButtonBehavior, Label):
    voice_mode_name = StringProperty('')



class SectionRelativeLayout(RelativeLayout):
    corner_radius = NumericProperty(12)
    section_name = StringProperty('')


class ModAmountsBox(BoxLayout):
    param_name = StringProperty('')
    lfo2_prop = NumericProperty(0)
    mod_wheel_prop = NumericProperty(0)
    velocity_prop = NumericProperty(0)
    aftertouch_prop = NumericProperty(0)
    mod_amount_line_background_color_string = StringProperty('#000000FF')


class MainControlsBox(BoxLayout):
    corner_radius = NumericProperty(0)


class ChordsMainControlsBox(BoxLayout):
    corner_radius = NumericProperty(0)


class MainSettingsBox(BoxLayout):
    corner_radius = NumericProperty(0)


class VoiceModeBox(BoxLayout):
    num_voice_modes = NumericProperty(6)
    corner_radius = NumericProperty(0)


class LegatoBox(BoxLayout):
    corner_radius = NumericProperty(0)


class ChordsButtonBox(BoxLayout):
    corner_radius = NumericProperty(0)


class FloatModeBox(BoxLayout):
    corner_radius = NumericProperty(0)

class LeftBar(BoxLayout):
    corner_radius = NumericProperty(0)


class TopBar(BoxLayout):
    corner_radius = NumericProperty(0)


class BottomBar(BoxLayout):
    corner_radius = NumericProperty(0)


class SettingsTopBar(BoxLayout):
    corner_radius = NumericProperty(0)

class ChordsTopBar(BoxLayout):
    corner_radius = NumericProperty(0)


class ChordsMainControlsBox(BoxLayout):
    corner_radius = NumericProperty(0)


class ControlSectionsGrid(GridLayout):
    corner_radius = NumericProperty(0)


class ControlSection(BoxLayout):
    corner_radius = NumericProperty(0)


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
    drag_start_pos = NumericProperty(0)
    text_color_string = StringProperty('#06070FFF')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mouse_inside_bounds = False

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
                return True
            return super(ModWheelValueLabel, self).on_touch_up(touch)
        

class AftertouchValueLabel(ButtonBehavior, Label):
    drag_start_pos = NumericProperty(0)
    text_color_string = StringProperty('#06070FFF')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mouse_inside_bounds = False

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
                return True
            return super(AftertouchValueLabel, self).on_touch_up(touch)


class ChordParamsGrid(GridLayout):
    corner_radius = NumericProperty(0)


class ChordParamsGridCell(ButtonBehavior, BoxLayout):
    section_name = StringProperty('')
    title = StringProperty('')
    param_name = StringProperty('')
    value_prop = NumericProperty(0)
    corner_radius = NumericProperty(0)
    value_color_string = StringProperty('#06070FFF')
    background_color_string = StringProperty('#438EFFFF')
    
    
class ChordParamValueLabel(ButtonBehavior, Label):
    section_name = StringProperty('')
    param_name = StringProperty('')
    drag_start_pos = NumericProperty(0)
    text_color_string = StringProperty('#06070FFF')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouseover)

        self.mouse_inside_bounds = False

    def on_mouseover(self, _, pos):
        if self.collide_point(*pos):
            if not self.mouse_inside_bounds:
                self.mouse_inside_bounds = True
                self.on_mouse_enter()

        else:
            if self.mouse_inside_bounds:
                self.mouse_inside_bounds = False
                self.on_mouse_exit()

    def on_mouse_enter(self):
        App.get_running_app().on_mouse_entered_param_control(self.param_name)

    def on_mouse_exit(self):
        App.get_running_app().on_mouse_exited_param_control(self.param_name)

    def handle_touch(self, device, button):
        #
        # Mouse Wheel
        #
        if not self.disabled:
            if device == 'mouse':
                if button == 'scrollup':
                    direction = -1 if App.get_running_app().invert_mouse_wheel else 1

                    if App.get_running_app().float_mode:
                        # We are in float mode, so use the minimum increment defined by
                        # NymphesPreset's float precision property
                        increment = float(direction) / pow(10, NymphesPreset.float_precision_num_decimals)

                    else:
                        increment = int(direction)

                    # Increment the property
                    App.get_running_app().increment_prop_value_for_param_name(self.param_name, increment)

                elif button == 'scrolldown':
                    direction = 1 if App.get_running_app().invert_mouse_wheel else -1

                    if App.get_running_app().float_mode:
                        # We are in float mode, so use the minimum decrement defined by
                        # NymphesPreset's float precision property
                        increment = float(direction) / pow(10, NymphesPreset.float_precision_num_decimals)

                    else:
                        increment = int(direction)

                    # Increment the property
                    App.get_running_app().increment_prop_value_for_param_name(self.param_name, increment)

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

                return True

            return super(ChordParamValueLabel, self).on_touch_down(touch)

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
                if App.get_running_app().float_mode:
                    # Use the minimum increment defined by
                    # NymphesPreset's float precision property
                    increment = round(curr_drag_distance * 0.05, NymphesPreset.float_precision_num_decimals)

                else:
                    increment = int(round(curr_drag_distance * (1/3)))

                # Increment the property's value
                App.get_running_app().increment_prop_value_for_param_name(self.param_name, increment)

                # Reset the drag start position to the current position
                self.drag_start_pos = curr_pos

                return True

            return super(ChordParamValueLabel, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if not self.disabled:
            if touch.grab_current == self:
                touch.ungrab(self)
                return True
            return super(ChordParamValueLabel, self).on_touch_up(touch)


class ChordSectionTitleLabel(ButtonBehavior, Label):
    this_chord_active = BooleanProperty(False)
