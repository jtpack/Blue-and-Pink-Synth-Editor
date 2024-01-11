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
import logging
from logging.handlers import RotatingFileHandler
import subprocess

kivy.require('2.1.0')
Config.read('app_config.ini')

#
# Logger Config
#

# Create logs directory if necessary
logs_directory_path = Path(Path(__file__).resolve().parent / 'logs/')
if not logs_directory_path.exists():
    logs_directory_path.mkdir()

# Get the root logger
root_logger = logging.getLogger()

# Formatter for logs
log_formatter = logging.Formatter(
    '%(asctime)s.%(msecs)03d - NymphesGUI  - %(levelname)s - %(message)s',
    datefmt='%Y-%d-%m %H:%M:%S'
)

# Handler for logging to files
file_handler = RotatingFileHandler(
    logs_directory_path / 'nymphes_gui.txt',
    maxBytes=1024,
    backupCount=3
)
file_handler.setFormatter(log_formatter)

# Handler for logging to the console
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# Get the logger for this module
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


class ParamsGridModCell(ButtonBehavior, BoxLayout):
    property_name = StringProperty('')
    nymphes_property = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    name_label_font_size = NumericProperty(14)
    section_name = StringProperty('')


class ParamsGridNonModCell(ButtonBehavior, BoxLayout):
    property_name = StringProperty('')
    nymphes_property = DictProperty({'value': 0})
    name_label_font_size = NumericProperty(14)
    section_name = StringProperty('')


class ParamsGridLfoConfigCell(ButtonBehavior, BoxLayout):
    nymphes_property = DictProperty({'type': 0, 'key_sync': 0})
    name_label_font_size = NumericProperty(14)
    section_name = StringProperty('')


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
    lfo2 = NumericProperty(0)
    wheel = NumericProperty(0)
    velocity = NumericProperty(0)
    aftertouch = NumericProperty(0)


