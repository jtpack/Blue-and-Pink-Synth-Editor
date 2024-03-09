from multiprocessing import Process
import time
from nymphes_osc.NymphesOSC import NymphesOSC


class NymphesOscProcess(Process):

    def __init__(self, server_host, server_port, client_host, client_port, nymphes_midi_channel, osc_log_level, midi_log_level, presets_directory_path):
        super(NymphesOscProcess, self).__init__()

        self.nymphes_osc_object = None

        self.server_host = server_host
        self.server_port = server_port
        self.client_host = client_host
        self.client_port = client_port
        self.nymphes_midi_channel = nymphes_midi_channel
        self.osc_log_level = osc_log_level
        self.midi_log_level = midi_log_level
        self.presets_directory_path = presets_directory_path

    def run(self):
        # Create the nymphes-osc object
        self.nymphes_osc_object = NymphesOSC(
            nymphes_midi_channel=self.nymphes_midi_channel,
            server_host=self.server_host,
            server_port=self.server_port,
            client_host=self.client_host,
            client_port=self.client_port,
            use_mdns=False,
            osc_log_level=self.osc_log_level,
            midi_log_level=self.midi_log_level,
            presets_directory_path=self.presets_directory_path
        )

        # Start updating
        try:
            while True:
                self.nymphes_osc_object.update()
                time.sleep(0.0001)
        except KeyboardInterrupt:
            Logger.warning(f'nymphes-osc is about to close')
            self.nymphes_osc_object.stop_osc_server()
