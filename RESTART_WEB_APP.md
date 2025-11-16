# How to Restart the Web App

## If the app is running in Cursor terminal:

1. **Find the terminal window** where `py run_web_app.py` is running
2. **Press `Ctrl+C`** to stop the server
3. **Run again**: `py run_web_app.py`

## Quick Restart Steps:

1. In the terminal where Flask is running:
   - Press `Ctrl+C` (this stops the server)

2. Then run:
   ```powershell
   py run_web_app.py
   ```

3. Your browser should automatically open (or refresh the existing tab)

## Alternative: Use the Batch File

Double-click `start_web_app.bat` - it will start a fresh instance.

## Note:

- **HTML/CSS/JS changes**: Usually just need browser refresh (F5)
- **Python changes** (`src/web_app.py`): Need to restart the server (Ctrl+C, then run again)


