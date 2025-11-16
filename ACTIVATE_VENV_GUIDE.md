# Virtual Environment Guide

## Quick Answer

**You don't need to manually activate the venv!** The `start_web_app.bat` script automatically uses the venv Python if available.

## Manual Activation (if needed)

If you want to manually activate the virtual environment:

### Command Prompt (CMD)
```batch
env\Scripts\activate.bat
```

### PowerShell
```powershell
env\Scripts\Activate.ps1
```

### After Activation
Once activated, you'll see `(env)` in your prompt, and you can run:
```batch
py run_web_app.py
```

To deactivate:
```batch
deactivate
```

## Using PDF Generation Without Activating Venv

**Good news!** The `start_web_app.bat` script automatically uses the venv Python if it exists, so WeasyPrint should work without manual activation.

Just run:
```batch
start_web_app.bat
```

This will:
1. Check for `env\Scripts\python.exe` first (has WeasyPrint installed)
2. Fall back to `py` launcher if venv doesn't exist
3. Fall back to `python` command as last resort

## PDF Generation Requirements

### Option 1: Use Browser Print-to-PDF (Recommended - No Setup Needed!)
1. Click any print button (Front, Back, Print Both)
2. Press Ctrl+P (or Cmd+P on Mac)
3. Select "Save as PDF" as destination
4. Make sure "Background graphics" is enabled
5. Save!

This works perfectly and requires no additional setup.

### Option 2: Install GTK3 Runtime (For WeasyPrint)
If you want to use the "Generate All PDFs" button:

1. **Install GTK3 Runtime** (Windows only):
   - Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
   - Install the GTK3 Runtime (MSYS2-based version recommended)
   - Restart the application

2. **Verify WeasyPrint is installed**:
   - Run: `env\Scripts\python.exe -c "import weasyprint; print('OK')"`
   - If error: Run `install_weasyprint.bat`

3. **Start app using venv**:
   - Use `start_web_app.bat` (it automatically uses venv Python)

## Troubleshooting

### "WeasyPrint not found"
- Use `start_web_app.bat` instead of `py run_web_app.py`
- Or manually activate venv first

### "GTK3 Runtime missing" error
- Install GTK3 Runtime (see Option 2 above)
- Or use browser Print-to-PDF instead (Option 1)

### Can't activate venv in PowerShell
- PowerShell may block scripts by default
- Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Then try activating again