class NymphesGuiApp(App):

    #
    # Properties and constants related to Encoders
    #

    # The encoders that control synthesizer parameters
    # go before the preset encoder
    num_param_encoders = 5

    # Encoder for controller presets. It is the last encoder
    preset_encoder_num = num_param_encoders

    encoder_display_names = ListProperty([''] * num_param_encoders)
    encoder_display_types = ListProperty([''] * num_param_encoders)
    encoder_display_values = ListProperty([''] * num_param_encoders)

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
    presets_spinner_values = ListProperty(NymphesGuiApp.presets_spinner_values_list())

    selected_section = StringProperty('')

    #
    # Nymphes Parameters
    #

    play_mode_name = StringProperty('POLY')
    legato = BooleanProperty(False)
    mod_source = NumericProperty(0)
    main_level = DictProperty({'value': 0})

    # Oscillator
    osc_wave = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    osc_pulsewidth = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})

    # Pitch
    pitch_detune = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    pitch_glide = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    pitch_chord = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    pitch_env_depth = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    pitch_lfo1 = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})

    # Amp
    amp_attack = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    amp_decay = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    amp_sustain = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    amp_release = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})

    # Mix
    mix_osc = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    mix_sub = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    mix_noise = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})

    # Filter 1
    lpf_cutoff = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    lpf_resonance = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    lpf_tracking = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})

    # Filter 2
    lpf_lfo1 = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    lpf_env_depth = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    hpf_cutoff = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})

    # Pitch / Filter Envelope
    pitch_filter_env_attack = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    pitch_filter_env_decay = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    pitch_filter_env_sustain = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    pitch_filter_env_release = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})

    # LFO1 (Filter / Pitch)
    lfo1_rate = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    lfo1_wave = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    lfo1_delay = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    lfo1_fade = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    lfo1_config = DictProperty({'type': 0, 'key_sync': 0})

    # LFO2
    lfo2_rate = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    lfo2_wave = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    lfo2_delay = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    lfo2_fade = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    lfo2_config = DictProperty({'type': 0, 'key_sync': 0})

    # Reverb
    reverb_size = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    reverb_decay = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    reverb_filter = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})
    reverb_mix = DictProperty({'value': 0, 'lfo2': 0, 'wheel': 0, 'velocity': 0, 'aftertouch': 0})

    #
    # Preset File Handling
    #

    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)

    def __init__(self, log_level=logging.INFO, **kwargs):
        super(NymphesGuiApp, self).__init__(**kwargs)

        # Set logger level
        logger.setLevel(log_level)

        #
        # Encoder Properties
        #
        self._encoder_bindings = {i: {'property_name': None, 'function': None} for i in range(self.num_param_encoders)}
        self._encoder_property_dict_key = [None] * self.num_param_encoders
        self._encoder_property_osc_addresses = [''] * self.num_param_encoders
        self._encoder_property_osc_value_maps = [None] * self.num_param_encoders
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
            logger.warning(f'Failed to create Encoders OSC client ({e})')
            
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
            logger.info(f'Using incoming host from config file for Nymphes OSC communication: {self._nymphes_osc_incoming_host}')

        else:
            #
            # Incoming host is not specified.
            # Try to automatically determine the local ip address
            #

            in_host = self._get_local_ip_address()
            self._nymphes_osc_incoming_host = in_host
            logger.info(f'Using detected local ip address for NYMPHES_OSC communication: {in_host}')

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
            logger.info(f'Using incoming host from config file for Encoder OSC communication: {self._encoder_osc_incoming_host}')

        else:
            #
            # Incoming host is not specified.
            # Try to automatically determine the local ip address
            #

            in_host = self._get_local_ip_address()
            self._encoder_osc_incoming_host = in_host
            logger.info(f'Using detected local ip address for Encoder OSC communication: {in_host}')

        self._encoder_osc_incoming_port = int(config['ENCODER_OSC']['incoming port'])

        #
        # Preset Files Path
        #
        if config.has_option('PRESETS', 'presets folder path'):
            self._presets_folder_path = Path(config['PRESETS']['presets folder path'])
        else:
            self._presets_folder_path = None

    def _reload_config_file(self):
        logger.info(f'Reloading config file at {self._config_file_path}')
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

        logger.info(f'Created config file at {filepath}')

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
                logger.warning(f'Failed to detect local IP address ({e})')

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

        logger.info(f'Started Nymphes OSC Server at {self._nymphes_osc_incoming_host}:{self._nymphes_osc_incoming_port}')

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
            logger.info('Stopped Nymphes OSC Server')

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

        logger.info(f'Started Encoder OSC Server at {self._encoder_osc_incoming_host}:{self._encoder_osc_incoming_port}')

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
            logger.info('Stopped Encoder OSC Server')

    def _register_as_nymphes_osc_client(self):
        """
        Register as a client with nymphes-osc by sending it a
        /register_client OSC message
        :return:
        """

        # To connect to the nymphes_osc server, we need
        # to send it a /register_host OSC message
        # with the port we are listening on.
        logger.info(f'Registering as client with nymphes-osc server at {self._nymphes_osc_outgoing_host}:{self._nymphes_osc_outgoing_port}...')
        self._send_nymphes_osc('/register_client', self._nymphes_osc_incoming_port)

    def _register_as_encoders_osc_client(self):
        """
        Register as a client with the Encoders device by sending it a
        /register_client OSC message
        :return:
        """
        if self._encoder_osc_client is not None:
            logger.info(f'Registering as client with Encoders server at {self._encoder_osc_outgoing_host}:{self._encoder_osc_outgoing_port}...')
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

        logger.debug(f'send_nymphes_osc: {address}, {[str(arg) + " " for arg in args]}')

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

            logger.debug(f'send_encoder_osc: {address}, {[str(arg) + " " for arg in args]}')

    def _on_nymphes_osc_message(self, address, *args):
        """
        An OSC message has been received from nymphes-osc
        :param address: str
        :param args: A list of arguments
        :return:
        """
        logger.debug(f'Received OSC Message from nymphes-osc: {address}, {[str(arg) + " " for arg in args]}')

        # App Status Messages
        #
        if address == '/client_registered':
            # Get the hostname and port
            #
            host_name = str(args[0])
            port = int(args[1])

            # We are connected to nymphes_osc
            self._connected_to_nymphes_osc = True

            logger.info(f'{address} ({host_name}:{port})')

        elif address == '/client_unregistered':
            # Get the hostname and port
            #
            host_name = str(args[0])
            port = int(args[1])

            # We are no longer connected to nymphes-osc
            self._connected_to_nymphes_osc = False

            logger.info(f'{address} ({host_name}:{port})')

        elif address == '/nymphes_connected':
            #
            # nymphes_midi has connected to a Nymphes synthesizer
            #

            # Get the names of the MIDI input and output ports
            self._nymphes_input_port = str(args[0])
            self._nymphes_output_port = str(args[1])

            # Update app state
            self._nymphes_connected = True

            logger.info(f'{address} (input_port: {self._nymphes_input_port}, output_port: {self._nymphes_output_port})')

        elif address == '/nymphes_disconnected':
            #
            # nymphes_midi is no longer connected to a Nymphes synthesizer
            #

            # Update app state
            self._nymphes_connected = False
            self._nymphes_input_port = None
            self._nymphes_output_port = None

            logger.info(f'{address}')

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

            logger.info(f'{address} ({self._curr_preset_type} {self._curr_preset_bank_and_number[0]}{self._curr_preset_bank_and_number[1]})')

        elif address == '/received_current_preset_from_midi_input_port':
            port_name = str(args[0])
            self._curr_preset_type = str(args[1])
            self._curr_preset_bank_and_number = str(args[2]), int(args[3])

            logger.info(
                f'{address} ({port_name}: {self._curr_preset_type} {self._curr_preset_bank_and_number[0]}{self._curr_preset_bank_and_number[1]})')

        elif address == '/loaded_file_into_current_preset':
            #
            # A preset file was loaded into Nymphes' current settings
            #

            # Get the filepath and store it
            self._curr_preset_filepath = Path(args[0])
            self._curr_preset_type = None
            self._curr_preset_bank_and_number = None, None

            logger.info(f'{address}: {self._curr_preset_filepath}')

        elif address == '/saved_current_preset_to_file':
            #
            # The current settings have been saved to a preset file
            #

            # Get the filepath and store it
            self._curr_preset_filepath = Path(args[0])

            logger.info(f'{address}: {self._curr_preset_filepath}')

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

            logger.info(f'{address}: {file_path} {preset_type} {bank_name}{preset_number}')

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

            logger.info(f'{address}: {file_path} {preset_type} {bank_name}{preset_number}')

        elif address == '/loaded_current_preset_into_nymphes_memory_slot':
            #
            # The current settings have been loaded into one of
            # Nymphes' memory slots
            #

            # Get the memory slot info
            preset_type = str(args[0])
            bank_name = str(args[1])
            preset_number = int(args[2])

            logger.info(f'{address}: {preset_type} {bank_name}{preset_number}')

        elif address == '/requested_preset_dump':
            #
            # A full preset dump has been requested
            #
            logger.info(f'{address}')

        elif address == '/received_preset_dump_from_nymphes':
            #
            # A single preset from a memory slot has been received
            # from Nymphes as a persistent import type SYSEX message
            #

            # Get the memory slot info
            preset_type = str(args[0])
            bank_name = str(args[1])
            preset_number = int(args[2])

            logger.info(f'{address}: {preset_type} {bank_name}{preset_number}')

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

            logger.info(f'{address}: {port_name} {preset_type} {bank_name}{preset_number}')

        elif address == '/midi_input_detected':
            #
            # A MIDI input port has been detected
            #

            # Get the name of the port
            port_name = str(args[0])

            # Add it to our list of detected MIDI input ports
            if port_name not in self._detected_midi_inputs:
                self._detected_midi_inputs.append(port_name)

            logger.info(f'{address} {port_name}')

        elif address == '/midi_input_no_longer_detected':
            #
            # A previously-detected MIDI input port is no longer found
            #

            # Get the name of the port
            port_name = str(args[0])

            # Remove it from our list of detected MIDI input ports
            if port_name in self._detected_midi_inputs:
                self._detected_midi_inputs.remove(port_name)

            logger.info(f'{address} {port_name}')
                
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

            logger.info(f'{address} {args}')

        elif address == '/midi_input_connected':
            #
            # A MIDI input port has been connected
            #

            # Get the name of the port
            port_name = str(args[0])

            # Add it to our list of connected MIDI input ports
            if port_name not in self._connected_midi_inputs:
                self._connected_midi_inputs.append(port_name)

            logger.info(f'{address} {port_name}')

        elif address == '/midi_input_disconnected':
            #
            # A previously-connected MIDI input port has been disconnected
            #

            # Get the name of the port
            port_name = str(args[0])

            # Remove it from our list of connected MIDI input ports
            if port_name in self._connected_midi_inputs:
                self._connected_midi_inputs.remove(port_name)

            logger.info(f'{address} {port_name}')

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

            logger.info(f'{address} {args}')

        elif address == '/midi_output_detected':
            #
            # A MIDI output port has been detected
            #

            # Get the name of the port
            port_name = str(args[0])

            # Add it to our list of detected MIDI output ports
            if port_name not in self._detected_midi_outputs:
                self._detected_midi_outputs.append(port_name)

            logger.info(f'{address} {port_name}')

        elif address == '/midi_output_no_longer_detected':
            #
            # A previously-detected MIDI output port is no longer found
            #

            # Get the name of the port
            port_name = str(args[0])

            # Remove it from our list of detected MIDI output ports
            if port_name in self._detected_midi_outputs:
                self._detected_midi_outputs.remove(port_name)

            logger.info(f'{address} {port_name}')

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

            logger.info(f'{address} {args}')

        elif address == '/midi_output_connected':
            #
            # A MIDI output port has been connected
            #

            # Get the name of the port
            port_name = str(args[0])

            # Add it to our list of connected MIDI output ports
            if port_name not in self._connected_midi_outputs:
                self._connected_midi_outputs.append(port_name)

            logger.info(f'{address} {port_name}')

        elif address == '/midi_output_disconnected':
            #
            # A previously-connected MIDI output port has been disconnected
            #

            # Get the name of the port
            port_name = str(args[0])

            # Remove it from our list of connected MIDI output ports
            if port_name in self._connected_midi_outputs:
                self._connected_midi_outputs.remove(port_name)

            logger.info(f'{address} {port_name}')

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

            logger.info(f'{address} {args}')

        elif address == '/mod_wheel':
            self._mod_wheel = int(args[0])
            logger.debug(f'{address}: {self._mod_wheel}')

        elif address == '/velocity':
            self._velocity = int(args[0])
            logger.debug(f'{address}: {self._velocity}')

        elif address == '/aftertouch':
            self._aftertouch = int(args[0])
            logger.debug(f'{address}: {self._aftertouch}')
            
        elif address == '/sustain_pedal':
            self._sustain_pedal = int(args[0])
            logger.debug(f'{address}: {self._sustain_pedal}')

        elif address == '/nymphes_midi_channel_changed':
            self._nymphes_midi_channel = int(args[0])
            logger.debug(f'{address}: {self._nymphes_midi_channel}')

        elif address == '/status':
            logger.info(f'{address}: {args[0]}')

        elif address == '/legato':
            self._legato = bool(args[0])
            logger.debug(f'{address}: {self._legato}')

        else:
            logger.info(f'Received unhandled OSC message: {address}')

    def _on_encoder_osc_message(self, address, *args):
        """
        An OSC message has been received from the Encoders device
        :param address: str
        :param args: A list of arguments
        :return:
        """
        logger.debug(f'Received OSC Message from Encoders device: {address}, {[str(arg) + " " for arg in args]}')

        # App Status Messages
        #
        if address == '/client_registered':
            # Get the hostname and port
            #
            host_name = str(args[0])
            port = int(args[1])

            # We are connected to the Encoder device
            self._connected_to_encoders = True

            logger.info(f'{address} ({host_name}:{port})')

        elif address == '/client_unregistered':
            # Get the hostname and port
            #
            host_name = str(args[0])
            port = int(args[1])

            # We are no longer connected to the Encoders device
            self._connected_to_encoders = False

            logger.info(f'{address} ({host_name}:{port})')

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
                         '--osc_log_level', 'WARNING',
                         '--midi_log_level', 'WARNING']
            command = ['python', '-m', 'nymphes_osc'] + arguments
            self._nymphes_osc_subprocess = subprocess.Popen(
                command,
                text=True
            )

            logger.info('Started the nymphes_osc subprocess')

        except Exception as e:
            logger.critical(f'Failed to start the nymphes_osc subprocess')

    def _stop_nymphes_osc_subprocess(self):
        """
        Stop the nymphes_osc subprocess if it is running
        :return:
        """
        logger.info('Stopping the nymphes_osc subprocess')
        if self._nymphes_osc_subprocess is not None:
            if self._nymphes_osc_subprocess.poll() is None:
                self._nymphes_osc_subprocess.terminate()
                self._nymphes_osc_subprocess.wait()

    def on_stop(self):
        """
        The app is about to close.
        :return:
        """
        logger.info('on_stop')

        # Stop the OSC servers
        self._stop_nymphes_osc_server()
        self._stop_encoder_osc_server()

        # Stop the nymphes_osc subprocess
        self._stop_nymphes_osc_subprocess()

    @staticmethod
    def presets_spinner_values_list():
        """
        Returns a list of text values for the presets spinner to show.
        """
        return [f'{kind} {bank}{num}' for kind in ['USER', 'FACTORY'] for bank in ['A', 'B', 'C', 'D', 'E', 'F', 'G']
                for num in [1, 2, 3, 4, 5, 6, 7]]

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
        print(f'preset_spinner_text_changed: {preset_index}')
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

        print(f'load path: {path}, filename: {filename}')

        # Send message to nymphes controller to load the preset file
        # TODO: Fix this
        self._send_nymphes_osc('/load_preset_file', filename)

    def save(self, path, filename):
        print(f'save path: {path}, filename: {filename}')

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

    def update_encoder_led_color(self, encoder_num):
        # Get the name of the parameter for this encoder
        property_name = self._encoder_bindings[encoder_num]['property_name']

        if property_name is not None:
            # Get the dict key currently used by this encoder
            key = self._encoder_property_dict_key[encoder_num]
            print(f'update_encoder_led_color enc: {encoder_num} prop: {property_name} dict key: {key}')

            # Detemine color based on the dictionary key
            if key == 'value':
                led_red = 100
                led_green = 100
                led_blue = 100
                led_brightness = 1.0

            elif key == 'lfo2':
                led_red = 100
                led_green = 0
                led_blue = 0
                led_brightness = 1.0

            elif key == 'wheel':
                led_red = 100
                led_green = 100
                led_blue = 0
                led_brightness = 1.0

            elif key == 'velocity':
                led_red = 0
                led_green = 255
                led_blue = 0
                led_brightness = 1.0

            elif key == 'aftertouch':
                led_red = 0
                led_green = 0
                led_blue = 255
                led_brightness = 1.0

            elif key == 'type':
                led_red = 100
                led_green = 0
                led_blue = 100
                led_brightness = 1.0

            elif key == 'key_sync':
                led_red = 0
                led_green = 100
                led_blue = 100
                led_brightness = 1.0

        else:
            # The encoder is not being used at the moment
            led_red = 0
            led_green = 0
            led_blue = 0
            led_brightness = 0.0

        # Send OSC message
        self._send_encoder_osc(
            '/encoder_led_color',
            encoder_num,
            led_red,
            led_green,
            led_blue,
            led_brightness
        )

    def update_all_encoder_led_colors(self):
        for encoder_num in range(self.num_param_encoders):
            self.update_encoder_led_color(encoder_num)

    def on_encoder_osc_message(self, address, *args):
        """
        An OSC message has been received from the encoders.
        :param address: str
        :param args: A list of arguments
        :return:
        """

        # print(f'on_encoder_osc_message: {address}, {[str(arg) + " " for arg in args]}')

        if address == '/client_registered':
            # We have just successfully registered as the encoders'
            # client.
            self._connected_to_encoders = True
            print("Connected to Encoders")

        elif address == '/client_removed':
            # We are no longer the encoders' client
            self._connected_to_encoders = False
            print("Disconnected from Encoders")

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
            print(f'Received unrecognized OSC Message: {address}')

    def on_encoder_pos(self, encoder_num, encoder_pos):
        if encoder_num < self.preset_encoder_num:
            # This is a parameter encoder
            #

            # Get the DictProperty for this encoder
            prop_name = self._encoder_bindings[encoder_num]['property_name']
            prop_dict = getattr(self, prop_name)

            # Get the current dict key for the encoder
            dict_key = self._encoder_property_dict_key[encoder_num]

            # Determine min and max values for the current property
            #
            if dict_key == 'type':
                min_val = 0
                max_val = 3
            elif dict_key == 'key_sync':
                min_val = 0
                max_val = 1
            else:
                min_val = 0
                max_val = 127

            # Apply the encoder's new value to the property
            new_val = prop_dict[dict_key] + encoder_pos
            if new_val < min_val:
                new_val = min_val
            if new_val > max_val:
                new_val = max_val

            if new_val != prop_dict[dict_key]:
                # Store the new value
                prop_dict[dict_key] = new_val

                # Prepare an OSC message to update the nymphes with the new value
                address = self._encoder_property_osc_addresses[encoder_num]
                if dict_key in ['lfo2', 'wheel', 'velocity', 'aftertouch']:
                    address += f'/mod/{self._encoder_property_dict_key[encoder_num]}'
                else:
                    address += f'/{self._encoder_property_dict_key[encoder_num]}'

                    # Send it
                self._send_nymphes_osc(address, new_val)

        else:
            # This is the preset encoder
            print(f'Preset Encoder Pos: {encoder_pos}')
            if encoder_pos > 0:
                self.load_next_preset()
            elif encoder_pos < 0:
                self.load_prev_preset()

    def on_encoder_button_short_press_ended(self, encoder_num):
        if encoder_num < self.preset_encoder_num:
            # This is a parameter encoder
            #

            # When an encoder button is pressed, cycle through the
            # dict keys of the property that it is bound to,
            # from value through each of the mod sources

            # Get the DictProperty for this encoder
            prop_name = self._encoder_bindings[encoder_num]['property_name']
            prop_dict = getattr(self, prop_name)
            keys = list(prop_dict.keys())

            # Get the index of the current key
            i = keys.index(self._encoder_property_dict_key[encoder_num])

            # Increment it but wrap around if we get past the bounds of the list
            i = (i + 1) % len(keys)

            # Get the new key
            key = keys[i]

            # Update the encoder's key
            self._encoder_property_dict_key[encoder_num] = key

            # Update the encoder's value type and value displays
            #
            if key == 'key_sync':
                # Key Sync has two discrete values, displayed as strings.
                #

                # Set the encoder's value type display
                self.encoder_display_types[encoder_num] = 'KEY SYNC'

                # Get the current value for Key Sync
                key_sync_int = prop_dict[key]

                # Get the string representation
                key_sync_string = self.string_for_lfo_key_sync(key_sync_int)

                # Set the encoder's value display
                self.encoder_display_values[encoder_num] = key_sync_string

            elif key == 'type':
                # LFO Type has four discrete values, displayed as strings
                #

                # Set the encoder's value type display
                self.encoder_display_types[encoder_num] = 'TYPE'

                # Get the current value for LFO Type
                lfo_type_int = prop_dict[key]

                # Get its string representation
                lfo_type_string = self.string_for_lfo_type(lfo_type_int)

                # Set the encoder's value display
                self.encoder_display_values[encoder_num] = lfo_type_string

            else:
                # This is just a numerical property with values from 0 to 127
                #

                # Update the encoder type display
                self.encoder_display_types[encoder_num] = key

                # Update the encoder value display
                self.encoder_display_values[encoder_num] = str(prop_dict[key])

            # Also update the encoder's LED color
            self.update_encoder_led_color(encoder_num)

            print(f'on_encoder_button_short_press_ended: {key}')

        else:
            # This is the preset encoder
            print(f'Preset Encoder Short Pressed')

    def on_encoder_button_long_press_started(self, encoder_num):
        if encoder_num < self.preset_encoder_num:
            # This is a parameter encoder
            #

            # When an encoder button is long pressed,
            # reset its dictionary key to the first one

            # Get the DictProperty for this encoder
            prop_name = self._encoder_bindings[encoder_num]['property_name']
            prop_dict = getattr(self, prop_name)
            keys = list(prop_dict.keys())

            # Get the new key
            key = keys[0]

            # Update the encoder's key
            self._encoder_property_dict_key[encoder_num] = key

            # Update the encoder's value type and value displays
            #
            if key == 'key_sync':
                # Key Sync has two discrete values, displayed as strings.
                #

                # Set the encoder's value type display
                self.encoder_display_types[encoder_num] = 'KEY SYNC'

                # Get the current value for Key Sync
                key_sync_int = prop_dict[key]

                # Get the string representation
                key_sync_string = self.string_for_lfo_key_sync(key_sync_int)

                # Set the encoder's value display
                self.encoder_display_values[encoder_num] = key_sync_string

            elif key == 'type':
                # LFO Type has four discrete values, displayed as strings
                #

                # Set the encoder's value type display
                self.encoder_display_types[encoder_num] = 'TYPE'

                # Get the current value for LFO Type
                lfo_type_int = prop_dict[key]

                # Get its string representation
                lfo_type_string = self.string_for_lfo_type(lfo_type_int)

                # Set the encoder's value display
                self.encoder_display_values[encoder_num] = lfo_type_string

            else:
                # This is just a numerical property with values from 0 to 127
                #

                # Update the encoder type display
                self.encoder_display_types[encoder_num] = key

                # Update the encoder value display
                self.encoder_display_values[encoder_num] = str(prop_dict[key])

            # Also update the encoder's LED color
            self.update_encoder_led_color(encoder_num)

            print(f'on_encoder_button_long_press_started: {key}')

        else:
            # This is the preset encoder
            print(f'Preset Encoder Long Pressed')