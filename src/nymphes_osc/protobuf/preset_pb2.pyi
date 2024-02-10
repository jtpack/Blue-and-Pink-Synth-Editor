from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class lfo_speed_mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    bpm: _ClassVar[lfo_speed_mode]
    slow: _ClassVar[lfo_speed_mode]
    fast: _ClassVar[lfo_speed_mode]
    tracking: _ClassVar[lfo_speed_mode]

class lfo_sync_mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    free: _ClassVar[lfo_sync_mode]
    key_synced: _ClassVar[lfo_sync_mode]

class voice_mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    poly: _ClassVar[voice_mode]
    uni_6: _ClassVar[voice_mode]
    uni_4: _ClassVar[voice_mode]
    uni_3: _ClassVar[voice_mode]
    uni_2: _ClassVar[voice_mode]
    mono: _ClassVar[voice_mode]
bpm: lfo_speed_mode
slow: lfo_speed_mode
fast: lfo_speed_mode
tracking: lfo_speed_mode
free: lfo_sync_mode
key_synced: lfo_sync_mode
poly: voice_mode
uni_6: voice_mode
uni_4: voice_mode
uni_3: voice_mode
uni_2: voice_mode
mono: voice_mode

class basic_inputs(_message.Message):
    __slots__ = ["wave", "lvl", "sub", "noise", "osc_lfo", "cut", "reson", "cut_eg", "a1", "d1", "s1", "r1", "lfo_rate", "lfo_wave", "pw", "glide", "dtune", "chord", "osc_eg", "hpf", "track", "cut_lfo", "a2", "d2", "s2", "r2", "lfo_delay", "lfo_fade"]
    WAVE_FIELD_NUMBER: _ClassVar[int]
    LVL_FIELD_NUMBER: _ClassVar[int]
    SUB_FIELD_NUMBER: _ClassVar[int]
    NOISE_FIELD_NUMBER: _ClassVar[int]
    OSC_LFO_FIELD_NUMBER: _ClassVar[int]
    CUT_FIELD_NUMBER: _ClassVar[int]
    RESON_FIELD_NUMBER: _ClassVar[int]
    CUT_EG_FIELD_NUMBER: _ClassVar[int]
    A1_FIELD_NUMBER: _ClassVar[int]
    D1_FIELD_NUMBER: _ClassVar[int]
    S1_FIELD_NUMBER: _ClassVar[int]
    R1_FIELD_NUMBER: _ClassVar[int]
    LFO_RATE_FIELD_NUMBER: _ClassVar[int]
    LFO_WAVE_FIELD_NUMBER: _ClassVar[int]
    PW_FIELD_NUMBER: _ClassVar[int]
    GLIDE_FIELD_NUMBER: _ClassVar[int]
    DTUNE_FIELD_NUMBER: _ClassVar[int]
    CHORD_FIELD_NUMBER: _ClassVar[int]
    OSC_EG_FIELD_NUMBER: _ClassVar[int]
    HPF_FIELD_NUMBER: _ClassVar[int]
    TRACK_FIELD_NUMBER: _ClassVar[int]
    CUT_LFO_FIELD_NUMBER: _ClassVar[int]
    A2_FIELD_NUMBER: _ClassVar[int]
    D2_FIELD_NUMBER: _ClassVar[int]
    S2_FIELD_NUMBER: _ClassVar[int]
    R2_FIELD_NUMBER: _ClassVar[int]
    LFO_DELAY_FIELD_NUMBER: _ClassVar[int]
    LFO_FADE_FIELD_NUMBER: _ClassVar[int]
    wave: float
    lvl: float
    sub: float
    noise: float
    osc_lfo: float
    cut: float
    reson: float
    cut_eg: float
    a1: float
    d1: float
    s1: float
    r1: float
    lfo_rate: float
    lfo_wave: float
    pw: float
    glide: float
    dtune: float
    chord: float
    osc_eg: float
    hpf: float
    track: float
    cut_lfo: float
    a2: float
    d2: float
    s2: float
    r2: float
    lfo_delay: float
    lfo_fade: float
    def __init__(self, wave: _Optional[float] = ..., lvl: _Optional[float] = ..., sub: _Optional[float] = ..., noise: _Optional[float] = ..., osc_lfo: _Optional[float] = ..., cut: _Optional[float] = ..., reson: _Optional[float] = ..., cut_eg: _Optional[float] = ..., a1: _Optional[float] = ..., d1: _Optional[float] = ..., s1: _Optional[float] = ..., r1: _Optional[float] = ..., lfo_rate: _Optional[float] = ..., lfo_wave: _Optional[float] = ..., pw: _Optional[float] = ..., glide: _Optional[float] = ..., dtune: _Optional[float] = ..., chord: _Optional[float] = ..., osc_eg: _Optional[float] = ..., hpf: _Optional[float] = ..., track: _Optional[float] = ..., cut_lfo: _Optional[float] = ..., a2: _Optional[float] = ..., d2: _Optional[float] = ..., s2: _Optional[float] = ..., r2: _Optional[float] = ..., lfo_delay: _Optional[float] = ..., lfo_fade: _Optional[float] = ...) -> None: ...

