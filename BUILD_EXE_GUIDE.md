# Building TuneGen Web App as Executable

This guide explains how to create a standalone Windows executable (.exe) file for TuneGen that can run on any Windows PC without requiring Python installation.

## Prerequisites

1. **Python 3.8+** installed on your development machine
2. **Virtual environment** activated (see `ACTIVATE_VENV_GUIDE.md`)
3. **All dependencies installed** (run `pip install -r requirements.txt`)

## Quick Build

1. **Activate your virtual environment:**
   ```bash
   env\Scripts\activate
   ```

2. **Run the build script:**
   ```bash
   python build_web_exe.py
   ```

3. **Wait for the build to complete** (this may take 5-10 minutes)

4. **Find your executable:**
   - Location: `dist\TuneGen-Web.exe`
   - This is a single file that contains everything needed

## Distributing the Executable

### Option 1: Single File Distribution

1. Copy `dist\TuneGen-Web.exe` to any folder
2. Copy `spotify.env` to the same folder (if you want to include Spotify credentials)
3. That's it! The exe is self-contained

### Option 2: Create a Distribution Package

Create a folder with:
```
TuneGen-Web/
├── TuneGen-Web.exe
├── spotify.env (optional)
└── README.txt (instructions for users)
```

## Running the Executable

1. **Double-click `TuneGen-Web.exe`**
2. A console window will open showing server logs
3. Your default web browser will automatically open to `http://127.0.0.1:5000`
4. The web app is now running!

## Important Notes

### Spotify Credentials

- If you include `spotify.env` with the executable, users won't need to set up Spotify credentials
- If you don't include it, users will need to create their own `spotify.env` file with their Spotify API credentials
- **Never commit `spotify.env` to version control** - it contains sensitive information

### Data Storage

- The executable creates folders in the same directory where it's run:
  - `data/` - Stores playlist history, track count history
  - `imported_tracks/` - Stores imported CSV files
  - `generated_cards/` - Stores generated HTML and PDF files

### Port Conflicts

- The app runs on port 5000 by default
- If port 5000 is already in use, the app will fail to start
- Users can close the console window to stop the server

### Firewall

- Windows Firewall may ask for permission the first time
- Users should allow the app through the firewall

## Troubleshooting

### "Failed to execute script" error

- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Try rebuilding: `python build_web_exe.py --clean`

### "Module not found" errors

- Check that all hidden imports are included in `build_web_exe.py`
- Some packages may need to be added manually

### Large file size

- The executable includes Python, Flask, and all dependencies
- Expect 50-100MB file size (this is normal)
- Using `--onefile` creates a single large file for easier distribution

### Slow startup

- The first startup may be slower as PyInstaller extracts files
- Subsequent startups are faster

## Advanced: Custom Icon

To add a custom icon to the executable:

1. Create or find a `.ico` file (Windows icon format)
2. Add to build script: `'--icon=icon.ico'`
3. Rebuild

## Advanced: No Console Window

To hide the console window (Windows only):

1. Change `'--console'` to `'--windowed'` in `build_web_exe.py`
2. Note: You won't see server logs, but the app will still run

## Building for Other Platforms

This script is for Windows. For other platforms:

- **Linux/Mac**: Use the same script but change semicolons (`;`) to colons (`:`) in `--add-data` arguments
- **Cross-platform**: Consider using Docker or a cloud deployment instead

## File Structure After Build

```
dist/
└── TuneGen-Web.exe  (standalone executable)

build/  (temporary build files - can be deleted)
└── TuneGen-Web/  (build cache)
```

The `build/` folder can be safely deleted after building.

