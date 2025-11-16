@echo off
REM Simple batch file to run Hitsteripy
REM This still requires Python to be installed and accessible in PATH

cd /d "%~dp0"

REM Try to find Python - use py launcher first, then try direct paths
set PYTHON_CMD=

REM Try Python launcher (py.exe)
py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py
    goto :run
)

REM Try direct python command
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    goto :run
)

REM Try venv python directly
if exist "env\Scripts\python.exe" (
    set PYTHON_CMD=env\Scripts\python.exe
    goto :run
)

echo ERROR: Could not find Python installation!
echo.
echo Please ensure Python is installed.
pause
exit /b 1

:run
REM Try to activate virtual environment if it exists (might fail if Python moved)
if exist "env\Scripts\activate.bat" (
    call env\Scripts\activate.bat 2>nul
)

REM Run the application
%PYTHON_CMD% -m src.main

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Error occurred. Press any key to exit...
    pause >nul
)