class reverb_inputs(_message.Message):
    __slots__ = ["size", "decay", "filter", "mix"]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    DECAY_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    MIX_FIELD_NUMBER: _ClassVar[int]
    size: float
    decay: float
    filter: float
    mix: float
    def __init__(self, size: _Optional[float] = ..., decay: _Optional[float] = ..., filter: _Optional[float] = ..., mix: _Optional[float] = ...) -> None: ...

class lfo_settings(_message.Message):
    __slots__ = ["lfo_1_speed_mode", "lfo_1_sync_mode", "lfo_2_speed_mode", "lfo_2_sync_mode"]
    LFO_1_SPEED_MODE_FIELD_NUMBER: _ClassVar[int]
    LFO_1_SYNC_MODE_FIELD_NUMBER: _ClassVar[int]
    LFO_2_SPEED_MODE_FIELD_NUMBER: _ClassVar[int]
    LFO_2_SYNC_MODE_FIELD_NUMBER: _ClassVar[int]
    lfo_1_speed_mode: lfo_speed_mode
    lfo_1_sync_mode: lfo_sync_mode
    lfo_2_speed_mode: lfo_speed_mode
    lfo_2_sync_mode: lfo_sync_mode
    def __init__(self, lfo_1_speed_mode: _Optional[_Union[lfo_speed_mode, str]] = ..., lfo_1_sync_mode: _Optional[_Union[lfo_sync_mode, str]] = ..., lfo_2_speed_mode: _Optional[_Union[lfo_speed_mode, str]] = ..., lfo_2_sync_mode: _Optional[_Union[lfo_sync_mode, str]] = ...) -> None: ...

class chord_info(_message.Message):
    __slots__ = ["root", "semi_1", "semi_2", "semi_3", "semi_4", "semi_5"]
    ROOT_FIELD_NUMBER: _ClassVar[int]
    SEMI_1_FIELD_NUMBER: _ClassVar[int]
    SEMI_2_FIELD_NUMBER: _ClassVar[int]
    SEMI_3_FIELD_NUMBER: _ClassVar[int]
    SEMI_4_FIELD_NUMBER: _ClassVar[int]
    SEMI_5_FIELD_NUMBER: _ClassVar[int]
    root: int
    semi_1: int
    semi_2: int
    semi_3: int
    semi_4: int
    semi_5: int
    def __init__(self, root: _Optional[int] = ..., semi_1: _Optional[int] = ..., semi_2: _Optional[int] = ..., semi_3: _Optional[int] = ..., semi_4: _Optional[int] = ..., semi_5: _Optional[int] = ...) -> None: ...

