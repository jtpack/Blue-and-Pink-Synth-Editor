from src.nymphes_osc.protobuf.preset_pb2 import preset, lfo_speed_mode, lfo_sync_mode, voice_mode
from pathlib import Path
import csv


class NymphesPreset:

    _csv_header_string = 'nymphes-midi preset v1.0.0'
    float_precision_num_decimals = 1

    _preset_params_map = {
        #
        # Oscillator Section
        #

        # Waveform
        'osc.wave.value':
            {'cc': 70,
             'mod_source': None,
             'preset_name': 'main.wave',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'osc.wave.lfo2':
            {'cc': 31,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.wave',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'osc.wave.mod_wheel':
            {'cc': 31,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.wave',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'osc.wave.velocity':
            {'cc': 31,
             'mod_source': 'velocity',
             'preset_name': 'velo.wave',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'osc.wave.aftertouch':
            {'cc': 31,
             'mod_source': 'aftertouch',
             'preset_name': 'after.wave',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Pulsewidth
        'osc.pulsewidth.value':
            {'cc': 12,
             'mod_source': None,
             'preset_name': 'main.pw',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'osc.pulsewidth.lfo2':
            {'cc': 36,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.pw',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'osc.pulsewidth.mod_wheel':
            {'cc': 36,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.pw',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'osc.pulsewidth.velocity':
            {'cc': 36,
             'mod_source': 'velocity',
             'preset_name': 'velo.pw',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'osc.pulsewidth.aftertouch':
            {'cc': 36,
             'mod_source': 'aftertouch',
             'preset_name': 'after.pw',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'osc.voice_mode.value':
            {'cc': 17,
             'mod_source': None,
             'preset_name': 'voice_mode',
             'type': int,
             'min': 0,
             'max': 5
             },

        'osc.legato.value': {
            'cc': 68,
            'mod_source': None,
            'preset_name': 'legato',
            'type': int,
            'min': 0,
            'max': 1
        },

        #
        # Mix Section
        #

        # Oscillator Level
        'mix.osc.value':
            {'cc': 9,
             'mod_source': None,
             'preset_name': 'main.lvl',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'mix.osc.lfo2':
            {'cc': 32,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.lvl',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'mix.osc.mod_wheel':
            {'cc': 32,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.lvl',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'mix.osc.velocity':
            {'cc': 32,
             'mod_source': 'velocity',
             'preset_name': 'velo.lvl',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'mix.osc.aftertouch':
            {'cc': 32,
             'mod_source': 'aftertouch',
             'preset_name': 'after.lvl',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Sub-Oscillator Level
        'mix.sub.value':
            {'cc': 10,
             'mod_source': None,
             'preset_name': 'main.sub',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'mix.sub.lfo2':
            {'cc': 33,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.sub',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'mix.sub.mod_wheel':
            {'cc': 33,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.sub',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'mix.sub.velocity':
            {'cc': 33,
             'mod_source': 'velocity',
             'preset_name': 'velo.sub',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'mix.sub.aftertouch':
            {'cc': 33,
             'mod_source': 'aftertouch',
             'preset_name': 'after.sub',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Noise Level
        'mix.noise.value':
            {'cc': 11,
             'mod_source': None,
             'preset_name': 'main.noise',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'mix.noise.lfo2':
            {'cc': 34,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.noise',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'mix.noise.mod_wheel':
            {'cc': 34,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.noise',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'mix.noise.velocity':
            {'cc': 34,
             'mod_source': 'velocity',
             'preset_name': 'velo.noise',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'mix.noise.aftertouch':
            {'cc': 34,
             'mod_source': 'aftertouch',
             'preset_name': 'after.noise',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'mix.level.value':
            {'cc': 7,
             'mod_source': None,
             'preset_name': 'amp_level',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        #
        # Pitch Section
        #

        # Glide
        'pitch.glide.value':
            {'cc': 5,
             'mod_source': None,
             'preset_name': 'main.glide',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.glide.lfo2':
            {'cc': 37,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.glide',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.glide.mod_wheel':
            {'cc': 37,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.glide',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.glide.velocity':
            {'cc': 37,
             'mod_source': 'velocity',
             'preset_name': 'velo.glide',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.glide.aftertouch':
            {'cc': 37,
             'mod_source': 'aftertouch',
             'preset_name': 'after.glide',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Detune
        'pitch.detune.value':
            {'cc': 15,
             'mod_source': None,
             'preset_name': 'main.dtune',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.detune.lfo2':
            {'cc': 39,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.dtune',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.detune.mod_wheel':
            {'cc': 39,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.dtune',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.detune.velocity':
            {'cc': 39,
             'mod_source': 'velocity',
             'preset_name': 'velo.dtune',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.detune.aftertouch':
            {'cc': 39,
             'mod_source': 'aftertouch',
             'preset_name': 'after.dtune',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Chord Selector
        'pitch.chord.value':
            {'cc': 16,
             'mod_source': None,
             'preset_name': 'main.chord',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.chord.lfo2':
            {'cc': 40,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.chord',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.chord.mod_wheel':
            {'cc': 40,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.chord',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.chord.velocity':
            {'cc': 40,
             'mod_source': 'velocity',
             'preset_name': 'velo.chord',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.chord.aftertouch':
            {'cc': 40,
             'mod_source': 'aftertouch',
             'preset_name': 'after.chord',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Pitch Envelope
        'pitch.eg.value':
            {'cc': 14,
             'mod_source': None,
             'preset_name': 'main.osc_eg',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.eg.lfo2':
            {'cc': 41,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.osc_eg',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.eg.mod_wheel':
            {'cc': 41,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.osc_eg',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.eg.velocity':
            {'cc': 41,
             'mod_source': 'velocity',
             'preset_name': 'velo.osc_eg',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.eg.aftertouch':
            {'cc': 41,
             'mod_source': 'aftertouch',
             'preset_name': 'after.osc_eg',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Pitch LFO1
        'pitch.lfo1.value':
            {'cc': 13,
             'mod_source': None,
             'preset_name': 'main.osc_lfo',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.lfo1.lfo2':
            {'cc': 35,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.osc_lfo',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.lfo1.mod_wheel':
            {'cc': 35,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.osc_lfo',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.lfo1.velocity':
            {'cc': 35,
             'mod_source': 'velocity',
             'preset_name': 'velo.osc_lfo',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'pitch.lfo1.aftertouch':
            {'cc': 35,
             'mod_source': 'aftertouch',
             'preset_name': 'after.osc_lfo',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        #
        # LPF Section
        #

        # Cutoff
        'lpf.cutoff.value':
            {'cc': 74,
             'mod_source': None,
             'preset_name': 'main.cut',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.cutoff.lfo2':
            {'cc': 42,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.cut',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.cutoff.mod_wheel':
            {'cc': 42,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.cut',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.cutoff.velocity':
            {'cc': 42,
             'mod_source': 'velocity',
             'preset_name': 'velo.cut',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.cutoff.aftertouch':
            {'cc': 42,
             'mod_source': 'aftertouch',
             'preset_name': 'after.cut',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Resonance
        'lpf.resonance.value':
            {'cc': 71,
             'mod_source': None,
             'preset_name': 'main.reson',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.resonance.lfo2':
            {'cc': 43,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.reson',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.resonance.mod_wheel':
            {'cc': 43,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.reson',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.resonance.velocity':
            {'cc': 43,
             'mod_source': 'velocity',
             'preset_name': 'velo.reson',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.resonance.aftertouch':
            {'cc': 43,
             'mod_source': 'aftertouch',
             'preset_name': 'after.reson',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Tracking
        'lpf.tracking.value':
            {'cc': 4,
             'mod_source': None,
             'preset_name': 'main.track',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.tracking.lfo2':
            {'cc': 46,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.track',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.tracking.mod_wheel':
            {'cc': 46,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.track',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.tracking.velocity':
            {'cc': 46,
             'mod_source': 'velocity',
             'preset_name': 'velo.track',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.tracking.aftertouch':
            {'cc': 46,
             'mod_source': 'aftertouch',
             'preset_name': 'after.track',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # LPF Envelope
        'lpf.eg.value':
            {'cc': 3,
             'mod_source': None,
             'preset_name': 'main.cut_eg',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.eg.lfo2':
            {'cc': 44,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.cut_eg',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.eg.mod_wheel':
            {'cc': 44,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.cut_eg',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.eg.velocity':
            {'cc': 44,
             'mod_source': 'velocity',
             'preset_name': 'velo.cut_eg',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.eg.aftertouch':
            {'cc': 44,
             'mod_source': 'aftertouch',
             'preset_name': 'after.cut_eg',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # LPF LFO1
        'lpf.lfo1.value':
            {'cc': 8,
             'mod_source': None,
             'preset_name': 'main.cut_lfo',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.lfo1.lfo2':
            {'cc': 47,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.cut_lfo',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.lfo1.mod_wheel':
            {'cc': 47,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.cut_lfo',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.lfo1.velocity':
            {'cc': 47,
             'mod_source': 'velocity',
             'preset_name': 'velo.cut_lfo',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lpf.lfo1.aftertouch':
            {'cc': 47,
             'mod_source': 'aftertouch',
             'preset_name': 'after.cut_lfo',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        #
        # HPF Section
        #

        # Cutoff
        'hpf.cutoff.value':
            {'cc': 81,
             'mod_source': None,
             'preset_name': 'main.hpf',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'hpf.cutoff.lfo2':
            {'cc': 45,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.hpf',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'hpf.cutoff.mod_wheel':
            {'cc': 45,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.hpf',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'hpf.cutoff.velocity':
            {'cc': 45,
             'mod_source': 'velocity',
             'preset_name': 'velo.hpf',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'hpf.cutoff.aftertouch':
            {'cc': 45,
             'mod_source': 'aftertouch',
             'preset_name': 'after.hpf',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        #
        # Pitch / Filter Envelope Section
        #

        # Attack
        'filter_eg.attack.value':
            {'cc': 79,
             'mod_source': None,
             'preset_name': 'main.a1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'filter_eg.attack.lfo2':
            {'cc': 48,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.a1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'filter_eg.attack.mod_wheel':
            {'cc': 48,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.a1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'filter_eg.attack.velocity':
            {'cc': 48,
             'mod_source': 'velocity',
             'preset_name': 'velo.a1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'filter_eg.attack.aftertouch':
            {'cc': 48,
             'mod_source': 'aftertouch',
             'preset_name': 'after.a1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Decay
        'filter_eg.decay.value':
            {'cc': 80,
             'mod_source': None,
             'preset_name': 'main.d1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'filter_eg.decay.lfo2':
            {'cc': 49,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.d1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'filter_eg.decay.mod_wheel':
            {'cc': 49,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.d1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'filter_eg.decay.velocity':
            {'cc': 49,
             'mod_source': 'velocity',
             'preset_name': 'velo.d1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'filter_eg.decay.aftertouch':
            {'cc': 49,
             'mod_source': 'aftertouch',
             'preset_name': 'after.d1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Sustain
        'filter_eg.sustain.value':
            {'cc': 82,
             'mod_source': None,
             'preset_name': 'main.s1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'filter_eg.sustain.lfo2':
            {'cc': 50,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.s1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'filter_eg.sustain.mod_wheel':
            {'cc': 50,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.s1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'filter_eg.sustain.velocity':
            {'cc': 50,
             'mod_source': 'velocity',
             'preset_name': 'velo.s1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'filter_eg.sustain.aftertouch':
            {'cc': 50,
             'mod_source': 'aftertouch',
             'preset_name': 'after.s1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Release
        'filter_eg.release.value':
            {'cc': 83,
             'mod_source': None,
             'preset_name': 'main.r1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'filter_eg.release.lfo2':
            {'cc': 51,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.r1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'filter_eg.release.mod_wheel':
            {'cc': 51,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.r1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'filter_eg.release.velocity':
            {'cc': 51,
             'mod_source': 'velocity',
             'preset_name': 'velo.r1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'filter_eg.release.aftertouch':
            {'cc': 51,
             'mod_source': 'aftertouch',
             'preset_name': 'after.r1',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        #
        # Amp Envelope Section
        #

        # Attack
        'amp_eg.attack.value':
            {'cc': 73,
             'mod_source': None,
             'preset_name': 'main.a2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'amp_eg.attack.lfo2':
            {'cc': 52,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.a2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'amp_eg.attack.mod_wheel':
            {'cc': 52,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.a2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'amp_eg.attack.velocity':
            {'cc': 52,
             'mod_source': 'velocity',
             'preset_name': 'velo.a2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'amp_eg.attack.aftertouch':
            {'cc': 52,
             'mod_source': 'aftertouch',
             'preset_name': 'after.a2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Decay
        'amp_eg.decay.value':
            {'cc': 84,
             'mod_source': None,
             'preset_name': 'main.d2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'amp_eg.decay.lfo2':
            {'cc': 53,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.d2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'amp_eg.decay.mod_wheel':
            {'cc': 53,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.d2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'amp_eg.decay.velocity':
            {'cc': 53,
             'mod_source': 'velocity',
             'preset_name': 'velo.d2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'amp_eg.decay.aftertouch':
            {'cc': 53,
             'mod_source': 'aftertouch',
             'preset_name': 'after.d2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Sustain
        'amp_eg.sustain.value':
            {'cc': 85,
             'mod_source': None,
             'preset_name': 'main.s2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'amp_eg.sustain.lfo2':
            {'cc': 54,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.s2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'amp_eg.sustain.mod_wheel':
            {'cc': 54,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.s2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'amp_eg.sustain.velocity':
            {'cc': 54,
             'mod_source': 'velocity',
             'preset_name': 'velo.s2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'amp_eg.sustain.aftertouch':
            {'cc': 54,
             'mod_source': 'aftertouch',
             'preset_name': 'after.s2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Release
        'amp_eg.release.value':
            {'cc': 72,
             'mod_source': None,
             'preset_name': 'main.r2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'amp_eg.release.lfo2':
            {'cc': 55,
             'mod_source': 'lfo2',
             'preset_name': 'lfo_2.r2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'amp_eg.release.mod_wheel':
            {'cc': 55,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.r2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'amp_eg.release.velocity':
            {'cc': 55,
             'mod_source': 'velocity',
             'preset_name': 'velo.r2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'amp_eg.release.aftertouch':
            {'cc': 55,
             'mod_source': 'aftertouch',
             'preset_name': 'after.r2',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        #
        # Pitch / Filter LFO (LFO 1) Section
        #

        # Rate
        'lfo1.rate.value':
            {'cc': 18,
             'mod_source': None,
             'preset_name': 'main.lfo_rate',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo1.rate.lfo2':
            {'cc': 56,
             'mod_source': 'lfo2',
             'preset_name': 'extra_lfo_2.lfo_1_rate',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo1.rate.mod_wheel':
            {'cc': 56,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.lfo_rate',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo1.rate.velocity':
            {'cc': 56,
             'mod_source': 'velocity',
             'preset_name': 'velo.lfo_rate',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo1.rate.aftertouch':
            {'cc': 56,
             'mod_source': 'aftertouch',
             'preset_name': 'after.lfo_rate',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Waveform
        'lfo1.wave.value':
            {'cc': 19,
             'mod_source': None,
             'preset_name': 'main.lfo_wave',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo1.wave.lfo2':
            {'cc': 57,
             'mod_source': 'lfo2',
             'preset_name': 'extra_lfo_2.lfo_1_wave',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo1.wave.mod_wheel':
            {'cc': 57,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.lfo_wave',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo1.wave.velocity':
            {'cc': 57,
             'mod_source': 'velocity',
             'preset_name': 'velo.lfo_wave',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo1.wave.aftertouch':
            {'cc': 57,
             'mod_source': 'aftertouch',
             'preset_name': 'after.lfo_wave',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Delay
        'lfo1.delay.value':
            {'cc': 20,
             'mod_source': None,
             'preset_name': 'main.lfo_delay',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo1.delay.lfo2':
            {'cc': 58,
             'mod_source': 'lfo2',
             'preset_name': 'extra_lfo_2.lfo_1_delay',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo1.delay.mod_wheel':
            {'cc': 58,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.lfo_delay',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo1.delay.velocity':
            {'cc': 58,
             'mod_source': 'velocity',
             'preset_name': 'velo.lfo_delay',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo1.delay.aftertouch':
            {'cc': 58,
             'mod_source': 'aftertouch',
             'preset_name': 'after.lfo_delay',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Fade
        'lfo1.fade.value':
            {'cc': 21,
             'mod_source': None,
             'preset_name': 'main.lfo_fade',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo1.fade.lfo2':
            {'cc': 59,
             'mod_source': 'lfo2',
             'preset_name': 'extra_lfo_2.lfo_1_fade',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo1.fade.mod_wheel':
            {'cc': 59,
             'mod_source': 'mod_wheel',
             'preset_name': 'mod_w.lfo_fade',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo1.fade.velocity':
            {'cc': 59,
             'mod_source': 'velocity',
             'preset_name': 'velo.lfo_fade',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo1.fade.aftertouch':
            {'cc': 59,
             'mod_source': 'aftertouch',
             'preset_name': 'after.lfo_fade',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Type
        'lfo1.type.value':
            {'cc': 22,
             'mod_source': None,
             'preset_name': 'lfo_settings.lfo_1_speed_mode',
             'type': int,
             'min': 0,
             'max': 3
             },

        # Key Sync
        'lfo1.key_sync.value':
            {'cc': 23,
             'mod_source': None,
             'preset_name': 'lfo_settings.lfo_1_sync_mode',
             'type': int,
             'min': 0,
             'max': 1
             },

        #
        # LFO 2 Section
        #

        # Rate
        'lfo2.rate.value':
            {'cc': 24,
             'mod_source': None,
             'preset_name': 'lfo_2.lfo_rate',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo2.rate.lfo2':
            {'cc': 60,
             'mod_source': 'lfo2',
             'preset_name': 'extra_lfo_2.lfo_2_rate',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo2.rate.mod_wheel':
            {'cc': 60,
             'mod_source': 'mod_wheel',
             'preset_name': 'extra_mod_w.lfo_2_rate',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo2.rate.velocity':
            {'cc': 60,
             'mod_source': 'velocity',
             'preset_name': 'extra_velo.lfo_2_rate',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo2.rate.aftertouch':
            {'cc': 60,
             'mod_source': 'aftertouch',
             'preset_name': 'extra_after.lfo_2_rate',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Waveform
        'lfo2.wave.value':
            {'cc': 25,
             'mod_source': None,
             'preset_name': 'main.lfo_wave',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo2.wave.lfo2':
            {'cc': 61,
             'mod_source': 'lfo2',
             'preset_name': 'extra_lfo_2.lfo_2_wave',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo2.wave.mod_wheel':
            {'cc': 61,
             'mod_source': 'mod_wheel',
             'preset_name': 'extra_mod_w.lfo_2_wave',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo2.wave.velocity':
            {'cc': 61,
             'mod_source': 'velocity',
             'preset_name': 'extra_velo.lfo_2_wave',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo2.wave.aftertouch':
            {'cc': 61,
             'mod_source': 'aftertouch',
             'preset_name': 'extra_after.lfo_2_wave',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Delay
        'lfo2.delay.value':
            {'cc': 26,
             'mod_source': None,
             'preset_name': 'main.lfo_delay',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo2.delay.lfo2':
            {'cc': 62,
             'mod_source': 'lfo2',
             'preset_name': 'extra_lfo_2.lfo_2_delay',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo2.delay.mod_wheel':
            {'cc': 62,
             'mod_source': 'mod_wheel',
             'preset_name': 'extra_mod_w.lfo_2_delay',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo2.delay.velocity':
            {'cc': 62,
             'mod_source': 'velocity',
             'preset_name': 'extra_velo.lfo_2_delay',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo2.delay.aftertouch':
            {'cc': 62,
             'mod_source': 'aftertouch',
             'preset_name': 'extra_after.lfo_2_delay',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Fade
        'lfo2.fade.value':
            {'cc': 27,
             'mod_source': None,
             'preset_name': 'main.lfo_fade',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo2.fade.lfo2':
            {'cc': 63,
             'mod_source': 'lfo2',
             'preset_name': 'extra_lfo_2.lfo_2_fade',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo2.fade.mod_wheel':
            {'cc': 63,
             'mod_source': 'mod_wheel',
             'preset_name': 'extra_mod_w.lfo_2_fade',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo2.fade.velocity':
            {'cc': 63,
             'mod_source': 'velocity',
             'preset_name': 'extra_velo.lfo_2_fade',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'lfo2.fade.aftertouch':
            {'cc': 63,
             'mod_source': 'aftertouch',
             'preset_name': 'extra_after.lfo_2_fade',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Type
        'lfo2.type.value':
            {'cc': 28,
             'mod_source': None,
             'preset_name': 'lfo_settings.lfo_1_speed_mode',
             'type': int,
             'min': 0,
             'max': 3
             },

        # Key Sync
        'lfo2.key_sync.value':
            {'cc': 29,
             'mod_source': None,
             'preset_name': 'lfo_settings.lfo_1_sync_mode',
             'type': int,
             'min': 0,
             'max': 1
             },

        #
        # Reverb Section
        #

        # Size
        'reverb.size.value':
            {'cc': 75,
             'mod_source': None,
             'preset_name': 'reverb.size',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'reverb.size.lfo2':
            {'cc': 86,
             'mod_source': 'lfo2',
             'preset_name': 'extra_lfo_2.reverb_size',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'reverb.size.mod_wheel':
            {'cc': 86,
             'mod_source': 'mod_wheel',
             'preset_name': 'extra_mod_w.reverb_size',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'reverb.size.velocity':
            {'cc': 86,
             'mod_source': 'velocity',
             'preset_name': 'extra_velo.reverb_size',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'reverb.size.aftertouch':
            {'cc': 86,
             'mod_source': 'aftertouch',
             'preset_name': 'extra_after.reverb_size',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Decay
        'reverb.decay.value':
            {'cc': 76,
             'mod_source': None,
             'preset_name': 'reverb.decay',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'reverb.decay.lfo2':
            {'cc': 87,
             'mod_source': 'lfo2',
             'preset_name': 'extra_lfo_2.reverb_decay',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'reverb.decay.mod_wheel':
            {'cc': 87,
             'mod_source': 'mod_wheel',
             'preset_name': 'extra_mod_w.reverb_decay',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'reverb.decay.velocity':
            {'cc': 87,
             'mod_source': 'velocity',
             'preset_name': 'extra_velo.reverb_decay',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'reverb.decay.aftertouch':
            {'cc': 87,
             'mod_source': 'aftertouch',
             'preset_name': 'extra_after.reverb_decay',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Filter
        'reverb.filter.value':
            {'cc': 77,
             'mod_source': None,
             'preset_name': 'reverb.filter',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'reverb.filter.lfo2':
            {'cc': 88,
             'mod_source': 'lfo2',
             'preset_name': 'extra_lfo_2.reverb_filter',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'reverb.filter.mod_wheel':
            {'cc': 88,
             'mod_source': 'mod_wheel',
             'preset_name': 'extra_mod_w.reverb_filter',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'reverb.filter.velocity':
            {'cc': 88,
             'mod_source': 'velocity',
             'preset_name': 'extra_velo.reverb_filter',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'reverb.filter.aftertouch':
            {'cc': 88,
             'mod_source': 'aftertouch',
             'preset_name': 'extra_after.reverb_filter',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        # Mix
        'reverb.mix.value':
            {'cc': 78,
             'mod_source': None,
             'preset_name': 'reverb.mix',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'reverb.mix.lfo2':
            {'cc': 89,
             'mod_source': 'lfo2',
             'preset_name': 'extra_lfo_2.reverb_mix',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'reverb.mix.mod_wheel':
            {'cc': 89,
             'mod_source': 'mod_wheel',
             'preset_name': 'extra_mod_w.reverb_mix',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'reverb.mix.velocity':
            {'cc': 89,
             'mod_source': 'velocity',
             'preset_name': 'extra_velo.reverb_mix',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        'reverb.mix.aftertouch':
            {'cc': 89,
             'mod_source': 'aftertouch',
             'preset_name': 'extra_after.reverb_mix',
             'type': float,
             'min': 0.0,
             'max': 127.0
             },

        #
        # Chord Sections
        #

        # Chord 1
        'chord_1.root.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_1.root',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_1.semi_1.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_1.semi_1',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_1.semi_2.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_1.semi_2',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_1.semi_3.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_1.semi_3',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_1.semi_4.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_1.semi_4',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_1.semi_5.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_1.semi_5',
             'type': int,
             'min': 0,
             'max': 127
             },

        # Chord 2
        'chord_2.root.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_2.root',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_2.semi_1.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_2.semi_1',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_2.semi_2.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_2.semi_2',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_2.semi_3.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_2.semi_3',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_2.semi_4.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_2.semi_4',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_2.semi_5.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_2.semi_5',
             'type': int,
             'min': 0,
             'max': 127
             },

        # Chord 3
        'chord_3.root.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_3.root',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_3.semi_1.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_3.semi_1',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_3.semi_2.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_3.semi_2',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_3.semi_3.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_3.semi_3',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_3.semi_4.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_3.semi_4',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_3.semi_5.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_3.semi_5',
             'type': int,
             'min': 0,
             'max': 127
             },

        # Chord 4
        'chord_4.root.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_4.root',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_4.semi_1.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_4.semi_1',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_4.semi_2.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_4.semi_2',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_4.semi_3.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_4.semi_3',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_4.semi_4.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_4.semi_4',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_4.semi_5.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_4.semi_5',
             'type': int,
             'min': 0,
             'max': 127
             },

        # Chord 5
        'chord_5.root.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_5.root',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_5.semi_1.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_5.semi_1',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_5.semi_2.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_5.semi_2',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_5.semi_3.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_5.semi_3',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_5.semi_4.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_5.semi_4',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_5.semi_5.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_5.semi_5',
             'type': int,
             'min': 0,
             'max': 127
             },

        # Chord 6
        'chord_6.root.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_6.root',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_6.semi_1.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_6.semi_1',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_6.semi_2.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_6.semi_2',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_6.semi_3.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_6.semi_3',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_6.semi_4.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_6.semi_4',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_6.semi_5.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_6.semi_5',
             'type': int,
             'min': 0,
             'max': 127
             },

        # Chord 7
        'chord_7.root.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_7.root',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_7.semi_1.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_7.semi_1',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_7.semi_2.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_7.semi_2',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_7.semi_3.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_7.semi_3',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_7.semi_4.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_7.semi_4',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_7.semi_5.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_7.semi_5',
             'type': int,
             'min': 0,
             'max': 127
             },

        # Chord 8
        'chord_8.root.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_8.root',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_8.semi_1.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_8.semi_1',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_8.semi_2.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_8.semi_2',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_8.semi_3.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_8.semi_3',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_8.semi_4.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_8.semi_4',
             'type': int,
             'min': 0,
             'max': 127
             },

        'chord_8.semi_5.value':
            {'cc': None,
             'mod_source': None,
             'preset_name': 'chord_8.semi_5',
             'type': int,
             'min': 0,
             'max': 127
             }
    }

    def __init__(self, sysex_data=None, filepath=None, print_logs_enabled=False):
        """
        If sysex_data is not None, then try to decode the data
        and use it as the underlying protobuf preset object.
        If filepath is not None, then try to decode the data in
        the file and use it as the underlying protobuf preset object.
        :param sysex_data: A list of bytes
        :param filepath:
        """
        self._print_logs_enabled = print_logs_enabled

        # Preset Metadata
        self._preset_import_type = None
        self._preset_type = None
        self._bank_name = None
        self._preset_number = None

        # Generate the underlying protobuf preset object
        # that we use for parameter storage
        #
        self._protobuf_preset = None

        if sysex_data is not None:
            # Use the supplied SYSEX data for our parameter values
            #
            self._protobuf_preset, self._preset_import_type, self._preset_type, self._bank_name, self._preset_number = self._protobuf_preset_from_sysex_data(
                sysex_data)

            self._log_message('Decoded SYSEX Data')
            self._log_message(f'preset_import_type: {self.preset_import_type}')
            self._log_message(f'preset_type: {self.preset_type}')
            self._log_message(f'bank_name: {self.bank_name}')
            self._log_message(f'preset_number: {self.preset_number}')

        elif filepath is not None:
            # Try loading parameters from the file
            self._protobuf_preset = self._protobuf_preset_from_file(filepath)

            self._log_message(f'Loaded preset file: {filepath}')

        else:
            # Create a preset with default values
            self._protobuf_preset = self._create_default_protobuf_preset()

            self._log_message('Using default preset values')

    @property
    def print_logs_enabled(self):
        return self._print_logs_enabled

    @print_logs_enabled.setter
    def print_logs_enabled(self, enable):
        self._print_logs_enabled = enable

    @property
    def preset_import_type(self):
        """
        If the preset was created by decoding a SYSEX message,
        then this will be either 'persistent' or 'non-persistent'.
        Otherwise it will be None.
        :return: str or None
        """
        return self._preset_import_type

    @property
    def preset_type(self):
        """
        If the preset was created by decoding a SYSEX message,
        then this will be either 'user' or 'factory'.
        Otherwise it will be None.
        :return: str or None
        """
        return self._preset_type

    @property
    def bank_name(self):
        """
        If the preset was created by decoding a SYSEX message,
        then this will be either one of the following:
        'A', 'B', 'C', 'D', 'E', 'F', 'G'.
        Otherwise it will be None.
        :return: str or None
        """
        return self._bank_name

    @property
    def preset_number(self):
        """
        If the preset was created by decoding a SYSEX message,
        then this will be either one of the following:
        1, 2, 3, 4, 5, 6, 7
        Otherwise it will be None.
        :return: int or None
        """
        return self._preset_number

    def all_params_dict(self):
        """
        Return a dictionary of all parameters, including metadata,
        preset import type, preset type, etc
        :return: dict
        """
        params_dict = {}

        # Populate metadata
        params_dict['preset_import_type'] = self._preset_import_type
        params_dict['preset_type'] = self._preset_type
        params_dict['bank_name'] = self._bank_name
        params_dict['preset_number'] = self._preset_number
        params_dict['float_precision_num_decimals'] = NymphesPreset.float_precision_num_decimals

        # Populate preset parameters
        for param_name in NymphesPreset.all_param_names():
            # Get the type for this parameter
            param_type = NymphesPreset.type_for_param_name(param_name)

            # Get the correct value for the parameter based
            # on its type
            if param_type == int:
                param_value = self.get_int(param_name)

            elif param_type == float:
                param_value = self.get_float(param_name)

            # Store the value
            params_dict[param_name] = param_value

        return params_dict

    def __repr__(self):
        # Construct a string with each parameter on a separate
        # line
        #
        params_string = ''
        for name, value in self.all_params_dict().items():
            params_string += (f'{name}: {value}' + '\n')

        # Return it
        return params_string

    @staticmethod
    def midi_cc_for_param_name(name):
        """
        Gets the MIDI Control Change number for the supplied
        parameter name.
        If the there is no midi_cc (in the case of chord parameters),
        then return None.
        Raises an Exception if the name is invalid.
        :param name: str
        :return: int or None
        """
        # Make sure the name is valid
        if name not in NymphesPreset._preset_params_map:
            raise Exception(f'Invalid parameter name: {name}')

        # Get and return the MIDI CC
        return NymphesPreset._preset_params_map[name]['cc']

    @staticmethod
    def mod_source_for_param_name(name):
        """
        Gets the modulation source for the supplied
        parameter name.
        If the parameter is not a modulation matrix
        parameter, then return None.
        Raises an Exception if the name is invalid.
        :param name: str
        :return: str or None
        """
        # Make sure the name is valid
        if name not in NymphesPreset._preset_params_map:
            raise Exception(f'Invalid parameter name: {name}')

        # Get and return the mod source
        return NymphesPreset._preset_params_map[name]['mod_source']

    @staticmethod
    def type_for_param_name(name):
        """
        Gets the type of the supplied parameter.
        Raises an Exception if the name is invalid.
        :param name: str
        :return: float or int
        """
        # Make sure the name is valid
        if name not in NymphesPreset._preset_params_map:
            raise Exception(f'Invalid parameter name: {name}')

        # Get and return the type
        return NymphesPreset._preset_params_map[name]['type']

    @staticmethod
    def min_val_for_param_name(name):
        """
        Gets the minimum value for the supplied parameter.
        Raises an Exception if the name is invalid.
        :param name: str
        :return: float or int
        """
        # Make sure the name is valid
        if name not in NymphesPreset._preset_params_map:
            raise Exception(f'Invalid parameter name: {name}')

        # Get and return the minimum value
        return NymphesPreset._preset_params_map[name]['min']

    @staticmethod
    def max_val_for_param_name(name):
        """
        Gets the maximum value for the supplied parameter.
        Raises an Exception if the name is invalid.
        :param name: str
        :return: float or int
        """
        # Make sure the name is valid
        if name not in NymphesPreset._preset_params_map:
            raise Exception(f'Invalid parameter name: {name}')

        # Get and return the maximum value
        return NymphesPreset._preset_params_map[name]['max']

    @staticmethod
    def param_name_for_preset_name(preset_name):
        """
        Gets the parameter name for the supplied preset name.
        Raises an Exception if the preset name is invalid.
        :param preset_name: str
        :return: str
        """
        # Create a dict of preset names
        preset_names_dict = {NymphesPreset._preset_params_map[param_name]['preset_name']: param_name for param_name in
                             NymphesPreset._preset_params_map.keys()}

        # Make sure preset_name is valid
        if preset_name not in preset_names_dict:
            raise Exception(f'Invalid preset name: {preset_name}')

        return preset_names_dict[preset_name]

    @staticmethod
    def param_names_for_midi_cc(midi_cc):
        """
        Gets a list of parameter names for the supplied midi_cc.
        Returns a list, as for modulation matrix
        parameters there will be four different names for each
        MIDI Control Change number.
        The list will be empty if midi_cc is not found.
        :param midi_cc: int from 0 to 127
        :return: A list of strings
        """
        # Make sure midi_cc is valid
        if midi_cc < 0 or midi_cc > 127:
            raise Exception(f'Invalid midi_cc: {midi_cc} (Should be between 0 and 127)')

        # Get and return the list of matching parameter names
        return [name for name, data in NymphesPreset._preset_params_map.items() if data['cc'] == midi_cc]

    @staticmethod
    def all_param_names():
        """
        Returns a list of all parameter names
        :return: A list of strings
        """
        return list(NymphesPreset._preset_params_map.keys())

    @staticmethod
    def all_section_names():
        """
        Returns a list of all parameter section names
        :return: A list of strings
        """
        # Get just the sections from all param names
        section_names = [param_name.split('.')[0] for param_name in NymphesPreset.all_param_names()]

        # Return only unique values
        return sorted(set(section_names))

    @staticmethod
    def features_for_section(section_name):
        """
        Returns a list of feature names for a section.
        This means the name of the feature itcls, ignoring
        value or mod matrix suffixes.
        :param section_name: str
        :return: A list of strings
        """
        # Make sure section_name is valid
        if section_name not in NymphesPreset.all_section_names():
            raise Exception(f'Invalid section_name: {section_name}')

        feature_names = []
        for param_name in NymphesPreset.all_param_names():
            section, feature, *_ = param_name.split('.')

            if section == section_name:
                feature_names.append(feature)

        # Remove duplicates and sort
        feature_names = sorted(set(feature_names))

        return feature_names

    @staticmethod
    def params_for_feature(section_name, feature_name):
        """
        Returns the parameter names for the supplied section
        and feature.
        Raises an Exception if section_name or feature_name
        are invalid, or if feature_name does not belong to
        section_name
        :param section_name: str
        :param feature_name: str
        :return: A list of strings
        """
        # Make sure section_name is valid
        if section_name not in NymphesPreset.all_section_names():
            raise Exception(f'Invalid section: {section_name}')

        # Get a list of features for the section
        features = NymphesPreset.features_for_section(section_name)

        # Make sure feature_name is valid
        if feature_name not in features:
            raise Exception(f'Invalid feature for {section_name} section: {feature_name}')

        # Collect all parameters that match the section and feature
        param_names = []
        for param_name in NymphesPreset.all_param_names():
            section, feature, *_ = param_name.split('.')

            if section == section_name and feature == feature_name:
                param_names.append(param_name)

        return param_names

    @staticmethod
    def param_for_target(section_name, feature_name, target_name):
        """
        Returns the name of the parameter for the supplied section,
        feature and target.
        Returns None if the feature does not have the specified target.
        Raises an Exception if target_name in invalid.
        :param section_name: str
        :param feature_name: str
        :param target_name: str. 'value', 'lfo2', 'mod_wheel', 'velocity', 'aftertouch'
        :return: str or None
        """
        # Make sure target_name is valid
        if target_name not in ['value', 'lfo2', 'mod_wheel', 'velocity', 'aftertouch']:
            raise Exception(f'Invalid target_name: {target_name}')

        # Get a list of all params for the feature
        param_names = NymphesPreset.params_for_feature(section_name, feature_name)

        if len(param_names) == 1:
            # This feature does not have any mod matrix params
            if target_name == 'value':
                return param_names[0]
            else:
                return None

        else:
            # This feature has mod matrix params.
            # Find the one that targets the value itcls.
            for param_name in param_names:
                section, feature, target = param_name.split('.')

                if target == target_name:
                    return param_name

    @staticmethod
    def section_for_param(param_name):
        """
        Returns the name of the section for the parameter.
        Raises an Exception if param_name is invalid.
        :param param_name: str
        :return: str
        """
        # Make sure the name is valid
        if param_name not in NymphesPreset._preset_params_map:
            raise Exception(f'Invalid parameter name: {param_name}')

        # Separate param_name into components
        components = param_name.split('.')

        # Return the first component
        return components[0]

    @staticmethod
    def feature_for_param(param_name):
        """
        Returns the name of the feature for the parameter.
        Raises an Exception if param_name is invalid.
        :param param_name: str
        :return: str
        """
        # Make sure the name is valid
        if param_name not in NymphesPreset._preset_params_map:
            raise Exception(f'Invalid parameter name: {param_name}')

        # Separate param_name into components
        components = param_name.split('.')

        # Return the second component
        return components[1]

    @staticmethod
    def target_for_param(param_name):
        """
        Returns the name of the target for the parameter.
        Raises an Exception if param_name is invalid.
        :param param_name: str
        :return: str
        """
        # Make sure the name is valid
        if param_name not in NymphesPreset._preset_params_map:
            raise Exception(f'Invalid parameter name: {param_name}')

        # Separate param_name into components
        components = param_name.split('.')

        # Return the last component
        return components[-1]

    def set_float(self, param_name, value):
        """
        Set a float parameter's value.
        Raises an Exception if param_name is invalid, if the parameter
        is not a float parameter, or if it is outside the min and max
        range.
        :param param_name: str
        :param value: float
        :return: True if value was different than the previous value
        for the parameter. False if it was the same.
        """
        # Make sure param_name is valid
        if param_name not in self.all_param_names():
            raise Exception(f'Invalid param_name: {param_name}')

        # Make sure this ia a float parameter
        if self.type_for_param_name(param_name) != float:
            raise Exception(f'{param_name} is not a float parameter')

        # Make sure the value is valid
        #
        min_val = self.min_val_for_param_name(param_name)
        max_val = self.max_val_for_param_name(param_name)
        if value < min_val or value > max_val:
            raise Exception(f'Invalid value: {value} (Should be between {min_val} and {max_val})')

        # Get the preset_param_name for this parameter
        preset_param_name = self._protobuf_preset_name_for_param_name(param_name)

        # Divide the value by 127.0 because the underlying protobuf preset
        # object uses 0.0 to 1.0 for float values
        value /= 127.0

        # Set the value in the preset
        return self._set_protobuf_preset_value(self._protobuf_preset, preset_param_name, value)

    def set_int(self, param_name, value):
        """
        Set any parameter's value using an int.
        If the parameter is actually a float parameter,
        then divide value by 127.0.
        :param param_name: str
        :param value: int. Should never be outside the range 0 to 127
        :return: True if value was different than the previous value
        for the parameter. False if it was the same.
        """


        # Make sure param_name is valid
        if param_name not in self.all_param_names():
            raise Exception(f'Invalid param_name: {param_name}')

        # Convert the value to float if this is actually
        # a float parameter
        if self.type_for_param_name(param_name) == float:
            value = value / 127.0

        # Make sure the value is valid
        #
        min_val = self.min_val_for_param_name(param_name)
        max_val = self.max_val_for_param_name(param_name)
        if value < min_val or value > max_val:
            raise Exception(f'Invalid value: {value} (should be between {min_val} and {max_val}')

        # Get the preset_param_name for this parameter
        preset_param_name = self._protobuf_preset_name_for_param_name(param_name)

        # Set the value in the preset
        return self._set_protobuf_preset_value(self._protobuf_preset, preset_param_name, value)

    def get_float(self, param_name):
        """
        Get a float parameter's value.
        Raises an Exception if param_name is invalid or if the
        parameter is not a float parameter.
        :param param_name: str
        :return: float
        """
        # Make sure param_name is valid
        if param_name not in self.all_param_names():
            raise Exception(f'Invalid param_name: {param_name}')

        # Get the parameter type
        if self.type_for_param_name(param_name) != float:
            raise Exception(f'{param_name} is not a float parameter')

        # Get the protobuf_preset_name for this parameter
        protobuf_preset_name = self._protobuf_preset_name_for_param_name(param_name)

        # Get the value from the protobuf preset
        value = self._get_protobuf_preset_value(self._protobuf_preset, protobuf_preset_name)

        # Multiply by 127.0
        value *= 127.0

        # Round and then return it
        return round(value, self.float_precision_num_decimals)

    def get_int(self, param_name):
        """
        Get the value of any parameter as an int.
        If the parameter is actually a float parameter, then it will be
        multiplied by 127.0, rounded, and converted to an int.
        Raises an Exception if param_name is invalid.
        :param param_name: str
        :return: int
        """
        # Make sure param_name is valid
        if param_name not in self.all_param_names():
            raise Exception(f'Invalid param_name: {param_name}')

        # Get the value
        value = int(self._get_protobuf_preset_value(self._protobuf_preset, self._protobuf_preset_name_for_param_name(param_name)))

        # Convert to int if this is a float param
        if self.type_for_param_name(param_name) == float:
            value = int(round(value * 127.0, 0))

        return value

    @staticmethod
    def float_equals(first_value, second_value):
        """
        Uses a limited amount of precision to determine
        whether the supplied float values are equal
        :param first_value:
        :param second_value:
        :return: True if the two values are equal. False if not.
        """
        v1 = int(round(first_value, NymphesPreset.float_precision_num_decimals) * pow(10, NymphesPreset.float_precision_num_decimals))
        v2 = int(round(second_value, NymphesPreset.float_precision_num_decimals) * pow(10, NymphesPreset.float_precision_num_decimals))
        return v1 == v2

    def save_preset_file(self, filepath):
        """
        Store all parameters in a CSV text file.
        This can be later loaded back into a NymphesPreset.
        Raises an Exception if filepath is invalid.
        :param filepath: Path or str
        :return:
        """
        # Validate file_path
        #
        if isinstance(filepath, str):
            # Create a Path from file_path
            filepath = Path(filepath)

        if not isinstance(filepath, Path):
            raise Exception(f'file_path is neither a Path nor a string ({filepath})')

        # Write all parameters to a CSV text file
        #
        with open(filepath, 'w') as file:
            # Write header row
            file.write(NymphesPreset._csv_header_string + '\n')

            # Write parameters to the file
            for name, value in self.all_params_dict().items():
                file.write(f'{name}, {value}' + '\n')

    def generate_sysex_data(self, preset_import_type, preset_type, bank_name, preset_number):
        """
        Generates MIDI SYSEX data that can be used to send a full preset
        to Nymphes.

        :param preset_import_type: (str) 'non-persistent' or 'persistent'
        :param preset_type: (str) 'user' or 'factory'
        :param bank_name: (str) 'A', 'B', 'C', 'D', 'E', 'F', 'G'
        :param preset_number: (int) 1, 2, 3, 4, 5, 6, 7
        :return: A list of bytes
        """
        import_types = ['non-persistent', 'persistent']
        preset_types = ['user', 'factory']
        bank_names = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        preset_nums = [1, 2, 3, 4, 5, 6, 7]

        # Validate arguments
        #
        if preset_import_type not in import_types:
            raise Exception(f'preset_import_type invalid: {preset_import_type}')

        if preset_type not in preset_types:
            raise Exception(f'preset_type invalid: {preset_type}')

        if bank_name not in bank_names:
            raise Exception(f'bank_name invalid (should be between "A" and "G"): {bank_name}')

        if preset_number not in preset_nums:
            raise Exception(f'preset_number invalid (should be between 1 and 7): {preset_number}')

        sysex_data = []

        # Dreadbox ID
        sysex_data.extend([0x00, 0x21, 0x35])

        # Device ID (unused)
        sysex_data.append(0x00)

        # Model ID - Nymphes
        sysex_data.append(0x06)

        # Preset Import Type
        # 0: Non-persistent preset load
        # 1: Persistent preset import
        sysex_data.append(import_types.index(preset_import_type))

        # User or Factory Preset Type
        # 0: User
        # 1: Factory
        sysex_data.append(preset_types.index(preset_type))

        # Bank Number
        # An int between 1 and 7
        sysex_data.append(bank_names.index(bank_name) + 1)

        # Preset Number
        # An int between 1 and 7
        sysex_data.append(preset_number)

        # Serialize the self._preset to a list of protobuf bytes
        protobuf_data = list(self._protobuf_preset.SerializeToString())

        # CRC
        #
        # Calculate CRC from the protobuf bytes
        crc_byte = self._calculate_crc8(protobuf_data)

        # Get nibble from the CRC
        crc_ms, crc_ls = self._nibble_from_byte(crc_byte)

        sysex_data.extend([crc_ls, crc_ms])

        # Get nibblized version of protobuf_data
        protobuf_nibbles = self._nibbles_from_bytes(protobuf_data)

        sysex_data.extend(protobuf_nibbles)

        return sysex_data

    @staticmethod
    def _set_protobuf_preset_value(protobuf_preset_object, protobuf_preset_name, value):
        """
        Set the specified parameter's value in the supplied protobuf preset object.
        Raises an Exception if the parameter name is invalid, or if an
        invalid value is specified for the parameter.
        :param protobuf_preset_object: The protobuf preset object
        :param protobuf_preset_name: (str) The name of the parameter within the preset object
        :param value: The value. A float or int
        :return: True if the new value was different than the old value
        """

        # Make sure preset_param_name is valid
        if protobuf_preset_name not in NymphesPreset._all_protobuf_preset_param_names():
            raise Exception(f'Invalid preset_param_name: {protobuf_preset_name}')

        # Get the parameter name for this preset name
        param_name = NymphesPreset.param_name_for_preset_name(protobuf_preset_name)

        # Make sure the value is within the correct range
        #
        min_val = NymphesPreset.min_val_for_param_name(param_name)
        max_val = NymphesPreset.max_val_for_param_name(param_name)
        if value < min_val or value > max_val:
            raise Exception(
                f'Invalid value for {protobuf_preset_name}: {value} (should be between {min_val} and {max_val}')

        #
        # Do nothing if the new value is not different from what we already have
        #

        curr_value = NymphesPreset._get_protobuf_preset_value(
            protobuf_preset_object,
            protobuf_preset_name
        )

        param_type = NymphesPreset.type_for_param_name(param_name)
        if param_type == int:
            if value == curr_value:
                return False

        elif param_type == float:
            if NymphesPreset.float_equals(value * 127.0, curr_value * 127.0):
                return False

        else:
            raise Exception(f'Invalid param type: {param_type}')

        #
        # Set the parameter's value
        #

        # Break the protobuf preset name into its components
        *components, val_name = protobuf_preset_name.split('.')

        # Get the object specified by the name,
        # digging down in the preset object one level per
        # component of the name
        obj = protobuf_preset_object
        for component in components:
            obj = getattr(obj, component)

        # Now set the value
        setattr(obj, val_name, value)

        return True

    @staticmethod
    def _get_protobuf_preset_value(protobuf_preset_object, protobuf_preset_param_name):
        """
        Get the specified parameter's value from the supplied protobuf preset object.
        Raises an Exception if the parameter name is invalid
        :param protobuf_preset_object: The protobuf preset object
        :param protobuf_preset_param_name: str
        :return: int or float
        """
        # Make sure preset_param_name is valid
        if protobuf_preset_param_name not in NymphesPreset._all_protobuf_preset_param_names():
            raise Exception(f'Invalid protobuf_preset_param_name: {protobuf_preset_param_name}')

        # Break the name into components separated by periods
        name_components = protobuf_preset_param_name.split('.')

        # Get the object specified by the name,
        # digging down in the preset one level per
        # component of the name
        obj = protobuf_preset_object
        for component in name_components:
            obj = getattr(obj, component)

        # Return the value
        return obj

    @staticmethod
    def _protobuf_preset_name_for_param_name(name):
        """
        Gets the preset name of the supplied parameter. This is the name
        used inside a preset object, with levels separated by periods.
        Raises an Exception if the name is invalid.
        :param name: str
        :return: str
        """
        # Make sure the name is valid
        if name not in NymphesPreset._preset_params_map:
            raise Exception(f'Invalid parameter name: {name}')

        # Get and return the preset name
        return NymphesPreset._preset_params_map[name]['preset_name']

    @staticmethod
    def _create_default_protobuf_preset():
        """
        Returns a protobuf preset object with default values
        for all of its parameters
        :return: A protobuf preset object
        """
        # Create a new preset message
        p = preset()

        # Parameter Values
        p.main.wave = 0.3453
        p.main.lvl = 1.0
        p.main.sub = 0.0
        p.main.noise = 0.0
        p.main.osc_lfo = 0.0
        p.main.cut = 1.0
        p.main.reson = 0.0
        p.main.cut_eg = 0.0
        p.main.a1 = 0.0
        p.main.d1 = 0.0
        p.main.s1 = 0.0
        p.main.r1 = 0.0
        p.main.lfo_rate = 0.0
        p.main.lfo_wave = 0.0
        p.main.pw = 0.0
        p.main.glide = 0.0
        p.main.dtune = 0.0
        p.main.chord = 0.0
        p.main.osc_eg = 0.0
        p.main.hpf = 0.0
        p.main.track = 0.0
        p.main.cut_lfo = 0.0
        p.main.a2 = 0.0
        p.main.d2 = 0.0
        p.main.s2 = 1.0
        p.main.r2 = 0.0
        p.main.lfo_delay = 0.0
        p.main.lfo_fade = 0.0

        p.reverb.size = 0.0
        p.reverb.decay = 0.0
        p.reverb.filter = 0.0
        p.reverb.mix = 0.0

        # Modulation Matrix Values
        #

        # LFO2
        p.lfo_2.wave = 0.0
        p.lfo_2.lvl = 0.0
        p.lfo_2.sub = 0.0
        p.lfo_2.noise = 0.0
        p.lfo_2.osc_lfo = 0.0
        p.lfo_2.cut = 0.0
        p.lfo_2.reson = 0.0
        p.lfo_2.cut_eg = 0.0
        p.lfo_2.a1 = 0.0
        p.lfo_2.d1 = 0.0
        p.lfo_2.s1 = 0.0
        p.lfo_2.r1 = 0.0
        p.lfo_2.lfo_rate = 0.0
        p.lfo_2.lfo_wave = 0.0
        p.lfo_2.pw = 0.0
        p.lfo_2.glide = 0.0
        p.lfo_2.dtune = 0.0
        p.lfo_2.chord = 0.0
        p.lfo_2.osc_eg = 0.0
        p.lfo_2.hpf = 0.0
        p.lfo_2.track = 0.0
        p.lfo_2.cut_lfo = 0.0
        p.lfo_2.a2 = 0.0
        p.lfo_2.d2 = 0.0
        p.lfo_2.s2 = 0.0
        p.lfo_2.r2 = 0.0
        p.lfo_2.lfo_delay = 0.0
        p.lfo_2.lfo_fade = 0.0

        # Mod Wheel
        p.mod_w.wave = 0.0
        p.mod_w.lvl = 0.0
        p.mod_w.sub = 0.0
        p.mod_w.noise = 0.0
        p.mod_w.osc_lfo = 0.0
        p.mod_w.cut = 0.0
        p.mod_w.reson = 0.0
        p.mod_w.cut_eg = 0.0
        p.mod_w.a1 = 0.0
        p.mod_w.d1 = 0.0
        p.mod_w.s1 = 0.0
        p.mod_w.r1 = 0.0
        p.mod_w.lfo_rate = 0.0
        p.mod_w.lfo_wave = 0.0
        p.mod_w.pw = 0.0
        p.mod_w.glide = 0.0
        p.mod_w.dtune = 0.0
        p.mod_w.chord = 0.0
        p.mod_w.osc_eg = 0.0
        p.mod_w.hpf = 0.0
        p.mod_w.track = 0.0
        p.mod_w.cut_lfo = 0.0
        p.mod_w.a2 = 0.0
        p.mod_w.d2 = 0.0
        p.mod_w.s2 = 0.0
        p.mod_w.r2 = 0.0
        p.mod_w.lfo_delay = 0.0
        p.mod_w.lfo_fade = 0.0

        # Velocity
        p.velo.wave = 0.0
        p.velo.lvl = 0.0
        p.velo.sub = 0.0
        p.velo.noise = 0.0
        p.velo.osc_lfo = 0.0
        p.velo.cut = 0.0
        p.velo.reson = 0.0
        p.velo.cut_eg = 0.0
        p.velo.a1 = 0.0
        p.velo.d1 = 0.0
        p.velo.s1 = 0.0
        p.velo.r1 = 0.0
        p.velo.lfo_rate = 0.0
        p.velo.lfo_wave = 0.0
        p.velo.pw = 0.0
        p.velo.glide = 0.0
        p.velo.dtune = 0.0
        p.velo.chord = 0.0
        p.velo.osc_eg = 0.0
        p.velo.hpf = 0.0
        p.velo.track = 0.0
        p.velo.cut_lfo = 0.0
        p.velo.a2 = 0.0
        p.velo.d2 = 0.0
        p.velo.s2 = 0.0
        p.velo.r2 = 0.0
        p.velo.lfo_delay = 0.0
        p.velo.lfo_fade = 0.0

        # Aftertouch
        p.after.wave = 0.0
        p.after.lvl = 0.0
        p.after.sub = 0.0
        p.after.noise = 0.0
        p.after.osc_lfo = 0.0
        p.after.cut = 0.0
        p.after.reson = 0.0
        p.after.cut_eg = 0.0
        p.after.a1 = 0.0
        p.after.d1 = 0.0
        p.after.s1 = 0.0
        p.after.r1 = 0.0
        p.after.lfo_rate = 0.0
        p.after.lfo_wave = 0.0
        p.after.pw = 0.0
        p.after.glide = 0.0
        p.after.dtune = 0.0
        p.after.chord = 0.0
        p.after.osc_eg = 0.0
        p.after.hpf = 0.0
        p.after.track = 0.0
        p.after.cut_lfo = 0.0
        p.after.a2 = 0.0
        p.after.d2 = 0.0
        p.after.s2 = 0.0
        p.after.r2 = 0.0
        p.after.lfo_delay = 0.0
        p.after.lfo_fade = 0.0

        # LFO Settings
        p.lfo_settings.lfo_1_speed_mode = lfo_speed_mode.slow
        p.lfo_settings.lfo_1_sync_mode = lfo_sync_mode.free
        p.lfo_settings.lfo_2_speed_mode = lfo_speed_mode.slow
        p.lfo_settings.lfo_2_sync_mode = lfo_sync_mode.free

        # Legato
        p.legato = 0

        # Voice Mode
        p.voice_mode = voice_mode.poly

        # Chord Settings
        p.chord_1.root = 0
        p.chord_1.semi_1 = 0
        p.chord_1.semi_2 = 0
        p.chord_1.semi_3 = 0
        p.chord_1.semi_4 = 0
        p.chord_1.semi_5 = 0

        p.chord_2.root = 0
        p.chord_2.semi_1 = 0
        p.chord_2.semi_2 = 0
        p.chord_2.semi_3 = 0
        p.chord_2.semi_4 = 0
        p.chord_2.semi_5 = 0

        p.chord_3.root = 0
        p.chord_3.semi_1 = 0
        p.chord_3.semi_2 = 0
        p.chord_3.semi_3 = 0
        p.chord_3.semi_4 = 0
        p.chord_3.semi_5 = 0

        p.chord_4.root = 0
        p.chord_4.semi_1 = 0
        p.chord_4.semi_2 = 0
        p.chord_4.semi_3 = 0
        p.chord_4.semi_4 = 0
        p.chord_4.semi_5 = 0

        p.chord_5.root = 0
        p.chord_5.semi_1 = 0
        p.chord_5.semi_2 = 0
        p.chord_5.semi_3 = 0
        p.chord_5.semi_4 = 0
        p.chord_5.semi_5 = 0

        p.chord_6.root = 0
        p.chord_6.semi_1 = 0
        p.chord_6.semi_2 = 0
        p.chord_6.semi_3 = 0
        p.chord_6.semi_4 = 0
        p.chord_6.semi_5 = 0

        p.chord_7.root = 0
        p.chord_7.semi_1 = 0
        p.chord_7.semi_2 = 0
        p.chord_7.semi_3 = 0
        p.chord_7.semi_4 = 0
        p.chord_7.semi_5 = 0

        p.chord_8.root = 0
        p.chord_8.semi_1 = 0
        p.chord_8.semi_2 = 0
        p.chord_8.semi_3 = 0
        p.chord_8.semi_4 = 0
        p.chord_8.semi_5 = 0

        # Extra LFO Parameters
        p.extra_lfo_2.lfo_1_rate = 0.0
        p.extra_lfo_2.lfo_1_wave = 0.0
        p.extra_lfo_2.lfo_1_delay = 0.0
        p.extra_lfo_2.lfo_1_fade = 0.0

        p.extra_lfo_2.lfo_2_rate = 0.0
        p.extra_lfo_2.lfo_2_wave = 0.0
        p.extra_lfo_2.lfo_2_delay = 0.0
        p.extra_lfo_2.lfo_2_fade = 0.0

        # "Extra Modulation Parameters",
        # ie: Modulation Matrix Targeting LFO2
        p.extra_mod_w.lfo_2_rate = 0.0
        p.extra_mod_w.lfo_2_wave = 0.0
        p.extra_mod_w.lfo_2_delay = 0.0
        p.extra_mod_w.lfo_2_fade = 0.0

        p.extra_velo.lfo_2_rate = 0.0
        p.extra_velo.lfo_2_wave = 0.0
        p.extra_velo.lfo_2_delay = 0.0
        p.extra_velo.lfo_2_fade = 0.0

        p.extra_after.lfo_2_rate = 0.0
        p.extra_after.lfo_2_wave = 0.0
        p.extra_after.lfo_2_delay = 0.0
        p.extra_after.lfo_2_fade = 0.0

        p.amp_level = 1.0

        return p

    @classmethod
    def _protobuf_preset_from_sysex_data(cls, sysex_data):
        """
        Extracts Nymphes preset data from the supplied MIDI sysex data.
        sysex_data should be a list of bytes.
        Raises an Exception if the data is not a valid Nymphes SYSEX preset dump.
        Returns a tuple: (preset_object, preset_import_type, user_or_factory, bank_number, preset_number)
        """

        # Verify Dreadbox Manufacturer ID
        if not (sysex_data[0] == 0x00 and sysex_data[1] == 0x21 and sysex_data[2] == 0x35):
            raise Exception('This sysex message does not have the id for Dreadbox')

        # Skip byte 3 - device ID, as it is not used

        # Verify Nymphes Model ID
        if sysex_data[4] != 0x06:
            raise Exception('This sysex message is Dreadbox, but the device id is not Nymphes')

        # Preset data starts at byte 11. It has been encoded using the protobuf
        # system, and then "nibblized" - each protobuf byte has been transmitted
        # as a pair of bytes because midi sysex only uses 7 bits of each byte.
        nibblized_protobuf_data = sysex_data[11:]

        # Un-nibblize the data - combine the nibbles to convert back to 8-bit bytes
        protobuf_data = cls._bytes_from_nibbles(nibblized_protobuf_data)

        # Verify CRC to make sure the data has not been corrupted
        #

        # Get the CRC check value, which also was nibblized
        sysex_crc_ls_nibble = sysex_data[9]
        sysex_crc_ms_nibble = sysex_data[10]

        # Calculate CRC from protobuf data
        crc = cls._calculate_crc8(protobuf_data)

        # Convert to nibbles
        protobuf_crc_ms_nibble, protobuf_crc_ls_nibble = cls._nibble_from_byte(crc)

        # Make sure the calculated CRC matches the transmitted CRC value
        if protobuf_crc_ms_nibble != sysex_crc_ms_nibble or protobuf_crc_ls_nibble != sysex_crc_ls_nibble:
            raise Exception(
                f'CRC failed: (sysex {sysex_crc_ms_nibble}:{sysex_crc_ls_nibble}, calculated from protobuf: {protobuf_crc_ms_nibble}, {protobuf_crc_ls_nibble})')

        # Convert protobuf data to a preset
        p = preset.FromString(bytes(protobuf_data))

        # Get the preset import type
        preset_import_type = 'persistent' if sysex_data[5] == 0x01 else 'non-persistent'

        # Determine user or factory preset type
        preset_type = 'user' if sysex_data[6] == 0 else 'factory'

        # Get bank name. We will return it as a capital letter from A to G
        bank_name = ['A', 'B', 'C', 'D', 'E', 'F', 'G'][sysex_data[7] - 1]

        # Get preset number. It is a number between 1 and 7
        preset_number = sysex_data[8]

        return p, preset_import_type, preset_type, bank_name, preset_number

    @staticmethod
    def _calculate_crc8(data):
        crc_table = [
            0x00, 0x31, 0x62, 0x53, 0xc4, 0xf5, 0xa6, 0x97, 0xb9, 0x88, 0xdb, 0xea, 0x7d,
            0x4c, 0x1f, 0x2e, 0x43, 0x72, 0x21, 0x10, 0x87, 0xb6, 0xe5, 0xd4, 0xfa, 0xcb,
            0x98, 0xa9, 0x3e, 0x0f, 0x5c, 0x6d, 0x86, 0xb7, 0xe4, 0xd5, 0x42, 0x73, 0x20,
            0x11, 0x3f, 0x0e, 0x5d, 0x6c, 0xfb, 0xca, 0x99, 0xa8, 0xc5, 0xf4, 0xa7, 0x96,
            0x01, 0x30, 0x63, 0x52, 0x7c, 0x4d, 0x1e, 0x2f, 0xb8, 0x89, 0xda, 0xeb, 0x3d,
            0x0c, 0x5f, 0x6e, 0xf9, 0xc8, 0x9b, 0xaa, 0x84, 0xb5, 0xe6, 0xd7, 0x40, 0x71,
            0x22, 0x13, 0x7e, 0x4f, 0x1c, 0x2d, 0xba, 0x8b, 0xd8, 0xe9, 0xc7, 0xf6, 0xa5,
            0x94, 0x03, 0x32, 0x61, 0x50, 0xbb, 0x8a, 0xd9, 0xe8, 0x7f, 0x4e, 0x1d, 0x2c,
            0x02, 0x33, 0x60, 0x51, 0xc6, 0xf7, 0xa4, 0x95, 0xf8, 0xc9, 0x9a, 0xab, 0x3c,
            0x0d, 0x5e, 0x6f, 0x41, 0x70, 0x23, 0x12, 0x85, 0xb4, 0xe7, 0xd6, 0x7a, 0x4b,
            0x18, 0x29, 0xbe, 0x8f, 0xdc, 0xed, 0xc3, 0xf2, 0xa1, 0x90, 0x07, 0x36, 0x65,
            0x54, 0x39, 0x08, 0x5b, 0x6a, 0xfd, 0xcc, 0x9f, 0xae, 0x80, 0xb1, 0xe2, 0xd3,
            0x44, 0x75, 0x26, 0x17, 0xfc, 0xcd, 0x9e, 0xaf, 0x38, 0x09, 0x5a, 0x6b, 0x45,
            0x74, 0x27, 0x16, 0x81, 0xb0, 0xe3, 0xd2, 0xbf, 0x8e, 0xdd, 0xec, 0x7b, 0x4a,
            0x19, 0x28, 0x06, 0x37, 0x64, 0x55, 0xc2, 0xf3, 0xa0, 0x91, 0x47, 0x76, 0x25,
            0x14, 0x83, 0xb2, 0xe1, 0xd0, 0xfe, 0xcf, 0x9c, 0xad, 0x3a, 0x0b, 0x58, 0x69,
            0x04, 0x35, 0x66, 0x57, 0xc0, 0xf1, 0xa2, 0x93, 0xbd, 0x8c, 0xdf, 0xee, 0x79,
            0x48, 0x1b, 0x2a, 0xc1, 0xf0, 0xa3, 0x92, 0x05, 0x34, 0x67, 0x56, 0x78, 0x49,
            0x1a, 0x2b, 0xbc, 0x8d, 0xde, 0xef, 0x82, 0xb3, 0xe0, 0xd1, 0x46, 0x77, 0x24,
            0x15, 0x3b, 0x0a, 0x59, 0x68, 0xff, 0xce, 0x9d, 0xac
        ]

        crc = 0x00
        for byte in data:
            crc = crc_table[crc ^ byte]
        return crc

    @staticmethod
    def _bytes_from_nibbles(nibbles):
        bytes_list = []

        for i in range(0, len(nibbles), 2):
            # The first byte in the nibble is the LSB
            nibble1 = nibbles[i]

            # The second byte in the nibble is the MSB,
            # so shift it by 4 bits
            nibble2 = nibbles[i + 1] << 4

            bytes_list.append(nibble1 + nibble2)

        return bytes_list

    @classmethod
    def _nibbles_from_bytes(cls, bytes_value):
        sysex_data = []

        for byte in bytes_value:
            ms, ls = cls._nibble_from_byte(byte)
            sysex_data.append(ls)
            sysex_data.append(ms)

        return sysex_data

    @staticmethod
    def _nibble_from_byte(byte):
        """
        Breaks byte into its most significant 4 bits and least significant 4 bits,
        and returns their values as a tuple of integers.
        Index 0 is the most significant value
        Index 1 is the least significant
        """
        # Shift the entire value right by 4 bits
        ms = byte >> 4

        # Use a bitwise AND to mask out the most significant
        # 4 bits, so only the least significant remain
        ls = byte & 0b00001111

        return ms, ls

    def _log_message(self, message):
        """
        Print a message to the console if logging is enabled.
        :param message: str
        :return:
        """
        if self.print_logs_enabled:
            print(f'NymphesMidi log: {message}')

    @staticmethod
    def _protobuf_preset_from_file(file_path):
        """
        Read the CSV file at file_path and return a protobuf
        preset object with the parameter values from the file.
        Raises an Exception if the file is invalid.
        file_path is a Path or a string
        """

        # Validate file_path
        #
        if isinstance(file_path, str):
            # Create a Path from file_path
            file_path = Path(file_path)

        if not isinstance(file_path, Path):
            raise Exception(f'file_path is neither a Path nor a string ({file_path})')

        # Create a dict to contain the values found in the preset file
        params_dict = {}

        # Read from the file
        with open(file_path) as file:
            # Create a CSV reader
            csv_reader = csv.reader(file)

            # Make sure the header row is correct
            header = next(csv_reader, None)[0]
            if header != NymphesPreset._csv_header_string:
                raise Exception(f'Preset file at {file_path} is invalid (unrecognized header row: {header})')

            # Read rows of the file into the params dict
            for row in csv_reader:
                name, value = row

                # Remove leading and trailing whitespace
                name = name.strip()
                value = value.strip()

                # Handle values of None
                if value == 'None':
                    value = None

                # Get correct values for each parameter
                elif name in NymphesPreset.all_param_names():
                    # Get the type for this parameter
                    param_type = NymphesPreset.type_for_param_name(name)

                    if param_type == float:
                        value = float(value) / 127.0

                    elif param_type == int:
                        value = int(value)

                # Store the value
                params_dict[name] = value

        # Create protobuf preset object and populate
        # it with the values read from the file
        p = NymphesPreset._create_default_protobuf_preset()

        for param_name, value in params_dict.items():
            # Only include parameters contained in a preset,
            # not NymphesPreset metadata.
            #
            if param_name in NymphesPreset.all_param_names():
                # Get the protobuf preset name for this parameter
                protobuf_preset_name = NymphesPreset._protobuf_preset_name_for_param_name(param_name)

                # Set the value
                NymphesPreset._set_protobuf_preset_value(p, protobuf_preset_name, value)

        # Return the protobuf preset
        return p

    @staticmethod
    def _all_protobuf_preset_param_names():
        """
        Returns a list of all names in a preset object
        :return: A list of strings
        """
        return [NymphesPreset._preset_params_map[param_name]['preset_name'] for param_name in NymphesPreset._preset_params_map.keys()]
