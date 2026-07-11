@echo off
title JARVIS Server - Uninstall Auto-Start
color 0C
echo.
echo ========================================
echo   J.A.R.V.I.S. - Uninstall Auto-Start
echo ========================================
echo.

:: Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Need administrator rights!
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b
)

echo [INFO] Removing scheduled task...
schtasks /delete /tn "JARVIS_Server" /f >nul 2>&1

if %errorlevel%==0 (
    echo.
    echo [OK] JARVIS auto-start removed
    echo [INFO] Server will no longer start with Windows
) else (
    echo.
    echo [INFO] No scheduled task found or already removed
)

echo.
pause
