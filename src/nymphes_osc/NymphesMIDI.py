import time
from queue import Queue
import copy
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
import mido
import mido.backends.rtmidi
from rtmidi import InvalidPortError
from src.nymphes_osc.NymphesPreset import NymphesPreset
from src.nymphes_osc.PresetEvents import PresetEvents
from src.nymphes_osc.MidiConnectionEvents import MidiConnectionEvents

# Create logs directory if necessary
logs_directory_path = Path(Path(__file__).resolve().parent / 'logs/')
if not logs_directory_path.exists():
    logs_directory_path.mkdir()

# Get the root logger
root_logger = logging.getLogger()

# Formatter for logs
log_formatter = logging.Formatter(
    '%(asctime)s.%(msecs)03d - NymphesMIDI - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Handler for logging to files
file_handler = RotatingFileHandler(
    logs_directory_path / 'nymphes_midi_log.txt',
    maxBytes=1024*1024*2,
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


class NymphesMIDI:
    """
    An object which allows full control of the Dreadbox Nymphes synthesizer via USB MIDI.
    """

    def __init__(
            self,
            notification_callback_function,
            log_level=logging.WARNING
    ):
        # Callback function for us to call with notifications.
        self._notification_callback_function = notification_callback_function

        # Set logger level
        logger.setLevel(log_level)

        # Construct filepath for the init preset file.
        # It will be in the same directory as this file.
        self.presets_directory_path = Path(__file__).resolve().parent / 'presets'

        # Create directory if it doesn't exist
        if not self.presets_directory_path.exists():
            try:
                self.presets_directory_path.mkdir()
                logger.info(f'Created presets directory at {self.presets_directory_path}')
            except Exception as e:
                logger.warning(f'Failed to create presets directory at {self.presets_directory_path} ({e})')

        # Construct the path to the init preset file
        self.init_preset_filepath = self.presets_directory_path / 'init.txt'

        # Create the init preset file if it does not exist
        #
        if not self.init_preset_filepath.exists():
            try:
                # Create a Nymphes Preset with default settings and write its
                # preset to disk
                p = NymphesPreset()
                p.save_preset_file(self.init_preset_filepath)
                logger.info(f'Created init preset file at {self.init_preset_filepath}')

            except Exception as e:
                logger.warning(f'Failed to create init preset file at {self.init_preset_filepath} ({e})')

        # Create the preset object used to track all current Nymphes parameter values
        try:
            self._curr_preset_object = NymphesPreset(filepath=self.init_preset_filepath)
            logger.info(f'Loaded init preset at {self.init_preset_filepath}')

        except Exception as e:
            logger.warning(f'Failed to load init preset at {self.init_preset_filepath} ({e})')

            # Create preset without loading init.txt
            self._curr_preset_object = NymphesPreset()

        # The MIDI channel to use when communicating with Nymphes.
        # This is non-zero-referenced, so 1 is channel 1.
        self._nymphes_midi_channel = 1

        # MIDI Input port for messages from Nymphes
        self._nymphes_midi_input_port_object = None

        # MIDI Output port for messages to Nymphes
        self._nymphes_midi_output_port_object = None

        # MIDI Port Scanning Timer
        self._midi_port_scan_interval_sec = 0.5
        self._midi_port_scan_last_timestamp = None

        # Names of Detected Non-Nymphes MIDI Ports
        self._detected_midi_inputs = []
        self._detected_midi_outputs = []

        # List of currently-connected MIDI ports
        self._connected_midi_input_port_objects = []
        self._connected_midi_output_port_objects = []

        # MIDI Message Receive Timer
        self._midi_message_receive_interval_sec = 0.0001
        self._midi_message_receive_last_timestamp = None

        # MIDI Message Send Queues

        # Queue for MIDI messages to be sent to Nymphes.
        # When Nymphes is not connected, the queue is deleted.
        self._nymphes_midi_message_send_queue = None

        # Queues for MIDI output ports. There will be one queue for
        # each connected MIDI output port.
        # When a MIDI output port is disconnected its queue is deleted.
        self._midi_message_send_queues = {}

        # Upon connecting to Nymphes, wait a short time and then
        # load the init preset file.
        # We use the timestamp below to schedule this.
        self._send_initial_preset_timestamp = None
        self._send_initial_preset_wait_time_sec = 0.1

        # After sending the initial preset, wait a short time and then
        # request a full preset dump via SYSEX.
        # We use the timestamp below to schedule the dump.
        self._send_full_sysex_dump_request_timestamp = None
        self._send_full_sysex_dump_request_wait_time_sec = 0.7

        #
        # When a preset is loaded on Nymphes, we receive the following:
        # 1. Bank MSB message (CC 0) indicating whether it is a user
        #    or factory preset
        # 2. Program Change message indicating preset bank and number
        # 3. SYSEX Message containing all preset data
        # 4. A series of MIDI CC messages representing most of the preset
        #    data (but not chord settings, as they are accessible only
        #    via SYSEX)
        #
        # We prefer to get all preset data using SYSEX, ignoring the
        # MIDI CCs that follow the SYSEX mesage, as SYSEX provides float
        # values for most of them and includes settings for chords.
        # However, on Windows, where we will likely not receive the SYSEX
        # message because it is larger than the hard-coded rtmidi message
        # receive size limit, we have to settle for getting the data via
        # MIDI CC.
        #

        # Once a preset has been load©ed, this will be
        # either 'user' or 'factory'
        self._curr_preset_type = None

        # Once a preset has been load©ed, this will contain
        # the bank name ('A' to 'G') and preset number (1 to 7)
        self._curr_preset_bank_and_number = (None, None)

        # When we receive a Program Change message from Nymphes, we know
        # that a preset has been load©ed and we can expect the preset's
        # data to follow as both SYSEX and MIDI CC.
        self._waiting_for_preset_data_from_nymphes = False
        self._waiting_for_preset_data_from_nymphes_until_timestamp = None
        self._waiting_for_preset_data_from_nymphes_duration_sec = 0.7

        # When a preset is loaded on Nymphes, upon receiving it via SYSEX
        # we need to ignore incoming MIDI Control Change messages from
        # Nymphes for a short time, as we already have all preset values
        # from the SYSEX message.
        self._ignore_control_change_messages_from_nymphes = False
        self._ignore_control_change_messages_from_nymphes_until_timestamp = None
        self._ignore_control_change_messages_from_nymphes_duration_sec = 0.5

        # Current Nymphes Mod Source
        # We track this so we can properly interpret incoming
        # modulation matrix MIDI CC messages
        self._curr_mod_source = 0

        # Preset objects for the presets in the Nymphes' memory.
        # If a full SYSEX dump has been done then we will have an
        # entry for every preset. If not, then we'll only have
        # entries for the presets that have been load©ed since
        # connecting to the Nymphes.
        # The dict key is a tuple. ie: For bank A, user preset 1: ('user', 'A', 1).
        # The value is a preset_pb2.preset object.
        self._nymphes_memory_slots_dict = {}

        # The key to the most-recently-loaded nymphes preset object
        self._curr_preset_dict_key = None

        # Flag indicating that a value in the current preset object has
        # been changed and we need to send the entire preset via SYSEX
        # to Nymphes and connected MIDI Output Ports.
        # This is only necessary when float parameter values have been
        # changed, or for int parameters with no associated MIDI CC
        # (ie: chord settings).
        self._preset_snapshot_needed = False
        self._preset_snapshot_timer_interval_sec = 0.1
        self._preset_snapshot_last_timestamp = None

        # A queue for notifying clients when things change.
        # It will contain dicts with the following keys:
        # 'name', 'value'
        self._notification_queue = Queue()

    @property
    def logging_enabled(self):
        return self._logging_enabled

    @logging_enabled.setter
    def logging_enabled(self, enable):
        self._logging_enabled = enable

    @property
    def nymphes_midi_channel(self):
        """
        This is not zero-referenced, so MIDI channel 1 will be returned as 1.
        :return:
        """
        return self._nymphes_midi_channel

    @nymphes_midi_channel.setter
    def nymphes_midi_channel(self, channel):
        """
        Set the MIDI channel used to communicate with Nymphes.
        Raises an Exception if channel is invalid.
        :param channel: (int) Must be between 1 and 16.
        :return:
        """
        # Validate channel
        if 1 > channel > 16:
            raise Exception(f'Invalid channel: {channel}')

        self._nymphes_midi_channel = channel

    @property
    def nymphes_connected(self):
        return self._nymphes_midi_input_port_object is not None and self._nymphes_midi_output_port_object is not None

    @property
    def nymphes_midi_ports(self):
        """
        Returns the names of the MIDI Input Port and Output Port
        for the connected Nymphes synthesizer.
        If no Nymphes is connected then return None.
        :return: Tuple containing two strings: (midi_input_port_name, midi_output_port_name)
        """
        if self.nymphes_connected:
            return self._nymphes_midi_input_port_object.name, self._nymphes_midi_output_port_object.name

        else:
            return None

    @property
    def detected_midi_inputs(self):
        """
        Returns the names of all detected MIDI input ports.
        :return: A list of strings
        """
        return self._detected_midi_inputs

    @property
    def detected_midi_outputs(self):
        """
        Returns the names of all detected MIDI output ports.
        :return: A list of strings
        """
        return self._detected_midi_outputs

    @property
    def curr_preset_object(self):
        """
        Returns a copy of the current preset object.
        Returns None if Nymphes is not connected.
        :return:
        """
        return copy.deepcopy(self._curr_preset_object) if self._curr_preset_object is not None else None

    @property
    def curr_preset_dict_key(self):
        """
        Returns the dictionary key to the current preset object.
        Returns None if Nymphes is not connected.
        :return: A tuple: (preset_type (str), bank_name (str), preset_number (int) ) or None
        """
        return self._curr_preset_dict_key

    @property
    def all_presets_dict(self):
        """
        Returns a copy of our dict containing all the presets we have received.
        Returns None if if Nymphes is not connected.
        :return: a dict
        """
        return copy.deepcopy(self._nymphes_memory_slots_dict) if self._nymphes_memory_slots_dict is not None else None

    @property
    def connected_midi_inputs(self):
        """
        Returns a list of the names of currently connected MIDI input ports
        :return: a list of strings
        """
        return [port.name for port in self._connected_midi_input_port_objects]

    @property
    def connected_midi_outputs(self):
        """
        Returns a list of the names of currently connected MIDI output ports
        :return: a list of strings
        """
        return [port.name for port in self._connected_midi_output_port_objects]

    def add_notification(self, name, value=None):
        """
        Add a notification to the queue.
        Notifications will be sent to registered callback functions in update().
        :param name: The name of the notification
        :param value: The value associated with the notification
        :return:
        """
        self._notification_queue.put({'name': name, 'value': value})

    def add_curr_preset_param_notification(self, param_name):
        """
        A convenience function for enqueuing a parameter notification
        to clients using the current preset's parameter values.
        If the parameter type is float, then a 'float_param' notification
        will be used.
        If int, then 'int_param' will be used.
        Raises an Exception if param_name is invalid.
        """
        # Validate param_name
        if param_name not in NymphesPreset.all_param_names():
            raise Exception(f'Invalid param_name: {param_name}')

        # Get the type for this parameter
        param_type = NymphesPreset.type_for_param_name(param_name)

        if param_type == int:
            type_string = 'int_param'
            value = self.curr_preset_object.get_int(param_name)

        elif param_type == float:
            type_string = 'float_param'
            value = self.curr_preset_object.get_float(param_name)

        self.add_notification(type_string, (param_name, value))

    def update(self):
        """
        This method should be called as often as possible, on the main thread.
        It handles automatic MIDI connection handling, MIDI message send and receive,
        and notification sending.
        :return:
        """

        # Send Queued Notifications
        #
        while not self._notification_queue.empty():
            # Get the data for the notification
            data = self._notification_queue.get()

            # Call the callback
            self._notification_callback_function(data['name'], data['value'])

        # Receive MIDI Messages
        #
        if self._midi_message_receive_last_timestamp is None or \
                time.time() - self._midi_message_receive_last_timestamp >= \
                self._midi_message_receive_interval_sec:

            # Handle Incoming MIDI Messages from Nymphes
            #
            if self.nymphes_connected:
                for midi_message in self._nymphes_midi_input_port_object.iter_pending():
                    self._on_message_from_nymphes(midi_message)

            # Handle Incoming MIDI Messages from Connected MIDI Input Ports
            #
            for port in self._connected_midi_input_port_objects:
                for midi_message in port.iter_pending():
                    self._on_message_from_midi_input_port(midi_message, port.name)

            # Store the current time
            self._midi_message_receive_last_timestamp = time.time()

        # Detect MIDI Ports
        #
        if self._midi_port_scan_last_timestamp is None or \
                time.time() - self._midi_port_scan_last_timestamp >= \
                self._midi_port_scan_interval_sec:

            # Detect MIDI Ports
            #
            self._detect_midi_input_ports()
            self._detect_midi_output_ports()

            if not self.nymphes_connected:
                # Get the first MIDI input port with nymphes in
                # its name
                nymphes_input_port_name = None
                for port_name in self._detected_midi_inputs:
                    if 'nymphes' in port_name.lower():
                        nymphes_input_port_name = port_name
                        break

                # Get the first MIDI output port with nymphes in
                # its name
                nymphes_output_port_name = None
                for port_name in self._detected_midi_outputs:
                    if 'nymphes' in port_name.lower():
                        nymphes_output_port_name = port_name
                        break

                if nymphes_input_port_name is not None and nymphes_output_port_name is not None:
                    # Try to connect to the ports
                    logger.info(f'Trying to auto-connect to Nymphes ports {nymphes_input_port_name} {nymphes_output_port_name}')
                    self.connect_nymphes(
                        input_port_name=nymphes_input_port_name,
                        output_port_name=nymphes_output_port_name
                    )

            # Store the current time
            self._midi_port_scan_last_timestamp = time.time()

        # Send the current preset to Nymphes and Connected MIDI Output Ports
        # if the snapshot flag is set
        #
        if self._preset_snapshot_last_timestamp is None or \
                time.time() - self._preset_snapshot_last_timestamp >= \
                self._preset_snapshot_timer_interval_sec:

            if self._preset_snapshot_needed:

                if self.nymphes_connected:
                    # Generate a list of bytes in the MIDI SYSEX format used by Nymphes
                    sysex_data = self._curr_preset_object.generate_sysex_data(
                        preset_import_type='non-persistent',
                        preset_type='user',
                        bank_name='A',
                        preset_number=1
                    )

                    # Create a mido MIDI SYSEX message from it
                    msg = mido.Message('sysex', data=sysex_data)

                    # Add it to the message send queue for Nymphes
                    self._send_to_nymphes(msg)

                    # Add it to the queues for all connected MIDI Output Ports
                    for port_object in self._connected_midi_output_port_objects:
                        self._send_to_midi_output_port(msg, port_object)

                    logger.info('Sent current preset to Nymphes and connected MIDI Output ports via SYSEX')

                # Clear the flag and store the current time
                # regardless of whether Nymphes was connected
                # and we actually sent out the preset via
                # SYSEX.
                #
                self._preset_snapshot_needed = False
                self._preset_snapshot_last_timestamp = time.time()

        # Recall First Preset Timer
        #
        if self._send_initial_preset_timestamp is not None:
            if time.time() >= self._send_initial_preset_timestamp:
                #
                # It is time to load the init preset file
                #
                self.load_init_file()

                # Reset the timestamp
                self._send_initial_preset_timestamp = None

        # Nymphes Full Dump Request Timer
        #
        if self._send_full_sysex_dump_request_timestamp is not None:
            if time.time() >= self._send_full_sysex_dump_request_timestamp:
                # It is time to send a full dump request
                self.request_preset_dump()

                # Reset the timestamp
                self._send_full_sysex_dump_request_timestamp = None

        # Waiting For Preset Data Timer
        #
        if self._waiting_for_preset_data_from_nymphes:
            if time.time() >= self._waiting_for_preset_data_from_nymphes_until_timestamp:
                #
                # It is time to stop waiting for preset data from Nymphes
                #
                self._stop_waiting_for_preset_data_from_nymphes()

        # Ignore Nymphes Control Change Messages Timer
        #
        if self._ignore_control_change_messages_from_nymphes:
            if time.time() >= self._ignore_control_change_messages_from_nymphes_until_timestamp:
                #
                # It is time to stop ignoring MIDI CC messages from Nymphes
                #
                self._stop_ignoring_control_change_messages_from_nymphes()

        # Send All Queued MIDI Messages to Nymphes
        #
        if self._nymphes_midi_message_send_queue is not None:
            while not self._nymphes_midi_message_send_queue.empty():
                msg = self._nymphes_midi_message_send_queue.get()
                self._nymphes_midi_output_port_object.send(msg)

        # Send All Queued Messages to MIDI Output Ports
        #
        for port, queue in self._midi_message_send_queues.items():
            while not queue.empty():
                msg = queue.get()
                port.send(msg)

    def connect_nymphes(self, input_port_name, output_port_name):
        """
        Connect the specified MIDI input and output ports
        and use as our ports for MIDI messages from Nymphes.
        Does nothing if the ports are already connected.
        :param input_port_name: str
        :param output_port_name: str
        :return:
        """
        if self.nymphes_connected:
            was_connected = True

            curr_input_port_name, curr_output_port_name = self.nymphes_midi_ports
            if (input_port_name, output_port_name) == (curr_input_port_name, curr_output_port_name):
                # We are already connected to these ports
                return

            else:
                # Close the currently-connected input port
                self._nymphes_midi_input_port_object.close()
                self._nymphes_midi_input_port_object = None
                logger.info(f'Disconnected Nymphes MIDI Input Port {curr_input_port_name}')

                # Close the currently-connected output port
                self._nymphes_midi_output_port_object.close()
                self._nymphes_midi_output_port_object = None
                self._nymphes_midi_message_send_queue = None
                logger.info(f'Disconnected Nymphes MIDI Output Port {curr_output_port_name}')
        else:
            was_connected = False

        # Try to connect to the new input port
        #
        try:
            self._nymphes_midi_input_port_object = mido.open_input(input_port_name)
            logger.info(f'Connected Nymphes MIDI Input Port {input_port_name}')

        except Exception as e:
            self._nymphes_midi_input_port_object = None
            logger.warning(f'Failed to connect Nymphes MIDI Input Port {input_port_name} ({e})')

        # Try to connect to the new output port
        #
        try:
            self._nymphes_midi_output_port_object = mido.open_output(output_port_name)

            # Create a MIDI message send queue for it
            self._nymphes_midi_message_send_queue = Queue()

            logger.info(f'Connected Nymphes MIDI Output Port {output_port_name}')

        except Exception as e:
            self._nymphes_midi_output_port_object = None
            self._nymphes_midi_message_send_queue = None

            logger.warning(f'Failed to connect Nymphes MIDI Output Port {output_port_name} ({e})')

        # Check whether we succeeded in connecting to Nymphes ports
        #
        if self.nymphes_connected:
            self._on_nymphes_connected()

        else:
            if was_connected:
                self._on_nymphes_disconnected()

    def disconnect_nymphes(self):
        """
        Disconnect the current Nymphes MIDI input and output ports.
        Does nothing if Nymphes is not connected.
        :return:
        """
        if not self.nymphes_connected:
            return

        # Close the currently-connected input port
        if self._nymphes_midi_input_port_object is not None:
            curr_input_port_name = self._nymphes_midi_input_port_object.name
            self._nymphes_midi_input_port_object.close()
            self._nymphes_midi_input_port_object = None
            logger.info(f'Disconnected Nymphes MIDI Input Port {curr_input_port_name}')

        # Close the currently-connected output port
        if self._nymphes_midi_output_port_object is not None:
            curr_output_port_name = self._nymphes_midi_output_port_object.name
            self._nymphes_midi_output_port_object.close()
            self._nymphes_midi_output_port_object = None
            logger.info(f'Disconnected Nymphes MIDI Output Port {curr_output_port_name}')

        # Notify Client that we are no longer connected
        self.add_notification(
            MidiConnectionEvents.nymphes_disconnected.value
        )

    def connect_midi_input(self, port_name):
        """
        Connect the specified MIDI input port and add it to our collection of
        connect MIDI input ports.
        Once the port has been connected, MIDI messages will be received from it and passed
        on to Nymphes and all connected MIDI output ports (except any MIDI output port with
        a name matching this input port).
        Does nothing if the port is already connected.
        :param port_name: str
        :return:
        """
        # Check whether the port is already connected
        if port_name in [port.name for port in self._connected_midi_input_port_objects]:
            # The port is already connected
            return

        # Connect the port
        port = mido.open_input(port_name)

        # Store the port
        self._connected_midi_input_port_objects.append(port)

        logger.info(f'Connected MIDI input port ({port_name})')

        # Notify Client
        self.add_notification(
            MidiConnectionEvents.midi_input_connected.value,
            port_name
        )

    def disconnect_midi_input(self, port_name):
        """
        Disconnect the specified MIDI input port.
        Raises an Exception if the port is not in the list of currently-connected
        MIDI Input ports.
        :param port_name: str
        :return:
        """
        # Validate port_name
        if port_name not in [port.name for port in self._connected_midi_input_port_objects]:
            raise Exception(f'MIDI Input Port {port_name} is not connected')
        
        # Remove the port from the collection
        for port in self._connected_midi_input_port_objects:
            if port.name == port_name:
                self._connected_midi_input_port_objects.remove(port)
                logger.info(f'Closing MIDI input port ({port.name})')

                # Disconnect the port
                port.close()

                # Notify Client
                self.add_notification(
                    MidiConnectionEvents.midi_input_disconnected.value,
                    port_name
                )

    def connect_midi_output(self, port_name):
        """
        Connect the specified MIDI output port and add it to our collection of
        connect MIDI output ports.
        Once the port has been connected, MIDI messages will be received from it and passed
        on to Nymphes and all connected MIDI output ports (except any MIDI output port with
        a name matching this output port).
        Does nothing if the port is already connected.
        :param port_name: str
        :return:
        """
        # Check whether the port is already connected
        if port_name in [port.name for port in self._connected_midi_output_port_objects]:
            # The port is already connected
            return

        # Connect the port
        port = mido.open_output(port_name)

        # Store the port
        self._connected_midi_output_port_objects.append(port)

        logger.info(f'Connected MIDI output port ({port_name})')

        # Create a message send queue for the port
        self._midi_message_send_queues[port] = Queue()

        # Notify Client
        self.add_notification(
            MidiConnectionEvents.midi_output_connected.value,
            port_name
        )

    def disconnect_midi_output(self, port_name):
        """
        Disconnect the specified MIDI output port.
        Raises an Exception if the port is not in the list of currently-connected
        MIDI Output ports.
        :param port_name: str
        :return:
        """
        # Validate port_name
        if port_name not in [port.name for port in self._connected_midi_output_port_objects]:
            raise Exception(f'MIDI Output Port {port_name} is not connected')

        # Remove the port from the collection
        for port in self._connected_midi_output_port_objects:
            if port.name == port_name:
                self._connected_midi_output_port_objects.remove(port)
                logger.info(f'Closing MIDI output port ({port.name})')

                # Disconnect the port
                port.close()

                # Notify Client
                self.add_notification(
                    MidiConnectionEvents.midi_output_disconnected.value,
                    port_name
                )

    #
    # Nymphes Preset Methods
    #
    def load_preset(self, preset_type, bank_name, preset_number):
        """
        Send the Nymphes a MIDI program change message to load
        the specified preset from its internal memory, and start
        waiting for Nymphes to load it and send back the data
        for the preset.
        Raises an Exception if arguments are invalid.
        :param preset_type: (str) Possible values: 'user', 'factory'
        :param bank_name: (str) Possible values: 'A', 'B', 'C', 'D', 'E', 'F', 'G'
        :param preset_number: (int) Possible values: 1, 2, 3, 4, 5, 6, 7
        :return:
        """
        preset_types = ['user', 'factory']
        bank_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        preset_numbers = [1, 2, 3, 4, 5, 6, 7]

        # Validate the arguments
        if preset_type not in preset_types:
            raise Exception(f'Invalid preset_type: {preset_type}')

        if bank_name not in bank_names:
            raise Exception(f'Invalid bank_name: {bank_name}')

        if preset_number not in preset_numbers:
            raise Exception(f'Invalid preset_number: {preset_number}')

        if self.nymphes_connected:
            # Store the preset type
            self._curr_preset_type = preset_type

            # Store the bank and preset number
            self._curr_preset_bank_and_number = bank_name, preset_number

            # Send a MIDI bank select message to let the Nymphes
            # know whether we will be loading a user or factory preset
            #
            msg = mido.Message('control_change',
                               channel=self.nymphes_midi_channel-1,
                               control=0,
                               value=preset_types.index(preset_type))
            self._send_to_nymphes(msg)

            # Send a MIDI program change message to load the preset
            #
            msg = mido.Message('program_change',
                               channel=self.nymphes_midi_channel-1,
                               program=(bank_names.index(bank_name) * 7) + preset_numbers.index(preset_number))
            self._send_to_nymphes(msg)

            # Send a notification that Nymphes has loaded a preset
            self.add_notification(
                name=PresetEvents.loaded_preset.value,
                value=(
                    self._curr_preset_type,
                    self._curr_preset_bank_and_number[0],
                    self._curr_preset_bank_and_number[1]
                )
            )

            # Start waiting for preset data to come back from Nymphes
            self._start_waiting_for_preset_data()

    def save_to_preset(self, preset_type, bank_name, preset_number):
        """
        A convenience method for sending the current settings
        to Nymphes as a SYSEX message, using a persistent import type
        so the preset is stored in one of Nymphes' preset slots. It
        will overwrite whatever is in that slot.
        :param preset_type: (str) ['user', 'factory'] or None if non-persistent
        :param bank_name: (str): ['A', 'B', 'C', 'D', 'E', 'F', 'G'] or None if non-persistent
        :param preset_number: (int): 1 to 7 or None if non-persistent
        :return:
        """
        self._send_preset_object_to_nymphes_preset_slot(
            preset_object=self._curr_preset_object,
            preset_type=preset_type,
            bank_name=bank_name,
            preset_number=preset_number
        )

        # Notify Client that we've just loaded the current settings into
        # one of Nymphes' preset slots
        self.add_notification(
            PresetEvents.saved_to_preset.value,
            (preset_type, bank_name, preset_number)
        )

    def _send_preset_object_to_nymphes_preset_slot(self, preset_object, preset_type, bank_name, preset_number):
        """
        Send the supplied preset_object to Nymphes as a SYSEX message,
        using a persistent import type so the preset is stored in
        one of Nymphes' preset slots. It will overwrite whatever is
        in that slot.
        :param preset_object: A preset object
        :param preset_type: (str) ['user', 'factory'] or None if non-persistent
        :param bank_name: (str): ['A', 'B', 'C', 'D', 'E', 'F', 'G'] or None if non-persistent
        :param preset_number: (int): 1 to 7 or None if non-persistent
        :return:
        """
        if self.nymphes_connected:
            # Generate a list of bytes in the MIDI SYSEX format used by Nymphes
            # for the preset_object
            sysex_data = preset_object.generate_sysex_data(
                'persistent',
                preset_type,
                bank_name,
                preset_number
            )

            # Create a mido MIDI SYSEX message from it
            msg = mido.Message('sysex', data=sysex_data)

            # Add it to the message send queue for Nymphes
            self._send_to_nymphes(msg)

    def load_file_to_preset(self, filepath, preset_type, bank_name, preset_number):
        """
        Load the file at filepath, and send its content to Nymphes
        as a SYSEX message, using a persistent import type to write
        to one of Nymphes' preset slots.
        Overwrites whatever was previously in the slot.
        :param filepath: A Path or string. The path to the preset file.
        :param preset_type: (str) ['user', 'factory']
        :param bank_name: (str): ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        :param preset_number: (int): 1 to 7
        :return:
        """
        if self.nymphes_connected:
            # Load the preset file into a preset object
            preset_object = NymphesPreset(filepath=filepath)

            # Generate a list of bytes in the MIDI SYSEX format used by Nymphes
            # for the preset_object
            sysex_data = preset_object.generate_sysex_data(
                'persistent',
                preset_type,
                bank_name,
                preset_number
            )

            # Create a mido MIDI SYSEX message from it
            msg = mido.Message('sysex', data=sysex_data)

            # Add it to the message send queue
            self._send_to_nymphes(msg)

            # Notify Client
            self.add_notification(
                PresetEvents.loaded_file_to_preset.value,
                (str(filepath), preset_type, bank_name, preset_number)
            )

    def load_file(self, filepath):
        """
        Load the preset file at filepath
        :param filepath: A Path or string. The path to the preset file.
        :return:
        """
        if self.nymphes_connected:
            # Load the preset file as the current preset
            self._curr_preset_object = NymphesPreset(filepath=filepath)

            # Notify Client
            self.add_notification(
                PresetEvents.loaded_file.value,
                str(filepath)
            )

            # Send all parameters to the client
            self.send_current_preset_notifications()

            # Send the preset to Nymphes and connected MIDI Output ports
            self._preset_snapshot_needed = True

    def load_init_file(self):
        """
        Load init.txt
        :return:
        """
        if self.nymphes_connected:
            logger.info(f'About to load init preset file at {self.init_preset_filepath}')

            self._curr_preset_object = NymphesPreset(filepath=self.init_preset_filepath)

            # Notify Client
            self.add_notification(
                PresetEvents.loaded_init_file.value,
                str(self.init_preset_filepath)
            )

            # Send all parameters to the client
            self.send_current_preset_notifications()

            # Send the preset to Nymphes and connected MIDI Output ports
            self._preset_snapshot_needed = True

    def save_to_file(self, filepath):
        """
        Save to a preset file.
        :param filepath: Path or str
        :return:
        """
        # Save to a preset file at filepath
        self._curr_preset_object.save_preset_file(filepath)

        # Send notification
        self.add_notification(
            PresetEvents.saved_to_file.value,
            str(filepath)
        )

    def save_preset_to_file(self, filepath, preset_type, bank_name, preset_number):
        """
        Save the contents of a preset slot to a file.
        Raises an Exception if the all_presets dictionary does not
        contain the specified preset.
        :param filepath: Path or str
        :param preset_type:
        :param bank_name:
        :param preset_number:
        :return:
        """
        # Make sure we have a preset object for the specified memory slot
        dict_key = preset_type, bank_name, preset_number
        if dict_key not in self._nymphes_memory_slots_dict:
            raise Exception(f'Invalid preset slot or there is no data for the slot ({dict_key})')

        # Get the preset object
        preset_object = self._nymphes_memory_slots_dict[dict_key]

        # Save to disk
        preset_object.save_preset_file(filepath)

        # Send notification
        self.add_notification(
            PresetEvents.saved_preset_to_file.value,
            (str(filepath), preset_type, bank_name, preset_number)
        )

    def request_preset_dump(self):
        """
        Send a full dump request message to Nymphes via SYSEX.
        Nymphes will respond by sending each of its presets as
        SYSEX messages, one by one.
        If no preset has been saved in a User slot then nothing will
        be sent for that slot.
        :return:
        """
        if self.nymphes_connected:
            logger.info('Requesting full preset dump from Nymphes')

            # Create a dump request message
            msg = mido.Message('sysex', data=[0x00, 0x21, 0x35, 0x00, 0x06, 0x02])

            # Send it to Nymphes
            self._send_to_nymphes(msg)

            # Send a notification
            self.add_notification(PresetEvents.requested_preset_dump.value)

    def set_param(self, param_name, int_value=None, float_value=None):
        """
        Used by software client to set a parameter's value by name,
        using either an integer or float value.
        Nymphes and all connected MIDI Output ports will be sent the
        parameter's new value.

        If an int is used and the parameter has a MIDI CC associated
        with it, then the new value will be sent as a MIDI CC. This
        applies equally to int-valued parameters and to float-valued
        parameters set using an int.

        If there is no associated MIDI CC (ie: chord settings), then
        the entire updated preset will be sent out as a SYSEX message.

        A float should only be used for float-valued parameters. The
        entire updated preset will be sent out as a SYSEX message.

        Raises an Exception if param_name is invalid.
        Raises an Exception if no value is supplied, or if both int_value
        and float_value are supplied.

        :param param_name: str
        :param int_value: int between 0 and the parameter's max (never greater than 127)
        :param float_value: float between 0.0 and 127.0
        :return:
        """
        # If there is no current preset, then don't do anything
        if self._curr_preset_object is None:
            return

        # Make sure param_name is valid
        if param_name not in NymphesPreset.all_param_names():
            raise Exception(f'Invalid param_name: {param_name}')

        # Make sure a value has been supplied
        if int_value is None and float_value is None:
            raise Exception('No value was supplied')

        # Make sure only one value has been supplied
        if int_value is not None and float_value is not None:
            raise Exception(f'Only one value should be supplied (int_value: {int_value}, float_value: {float_value}')

        if int_value is not None:
            #
            # The value has been supplied as an int.
            #
            # Set the parameter
            self._curr_preset_object.set_int(param_name, int_value)

            # Send MIDI Control Change messages to Nymphes and MIDI Output
            # Ports if there is an associated MIDI CC for the parameter
            #
            control = NymphesPreset.midi_cc_for_param_name(param_name)

            if control is not None:
                #
                # This parameter has an associated MIDI CC.
                #

                #
                # Before sending MIDI Control Change Message, determine whether
                # we need to first set the modulation source
                #
                mod_source = NymphesPreset.mod_source_for_param_name(param_name)
                if mod_source is not None:
                    mod_source_names = ['lfo2', 'mod_wheel', 'velocity', 'aftertouch']

                    # Create a MIDI message to send
                    msg = mido.Message('control_change',
                                       channel=self.nymphes_midi_channel - 1,
                                       control=30,
                                       value=mod_source_names.index(mod_source))

                    # Send to Nymphes
                    self._send_to_nymphes(msg)

                    # Send to connected MIDI Output ports
                    for port_object in self._connected_midi_output_port_objects:
                        self._send_to_midi_output_port(msg, port_object)

                #
                # Send the MIDI CC Message for the parameter itself
                #

                # Create a MIDI message
                msg = mido.Message('control_change',
                                   channel=self.nymphes_midi_channel - 1,
                                   control=control,
                                   value=int_value)

                # Send to Nymphes
                self._send_to_nymphes(msg)

                # Send to connected MIDI Output ports
                for port_object in self._connected_midi_output_port_objects:
                    self._send_to_midi_output_port(msg, port_object)

            else:
                #
                # There is no MIDI CC associated with this parameter,
                # so we need to send the entire updated preset as a
                # SYSEX message
                #
                self._preset_snapshot_needed = True

        elif float_value is not None:
            #
            # The value has been supplied as a float
            #

            # Update the parameter's value
            self._curr_preset_object.set_float(param_name, float_value)

            # We need to send the entire updated preset via SYSEX
            self._preset_snapshot_needed = True

    def set_mod_wheel(self, value):
        """
        Send mod wheel MIDI Control Change message to Nymphes
        :param value: (int) 0 to 127
        :return:
        """
        if value < 0 or value > 127:
            raise Exception(f'Invalid value: {value} (should be between 0 and 127)')

        msg = mido.Message('control_change',
                           channel=self.nymphes_midi_channel-1,
                           control=1,
                           value=value)

        self._send_to_nymphes(msg)

        # Send to connected MIDI Output ports
        for port_object in self._connected_midi_output_port_objects:
            self._send_to_midi_output_port(msg, port_object)

    def set_channel_aftertouch(self, value):
        """
        Send channel aftertouch MIDI message to Nymphes
        :param value: (int) 0 to 127
        :return:
        """
        if value < 0 or value > 127:
            raise Exception(f'Invalid value: {value} (should be between 0 and 127)')

        msg = mido.Message('aftertouch',
                           channel=self.nymphes_midi_channel-1,
                           value=value)

        self._send_to_nymphes(msg)

        # Send to connected MIDI Output ports
        for port_object in self._connected_midi_output_port_objects:
            self._send_to_midi_output_port(msg, port_object)

    def set_sustain_pedal(self, value):
        """
        Send Sustain Pedal MIDI Control Change message (CC 64) to Nymphes
        :param value: (int) 0 or 1
        :return:
        """
        if value < 0 or value > 1:
            raise Exception(f'Invalid value: {value} (should be 0 or 1)')

        # Although the Nymphes manual indicates that the sustain pedal's value
        # should be 0 or 1, Nymphes itself requires the MIDI CC's value to be
        # 127 to activate sustain.
        if value != 0:
            value = 127

        msg = mido.Message('control_change',
                           channel=self.nymphes_midi_channel-1,
                           control=64,
                           value=value)

        self._send_to_nymphes(msg)

        # Send to connected MIDI Output ports
        for port_object in self._connected_midi_output_port_objects:
            self._send_to_midi_output_port(msg, port_object)

    def _send_to_nymphes(self, msg):
        """
        Add a MIDI message to the Nymphes queue.
        If Nymphes is not currently connected then do nothing.
        :param msg: A mido MIDI message
        :return:
        """
        if self.nymphes_connected:
            self._nymphes_midi_message_send_queue.put(msg)

    def _send_to_midi_output_port(self, msg, port_object):
        """
        Add a MIDI message to the queue for a specific MIDI output
        port (not Nymphes).
        Raises an Exception if there is no queue for port_object.
        :param msg: A mido MIDI message
        :param port_object: A mido output port object
        :return:
        """
        if port_object not in self._connected_midi_output_port_objects:
            raise Exception(f'Invalid MIDI Output Port Object: {port_object} (There is no message send queue for this port)')

        # Add the message to the queue for the port
        self._midi_message_send_queues[port_object].put(msg)

    def _send_to_connected_midi_output_ports(self, msg):
        """
        A convenience method for sending a message to all
        connected MIDI Output ports
        :param msg: A mido MIDI message
        :return:
        """
        for port_object in self._connected_midi_output_port_objects:
            self._send_to_midi_output_port(msg, port_object)

    def _on_message_from_nymphes(self, msg):
        """
        A MIDI message has been received from Nymphes.
        Interpret it. If it affects the current preset's
        values, then notify the software client.
        We always send a copy of any MIDI message received
        from Nymphes to all connected MIDI Output ports.
        :param msg: A mido MIDI Message object
        :return:
        """
        if msg.type == 'sysex':
            # Try to interpret this SYSEX message as a Nymphes preset
            try:
                preset_import_type, preset_key = self._handle_sysex_message(msg)

                if preset_import_type == 'non-persistent':
                    #
                    # This was a non-persistent preset import type,
                    # so the current preset's parameter values have
                    # changed.
                    #

                    # If we were waiting for preset data, we now have it
                    if self._waiting_for_preset_data_from_nymphes:
                        self._stop_waiting_for_preset_data_from_nymphes()

                    # Start ignoring Control Change messages from Nymphes for a short time,
                    # as the SYSEX message provided all parameter values with higher
                    # precision than Control Change messages allow.
                    self._start_ignoring_control_change_messages_from_nymphes()

                    # Send notifications for all preset parameters
                    for param_name in NymphesPreset.all_param_names():
                        self.add_curr_preset_param_notification(param_name)

                        # Log the parameters
                        param_type = NymphesPreset.type_for_param_name(param_name)

                        if param_type == float:
                            logger.debug(f'{param_name}: {self._curr_preset_object.get_float(param_name)}')

                        elif param_type == int:
                            logger.debug(f'{param_name}: {self._curr_preset_object.get_int(param_name)}')

                elif preset_import_type == 'persistent':
                    #
                    # This was a SYSEX dump of a preset from a Nymphes
                    # preset slot, so it did not affect the current
                    # parameter values
                    #

                    # Send a notification that a preset dump has been received
                    self.add_notification(
                        PresetEvents.received_preset_dump_from_nymphes.value,
                        preset_key
                    )

            except Exception as e:
                logger.warning(f'Failed to handle SYSEX message from Nymphes ({e})')

        elif msg.is_cc():
            if not self._ignore_control_change_messages_from_nymphes:
                # Make sure the message was received on the Nymphes MIDI Channel
                if msg.channel != self._nymphes_midi_channel - 1:
                    logger.warning(f'Received a MIDI Control Change message from Nymphes on a different channel: {msg}')

                else:
                    if msg.control == 0:
                        #
                        # Bank MSB Message
                        # This message is sent by Nymphes when a preset is loaded,
                        # just before the Program Change message and SYSEX message.
                        # We will log it, but do nothing else, as we will get the
                        # same information from the SYSEX message itself.
                        #

                        if msg.value == 0:
                            self._curr_preset_type = 'user'
                            logger.info('Received Bank MSB 0 (User Bank) from Nymphes')

                        elif msg.value == 1:
                            self._curr_preset_type = 'factory'
                            logger.info('Received Bank MSB 1 (Factory Bank) from Nymphes')

                        else:
                            self._curr_preset_type = None
                            logger.warning(f'Received unknown Bank MSB value from Nymphes ({msg.value})')

                    elif msg.control == 30:
                        #
                        # Nymphes' Modulation Source has just changed
                        #

                        # Store the new mod source
                        self._curr_mod_source = msg.value

                        # Send a notification
                        self.add_notification('mod_source', msg.value)

                        # Log the message
                        logger.debug(f'mod_source: {msg.value}')

                    else:
                        #
                        # Try to handle this MIDI Control Change message
                        # as a Nymphes preset parameter
                        #

                        # Get parameter name (or names, if this is a mod matrix control change
                        # message)
                        param_names_for_this_cc = NymphesPreset.param_names_for_midi_cc(msg.control)

                        if len(param_names_for_this_cc) == 0:
                            #
                            # This is not a Nymphes parameter
                            #

                            logger.warning(f'Received unhandled MIDI CC Message from Nymphes: {msg}')

                        if len(param_names_for_this_cc) == 1:
                            #
                            # This is a non mod-matrix parameter
                            #

                            # Set the parameter value in the current preset
                            was_new_value = self._curr_preset_object.set_int(param_names_for_this_cc[0], msg.value)
                            if was_new_value or self._waiting_for_preset_data_from_nymphes:
                                #
                                # This was a new value for the parameter,
                                # or we are currently not ignoring duplicate
                                # MIDI CC messages because we are waiting for
                                # preset data from Nymphes
                                #

                                # Send a notification
                                self.add_notification('int_param', (param_names_for_this_cc[0], msg.value))

                                # Log the message
                                logger.debug(f'{param_names_for_this_cc[0]}: {msg.value}')

                        else:
                            #
                            # This is a mod matrix parameter, so we need to
                            # check the current mod source in order to
                            # determine which preset parameter this MIDI CC matches.
                            #

                            # Get the name of the current modulation source
                            curr_mod_source_name = ['lfo2', 'mod_wheel', 'velocity', 'aftertouch'][self._curr_mod_source]

                            # Find the correct parameter name and set its value
                            #
                            for param_name in param_names_for_this_cc:
                                if NymphesPreset.target_for_param(param_name) == curr_mod_source_name:

                                    # Set the parameter value in the current preset
                                    was_new_value = self._curr_preset_object.set_int(param_name, msg.value)
                                    if was_new_value or self._waiting_for_preset_data_from_nymphes:
                                        #
                                        # This was a new value for the parameter,
                                        # or we are currently not ignoring duplicate
                                        # MIDI CC messages because we are waiting for
                                        # preset data from Nymphes
                                        #

                                        # Send a notification
                                        self.add_notification('int_param', (param_name, msg.value))

                                        # Log the message
                                        logger.debug(f'{param_name}: {msg.value}')

        elif msg.type == 'program_change':
            if msg.channel == self._nymphes_midi_channel - 1:
                #
                # We have received a program change message from Nymphes.
                #

                # Parse into bank name and preset number
                bank_name, preset_number = self._parse_midi_program_change_message(msg)

                # Store them
                self._curr_preset_bank_and_number = bank_name, preset_number

                logger.info(
                    f'Received Program Change Message from Nymphes (Bank {bank_name}, Preset {preset_number})')

                # Send a notification that Nymphes has loaded a preset
                self.add_notification(
                    name=PresetEvents.loaded_preset.value,
                    value=(
                        self._curr_preset_type,
                        self._curr_preset_bank_and_number[0],
                        self._curr_preset_bank_and_number[1]
                    )
                )

                # Start waiting for the preset's data to arrive via
                # SYSEX and MIDI CC
                self._start_waiting_for_preset_data()

        else:
            #
            # This is not a recognized MIDI message.
            #
            logger.warning(f'Received unhandled MIDI message from Nymphes ({msg})')

        # We always send a copy of any message from Nymphes to all
        # connected MIDI Output ports
        self._send_to_connected_midi_output_ports(msg)

    def _on_message_from_midi_input_port(self, msg, port):
        """
        A MIDI message has been received from a connected
        MIDI input port. Interpret it. If it affects the
        current preset's values, then notify the software
        client.
        We always send a copy of the message to Nymphes.
        :param msg: A mido MIDI Message object
        :param port: (str) The name of the mido MIDI Input
        port that received the message
        :return:
        """
        if msg.type == 'sysex':
            # Try to interpret this SYSEX message as a Nymphes preset
            try:
                preset_import_type, preset_key = self._handle_sysex_message(msg)

                if preset_import_type == 'non-persistent':
                    #
                    # This was a non-persistent preset import type,
                    # so the current preset's parameter values have
                    # changed.
                    #

                    # Send a notification that the current preset parameters
                    # were received from a MIDI input port
                    self.add_notification(PresetEvents.loaded_preset_dump_from_midi_input_port.value)

                    # Send notifications for all preset parameters
                    for param_name in NymphesPreset.all_param_names():
                        self.add_curr_preset_param_notification(param_name)

                        # Log the parameters
                        param_type = NymphesPreset.type_for_param_name(param_name)

                        if param_type == float:
                            logger.debug(f'{param_name}: {self._curr_preset_object.get_float(param_name)}')

                        elif param_type == int:
                            logger.debug(f'{param_name}: {self._curr_preset_object.get_int(param_name)}')

                elif preset_import_type == 'persistent':
                    #
                    # This is a SYSEX message that writes a preset
                    # into a Nymphes preset slot
                    #

                    # Send a notification
                    self.add_notification(
                        PresetEvents.saved_preset_dump_from_midi_input_port_to_preset.value,
                        preset_key
                    )

            except Exception as e:
                pass

        elif msg.is_cc():

            # Only handle MIDI CC messages received on the Nymphes MIDI Channel
            if msg.channel == self._nymphes_midi_channel - 1:
                if msg.control == 0:
                    #
                    # Bank MSB Message
                    # This tells Nymphes to select either the User or Factory bank
                    # for Program Change messages that follow it.
                    #

                    if msg.value == 0:
                        logger.info(f'Received Bank MSB 0 (User Bank) from {port}')
                    elif msg.value == 1:
                        logger.info(f'Received Bank MSB 1 (Factory Bank) from {port}')
                    else:
                        logger.warning(f'Received unknown Bank MSB value from {port} ({msg.value})')

                elif msg.control == 1:
                    #
                    # Mod Wheel Message
                    #

                    # Send a mod wheel notification to clients
                    self.add_notification('mod_wheel', msg.value)

                    # Log the message
                    logger.debug(f'{port}: mod_wheel', msg.value)

                elif msg.control == 30:
                    #
                    # This sets Nymphes' Modulation Source
                    #

                    # Store the new mod source
                    self._curr_mod_source = msg.value

                    # Send a notification
                    self.add_notification('mod_source', msg.value)

                    # Log the message
                    logger.debug(f'{port}: mod_source: {msg.value}')

                elif msg.control == 64:
                    #
                    # This is sustain pedal
                    #

                    # Send a notification
                    self.add_notification('sustain_pedal', msg.value)

                    # Log the message
                    logger.debug(f'{port}: sustain_pedal: {msg.value}')

                else:
                    #
                    # Try to handle this MIDI Control Change message
                    # as a Nymphes preset parameter
                    #

                    # Get parameter name (or names, if this is a mod matrix control change
                    # message)
                    param_names_for_this_cc = NymphesPreset.param_names_for_midi_cc(msg.control)

                    if len(param_names_for_this_cc) == 0:
                        #
                        # This is not a Nymphes parameter
                        #

                        logger.warning(f'Received unhandled MIDI CC Message from {port}: {msg}')

                    if len(param_names_for_this_cc) == 1:
                        #
                        # This is a non mod-matrix parameter
                        #

                        # Set the parameter value in the current preset
                        if self._curr_preset_object.set_int(param_names_for_this_cc[0], msg.value):
                            #
                            # This was a new value for the parameter
                            #

                            # Send a notification
                            self.add_curr_preset_param_notification(param_names_for_this_cc[0])

                            # Log the message
                            logger.debug(f'{port}: {param_names_for_this_cc[0]}: {msg.value}')

                    else:
                        #
                        # This is a mod matrix parameter, so we need to
                        # check the current mod source in order to
                        # determine which preset parameter this MIDI CC matches.
                        #

                        # Get the name of the current modulation source
                        curr_mod_source_name = ['lfo2', 'mod_wheel', 'velocity', 'aftertouch'][self._curr_mod_source]

                        # Find the correct parameter name and set its value
                        #
                        for param_name in param_names_for_this_cc:
                            if NymphesPreset.target_for_param(param_name) == curr_mod_source_name:

                                # Set the parameter value in the current preset
                                if self._curr_preset_object.set_int(param_name, msg.value):
                                    #
                                    # This was a new value for the parameter
                                    #

                                    # Send a notification
                                    self.add_curr_preset_param_notification(param_name)

                                    # Log the message
                                    logger.debug(f'{port}: {param_name}: {msg.value}')

        elif msg.type == 'program_change':
            if msg.channel == self._nymphes_midi_channel - 1:
                #
                # We have received a program change message.
                # We will log it, and pass it on to Nymphes.
                #

                bank_name, preset_number = self._parse_midi_program_change_message(msg)
                logger.info(
                    f'Received Program Change Message from {port} (Bank {bank_name}, Preset {preset_number})')

        elif msg.type == 'note_on' and msg.velocity != 0:
            if msg.channel == self._nymphes_midi_channel - 1:

                # Extract the velocity of the note and send to clients
                # so they can display it to the user
                self.add_notification('velocity', msg.velocity)

                # Log the message
                logger.debug(f'{port}: velocity: {msg.velocity}')

        elif msg.type == 'aftertouch':
            if msg.channel == self._nymphes_midi_channel - 1:

                # Send aftertouch to clients so they can display it to the user
                self.add_notification('aftertouch', msg.value)

                # Log the message
                logger.debug(f'{port}: aftertouch: {msg.value}')

        # Send a copy of the message to Nymphes
        self._send_to_nymphes(msg)

    def _handle_sysex_message(self, msg):
        """
        A SYSEX message has been received.
        Try to interpret the message as a Nymphes preset and
        store its contents.
        Raise an Exception if the message is invalid.
        :param msg: A mido MIDI message
        :return: A tuple: (preset_import_type, preset_key)
        """
        try:
            p = NymphesPreset(sysex_data=msg.data)

            # Construct a dictionary key from the preset's type, bank and number
            preset_key = (p.preset_type, p.bank_name, p.preset_number)

            # Get the preset import type
            preset_import_type = p.preset_import_type

            if preset_import_type == 'persistent':
                #
                # This is a SYSEX dump of a preset in a preset slot.
                # Store a copy of the preset object in the all presets dictionary
                self._nymphes_memory_slots_dict[preset_key] = p

            elif preset_import_type == 'non-persistent':
                #
                # A preset has been loaded from one of Nymphes'
                # preset slots
                #

                # This is now the current preset.
                # Store a copy of it.
                self._curr_preset_object = copy.deepcopy(p)

                # Store the key to the current preset
                self._curr_preset_dict_key = preset_key

            # Log the message
            status_message = 'Nymphes preset received via SYSEX ('
            status_message += f'Bank {p.bank_name}, '
            status_message += f'{p.preset_type.capitalize()} Preset {p.preset_number}, '
            status_message += f'{p.preset_import_type.capitalize()} Import'
            status_message += ')'
            logger.info(status_message)

            return preset_import_type,  preset_key

        except Exception as e:
            pass

    @staticmethod
    def _parse_midi_program_change_message(msg):
        """
        Attempt to interpret the supplied MIDI Program Change message
        as a Nymphes bank/preset number.
        Raises an Exception if msg is not a Program Change message.
        :param msg: A mido Message
        :return: A tuple (str(bank_name), int(preset_number))
        """
        if msg.type != 'program_change':
            raise Exception(f'msg type is not program_change ({msg})')

        # Get the raw program change value
        program_num = msg.program

        # Determine the bank name (A to G)
        bank_num = int(program_num / 7)
        bank_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        bank_name = bank_names[bank_num]

        # Calculate the preset number (1 to 7)
        preset_number = f'{(program_num % 7) + 1}'

        return bank_name, preset_number

    def _on_nymphes_connected(self):
        # Notify Client
        self.add_notification(
            MidiConnectionEvents.nymphes_connected.value,
            self.nymphes_midi_ports
        )

        # Schedule the sending of the init preset
        self._send_initial_preset_timestamp = time.time() + self._send_initial_preset_wait_time_sec

        # Schedule a full preset dump request a short time later
        self._send_full_sysex_dump_request_timestamp = self._send_initial_preset_timestamp + self._send_full_sysex_dump_request_wait_time_sec

    def _on_nymphes_disconnected(self):
        # Clear out all_presets_dict
        #
        self._curr_preset_dict_key = None
        self._nymphes_memory_slots_dict = {}

        # Notify client
        self.add_notification(
            MidiConnectionEvents.nymphes_disconnected.value
        )

    def _on_midi_input_port_detected(self, port_name):
        logger.info(f'MIDI Input Port detected ({port_name})')

        # Notify Client
        self.add_notification(
            MidiConnectionEvents.midi_input_detected.value,
            port_name
        )

    def _on_midi_input_port_no_longer_detected(self, port_name):
        # Notify Client
        self.add_notification(
            MidiConnectionEvents.midi_input_no_longer_detected.value,
            port_name
        )

        if self.nymphes_connected and port_name == self.nymphes_midi_ports[0]:
            #
            # The Nymphes input port is no longer detected
            #

            logger.info(f'Nymphes MIDI Input Port {port_name} no longer detected')

            # Disconnect from Nymphes input and output ports
            self.disconnect_nymphes()

        else:
            logger.info(f'MIDI Input Port {port_name} no longer detected')

            if port_name in self.connected_midi_inputs:
                #
                # This was a connected MIDI input port
                #

                self.disconnect_midi_input(port_name)

    def _on_midi_output_port_detected(self, port_name):
        logger.info(f'MIDI Output Port detected ({port_name})')

        # Notify Client
        self.add_notification(
            MidiConnectionEvents.midi_output_detected.value,
            port_name
        )

    def _on_midi_output_port_no_longer_detected(self, port_name):
        # Notify Client
        self.add_notification(
            MidiConnectionEvents.midi_output_no_longer_detected.value,
            port_name
        )

        if self.nymphes_connected and port_name == self.nymphes_midi_ports[1]:
            #
            # The Nymphes output port is no longer detected
            #
            logger.info(f'Nymphes MIDI Output Port {port_name} no longer detected')

            # Disconnect from Nymphes input and output ports
            self.disconnect_nymphes()
            
        else:
            logger.info(f'MIDI Output Port {port_name} no longer detected')

            if port_name in self.connected_midi_outputs:
                #
                # This was a connected MIDI output port
                #

                self.disconnect_midi_output(port_name)

    def _detect_midi_input_ports(self):
        """
        Detect MIDI input ports.
        """
        # Sometimes getting port names causes an Exception...
        try:
            # Get a list of all MIDI input ports
            port_names = mido.get_input_names()

            # Remove None if it is in the list of port names.
            # A recently-disconnected port may be added as None.
            # Perhaps this is a bug in mido.
            port_names = [port_name for port_name in port_names if port_name is not None]

            #
            # Determine whether any new ports have been detected,
            # or previously-detected ports are no longer detected
            #

            if set(port_names) != set(self._detected_midi_inputs):
                # There has been some kind of change to the list of detected MIDI ports.

                # Handle ports that are no longer detected
                #
                for port_name in self._detected_midi_inputs:
                    if port_name not in port_names:
                        # This port is no longer detected.
                        self._detected_midi_inputs.remove(port_name)

                        # Call the event handler
                        self._on_midi_input_port_no_longer_detected(port_name)

                # Handle newly-detected MIDI ports
                #
                for port_name in port_names:
                    if port_name not in self._detected_midi_inputs:
                        # This port has just been detected.
                        self._detected_midi_inputs.append(port_name)

                        # Call the event handler
                        self._on_midi_input_port_detected(port_name)

        except InvalidPortError:
            # Sometimes an exception is thrown when trying to get port names.
            # Do nothing
            pass

    def _detect_midi_output_ports(self):
        """
        Detect MIDI output ports.
        """
        # Sometimes getting port names causes an Exception...
        try:
            # Get a list of all MIDI output ports
            port_names = mido.get_output_names()

            # Remove None if it is in the list of port names.
            # A recently-disconnected port may be added as None.
            # Perhaps this is a bug in mido.
            port_names = [port_name for port_name in port_names if port_name is not None]

            #
            # Determine whether any new ports have been detected,
            # or previously-detected ports are no longer detected
            #

            if set(port_names) != set(self._detected_midi_outputs):
                # There has been some kind of change to the list of detected MIDI ports.

                # Handle ports that are no longer detected
                #
                for port_name in self._detected_midi_outputs:
                    if port_name not in port_names:
                        # This port is no longer detected.
                        self._detected_midi_outputs.remove(port_name)

                        # Call the event handler
                        self._on_midi_output_port_no_longer_detected(port_name)

                # Handle newly-detected MIDI ports
                #
                for port_name in port_names:
                    if port_name not in self._detected_midi_outputs:
                        # This port has just been detected.
                        self._detected_midi_outputs.append(port_name)

                        # Call the event handler
                        self._on_midi_output_port_detected(port_name)

        except InvalidPortError:
            # Sometimes an exception is thrown when trying to get port names.
            # Do nothing
            pass

    def _start_ignoring_control_change_messages_from_nymphes(self):
        # Set the flag to True
        self._ignore_control_change_messages_from_nymphes = True

        # Set the time when we stop ignoring the messages
        self._ignore_control_change_messages_from_nymphes_until_timestamp = \
            time.time() + \
            self._ignore_control_change_messages_from_nymphes_duration_sec

        logger.debug('Starting to ignore incoming MIDI CC messages from Nymphes')

    def _stop_ignoring_control_change_messages_from_nymphes(self):
        self._ignore_control_change_messages_from_nymphes = False
        self._ignore_control_change_messages_from_nymphes_until_timestamp = None

        logger.debug('No longer ignoring incoming MIDI CC messages from Nymphes')

    def _start_waiting_for_preset_data(self):
        # Set the flag to True
        self._waiting_for_preset_data_from_nymphes = True

        # Set the time when we stop waiting for preset data
        self._waiting_for_preset_data_from_nymphes_until_timestamp = \
            time.time() + \
            self._waiting_for_preset_data_from_nymphes_duration_sec

        logger.debug('Starting to wait for preset data from Nymphes')

    def _stop_waiting_for_preset_data_from_nymphes(self):
        self._waiting_for_preset_data_from_nymphes = False
        self._waiting_for_preset_data_from_nymphes_until_timestamp = None

        logger.debug('No longer waiting for preset data from Nymphes')

    def send_current_preset_notifications(self):
        """
        Send notifications for all parameters in the current preset.
        """
        for param_name in NymphesPreset.all_param_names():
            self.add_curr_preset_param_notification(param_name)
