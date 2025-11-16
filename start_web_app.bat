@echo off
REM Batch file to start Hitsteripy Web App during development

cd /d "%~dp0"

REM Try to find Python
set PYTHON_CMD=

py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py
    goto :run
)

python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    goto :run
)

if exist "env\Scripts\python.exe" (
    set PYTHON_CMD=env\Scripts\python.exe
    goto :run
)

echo ERROR: Could not find Python!
pause
exit /b 1

:run
echo Starting Hitsteripy Web App...
echo.
%PYTHON_CMD% run_web_app.py

