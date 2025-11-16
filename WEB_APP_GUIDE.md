# Hitsteripy Web App Guide

## Overview

Hitsteripy now has a **modern web-based GUI**! Run the executable and a web browser will open automatically with a clean, tab-based interface.

## Quick Start

### Development Mode

Run the web app in development:

```bash
python run_web_app.py
```

This will:
- Start the Flask web server on `http://127.0.0.1:5000`
- Automatically open your default web browser
- Show server logs in the console

### Production Build (Executable)

Build the web app as an executable:

```bash
python build_web_exe.py
```

The executable will be in `dist/Hitsteripy-Web.exe`. When you run it:
- A web server starts automatically
- Your browser opens to the app
- The console shows server logs (press Ctrl+C to stop)

## Features

### Tab-Based Interface

1. **🎵 Playlist Tab**
   - Set Spotify playlist URL
   - View and select from recent playlists
   - Set track count (10, 50, 100, 200, or "all")
   - View recent track counts

2. **📂 Import Tab**
   - Import tracks from your selected playlist
   - Progress indicator during import
   - Success/error messages

3. **📇 Generate Tab**
   - Select an imported CSV file
   - Generate HTML cards
   - View generation status

4. **👁️ Preview Tab**
   - Preview cards before/after generation
   - Navigate between tracks (Prev/Next buttons)
   - Switch between Front and Back views
   - Real-time preview rendering

5. **🪵 Logs Tab**
   - View all application logs
   - Color-coded (Info/Success/Error)
   - Auto-refreshing

### Status Bar

Always visible at the top showing:
- Current playlist name
- Track count setting
- Spotify connection status

## How It Works

1. **Set Playlist**: Enter a Spotify playlist URL or select from history
2. **Set Track Count**: Choose how many tracks to import (or "all")
3. **Import Tracks**: Fetches tracks from Spotify and saves to CSV
4. **Generate Cards**: Creates printable HTML cards from the CSV
5. **Preview**: View individual cards before printing

## Building the Web Executable

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Build:**
   ```bash
   python build_web_exe.py
   ```

3. **Find executable:**
   - Location: `dist/Hitsteripy-Web.exe`
   - Copy `spotify.env` to the same folder as the .exe

## Troubleshooting

### Port Already in Use

If port 5000 is already in use, edit `run_web_app.py` or `src/web_app.py`:
```python
run_web_app(host='127.0.0.1', port=5001, open_browser=True)  # Change port
```

### Browser Doesn't Open

- Check console for errors
- Manually navigate to `http://127.0.0.1:5000`

### Spotify Connection Issues

- Check that `spotify.env` exists and has valid credentials
- View the Logs tab for detailed error messages

## UI Design

- **Modern, minimal design** with clean colors
- **Responsive layout** that works on different screen sizes
- **Tab-based navigation** for easy access to all features
- **Real-time status updates** in the status bar
- **Card preview** with iframe rendering for accurate display

## Differences from Console Version

| Feature | Console Version | Web Version |
|---------|----------------|-------------|
| Interface | Text-based menu | Web-based tabs |
| Card Preview | No preview | Full preview with navigation |
| Status Updates | View logs menu | Real-time status bar |
| History | Stored in files | Displayed in UI |
| Accessibility | Keyboard navigation | Mouse/touch friendly |

## Technical Details

- **Backend**: Flask (Python web framework)
- **Frontend**: Vanilla JavaScript (no frameworks needed)
- **Styling**: Modern CSS with CSS variables
- **Communication**: REST API (JSON)
- **Port**: 5000 (configurable)

Enjoy the new web interface! 🎉

