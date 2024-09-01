import os
import sys
from PyInstaller.utils.hooks import collect_all

# Collect necessary binaries, data, and hidden imports for 'plyer'
binaries, datas, hiddenimports = collect_all('plyer')

block_cipher = None

a = Analysis(
    ['pomodoro.py'],  # Your main Python script file
    pathex=['.'],  # Set to current directory
    binaries=binaries,  # Include any binaries needed
    datas=datas,  # Include any data files needed
    hiddenimports=hiddenimports,  # Include hidden imports needed
    hookspath=[],  # No additional hooks path
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pomodoro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False  # Change this to False to hide the terminal window
)


coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pomodoro_timer'
)
