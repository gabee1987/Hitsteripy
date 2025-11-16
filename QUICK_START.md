# Quick Start Guide - Running Hitsteripy

## The Problem: "pip is not recognized"

You're seeing this error because you need to **activate your virtual environment** first, or use `python -m pip` instead of just `pip`.

## Solution 1: Activate Virtual Environment (Recommended)

Since you're using **PowerShell**, run:

```powershell
.\env\Scripts\Activate.ps1
```

If you get an execution policy error, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate:
```powershell
.\env\Scripts\Activate.ps1
```

**Or use Command Prompt (cmd):**
```cmd
env\Scripts\activate.bat
```

After activation, you'll see `(env)` in your prompt, and then `pip` will work!

## Solution 2: Use Python -m pip (No Activation Needed)

Instead of `pip install pyinstaller`, use:

```powershell
python -m pip install pyinstaller
```

This works even without activating the virtual environment!

## Solution 3: Use the Batch Files (Easiest)

I've created helper batch files for you:

### Install PyInstaller:
**Double-click**: `install_pyinstaller.bat`

This will:
- Activate your virtual environment automatically
- Install PyInstaller
- Show you when it's done

### Run the App:
**Double-click**: `run_hitsteripy.bat`

This will:
- Activate your virtual environment automatically  
- Run the application

## Building the Executable

After installing PyInstaller (using any method above), run:

```powershell
python build_exe.py
```

Or if you activated the venv:
```powershell
python build_exe.py
```

The executable will be created in `dist/Hitsteripy.exe`

## Summary

| What you want to do | Command |
|---------------------|---------|
| Activate venv (PowerShell) | `.\env\Scripts\Activate.ps1` |
| Activate venv (CMD) | `env\Scripts\activate.bat` |
| Install PyInstaller | `python -m pip install pyinstaller` |
| Install PyInstaller (easier) | Double-click `install_pyinstaller.bat` |
| Build executable | `python build_exe.py` |
| Run app | Double-click `run_hitsteripy.bat` |

