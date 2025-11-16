@echo off
REM Batch file to start Hitsteripy Web App during development
REM This script automatically uses the virtual environment Python if available

cd /d "%~dp0"

REM Priority: 1) venv Python, 2) py launcher, 3) direct python
set PYTHON_CMD=

REM First, try venv Python (has WeasyPrint installed)
if exist "env\Scripts\python.exe" (
    set PYTHON_CMD=env\Scripts\python.exe
    echo Using virtual environment Python (includes WeasyPrint)
    goto :run
)

REM Fallback to py launcher
py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py
    echo Using Python launcher (py)
    echo NOTE: If WeasyPrint doesn't work, use venv Python: env\Scripts\python.exe
    goto :run
)

REM Fallback to direct python command
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    echo Using Python (python)
    echo NOTE: If WeasyPrint doesn't work, use venv Python: env\Scripts\python.exe
    goto :run
)

echo ERROR: Could not find Python!
echo.
echo Please ensure Python is installed or activate the virtual environment:
echo   env\Scripts\activate
pause
exit /b 1

:run
echo.
echo Starting Hitsteripy Web App...
echo.
%PYTHON_CMD% run_web_app.py

