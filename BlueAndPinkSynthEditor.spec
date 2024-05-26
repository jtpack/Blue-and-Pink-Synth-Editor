# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path


a = Analysis(
    ['src/blue_and_pink_synth_editor/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/blue_and_pink_synth_editor/app_config.ini', 'src/blue_and_pink_synth_editor'),
        ('src/blue_and_pink_synth_editor/blueandpinksyntheditor.kv', 'src/blue_and_pink_synth_editor'),
        ('src/blue_and_pink_synth_editor/value_control.py', 'src/blue_and_pink_synth_editor'),
        ('src/blue_and_pink_synth_editor/misc_widgets.py', 'src/blue_and_pink_synth_editor'),
        ('src/blue_and_pink_synth_editor/load_dialog.py', 'src/blue_and_pink_synth_editor'),
        ('src/blue_and_pink_synth_editor/save_dialog.py', 'src/blue_and_pink_synth_editor'),
        ('src/blue_and_pink_synth_editor/error_dialog.py', 'src/blue_and_pink_synth_editor'),
        ('src/blue_and_pink_synth_editor/synth_editor_value_controls.py', 'src/blue_and_pink_synth_editor'),
        ('src/blue_and_pink_synth_editor/icon.png', 'src/blue_and_pink_synth_editor')
    ],
    hiddenimports=[str(Path(os.path.expanduser('~')) / 'nymphes-osc'), 'zeroconf._utils.ipaddress', 'zeroconf._handlers.answers'],
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
