@echo off
REM Script to update the distribution folder with the newly built executable

cd /d "%~dp0"

set DIST_DIR=Hitsteripy_Distribution
set EXE_SOURCE=dist\Hitsteripy.exe

echo ========================================
echo Updating Distribution Folder
echo ========================================
echo.

REM Check if new exe exists
if not exist "%EXE_SOURCE%" (
    echo ERROR: New Hitsteripy.exe not found!
    echo Expected location: %EXE_SOURCE%
    echo.
    echo Please build the executable first:
    echo   py build_exe.py
    pause
    exit /b 1
)

REM Check if distribution folder exists
if not exist "%DIST_DIR%" (
    echo Distribution folder not found. Creating it...
    call package_for_distribution.bat
    exit /b 0
)

REM Create backup of old exe
if exist "%DIST_DIR%\Hitsteripy.exe" (
    echo Backing up old executable...
    copy "%DIST_DIR%\Hitsteripy.exe" "%DIST_DIR%\Hitsteripy.exe.old" >nul 2>&1
    echo [OK] Old exe backed up as Hitsteripy.exe.old
)

REM Copy new exe
echo.
echo Updating executable...
copy "%EXE_SOURCE%" "%DIST_DIR%\Hitsteripy.exe" /Y
if %errorlevel% == 0 (
    echo [OK] New Hitsteripy.exe copied to distribution folder
) else (
    echo [ERROR] Failed to copy executable
    pause
    exit /b 1
)

REM Check file sizes
for %%F in ("%EXE_SOURCE%") do set NEW_SIZE=%%~zF
for %%F in ("%DIST_DIR%\Hitsteripy.exe.old") do set OLD_SIZE=%%~zF 2>nul

if defined OLD_SIZE (
    echo.
    echo File sizes:
    echo   Old: %OLD_SIZE% bytes
    echo   New: %NEW_SIZE% bytes
)

echo.
echo ========================================
echo Update Complete!
echo ========================================
echo.
echo Distribution folder updated: %CD%\%DIST_DIR%
echo.
echo Your data folders are preserved:
echo   - data/ (playlist history)
echo   - imported_tracks/ (CSV files)
echo   - generated_cards/ (generated HTML files)
echo.
echo You can now test the new executable:
echo   cd %DIST_DIR%
echo   Hitsteripy.exe
echo.
pause

