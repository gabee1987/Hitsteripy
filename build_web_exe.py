"""
PyInstaller build script for TuneGen Web App
Creates a standalone Windows executable that runs a web server
"""
import PyInstaller.__main__
import os
import sys

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

print("=" * 60)
print("Building TuneGen Web App Executable")
print("=" * 60)
print()

# Build PyInstaller command
build_args = [
    'run_web_app.py',  # Entry point for web app
    '--name=TuneGen-Web',
    '--onefile',  # Create a single executable file
    '--console',  # Show console (to see server logs)
    '--clean',  # Clean PyInstaller cache
    '--noconfirm',  # Overwrite output without asking
    '--icon=NONE',  # No icon (you can add one later)
]

# Add data files (Windows uses semicolon as separator)
print("Adding data files...")
data_files = [
    ('templates', 'templates'),
    ('assets', 'assets'),
    ('web_templates', 'web_templates'),
    ('web_static', 'web_static'),
]

for src, dst in data_files:
    if os.path.exists(src):
        build_args.extend(['--add-data', f'{src};{dst}'])
        print(f"  ✓ Added {src} -> {dst}")
    else:
        print(f"  ✗ Warning: {src} not found")

# Add spotify.env if it exists
if os.path.exists('spotify.env'):
    build_args.extend(['--add-data', f'spotify.env;.'])
    print("  ✓ Added spotify.env")
else:
    print("  ⚠ Warning: spotify.env not found - app will need Spotify credentials")

print()

# Add hidden imports
print("Adding hidden imports...")
hidden_imports = [
    'PIL', 'PIL.Image',
    'jinja2',
    'spotipy',
    'flask',
    'werkzeug',
    'rich',
    'qrcode',
    'weasyprint',
    'cffi',
    'pydyf',
    'tinycss2',
    'cssselect2',
    'Pyphen',
    'fonttools',
    'tinyhtml5',
]

for imp in hidden_imports:
    build_args.extend(['--hidden-import', imp])

# Collect submodules for complex packages
build_args.extend([
    '--collect-submodules', 'flask',
    '--collect-submodules', 'jinja2',
    '--collect-submodules', 'weasyprint',
    '--collect-submodules', 'cffi',
])

print("  ✓ Added all required imports")
print()

# Run PyInstaller
print("Starting PyInstaller build...")
print("This may take several minutes...")
print()
PyInstaller.__main__.run(build_args)

print()
print("=" * 60)
print("Build Complete!")
print("=" * 60)
print(f"Executable location: dist\\TuneGen-Web.exe")
print()
print("To distribute:")
print("  1. Copy dist\\TuneGen-Web.exe to any folder")
print("  2. Copy spotify.env to the same folder (if needed)")
print("  3. Run TuneGen-Web.exe - it will start the web server")
print("  4. The browser will open automatically")
print("=" * 60)

