@echo off
title JARVIS Server - Install Auto-Start
color 0B
echo.
echo ========================================
echo   J.A.R.V.I.S. - Install Auto-Start
echo ========================================
echo.
echo This will configure JARVIS to start automatically when Windows starts.
echo.

:: Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Need administrator rights!
    echo Right-click this file and select "Run as administrator"
    pause
    exit /b
)

echo [INFO] Creating scheduled task...

:: Delete existing task if exists
schtasks /delete /tn "JARVIS_Server" /f >nul 2>&1

:: Create new task
schtasks /create /tn "JARVIS_Server" /tr "\"C:\Users\Kimet\AppData\Local\Programs\Python\Python311\python.exe\" \"%~dp0..\backend\main.py\"" /sc onlogon /rl highest /f

if %errorlevel%==0 (
    echo.
    echo [OK] JARVIS will now start automatically with Windows
    echo [INFO] Task name: JARVIS_Server
    echo.
    echo To remove auto-start, run: uninstall.bat
) else (
    echo.
    echo [ERROR] Failed to create scheduled task
)

echo.
pause
