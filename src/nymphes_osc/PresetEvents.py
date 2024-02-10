from enum import Enum


class PresetEvents(Enum):
    # Loading Presets
    loaded_preset = 'loaded_preset'
    loaded_file = 'loaded_file'
    loaded_init_file = 'loaded_init_file'

    # Saving to Preset Slots
    saved_to_preset = 'saved_to_preset'
    loaded_file_to_preset = 'loaded_file_to_preset'

    # Saving to Preset Files
    saved_to_file = 'saved_to_file'
    saved_preset_to_file = 'saved_preset_to_file'

    # Other
    requested_preset_dump = 'requested_preset_dump'
    received_preset_dump_from_nymphes = 'received_preset_dump_from_nymphes'
    saved_preset_dump_from_midi_input_port_to_preset = 'saved_preset_dump_from_midi_input_port_to_preset'
    loaded_preset_dump_from_midi_input_port = 'loaded_preset_dump_from_midi_input_port'

    @staticmethod
    def all_values():
        """
        Return a list of all PresetEvent values.
        :return: A list of strings
        """
        return [
            PresetEvents.loaded_preset.value,
            PresetEvents.loaded_preset_dump_from_midi_input_port.value,

            PresetEvents.saved_to_file.value,
            PresetEvents.saved_preset_to_file.value,
            PresetEvents.loaded_file.value,
            PresetEvents.loaded_file_to_preset.value,
            PresetEvents.loaded_init_file.value,

            PresetEvents.saved_to_preset.value,

            PresetEvents.requested_preset_dump.value,
            PresetEvents.received_preset_dump_from_nymphes.value,
            PresetEvents.saved_preset_dump_from_midi_input_port_to_preset.value
        ]
