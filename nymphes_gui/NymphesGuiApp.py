import kivy
from kivy.app import App
from kivy.config import Config
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


class NymphesGuiApp(App):

    def __init__(self, log_level=logging.INFO, **kwargs):
        super(NymphesGuiApp, self).__init__(**kwargs)

        # Set logger level
        logger.setLevel(log_level)

        #
        # nymphes-osc Subprocess, when it is started
        #
        self._nymphes_osc_subprocess = None

        #
        # OSC Communication Objects
        #

        self._nymphes_osc_incoming_host = None
        self._nymphes_osc_incoming_port = None
        self._nymphes_osc_outgoing_host = None
        self._nymphes_osc_outgoing_port = None

        self._nymphes_osc_client = None
        self._nymphes_osc_server = None
        self._nymphes_osc_server_thread = None
        self._nymphes_osc_dispatcher = Dispatcher()

        self._encoder_osc_incoming_host = None
        self._encoder_osc_incoming_port = None
        self._encoder_osc_outgoing_host = None
        self._encoder_osc_outgoing_port = None

        self._encoder_osc_client = None
        self._encoder_osc_server = None
        self._encoder_osc_server_thread = None
        self._encoder_osc_dispatcher = Dispatcher()

        self._connected_to_nymphes_osc = False
        self._connected_to_encoders = False

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
        #self._start_nymphes_osc_subprocess()

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
        # Register as client with nymphes-osc and Encoders device
        #
        self._register_as_nymphes_osc_client()
        self._register_as_encoders_osc_client()

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

        elif address == '/loaded_preset_dump_from_midi_input_port_into_nymphes_memory_slot':
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

        elif address == '/midi_input_port_detected':
            #
            # A MIDI input port has been detected
            #

            # Get the name of the port
            port_name = str(args[0])

            # Add it to our list of detected MIDI input ports
            if port_name not in self._detected_midi_inputs:
                self._detected_midi_inputs.append(port_name)

            logger.info(f'{address} {port_name}')

        elif address == '/midi_input_port_no_longer_detected':
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

        elif address == '/midi_input_port_connected':
            #
            # A MIDI input port has been connected
            #

            # Get the name of the port
            port_name = str(args[0])

            # Add it to our list of connected MIDI input ports
            if port_name not in self._connected_midi_inputs:
                self._connected_midi_inputs.append(port_name)

            logger.info(f'{address} {port_name}')

        elif address == '/midi_input_port_disconnected':
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

        elif address == '/midi_output_port_detected':
            #
            # A MIDI output port has been detected
            #

            # Get the name of the port
            port_name = str(args[0])

            # Add it to our list of detected MIDI output ports
            if port_name not in self._detected_midi_outputs:
                self._detected_midi_outputs.append(port_name)

            logger.info(f'{address} {port_name}')

        elif address == '/midi_output_port_no_longer_detected':
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

        elif address == '/midi_output_port_connected':
            #
            # A MIDI output port has been connected
            #

            # Get the name of the port
            port_name = str(args[0])

            # Add it to our list of connected MIDI output ports
            if port_name not in self._connected_midi_outputs:
                self._connected_midi_outputs.append(port_name)

            logger.info(f'{address} {port_name}')

        elif address == '/midi_output_port_disconnected':
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
            arguments = ['--port 1237', '--host 127.0.0.1', '--midi_channel 1', '--debug_osc']
            command = ['python', '-m', 'nymphes_osc'] + arguments
            self._nymphes_osc_subprocess = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
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

