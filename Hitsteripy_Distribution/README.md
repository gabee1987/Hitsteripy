# How to Use Hitsteripy.exe

## ✅ Your Executable is Ready!

Your standalone executable is located at:

```
dist/Hitsteripy.exe
```

## Quick Start

### Option 1: Double-Click (Simplest)

1. **Navigate to the `dist` folder**
2. **Double-click `Hitsteripy.exe`**
3. That's it! The app should start.

### Option 2: Copy to Desktop (Recommended)

1. **Copy `Hitsteripy.exe`** from `dist` folder to your Desktop (or anywhere you want)
2. **Copy `spotify.env`** to the same folder as the .exe
3. **Double-click `Hitsteripy.exe`** on your Desktop

> **Note:** The first time you run it, Windows might show a security warning. Click "More info" and then "Run anyway" if you trust the executable.

## Important: Spotify Credentials

The app needs your Spotify API credentials. Make sure `spotify.env` is in the same folder as `Hitsteripy.exe`.

If the app can't find `spotify.env`, you'll see an error. Just copy it from the project root to where your .exe is.

## What Happens When You Run It

The app will:

1. Open a console window (black window with colored text)
2. Show the main menu
3. Create these folders automatically (if they don't exist):
   - `data/` - Stores your playlist history
   - `imported_tracks/` - Stores imported track CSV files
   - `generated_cards/` - Stores generated HTML card files

## Troubleshooting

### "spotify.env not found"

- Make sure `spotify.env` is in the same folder as `Hitsteripy.exe`
- Or copy it to the same location

### "Windows protected your PC" / Security Warning

- This is normal for PyInstaller executables
- Click "More info" → "Run anyway"
- Your antivirus might flag it as suspicious (false positive)

### App closes immediately

- Make sure `spotify.env` exists and has valid credentials
- Try running from Command Prompt to see error messages:
  ```cmd
  cd C:\path\to\exe
  Hitsteripy.exe
  ```

### "Module not found" errors

- Rebuild the executable: `py build_exe.py`
- Make sure all dependencies are installed

## Sharing the App

To share with others:

1. **Copy these files/folders:**
   - `Hitsteripy.exe`
   - `spotify.env` (they'll need to add their own credentials)
2. **Create a ZIP file** with:

   - `Hitsteripy.exe`
   - `spotify.env` (template with instructions)

3. **Include instructions** that they need to:
   - Edit `spotify.env` with their Spotify API credentials
   - Put both files in the same folder
   - Run `Hitsteripy.exe`

## File Structure

Your distribution folder should look like:

```
MyApp/
├── Hitsteripy.exe       ← The app
├── spotify.env          ← Your Spotify credentials
├── data/                ← Created automatically
├── imported_tracks/     ← Created automatically
└── generated_cards/     ← Created automatically
```

## Tips

- **Create a Desktop shortcut**: Right-click `Hitsteripy.exe` → "Create shortcut" → Drag to Desktop
- **Pin to Taskbar**: Right-click the running app → "Pin to taskbar"
- **Run as administrator**: Usually not needed, but if you have permission issues, right-click → "Run as administrator"

## Need Help?

If something doesn't work:

1. Check that `spotify.env` exists and has valid credentials
2. Run from Command Prompt to see error messages
3. Rebuild if needed: `py build_exe.py`
