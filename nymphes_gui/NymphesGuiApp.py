import kivy
from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.config import Config
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, DictProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.factory import Factory
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.osc_message_builder import OscMessageBuilder
import threading
import configparser
from pathlib import Path
import netifaces
# import logging
# from logging.handlers import RotatingFileHandler
from kivy.logger import Logger, LOG_LEVELS
Logger.setLevel(LOG_LEVELS["debug"])
import subprocess
from nymphes_osc.NymphesPreset import NymphesPreset
from functools import partial

kivy.require('2.1.0')
Config.read('app_config.ini')


class NymphesGuiApp(App):

    def presets_spinner_values_list():
        """
        Returns a list of text values for the presets spinner to show.
        """
        return [f'{kind} {bank}{num}' for kind in ['USER', 'FACTORY'] for bank in ['A', 'B', 'C', 'D', 'E', 'F', 'G']
                for num in [1, 2, 3, 4, 5, 6, 7]]

    #
    # App Status Parameters
    #

    nymphes_connected = BooleanProperty(False)
    nymphes_midi_channel = NumericProperty(1)
    mod_wheel = NumericProperty(0)
    velocity = NumericProperty(0)
    aftertouch = NumericProperty(0)
    non_nymphes_midi_input_names = ListProperty([])
    non_nymphes_midi_output_names = ListProperty([])
    midi_controller_input_name = StringProperty('Not Connected')
    midi_controller_input_connected = BooleanProperty(False)
    midi_controller_output_name = StringProperty('Not Connected')
    midi_controller_output_connected = BooleanProperty(False)
    presets_spinner_text = StringProperty('PRESET')
    presets_spinner_values = ListProperty(presets_spinner_values_list())

    selected_section = StringProperty('')

    #
    # Nymphes Parameters
    #

    osc_wave_value = NumericProperty(0)
    osc_wave_lfo2 = NumericProperty(0)
    osc_wave_mod_wheel = NumericProperty(0)
    osc_wave_velocity = NumericProperty(0)
    osc_wave_aftertouch = NumericProperty(0)

    osc_pulsewidth_value = NumericProperty(21)
    osc_pulsewidth_lfo2 = NumericProperty(0)
    osc_pulsewidth_mod_wheel = NumericProperty(0)
    osc_pulsewidth_velocity = NumericProperty(0)
    osc_pulsewidth_aftertouch = NumericProperty(0)

    osc_voice_mode_value = NumericProperty(0)
    osc_legato_value = NumericProperty(0)

    mix_osc_value = NumericProperty(0)
    mix_osc_lfo2 = NumericProperty(0)
    mix_osc_mod_wheel = NumericProperty(0)
    mix_osc_velocity = NumericProperty(0)
    mix_osc_aftertouch = NumericProperty(0)

    mix_sub_value = NumericProperty(0)
    mix_sub_lfo2 = NumericProperty(0)
    mix_sub_mod_wheel = NumericProperty(0)
    mix_sub_velocity = NumericProperty(0)
    mix_sub_aftertouch = NumericProperty(0)

    mix_noise_value = NumericProperty(0)
    mix_noise_lfo2 = NumericProperty(0)
    mix_noise_mod_wheel = NumericProperty(0)
    mix_noise_velocity = NumericProperty(0)
    mix_noise_aftertouch = NumericProperty(0)

    mix_level_value = NumericProperty(0)

    pitch_glide_value = NumericProperty(0)
    pitch_glide_lfo2 = NumericProperty(0)
    pitch_glide_mod_wheel = NumericProperty(0)
    pitch_glide_velocity = NumericProperty(0)
    pitch_glide_aftertouch = NumericProperty(0)

    pitch_detune_value = NumericProperty(0)
    pitch_detune_lfo2 = NumericProperty(0)
    pitch_detune_mod_wheel = NumericProperty(0)
    pitch_detune_velocity = NumericProperty(0)
    pitch_detune_aftertouch = NumericProperty(0)

    pitch_chord_value = NumericProperty(0)
    pitch_chord_lfo2 = NumericProperty(0)
    pitch_chord_mod_wheel = NumericProperty(0)
    pitch_chord_velocity = NumericProperty(0)
    pitch_chord_aftertouch = NumericProperty(0)

    pitch_eg_value = NumericProperty(0)
    pitch_eg_lfo2 = NumericProperty(0)
    pitch_eg_mod_wheel = NumericProperty(0)
    pitch_eg_velocity = NumericProperty(0)
    pitch_eg_aftertouch = NumericProperty(0)

    pitch_lfo1_value = NumericProperty(0)
    pitch_lfo1_lfo2 = NumericProperty(0)
    pitch_lfo1_mod_wheel = NumericProperty(0)
    pitch_lfo1_velocity = NumericProperty(0)
    pitch_lfo1_aftertouch = NumericProperty(0)

    lpf_cutoff_value = NumericProperty(0)
    lpf_cutoff_lfo2 = NumericProperty(0)
    lpf_cutoff_mod_wheel = NumericProperty(0)
    lpf_cutoff_velocity = NumericProperty(0)
    lpf_cutoff_aftertouch = NumericProperty(0)

    lpf_resonance_value = NumericProperty(0)
    lpf_resonance_lfo2 = NumericProperty(0)
    lpf_resonance_mod_wheel = NumericProperty(0)
    lpf_resonance_velocity = NumericProperty(0)
    lpf_resonance_aftertouch = NumericProperty(0)

    lpf_tracking_value = NumericProperty(0)
    lpf_tracking_lfo2 = NumericProperty(0)
    lpf_tracking_mod_wheel = NumericProperty(0)
    lpf_tracking_velocity = NumericProperty(0)
    lpf_tracking_aftertouch = NumericProperty(0)

    lpf_eg_value = NumericProperty(0)
    lpf_eg_lfo2 = NumericProperty(0)
    lpf_eg_mod_wheel = NumericProperty(0)
    lpf_eg_velocity = NumericProperty(0)
    lpf_eg_aftertouch = NumericProperty(0)

    lpf_lfo1_value = NumericProperty(0)
    lpf_lfo1_lfo2 = NumericProperty(0)
    lpf_lfo1_mod_wheel = NumericProperty(0)
    lpf_lfo1_velocity = NumericProperty(0)
    lpf_lfo1_aftertouch = NumericProperty(0)

    hpf_cutoff_value = NumericProperty(0)
    hpf_cutoff_lfo2 = NumericProperty(0)
    hpf_cutoff_mod_wheel = NumericProperty(0)
    hpf_cutoff_velocity = NumericProperty(0)
    hpf_cutoff_aftertouch = NumericProperty(0)

    filter_eg_attack_value = NumericProperty(0)
    filter_eg_attack_lfo2 = NumericProperty(0)
    filter_eg_attack_mod_wheel = NumericProperty(0)
    filter_eg_attack_velocity = NumericProperty(0)
    filter_eg_attack_aftertouch = NumericProperty(0)

    filter_eg_decay_value = NumericProperty(0)
    filter_eg_decay_lfo2 = NumericProperty(0)
    filter_eg_decay_mod_wheel = NumericProperty(0)
    filter_eg_decay_velocity = NumericProperty(0)
    filter_eg_decay_aftertouch = NumericProperty(0)

    filter_eg_sustain_value = NumericProperty(0)
    filter_eg_sustain_lfo2 = NumericProperty(0)
    filter_eg_sustain_mod_wheel = NumericProperty(0)
    filter_eg_sustain_velocity = NumericProperty(0)
    filter_eg_sustain_aftertouch = NumericProperty(0)

    filter_eg_release_value = NumericProperty(0)
    filter_eg_release_lfo2 = NumericProperty(0)
    filter_eg_release_mod_wheel = NumericProperty(0)
    filter_eg_release_velocity = NumericProperty(0)
    filter_eg_release_aftertouch = NumericProperty(0)

    amp_eg_attack_value = NumericProperty(0)
    amp_eg_attack_lfo2 = NumericProperty(0)
    amp_eg_attack_mod_wheel = NumericProperty(0)
    amp_eg_attack_velocity = NumericProperty(0)
    amp_eg_attack_aftertouch = NumericProperty(0)

    amp_eg_decay_value = NumericProperty(0)
    amp_eg_decay_lfo2 = NumericProperty(0)
    amp_eg_decay_mod_wheel = NumericProperty(0)
    amp_eg_decay_velocity = NumericProperty(0)
    amp_eg_decay_aftertouch = NumericProperty(0)

    amp_eg_sustain_value = NumericProperty(0)
    amp_eg_sustain_lfo2 = NumericProperty(0)
    amp_eg_sustain_mod_wheel = NumericProperty(0)
    amp_eg_sustain_velocity = NumericProperty(0)
    amp_eg_sustain_aftertouch = NumericProperty(0)

    amp_eg_release_value = NumericProperty(0)
    amp_eg_release_lfo2 = NumericProperty(0)
    amp_eg_release_mod_wheel = NumericProperty(0)
    amp_eg_release_velocity = NumericProperty(0)
    amp_eg_release_aftertouch = NumericProperty(0)

    lfo1_rate_value = NumericProperty(0)
    lfo1_rate_lfo2 = NumericProperty(0)
    lfo1_rate_mod_wheel = NumericProperty(0)
    lfo1_rate_velocity = NumericProperty(0)
    lfo1_rate_aftertouch = NumericProperty(0)

    lfo1_wave_value = NumericProperty(0)
    lfo1_wave_lfo2 = NumericProperty(0)
    lfo1_wave_mod_wheel = NumericProperty(0)
    lfo1_wave_velocity = NumericProperty(0)
    lfo1_wave_aftertouch = NumericProperty(0)

    lfo1_delay_value = NumericProperty(0)
    lfo1_delay_lfo2 = NumericProperty(0)
    lfo1_delay_mod_wheel = NumericProperty(0)
    lfo1_delay_velocity = NumericProperty(0)
    lfo1_delay_aftertouch = NumericProperty(0)

    lfo1_fade_value = NumericProperty(0)
    lfo1_fade_lfo2 = NumericProperty(0)
    lfo1_fade_mod_wheel = NumericProperty(0)
    lfo1_fade_velocity = NumericProperty(0)
    lfo1_fade_aftertouch = NumericProperty(0)

    lfo1_type_value = NumericProperty(0)
    lfo1_key_sync_value = NumericProperty(0)

    lfo2_rate_value = NumericProperty(0)
    lfo2_rate_lfo2 = NumericProperty(0)
    lfo2_rate_mod_wheel = NumericProperty(0)
    lfo2_rate_velocity = NumericProperty(0)
    lfo2_rate_aftertouch = NumericProperty(0)

    lfo2_wave_value = NumericProperty(0)
    lfo2_wave_lfo2 = NumericProperty(0)
    lfo2_wave_mod_wheel = NumericProperty(0)
    lfo2_wave_velocity = NumericProperty(0)
    lfo2_wave_aftertouch = NumericProperty(0)

    lfo2_delay_value = NumericProperty(0)
    lfo2_delay_lfo2 = NumericProperty(0)
    lfo2_delay_mod_wheel = NumericProperty(0)
    lfo2_delay_velocity = NumericProperty(0)
    lfo2_delay_aftertouch = NumericProperty(0)

    lfo2_fade_value = NumericProperty(0)
    lfo2_fade_lfo2 = NumericProperty(0)
    lfo2_fade_mod_wheel = NumericProperty(0)
    lfo2_fade_velocity = NumericProperty(0)
    lfo2_fade_aftertouch = NumericProperty(0)

    lfo2_type_value = NumericProperty(0)
    lfo2_key_sync_value = NumericProperty(0)

    reverb_size_value = NumericProperty(0)
    reverb_size_lfo2 = NumericProperty(0)
    reverb_size_mod_wheel = NumericProperty(0)
    reverb_size_velocity = NumericProperty(0)
    reverb_size_aftertouch = NumericProperty(0)

    reverb_decay_value = NumericProperty(0)
    reverb_decay_lfo2 = NumericProperty(0)
    reverb_decay_mod_wheel = NumericProperty(0)
    reverb_decay_velocity = NumericProperty(0)
    reverb_decay_aftertouch = NumericProperty(0)

    reverb_filter_value = NumericProperty(0)
    reverb_filter_lfo2 = NumericProperty(0)
    reverb_filter_mod_wheel = NumericProperty(0)
    reverb_filter_velocity = NumericProperty(0)
    reverb_filter_aftertouch = NumericProperty(0)

    reverb_mix_value = NumericProperty(0)
    reverb_mix_lfo2 = NumericProperty(0)
    reverb_mix_mod_wheel = NumericProperty(0)
    reverb_mix_velocity = NumericProperty(0)
    reverb_mix_aftertouch = NumericProperty(0)

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

    play_mode_name = StringProperty('POLY')
    legato = BooleanProperty(False)
    mod_source = NumericProperty(0)
    main_level = DictProperty({'value': 0})

    #
    # Preset File Handling
    #

    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(NymphesGuiApp, self).__init__(**kwargs)

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
        self._nymphes_osc_subprocess = None

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
        self._nymphes_connected = False

        # The MIDI channel used when communicating with Nymphes.
        # This is non-zero-referenced, so 1 is channel 1.
        self._nymphes_midi_channel = 1

        self._mod_wheel = 0
        self._velocity = 0
        self._aftertouch = 0
        self._sustain_pedal = 0
        self._legato = False

        # If the current preset was loaded from a file,
        # then this will be a Path object
        self._curr_preset_filepath = None

        # Names of Detected MIDI Ports (Including Nymphes Ports)
        self._detected_midi_inputs = []
        self._detected_midi_outputs = []

        # Names of Connected Non-Nymphes MIDI Ports
        self._connected_midi_inputs = []
        self._connected_midi_outputs = []

        # Names of Connected Nymphes MIDI Ports
        self._nymphes_input_port = None
        self._nymphes_output_port = None

        # Once a preset has been recalled, this will be
        # either 'user' or 'factory'
        self._curr_preset_type = None

        # Once a preset has been recalled, this will contain
        # the bank name ('A' to 'G') and preset number (1 to 7)
        self._curr_preset_bank_and_number = (None, None)

        # Curr Preset Index - Used for Preset Spinner
        self._curr_preset_index = None


        #
        # Preset File Handling
        #
        self._popup = None

        #
        # Get Configuration From config.txt
        #

        # Get the parent folder of this python file
        curr_dir = Path(__file__).resolve().parent

        # Build path to config file
        self._config_file_path = curr_dir / 'config.txt'

        # Create a config file if one doesn't exist
        if not Path(self._config_file_path).exists():
            self._create_config_file(self._config_file_path)

        # Load contents of config file
        self._load_config_file(self._config_file_path)

    def on_start(self):
        # Start the nymphes_osc subprocess
        self._start_nymphes_osc_subprocess()

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
        self.select_section('oscillator_top_row')

    def set_play_mode_by_name(self, play_mode_name):
        """
        Used to set the play mode by name instead of using a number.
        Possible names are:
        POLY
        UNI-A
        UNI-B
        TRI
        DUO
        MONO
        """

        if play_mode_name == 'POLY':
            play_mode_int = 0

        elif play_mode_name == 'UNI-A':
            play_mode_int = 1

        elif play_mode_name == 'UNI-B':
            play_mode_int = 2

        elif play_mode_name == 'TRI':
            play_mode_int = 3

        elif play_mode_name == 'DUO':
            play_mode_int = 4

        elif play_mode_name == 'MONO':
            play_mode_int = 5

        else:
            raise Exception(f'Invalid play mode string: {play_mode_name}')

        # Update the current play mode
        self.play_mode_name = play_mode_name

        # Send the command to the Nymphes
        self._send_nymphes_osc('/osc/voice_mode/value', play_mode_int)

    def set_legato(self, enable_legato):
        """
        enable_legato should be a bool
        """

        # Update the property
        self.legato = enable_legato

        # Send the command to the Nymphes
        self._send_nymphes_osc('/osc/legato/value', 1 if enable_legato else 0)

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

        #
        # Preset Files Path
        #
        if config.has_option('PRESETS', 'presets folder path'):
            self._presets_folder_path = Path(config['PRESETS']['presets folder path'])
        else:
            self._presets_folder_path = None

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
        with open(filepath, 'w') as config_file:
            config.write(config_file)

        Logger.info(f'Created config file at {filepath}')

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
                Logger.warning(f'Failed to detect local IP address ({e})')

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

        Logger.info(f'Started Nymphes OSC Server at {self._nymphes_osc_incoming_host}:{self._nymphes_osc_incoming_port}')

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
            Logger.info('Stopped Nymphes OSC Server')

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

        Logger.info(f'Started Encoder OSC Server at {self._encoder_osc_incoming_host}:{self._encoder_osc_incoming_port}')

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
            Logger.info('Stopped Encoder OSC Server')

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

        Logger.debug(f'send_nymphes_osc: {address}, {[str(arg) + " " for arg in args]}')

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

            # We are connected to nymphes_osc
            self._connected_to_nymphes_osc = True

            Logger.info(f'{address} ({host_name}:{port})')

        elif address == '/client_unregistered':
            # Get the hostname and port
            #
            host_name = str(args[0])
            port = int(args[1])

            # We are no longer connected to nymphes-osc
            self._connected_to_nymphes_osc = False

            Logger.info(f'{address} ({host_name}:{port})')

        elif address == '/nymphes_connected':
            #
            # nymphes_midi has connected to a Nymphes synthesizer
            #

            # Get the names of the MIDI input and output ports
            self._nymphes_input_port = str(args[0])
            self._nymphes_output_port = str(args[1])

            # Update app state
            self._nymphes_connected = True

            Logger.info(f'{address} (input_port: {self._nymphes_input_port}, output_port: {self._nymphes_output_port})')

        elif address == '/nymphes_disconnected':
            #
            # nymphes_midi is no longer connected to a Nymphes synthesizer
            #

            # Update app state
            self._nymphes_connected = False
            self._nymphes_input_port = None
            self._nymphes_output_port = None

            Logger.info(f'{address}')

        elif address == '/recalled_preset':
            #
            # The Nymphes synthesizer has just recalled a preset
            #

            # Get the preset type, bank and number
            #
            self._curr_preset_type = str(args[0])
            self._curr_preset_bank_and_number = str(args[1]), int(args[2])

            # Get the spinner index for the current preset
            self._curr_preset_index = NymphesGuiApp.index_from_preset_info(
                bank_name=self._curr_preset_bank_and_number[0],
                preset_num=self._curr_preset_bank_and_number[1],
                preset_type=self._curr_preset_type
            )

            # Update the preset spinner's text
            self.presets_spinner_text = NymphesGuiApp.presets_spinner_values_list()[self._curr_preset_index]

            Logger.info(f'{address} ({self._curr_preset_type} {self._curr_preset_bank_and_number[0]}{self._curr_preset_bank_and_number[1]})')

        elif address == '/received_current_preset_from_midi_input_port':
            port_name = str(args[0])
            self._curr_preset_type = str(args[1])
            self._curr_preset_bank_and_number = str(args[2]), int(args[3])

            Logger.info(
                f'{address} ({port_name}: {self._curr_preset_type} {self._curr_preset_bank_and_number[0]}{self._curr_preset_bank_and_number[1]})')

        elif address == '/loaded_file_into_current_preset':
            #
            # A preset file was loaded into Nymphes' current settings
            #

            # Get the filepath and store it
            self._curr_preset_filepath = Path(args[0])
            self._curr_preset_type = None
            self._curr_preset_bank_and_number = None, None

            Logger.info(f'{address}: {self._curr_preset_filepath}')

        elif address == '/saved_current_preset_to_file':
            #
            # The current settings have been saved to a preset file
            #

            # Get the filepath and store it
            self._curr_preset_filepath = Path(args[0])

            Logger.info(f'{address}: {self._curr_preset_filepath}')

        elif address == '/saved_memory_slot_to_file':
            #
            # A Nymphes memory slot has been saved to a preset file
            #

            # Get the filepath
            file_path = Path(args[0])

            # Get the memory slot info
            preset_type = str(args[1])
            bank_name = str(args[2])
            preset_number = int(args[3])

            Logger.info(f'{address}: {file_path} {preset_type} {bank_name}{preset_number}')

        elif address == '/loaded_file_into_nymphes_memory_slot':
            #
            # A preset file has been loaded into one of Nymphes'
            # memory slots
            #

            # Get the filepath
            file_path = Path(args[0])

            # Get the memory slot info
            preset_type = str(args[1])
            bank_name = str(args[2])
            preset_number = int(args[3])

            Logger.info(f'{address}: {file_path} {preset_type} {bank_name}{preset_number}')

        elif address == '/loaded_current_preset_into_nymphes_memory_slot':
            #
            # The current settings have been loaded into one of
            # Nymphes' memory slots
            #

            # Get the memory slot info
            preset_type = str(args[0])
            bank_name = str(args[1])
            preset_number = int(args[2])

            Logger.info(f'{address}: {preset_type} {bank_name}{preset_number}')

        elif address == '/requested_preset_dump':
            #
            # A full preset dump has been requested
            #
            Logger.info(f'{address}')

        elif address == '/received_preset_dump_from_nymphes':
            #
            # A single preset from a memory slot has been received
            # from Nymphes as a persistent import type SYSEX message
            #

            # Get the memory slot info
            preset_type = str(args[0])
            bank_name = str(args[1])
            preset_number = int(args[2])

            Logger.info(f'{address}: {preset_type} {bank_name}{preset_number}')

        elif address == '/loaded_preset_dump_from_midi_input_into_nymphes_memory_slot':
            #
            # A persistent preset import type SYSEX message has been
            # received from a MIDI input port.
            #

            # Get the port name
            port_name = str(args[0])

            # Get the memory slot info
            preset_type = str(args[1])
            bank_name = str(args[2])
            preset_number = int(args[3])

            Logger.info(f'{address}: {port_name} {preset_type} {bank_name}{preset_number}')

        elif address == '/midi_input_detected':
            #
            # A MIDI input port has been detected
            #

            # Get the name of the port
            port_name = str(args[0])

            # Add it to our list of detected MIDI input ports
            if port_name not in self._detected_midi_inputs:
                self._detected_midi_inputs.append(port_name)

            Logger.info(f'{address} {port_name}')

        elif address == '/midi_input_no_longer_detected':
            #
            # A previously-detected MIDI input port is no longer found
            #

            # Get the name of the port
            port_name = str(args[0])

            # Remove it from our list of detected MIDI input ports
            if port_name in self._detected_midi_inputs:
                self._detected_midi_inputs.remove(port_name)

            Logger.info(f'{address} {port_name}')
                
        elif address == '/detected_midi_inputs':
            #
            # A full list of detected MIDI input ports has been sent
            #
        
            # Get the port names
            port_names = []
            for arg in args:
                port_names.append(str(arg))
                
            # Replace our list of detected MIDI inputs
            self._detected_midi_inputs = port_names

            Logger.info(f'{address} {args}')

        elif address == '/midi_input_connected':
            #
            # A MIDI input port has been connected
            #

            # Get the name of the port
            port_name = str(args[0])

            # Add it to our list of connected MIDI input ports
            if port_name not in self._connected_midi_inputs:
                self._connected_midi_inputs.append(port_name)

            Logger.info(f'{address} {port_name}')

        elif address == '/midi_input_disconnected':
            #
            # A previously-connected MIDI input port has been disconnected
            #

            # Get the name of the port
            port_name = str(args[0])

            # Remove it from our list of connected MIDI input ports
            if port_name in self._connected_midi_inputs:
                self._connected_midi_inputs.remove(port_name)

            Logger.info(f'{address} {port_name}')

        elif address == '/connected_midi_inputs':
            #
            # A full list of connected MIDI input ports has been sent
            #

            # Get the port names
            port_names = []
            for arg in args:
                port_names.append(str(arg))

            # Replace our list of connected MIDI inputs
            self._connected_midi_inputs = port_names

            Logger.info(f'{address} {args}')

        elif address == '/midi_output_detected':
            #
            # A MIDI output port has been detected
            #

            # Get the name of the port
            port_name = str(args[0])

            # Add it to our list of detected MIDI output ports
            if port_name not in self._detected_midi_outputs:
                self._detected_midi_outputs.append(port_name)

            Logger.info(f'{address} {port_name}')

        elif address == '/midi_output_no_longer_detected':
            #
            # A previously-detected MIDI output port is no longer found
            #

            # Get the name of the port
            port_name = str(args[0])

            # Remove it from our list of detected MIDI output ports
            if port_name in self._detected_midi_outputs:
                self._detected_midi_outputs.remove(port_name)

            Logger.info(f'{address} {port_name}')

        elif address == '/detected_midi_outputs':
            #
            # A full list of detected MIDI output ports has been sent
            #

            # Get the port names
            port_names = []
            for arg in args:
                port_names.append(str(arg))

            # Replace our list of detected MIDI outputs
            self._detected_midi_outputs = port_names

            Logger.info(f'{address} {args}')

        elif address == '/midi_output_connected':
            #
            # A MIDI output port has been connected
            #

            # Get the name of the port
            port_name = str(args[0])

            # Add it to our list of connected MIDI output ports
            if port_name not in self._connected_midi_outputs:
                self._connected_midi_outputs.append(port_name)

            Logger.info(f'{address} {port_name}')

        elif address == '/midi_output_disconnected':
            #
            # A previously-connected MIDI output port has been disconnected
            #

            # Get the name of the port
            port_name = str(args[0])

            # Remove it from our list of connected MIDI output ports
            if port_name in self._connected_midi_outputs:
                self._connected_midi_outputs.remove(port_name)

            Logger.info(f'{address} {port_name}')

        elif address == '/connected_midi_outputs':
            #
            # A full list of connected MIDI output ports has been sent
            #

            # Get the port names
            port_names = []
            for arg in args:
                port_names.append(str(arg))

            # Replace our list of connected MIDI outputs
            self._connected_midi_outputs = port_names

            Logger.info(f'{address} {args}')

        elif address == '/mod_wheel':
            self._mod_wheel = int(args[0])
            Logger.debug(f'{address}: {self._mod_wheel}')

        elif address == '/velocity':
            self._velocity = int(args[0])
            Logger.debug(f'{address}: {self._velocity}')

        elif address == '/aftertouch':
            self._aftertouch = int(args[0])
            Logger.debug(f'{address}: {self._aftertouch}')
            
        elif address == '/sustain_pedal':
            self._sustain_pedal = int(args[0])
            Logger.debug(f'{address}: {self._sustain_pedal}')

        elif address == '/nymphes_midi_channel_changed':
            self._nymphes_midi_channel = int(args[0])
            Logger.debug(f'{address}: {self._nymphes_midi_channel}')

        elif address == '/status':
            Logger.info(f'{address}: {args[0]}')

        elif address == '/legato':
            self._legato = bool(args[0])
            Logger.debug(f'{address}: {self._legato}')

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

                    # Use a float to represent the value
                    # only if needed to capture it.
                    # Otherwise use an int.
                    #
                    float_value = round(args[0], NymphesPreset.float_precision_num_decimals)
                    int_value = int(args[0])

                    if float_value - int_value >= (1.0 / NymphesPreset.float_precision_num_decimals):
                        # We need to use the float value
                        value = float_value
                    else:
                        # We can use the int value
                        value = int_value

                else:
                    #
                    # This is an integer value
                    #
                    value = int(args[0])

                # Set our property for this parameter
                setattr(self, param_name.replace('.', '_'), value)

                Logger.debug(f'Received param name {param_name}: {args[0]}')

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

            Logger.info(f'{address} ({host_name}:{port})')

        elif address == '/client_unregistered':
            # Get the hostname and port
            #
            host_name = str(args[0])
            port = int(args[1])

            # We are no longer connected to the Encoders device
            self._connected_to_encoders = False

            Logger.info(f'{address} ({host_name}:{port})')

    def _start_nymphes_osc_subprocess(self):
        """
        Start the nymphes_osc subprocess, which handles all
        communication with the Nymphes synthesizer and with
        which we communicate with via OSC.
        :return:
        """
        try:
            arguments = ['--server_host', self._nymphes_osc_outgoing_host,
                         '--server_port', str(self._nymphes_osc_outgoing_port),
                         '--client_host', self._nymphes_osc_incoming_host,
                         '--client_port', str(self._nymphes_osc_incoming_port),
                         '--midi_channel', str(self._nymphes_midi_channel),
                         '--osc_log_level', 'warning',
                         '--midi_log_level', 'warning']
            command = ['python', '-m', 'nymphes_osc'] + arguments
            self._nymphes_osc_subprocess = subprocess.Popen(
                command,
                text=True
            )

            Logger.info('Started the nymphes_osc subprocess')

        except Exception as e:
            Logger.critical(f'Failed to start the nymphes_osc subprocess')

    def _stop_nymphes_osc_subprocess(self):
        """
        Stop the nymphes_osc subprocess if it is running
        :return:
        """
        Logger.info('Stopping the nymphes_osc subprocess')
        if self._nymphes_osc_subprocess is not None:
            if self._nymphes_osc_subprocess.poll() is None:
                self._nymphes_osc_subprocess.terminate()
                self._nymphes_osc_subprocess.wait()

    def on_stop(self):
        """
        The app is about to close.
        :return:
        """
        Logger.info('on_stop')

        # Stop the OSC servers
        self._stop_nymphes_osc_server()
        self._stop_encoder_osc_server()

        # Stop the nymphes_osc subprocess
        self._stop_nymphes_osc_subprocess()

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

    def preset_spinner_text_changed(self, preset_index, preset_text):
        Logger.debug(f'preset_spinner_text_changed: {preset_index}')
        self.load_preset_by_index(preset_index)

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
        if preset_index < 0 or preset_index >= len(NymphesGuiApp.presets_spinner_values_list()):
            raise Exception(f'Invalid preset_index: {preset_index}')

        # Parse preset_index into preset type, bank and number
        preset_info = NymphesGuiApp.parse_preset_index(preset_index)

        # Load the preset
        self.load_preset(preset_info['bank_name'],
                         preset_info['preset_num'],
                         preset_info['preset_type'])

    def load_preset(self, bank_name, preset_num, preset_type):
        # TODO: Fix this
        self._send_nymphes_osc(
            '/load_preset',
            bank_name,
            preset_num,
            preset_type
        )

    #
    # Preset File Handling
    #

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        self.dismiss_popup()

        Logger.debug(f'load path: {path}, filename: {filename}')

        # Send message to nymphes controller to load the preset file
        # TODO: Fix this
        self._send_nymphes_osc('/load_preset_file', filename)

    def save(self, path, filename):
        Logger.debug(f'save path: {path}, filename: {filename}')

        self.dismiss_popup()

    def load_next_preset(self):
        if self.curr_preset_index is None:
            # No preset was loaded, so choose the first one
            preset_index = 0
        else:
            preset_index = (self.curr_preset_index + 1) % len(NymphesGuiApp.presets_spinner_values_list())

        self.load_preset_by_index(preset_index)

    def load_prev_preset(self):
        if self.curr_preset_index is None or self.curr_preset_index == 0:
            # Choose the last preset
            preset_index = len(NymphesGuiApp.presets_spinner_values_list()) - 1
        else:
            preset_index = self.curr_preset_index - 1

        self.load_preset_by_index(preset_index)

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
            info("Connected to Encoders")

        elif address == '/client_removed':
            # We are no longer the encoders' client
            self._connected_to_encoders = False
            info("Disconnected from Encoders")

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

    def set_prop_value(self, prop_name, value):
        # Update the property's value
        setattr(self, prop_name, value)

        # Send an OSC message for this parameter with the new value
        self._send_nymphes_osc(f'/{prop_name.replace("_", "/")}', value)

    def get_prop_value_for_param_name(self, param_name):
        # Convert the parameter name to the name
        # of our corresponding property
        property_name = param_name.replace('.', '_')

        # Get the property's current value
        return getattr(self, property_name)

    def set_prop_value_for_param_name(self, param_name, value):
        # Convert the parameter name to the name
        # of our corresponding property
        property_name = param_name.replace('.', '_')

        # Set the property's value
        self.set_prop_value(property_name, value)

    def increment_prop_value_for_param_name(self, param_name, amount):
        Logger.debug(f'increment_param: {param_name} {amount}')

        # Convert the parameter name to the name
        # of our corresponding property
        property_name = param_name.replace('.', '_')

        # Get the property's current value
        curr_val = getattr(self, property_name)

        # Calculate the new value
        new_val = curr_val + amount

        # If the increment was an integer, then
        # round the new value to the nearest int
        if isinstance(amount, int):
            new_val = int(round(new_val))

        # Make sure the value is within the correct bounds
        min_val = NymphesPreset.min_val_for_param_name(param_name)
        max_val = NymphesPreset.max_val_for_param_name(param_name)

        if new_val < min_val:
            new_val = min_val

        if new_val > max_val:
            new_val = max_val

        # Set the property's value
        self.set_prop_value(property_name, new_val)


