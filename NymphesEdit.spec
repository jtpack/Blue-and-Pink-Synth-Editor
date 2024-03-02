# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path


a = Analysis(
    ['src/nymphes_gui/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/nymphes_gui/app_config.ini', 'src/nymphes_gui'),
        ('src/nymphes_gui/nymphesgui.kv', 'src/nymphes_gui'),
        ('nymphes-osc', '.')
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
    name='main',
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
    name='NymphesEdit',
)
app = BUNDLE(
    coll,
    name='NymphesEdit.app',
    icon=None,
    bundle_identifier=None,
)