class extra_lfo_2_parameters(_message.Message):
    __slots__ = ["lfo_1_rate", "lfo_1_wave", "lfo_1_delay", "lfo_1_fade", "lfo_2_rate", "lfo_2_wave", "lfo_2_delay", "lfo_2_fade", "reverb_size", "reverb_decay", "reverb_filter", "reverb_mix"]
    LFO_1_RATE_FIELD_NUMBER: _ClassVar[int]
    LFO_1_WAVE_FIELD_NUMBER: _ClassVar[int]
    LFO_1_DELAY_FIELD_NUMBER: _ClassVar[int]
    LFO_1_FADE_FIELD_NUMBER: _ClassVar[int]
    LFO_2_RATE_FIELD_NUMBER: _ClassVar[int]
    LFO_2_WAVE_FIELD_NUMBER: _ClassVar[int]
    LFO_2_DELAY_FIELD_NUMBER: _ClassVar[int]
    LFO_2_FADE_FIELD_NUMBER: _ClassVar[int]
    REVERB_SIZE_FIELD_NUMBER: _ClassVar[int]
    REVERB_DECAY_FIELD_NUMBER: _ClassVar[int]
    REVERB_FILTER_FIELD_NUMBER: _ClassVar[int]
    REVERB_MIX_FIELD_NUMBER: _ClassVar[int]
    lfo_1_rate: float
    lfo_1_wave: float
    lfo_1_delay: float
    lfo_1_fade: float
    lfo_2_rate: float
    lfo_2_wave: float
    lfo_2_delay: float
    lfo_2_fade: float
    reverb_size: float
    reverb_decay: float
    reverb_filter: float
    reverb_mix: float
    def __init__(self, lfo_1_rate: _Optional[float] = ..., lfo_1_wave: _Optional[float] = ..., lfo_1_delay: _Optional[float] = ..., lfo_1_fade: _Optional[float] = ..., lfo_2_rate: _Optional[float] = ..., lfo_2_wave: _Optional[float] = ..., lfo_2_delay: _Optional[float] = ..., lfo_2_fade: _Optional[float] = ..., reverb_size: _Optional[float] = ..., reverb_decay: _Optional[float] = ..., reverb_filter: _Optional[float] = ..., reverb_mix: _Optional[float] = ...) -> None: ...

class extra_modulation_parameters(_message.Message):
    __slots__ = ["lfo_2_rate", "lfo_2_wave", "lfo_2_delay", "lfo_2_fade", "reverb_size", "reverb_decay", "reverb_filter", "reverb_mix"]
    LFO_2_RATE_FIELD_NUMBER: _ClassVar[int]
    LFO_2_WAVE_FIELD_NUMBER: _ClassVar[int]
    LFO_2_DELAY_FIELD_NUMBER: _ClassVar[int]
    LFO_2_FADE_FIELD_NUMBER: _ClassVar[int]
    REVERB_SIZE_FIELD_NUMBER: _ClassVar[int]
    REVERB_DECAY_FIELD_NUMBER: _ClassVar[int]
    REVERB_FILTER_FIELD_NUMBER: _ClassVar[int]
    REVERB_MIX_FIELD_NUMBER: _ClassVar[int]
    lfo_2_rate: float
    lfo_2_wave: float
    lfo_2_delay: float
    lfo_2_fade: float
    reverb_size: float
    reverb_decay: float
    reverb_filter: float
    reverb_mix: float
    def __init__(self, lfo_2_rate: _Optional[float] = ..., lfo_2_wave: _Optional[float] = ..., lfo_2_delay: _Optional[float] = ..., lfo_2_fade: _Optional[float] = ..., reverb_size: _Optional[float] = ..., reverb_decay: _Optional[float] = ..., reverb_filter: _Optional[float] = ..., reverb_mix: _Optional[float] = ...) -> None: ...

