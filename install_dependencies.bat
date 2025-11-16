@echo off
REM Batch file to install all dependencies in the virtual environment

cd /d "%~dp0"

REM Try to find Python - prioritize venv Python
set PYTHON_CMD=

REM First, try venv Python (preferred)
if exist "env\Scripts\python.exe" (
    set PYTHON_CMD=env\Scripts\python.exe
    echo Using virtual environment Python
    goto :install
)

REM Fallback to py launcher
py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py -m pip
    echo Using Python launcher (py)
    echo WARNING: Installing to system Python. Consider creating a venv first!
    echo   py -m venv env
    echo   Then run this script again.
    goto :install_system
)

REM Fallback to direct python command
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python -m pip
    echo Using Python (python)
    echo WARNING: Installing to system Python. Consider creating a venv first!
    echo   python -m venv env
    echo   Then run this script again.
    goto :install_system
)

echo ERROR: Could not find Python!
echo.
echo Please ensure Python is installed and accessible.
pause
exit /b 1

:install
echo.
echo Installing dependencies from requirements.txt...
echo This may take a few minutes...
echo.

%PYTHON_CMD% -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo WARNING: Failed to upgrade pip, continuing anyway...
)

if exist "requirements.txt" (
    %PYTHON_CMD% -m pip install -r requirements.txt
    
    if %errorlevel% == 0 (
        echo.
        echo ============================================================
        echo Dependencies installed successfully!
        echo.
        echo You can now start the app with:
        echo   start_web_app.bat
        echo ============================================================
    ) else (
        echo.
        echo ERROR: Failed to install some dependencies
        echo.
        echo Try manually:
        echo   %PYTHON_CMD% -m pip install -r requirements.txt
    )
) else (
    echo ERROR: requirements.txt not found!
    echo.
    echo Installing essential packages manually...
    %PYTHON_CMD% -m pip install flask werkzeug jinja2 spotipy python-dotenv rich qrcode pillow weasyprint
)

echo.
pause
exit /b 0

:install_system
echo.
echo Installing dependencies from requirements.txt...
echo This may take a few minutes...
echo.

%PYTHON_CMD% install --upgrade pip
if exist "requirements.txt" (
    %PYTHON_CMD% install -r requirements.txt
    
    if %errorlevel% == 0 (
        echo.
        echo ============================================================
        echo Dependencies installed successfully!
        echo.
        echo You can now start the app with:
        echo   start_web_app.bat
        echo ============================================================
    ) else (
        echo.
        echo ERROR: Failed to install some dependencies
    )
) else (
    echo ERROR: requirements.txt not found!
    echo.
    echo Installing essential packages manually...
    %PYTHON_CMD% install flask werkzeug jinja2 spotipy python-dotenv rich qrcode pillow weasyprint
)

echo.
pause
exit /b 0

