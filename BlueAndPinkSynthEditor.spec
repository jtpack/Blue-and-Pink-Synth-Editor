# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

hidden_imports=['zeroconf._utils.ipaddress', 'zeroconf._handlers.answers']

if sys.platform == "win32":
    hidden_imports.append('win32timezone')

a = Analysis(
    ['src/blue_and_pink_synth_editor/__main__.py'],
    pathex=[str(Path(os.path.expanduser('~')) / 'nymphes-osc')],
    binaries=[],
    datas=[
        ('src/blue_and_pink_synth_editor/app_config.ini', 'src/blue_and_pink_synth_editor'),
        ('src/blue_and_pink_synth_editor/blueandpinksyntheditor.kv', 'src/blue_and_pink_synth_editor'),
        ('src/blue_and_pink_synth_editor/ui_controls/bottom_bar.kv', 'src/blue_and_pink_synth_editor/ui_controls'),
        ('src/blue_and_pink_synth_editor/ui_controls/chords_screen.kv', 'src/blue_and_pink_synth_editor/ui_controls'),
        ('src/blue_and_pink_synth_editor/ui_controls/demo_mode_popup.kv', 'src/blue_and_pink_synth_editor/ui_controls'),
        ('src/blue_and_pink_synth_editor/ui_controls/nymphes_setup_instructions_popup.kv', 'src/blue_and_pink_synth_editor/ui_controls'),
        ('src/blue_and_pink_synth_editor/ui_controls/error_dialog.kv', 'src/blue_and_pink_synth_editor/ui_controls'),
        ('src/blue_and_pink_synth_editor/ui_controls/left_bar.kv', 'src/blue_and_pink_synth_editor/ui_controls'),
        ('src/blue_and_pink_synth_editor/ui_controls/params_grid_lfo_config_cell.kv', 'src/blue_and_pink_synth_editor/ui_controls'),
        ('src/blue_and_pink_synth_editor/ui_controls/params_grid_mod_cell.kv', 'src/blue_and_pink_synth_editor/ui_controls'),
        ('src/blue_and_pink_synth_editor/ui_controls/params_grid_non_mod_cell.kv', 'src/blue_and_pink_synth_editor/ui_controls'),
        ('src/blue_and_pink_synth_editor/ui_controls/preset_load_screen.kv', 'src/blue_and_pink_synth_editor/ui_controls'),
        ('src/blue_and_pink_synth_editor/ui_controls/preset_save_screen.kv', 'src/blue_and_pink_synth_editor/ui_controls'),
        ('src/blue_and_pink_synth_editor/ui_controls/demo_mode_screen.kv', 'src/blue_and_pink_synth_editor/ui_controls'),
        ('src/blue_and_pink_synth_editor/ui_controls/settings_screen.kv', 'src/blue_and_pink_synth_editor/ui_controls'),
        ('src/blue_and_pink_synth_editor/ui_controls/synth_editor_value_controls.kv', 'src/blue_and_pink_synth_editor/ui_controls'),
        ('src/blue_and_pink_synth_editor/ui_controls/top_bar.kv', 'src/blue_and_pink_synth_editor/ui_controls'),
        ('src/blue_and_pink_synth_editor/icon.png', 'src/blue_and_pink_synth_editor'),
        ('icon.ico', '.')
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BlueAndPinkSynthEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="icon.ico"
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BlueAndPinkSynthEditor',
)
app = BUNDLE(
    coll,
    name='BlueAndPinkSynthEditor.app',
    icon='icons.icns',
    bundle_identifier=None,
)