class preset(_message.Message):
    __slots__ = ["main", "reverb", "lfo_2", "mod_w", "velo", "after", "lfo_settings", "legato", "voice_mode", "chord_1", "chord_2", "chord_3", "chord_4", "chord_5", "chord_6", "chord_7", "chord_8", "extra_lfo_2", "extra_mod_w", "extra_velo", "extra_after", "amp_level"]
    MAIN_FIELD_NUMBER: _ClassVar[int]
    REVERB_FIELD_NUMBER: _ClassVar[int]
    LFO_2_FIELD_NUMBER: _ClassVar[int]
    MOD_W_FIELD_NUMBER: _ClassVar[int]
    VELO_FIELD_NUMBER: _ClassVar[int]
    AFTER_FIELD_NUMBER: _ClassVar[int]
    LFO_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    LEGATO_FIELD_NUMBER: _ClassVar[int]
    VOICE_MODE_FIELD_NUMBER: _ClassVar[int]
    CHORD_1_FIELD_NUMBER: _ClassVar[int]
    CHORD_2_FIELD_NUMBER: _ClassVar[int]
    CHORD_3_FIELD_NUMBER: _ClassVar[int]
    CHORD_4_FIELD_NUMBER: _ClassVar[int]
    CHORD_5_FIELD_NUMBER: _ClassVar[int]
    CHORD_6_FIELD_NUMBER: _ClassVar[int]
    CHORD_7_FIELD_NUMBER: _ClassVar[int]
    CHORD_8_FIELD_NUMBER: _ClassVar[int]
    EXTRA_LFO_2_FIELD_NUMBER: _ClassVar[int]
    EXTRA_MOD_W_FIELD_NUMBER: _ClassVar[int]
    EXTRA_VELO_FIELD_NUMBER: _ClassVar[int]
    EXTRA_AFTER_FIELD_NUMBER: _ClassVar[int]
    AMP_LEVEL_FIELD_NUMBER: _ClassVar[int]
    main: basic_inputs
    reverb: reverb_inputs
    lfo_2: basic_inputs
    mod_w: basic_inputs
    velo: basic_inputs
    after: basic_inputs
    lfo_settings: lfo_settings
    legato: bool
    voice_mode: voice_mode
    chord_1: chord_info
    chord_2: chord_info
    chord_3: chord_info
    chord_4: chord_info
    chord_5: chord_info
    chord_6: chord_info
    chord_7: chord_info
    chord_8: chord_info
    extra_lfo_2: extra_lfo_2_parameters
    extra_mod_w: extra_modulation_parameters
    extra_velo: extra_modulation_parameters
    extra_after: extra_modulation_parameters
    amp_level: float
    def __init__(self, main: _Optional[_Union[basic_inputs, _Mapping]] = ..., reverb: _Optional[_Union[reverb_inputs, _Mapping]] = ..., lfo_2: _Optional[_Union[basic_inputs, _Mapping]] = ..., mod_w: _Optional[_Union[basic_inputs, _Mapping]] = ..., velo: _Optional[_Union[basic_inputs, _Mapping]] = ..., after: _Optional[_Union[basic_inputs, _Mapping]] = ..., lfo_settings: _Optional[_Union[lfo_settings, _Mapping]] = ..., legato: bool = ..., voice_mode: _Optional[_Union[voice_mode, str]] = ..., chord_1: _Optional[_Union[chord_info, _Mapping]] = ..., chord_2: _Optional[_Union[chord_info, _Mapping]] = ..., chord_3: _Optional[_Union[chord_info, _Mapping]] = ..., chord_4: _Optional[_Union[chord_info, _Mapping]] = ..., chord_5: _Optional[_Union[chord_info, _Mapping]] = ..., chord_6: _Optional[_Union[chord_info, _Mapping]] = ..., chord_7: _Optional[_Union[chord_info, _Mapping]] = ..., chord_8: _Optional[_Union[chord_info, _Mapping]] = ..., extra_lfo_2: _Optional[_Union[extra_lfo_2_parameters, _Mapping]] = ..., extra_mod_w: _Optional[_Union[extra_modulation_parameters, _Mapping]] = ..., extra_velo: _Optional[_Union[extra_modulation_parameters, _Mapping]] = ..., extra_after: _Optional[_Union[extra_modulation_parameters, _Mapping]] = ..., amp_level: _Optional[float] = ...) -> None: ...
