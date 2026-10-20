@echo off
setlocal
title Flying Cabs Platform
echo ============================================================
echo   Starting Flying Cabs Platform - Next-Gen Aero Mobility
echo ============================================================
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel% equ 0 (
    py run.py
    exit /b
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" run.py
    exit /b
)

where python >nul 2>nul
if %errorlevel% equ 0 (
    python run.py
    exit /b
)

echo Python launcher or Python 3.12 executable not found in standard paths.
pause
