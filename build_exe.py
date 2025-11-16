"""
PyInstaller build script for Hitsteripy
Creates a standalone Windows executable

Usage:
    python build_exe.py
"""
import PyInstaller.__main__
import os
import sys

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Build PyInstaller command
build_args = [
    'src/main.py',
    '--name=Hitsteripy',
    '--onefile',  # Create a single executable file
    '--console',  # Show console (required for this console app)
    '--clean',  # Clean PyInstaller cache
    '--noconfirm',  # Overwrite output without asking
]

# Add data files (Windows uses semicolon as separator)
if os.path.exists('templates'):
    build_args.extend(['--add-data', f'templates;templates'])

if os.path.exists('assets'):
    build_args.extend(['--add-data', f'assets;assets'])

if os.path.exists('spotify.env'):
    build_args.extend(['--add-data', f'spotify.env;.'])

# Add hidden imports
build_args.extend([
    '--hidden-import', 'PIL',
    '--hidden-import', 'PIL.Image',
    '--hidden-import', 'jinja2',
    '--hidden-import', 'spotipy',
    '--hidden-import', 'prompt_toolkit',
    '--hidden-import', 'rich',
    '--hidden-import', 'qrcode',
    '--collect-submodules', 'prompt_toolkit',
    '--collect-submodules', 'rich',
])

# Run PyInstaller
PyInstaller.__main__.run(build_args)
