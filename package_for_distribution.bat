@echo off
REM Script to package Hitsteripy.exe with required files for distribution

cd /d "%~dp0"

set DIST_DIR=Hitsteripy_Distribution
set EXE_SOURCE=dist\Hitsteripy.exe
set ENV_SOURCE=spotify.env

echo ========================================
echo Packaging Hitsteripy for Distribution
echo ========================================
echo.

REM Check if exe exists
if not exist "%EXE_SOURCE%" (
    echo ERROR: Hitsteripy.exe not found!
    echo Expected location: %EXE_SOURCE%
    echo.
    echo Please build the executable first:
    echo   py build_exe.py
    pause
    exit /b 1
)

REM Create distribution folder
if exist "%DIST_DIR%" (
    echo Removing old distribution folder...
    rmdir /s /q "%DIST_DIR%"
)

mkdir "%DIST_DIR%"
echo Created distribution folder: %DIST_DIR%
echo.

REM Copy executable
echo Copying executable...
copy "%EXE_SOURCE%" "%DIST_DIR%\"
if %errorlevel% == 0 (
    echo [OK] Hitsteripy.exe copied
) else (
    echo [ERROR] Failed to copy executable
    pause
    exit /b 1
)

REM Copy spotify.env if it exists
if exist "%ENV_SOURCE%" (
    echo Copying spotify.env...
    copy "%ENV_SOURCE%" "%DIST_DIR%\"
    echo [OK] spotify.env copied
    echo.
    echo NOTE: Make sure to update spotify.env with correct credentials!
) else (
    echo [WARNING] spotify.env not found - you'll need to add it manually
    echo Creating template...
    (
        echo SPOTIFY_CLIENT_ID=your_client_id
        echo SPOTIFY_CLIENT_SECRET=your_client_secret
    ) > "%DIST_DIR%\spotify.env.template"
    echo [OK] Created spotify.env.template
)

REM Copy README
if exist "HOW_TO_USE_EXE.md" (
    copy "HOW_TO_USE_EXE.md" "%DIST_DIR%\README.md"
    echo [OK] README copied
)

echo.
echo ========================================
echo Packaging Complete!
echo ========================================
echo.
echo Distribution folder: %CD%\%DIST_DIR%
echo.
echo Contents:
dir /b "%DIST_DIR%"
echo.
echo You can now:
echo   1. Copy the entire "%DIST_DIR%" folder anywhere
echo   2. Run Hitsteripy.exe from that folder
echo   3. Share the folder with others (they need their own spotify.env)
echo.
pause