class ParamValueLabel(ButtonBehavior, Label):
    section_name = StringProperty('')
    param_name = StringProperty('')
    drag_start_pos = NumericProperty(0)

    def handle_touch(self, device, button):
        if device == 'mouse':
            if button == 'scrollup':
                App.get_running_app().increment_prop_value_for_param_name(self.param_name + '.value', 1)
            elif button == 'scrolldown':
                App.get_running_app().increment_prop_value_for_param_name(self.param_name + '.value', -1)

        else:
            Logger.debug(f'{self.param_name} {device} {button}')

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.button == 'left':
            touch.grab(self)

            # Store the starting y position of the touch
            self.drag_start_pos = int(touch.pos[1])

            return True
        return super(ParamValueLabel, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current == self:
            # Get the current y position
            curr_pos = int(touch.pos[1])

            # Calculate the distance from the starting drag position
            curr_drag_distance = (self.drag_start_pos - curr_pos) * -1

            # Get the current value of the property and the min and max limits
            # for the parameter
            param_name = self.param_name + '.value'
            curr_val = App.get_running_app().get_prop_value_for_param_name(param_name)
            min_val = NymphesPreset.min_val_for_param_name(param_name)
            max_val = NymphesPreset.max_val_for_param_name(param_name)

            # Scale the drag distance and use as the increment
            increment_amount = round(curr_drag_distance * 0.1)

            # Calculate new value and make sure we don't exceed the
            # value's bounds
            new_val = curr_val + increment_amount
            if min_val <= new_val <= max_val:
                # Set the parameter to the new value
                App.get_running_app().set_prop_value_for_param_name(param_name, new_val)

            else:
                if new_val < min_val:
                    # Set the parameter to the min value
                    App.get_running_app().set_prop_value_for_param_name(param_name, min_val)

                elif new_val > max_val:
                    # Set the parameter to the max value
                    App.get_running_app().set_prop_value_for_param_name(param_name, max_val)

            # Reset the drag start position to the current position
            self.drag_start_pos = curr_pos

            return True

        return super(ParamValueLabel, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            touch.ungrab(self)
            return True
        return super(ParamValueLabel, self).on_touch_up(touch)

    # def on_touch_down(self, touch):
    #     if super(ParamValueLabel, self).on_touch_down(touch):
    #         return True
    #
    #     Logger.debug(f'{touch.device} {touch.button}')
    #
    #     if touch.device == 'mouse':
    #         if touch.button == 'scrollup':
    #             app = App.get_running_app()
    #             app.increment_param(self.param_name)
    #             self.curr_value += 1
    #             return True
    #
    #         elif touch.button == 'scrolldown':
    #             app = App.get_running_app()
    #             app.decrement_param(self.param_name)
    #             return True
    #
    #     return False

    # def on_touch_up(self, touch):
    #     if super(ParamValueLabel, self).on_touch_up(touch):
    #         return True
    #
    #     if 'button' in touch.profile and touch.button.find('scroll') != -1:
    #         Logger.debug('Mouse wheel up')
    #         return True
    #
    #     return False

    # def on_scroll(self, instance, x, y, dx, dy):
    #     Logger.debug(f'{self.text} on_scroll: dx {dx} dy {dy}')


class ParamsGridModCell(BoxLayout):
    name_label_font_size = NumericProperty(14)
    section_name = StringProperty('')
    title = StringProperty('')
    param_name = StringProperty('')

    value_prop = NumericProperty(0)
    lfo2_prop = NumericProperty(0)
    mod_wheel_prop = NumericProperty(0)
    velocity_prop = NumericProperty(0)
    aftertouch_prop = NumericProperty(0)


class ParamsGridNonModCell(ButtonBehavior, BoxLayout):
    name_label_font_size = NumericProperty(14)
    section_name = StringProperty('')
    title = StringProperty('')
    param_name = StringProperty('')
    value_prop = NumericProperty(0)


class ParamsGridLfoConfigCell(ButtonBehavior, BoxLayout):
    name_label_font_size = NumericProperty(14)
    section_name = StringProperty('')
    type_prop = NumericProperty(0)
    key_sync_prop = NumericProperty(0)


class ParamsGridPlaceholderCell(Widget):
    pass


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)


class ModAmountLine(Widget):
    midi_val = NumericProperty(0) # This is 0 to 127
    color_hex = StringProperty('#FFFFFFFF')


class PlayModeButton(ButtonBehavior, Label):
    play_mode_name = StringProperty('')


class PlayModeSectionBox(BoxLayout):
    corner_radius = NumericProperty(20)


class LegatoSectionBox(BoxLayout):
    corner_radius = NumericProperty(20)


class SectionRelativeLayout(RelativeLayout):
    corner_radius = NumericProperty(12)
    section_name = StringProperty('')


class SectionTitleLabel(ButtonBehavior, Label):
    pass

#class OscillatorSectionBox(SectionRelativeLayout):
    # def __init__(self, **kwargs):
    #     super(OscillatorSectionBox, self).__init__(**kwargs)
    #
    #     section_title_label = SectionTitleLabel(text='OSCILLATOR')
    #     section_title_label.id = 'section_title_label'






class ParameterBox(ButtonBehavior, BoxLayout):
    name = StringProperty('NAME')
    value = NumericProperty(0)
    lfo2 = NumericProperty(0)
    wheel = NumericProperty(0)
    velocity = NumericProperty(0)
    aftertouch = NumericProperty(0)

    def on_release(self):
        # Create a popup
        popup = ModParameterPopup(title=self.name)
        popup.name = self.name
        popup.value = self.value
        popup.lfo2 = self.lfo2
        popup.wheel = self.wheel
        popup.velocity = self.velocity
        popup.aftertouch = self.aftertouch
        popup.open()


class ModParameterPopup(Popup):
    name = StringProperty('NAME')
    value = NumericProperty(0)
    lfo2 = NumericProperty(0)
    wheel = NumericProperty(0)
    velocity = NumericProperty(0)
    aftertouch = NumericProperty(0)

    def on_value_slider(self, new_value):
        self.value = new_value


class ModAmountsBox(BoxLayout):
    lfo2_prop = NumericProperty(0)
    mod_wheel_prop = NumericProperty(0)
    velocity_prop = NumericProperty(0)
    aftertouch_prop = NumericProperty(0)
