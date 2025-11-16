@echo off
REM Batch file to install WeasyPrint for PDF generation
REM Note: On Windows, WeasyPrint also requires GTK3 Runtime libraries

cd /d "%~dp0"

REM Try to find Python - use py launcher first, then try direct paths
set PYTHON_CMD=

REM Try Python launcher (py.exe)
py --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=py -m pip
    echo Using Python launcher (py)
    goto :install
)

REM Try direct python command
python --version >nul 2>&1
if %errorlevel% == 0 (
    set PYTHON_CMD=python -m pip
    echo Using Python (python)
    goto :install
)

REM Try venv python directly
if exist "env\Scripts\python.exe" (
    set PYTHON_CMD=env\Scripts\python.exe -m pip
    echo Using venv Python directly
    goto :install
)

echo ERROR: Could not find Python installation!
echo.
echo Please ensure Python is installed and accessible.
echo You can try:
echo   1. Install Python from python.org
echo   2. Use py launcher: py -m pip install weasyprint
echo   3. Recreate venv: py -m venv env
pause
exit /b 1

:install
echo.
echo Installing WeasyPrint...
echo This may take a few minutes as it includes dependencies...
echo.
%PYTHON_CMD% -m pip install weasyprint

if %errorlevel% == 0 (
    echo.
    echo ============================================================
    echo WeasyPrint installed successfully!
    echo.
    echo IMPORTANT: On Windows, WeasyPrint also requires GTK3 Runtime.
    echo.
    echo To use PDF generation, you need to install GTK3 Runtime:
    echo   1. Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
    echo   2. Install GTK3 Runtime (MSYS2-based version recommended)
    echo   3. Restart the application
    echo.
    echo Alternative: Use browser Print-to-PDF instead
    echo   - Click the print buttons to open pages
    echo   - Use browser's print dialog (Ctrl+P)
    echo   - Select "Save as PDF" as destination
    echo   - Make sure "Background graphics" is enabled
    echo ============================================================
    echo.
    echo Testing WeasyPrint import...
    %PYTHON_CMD% show weasyprint 2>&1 | findstr /C:"Version" >nul
    if %errorlevel% == 0 (
        echo WeasyPrint is installed correctly!
    ) else (
        echo WARNING: WeasyPrint may not work without GTK3 Runtime.
    )
) else (
    echo.
    echo ERROR: Failed to install WeasyPrint
    echo.
    echo Try manually:
    echo   %PYTHON_CMD% install weasyprint
    echo.
    echo Note: WeasyPrint may require GTK3 Runtime on Windows.
)

pause
