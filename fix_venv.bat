@echo off
REM Script to fix broken virtual environment by recreating it

cd /d "%~dp0"

echo ========================================
echo Fixing Virtual Environment
echo ========================================
echo.

REM Find Python
set PYTHON_CMD=

py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py
    echo Found Python launcher (py)
    goto :recreate
)

python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python
    echo Found Python (python)
    goto :recreate
)

echo ERROR: Could not find Python!
echo Please install Python from python.org
pause
exit /b 1

:recreate
echo.
echo Python command: %PYTHON_CMD%
echo.

REM Backup old venv if it exists
if exist "env" (
    echo Backing up old virtual environment...
    if exist "env_backup" rmdir /s /q env_backup
    move env env_backup
    echo Old venv moved to env_backup
    echo.
)

REM Create new venv
echo Creating new virtual environment...
%PYTHON_CMD% -m venv env

if %errorlevel% == 0 (
    echo Virtual environment created successfully!
    echo.
    echo Activating and installing dependencies...
    call env\Scripts\activate.bat
    %PYTHON_CMD% -m pip install --upgrade pip
    %PYTHON_CMD% -m pip install -r requirements.txt
    echo.
    echo ========================================
    echo Virtual environment fixed!
    echo ========================================
    echo You can now use:
    echo   - Double-click run_hitsteripy.bat to run the app
    echo   - Double-click install_pyinstaller.bat to install PyInstaller
) else (
    echo ERROR: Failed to create virtual environment
    echo.
    if exist "env_backup" (
        echo Restoring backup...
        if exist "env" rmdir /s /q env
        move env_backup env
    )
)

pause
