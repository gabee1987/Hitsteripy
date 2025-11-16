"""
PyInstaller build script for Hitsteripy Web App
Creates a standalone Windows executable that runs a web server
"""
import PyInstaller.__main__
import os
import sys

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Build PyInstaller command
build_args = [
    'run_web_app.py',  # Entry point for web app
    '--name=Hitsteripy-Web',
    '--onefile',  # Create a single executable file
    '--console',  # Show console (to see server logs)
    '--clean',  # Clean PyInstaller cache
    '--noconfirm',  # Overwrite output without asking
]

# Add data files (Windows uses semicolon as separator)
if os.path.exists('templates'):
    build_args.extend(['--add-data', f'templates;templates'])

if os.path.exists('assets'):
    build_args.extend(['--add-data', f'assets;assets'])

if os.path.exists('web_templates'):
    build_args.extend(['--add-data', f'web_templates;web_templates'])

if os.path.exists('web_static'):
    build_args.extend(['--add-data', f'web_static;web_static'])

if os.path.exists('spotify.env'):
    build_args.extend(['--add-data', f'spotify.env;.'])

# Add hidden imports
build_args.extend([
    '--hidden-import', 'PIL',
    '--hidden-import', 'PIL.Image',
    '--hidden-import', 'jinja2',
    '--hidden-import', 'spotipy',
    '--hidden-import', 'flask',
    '--hidden-import', 'werkzeug',
    '--hidden-import', 'rich',
    '--hidden-import', 'qrcode',
    '--collect-submodules', 'flask',
    '--collect-submodules', 'jinja2',
])

# Run PyInstaller
PyInstaller.__main__.run(build_args)

