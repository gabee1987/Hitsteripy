# Building Hitsteripy as a Windows Executable

This guide explains how to create a standalone Windows executable (.exe) from your Python application.

## Quick Start: Simple Batch File (Easiest)

If Python is already installed on your system:

1. **Double-click `run_hitsteripy.bat`** - That's it!

   - Still requires Python installed
   - Fastest option
   - No building needed

## Creating a Standalone Executable (Recommended)

This creates a single `.exe` file that can run on any Windows computer without Python installed.

### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

### Step 2: Build the Executable

```bash
python build_exe.py
```

Or use PyInstaller directly:
```bash
pyinstaller build_exe.py
```

### Step 3: Find Your Executable

After building, you'll find:
- **Executable**: `dist/Hitsteripy.exe`
- **Build files**: `build/` folder (can be deleted)
- **Spec file**: `Hitsteripy.spec` (configuration file)

### Step 4: Distribute

To share the app:
1. Copy `dist/Hitsteripy.exe` to any location
2. Make sure `spotify.env` is in the same folder as the .exe (or it will look in the current directory)
3. The app will create `data/`, `imported_tracks/`, and `generated_cards/` folders as needed

## Notes

- **First build may take 2-5 minutes** - PyInstaller is bundling all dependencies
- **File size**: The .exe will be ~50-100MB (includes Python interpreter and all libraries)
- **Antivirus warnings**: Some antivirus software may flag PyInstaller executables as suspicious. This is a false positive common with PyInstaller.
- **Environment file**: Make sure `spotify.env` is accessible - PyInstaller includes it in the bundle

## Customization

### Change Icon

Edit `build_exe.py` and replace:
```python
'--icon=NONE',
```
with:
```python
'--icon=path/to/your/icon.ico',
```

### Hide Console Window

If you want to hide the console (not recommended for this console app), edit `build_exe.py`:
- Remove `'--console',`
- Add `'--windowed',` or `'--noconsole',`

## Troubleshooting

**"Module not found" errors:**
- Add missing modules to `--hidden-import` in `build_exe.py`

**"File not found" errors:**
- Make sure data files (templates, env files) are included with `--add-data`
- Use semicolon (`;`) separator on Windows: `'--add-data', 'source;destination'`

**Large file size:**
- Normal for PyInstaller - it includes Python and all dependencies
- Use `--onefile` for single file, or remove it for a folder structure

## Alternative: Manual PyInstaller Command

If you prefer to build manually:

```bash
pyinstaller --onefile --console --name=Hitsteripy --add-data "templates;templates" --add-data "spotify.env;." --hidden-import PIL --hidden-import jinja2 --hidden-import spotipy --hidden-import prompt_toolkit --hidden-import rich --hidden-import qrcode src/main.py
```

