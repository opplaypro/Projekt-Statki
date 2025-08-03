# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path
import arcade

# Znajdź ścieżkę do zasobów biblioteki arcade
arcade_resources_path = Path(sys.modules['arcade'].__file__).parent / 'resources'

a = Analysis(
    ['gui_windows.py'],
    pathex=[],
    binaries=[],
    datas=[(str(arcade_resources_path), 'arcade/resources')],
    hiddenimports=[
        "arcade.gl",
        "pyperclip"
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='gui_windows',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='favicon.ico',
)