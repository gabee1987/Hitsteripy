@echo off
REM Batch file to install PyInstaller in the virtual environment

cd /d "%~dp0"

REM Try to find Python - use py launcher first, then try direct paths
set PYTHON_CMD=

REM Try Python launcher (py.exe)
py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py
    echo Using Python launcher (py)
    goto :install
)

REM Try direct python command
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    echo Using Python (python)
    goto :install
)

REM Try venv python directly (even if broken, might work)
if exist "env\Scripts\python.exe" (
    set PYTHON_CMD=env\Scripts\python.exe
    echo Using venv Python directly
    goto :install
)

echo ERROR: Could not find Python installation!
echo.
echo Please ensure Python is installed and accessible.
echo You can try:
echo   1. Install Python from python.org
echo   2. Use py launcher: py -m pip install pyinstaller
echo   3. Recreate venv: py -m venv env
pause
exit /b 1

:install
echo.
echo Installing PyInstaller...
%PYTHON_CMD% -m pip install pyinstaller

if %errorlevel% == 0 (
    echo.
    echo PyInstaller installed successfully!
    echo You can now run: %PYTHON_CMD% build_exe.py
) else (
    echo.
    echo ERROR: Failed to install PyInstaller
    echo.
    echo Try manually:
    echo   %PYTHON_CMD% -m pip install pyinstaller
)

pause
