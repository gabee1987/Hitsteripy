@echo off
REM Script to clean the distribution folder (removes generated data but keeps exe and config)

cd /d "%~dp0"

set DIST_DIR=Hitsteripy_Distribution

echo ========================================
echo Clean Distribution Folder
echo ========================================
echo.
echo WARNING: This will delete:
echo   - generated_cards/ folder
echo   - imported_tracks/ folder
echo   - data/ folder (playlist history)
echo.
echo It will KEEP:
echo   - Hitsteripy.exe
echo   - spotify.env
echo   - README.md
echo.
set /p CONFIRM="Are you sure you want to continue? (Y/N): "

if /i not "%CONFIRM%"=="Y" (
    echo Cancelled.
    pause
    exit /b 0
)

if not exist "%DIST_DIR%" (
    echo Distribution folder not found!
    pause
    exit /b 1
)

echo.
echo Cleaning...

if exist "%DIST_DIR%\generated_cards" (
    rmdir /s /q "%DIST_DIR%\generated_cards"
    echo [OK] Removed generated_cards/
)

if exist "%DIST_DIR%\imported_tracks" (
    rmdir /s /q "%DIST_DIR%\imported_tracks"
    echo [OK] Removed imported_tracks/
)

if exist "%DIST_DIR%\data" (
    rmdir /s /q "%DIST_DIR%\data"
    echo [OK] Removed data/
)

echo.
echo ========================================
echo Clean Complete!
echo ========================================
echo.
echo The distribution folder is now clean and ready for fresh testing.
pause

