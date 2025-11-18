@echo off
REM Simple batch file to build TuneGen Web App executable
REM Make sure your virtual environment is activated first!

echo ============================================================
echo Building TuneGen Web App Executable
echo ============================================================
echo.

REM Check if virtual environment is activated
python -c "import sys; sys.exit(0 if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) else 1)" 2>nul
if %errorlevel% neq 0 (
    echo WARNING: Virtual environment may not be activated!
    echo Please run: env\Scripts\activate
    echo.
    pause
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: PyInstaller is not installed!
    echo Please run: pip install pyinstaller
    echo.
    pause
    exit /b 1
)

REM Run the build script
python build_web_exe.py

echo.
echo ============================================================
echo Build process completed!
echo ============================================================
echo.
pause

