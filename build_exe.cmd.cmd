@echo off
setlocal

REM ===== Paths =====
set "PROJ=%~dp0"
set "PY_VENV=%PROJ%venv\Scripts\python.exe"

REM ===== Determine which Python to use =====
if exist "%PY_VENV%" (
  set "PY=%PY_VENV%"
  echo Using virtual environment Python
) else (
  REM Try to find system Python
  where python >nul 2>&1
  if %errorlevel% equ 0 (
    set "PY=python"
    echo Using system Python
  ) else (
    echo ERROR: Python not found!
    pause
    exit /b 1
  )
)

REM ===== Create venv if missing =====
if not exist "%PROJ%venv\" (
  echo Creating virtual environment...
  "%PY%" -m venv "%PROJ%venv"
  if %errorlevel% neq 0 (
    echo WARNING: Failed to create venv, using system Python
    set "PY=python"
  ) else (
    set "PY=%PY_VENV%"
  )
)

REM ===== Install deps =====
echo Installing dependencies...
"%PY%" -m pip install --upgrade pip --quiet
"%PY%" -m pip install pyinstaller customtkinter --quiet

REM ===== Build .exe (onefile, no console, include push_it.sh) =====
REM Note: --add-data "src;dst" uses semicolon on Windows
echo Building EXE...
echo.

REM Try to close any running GitPusher.exe processes
echo Checking for running GitPusher.exe...
tasklist /FI "IMAGENAME eq GitPusher.exe" 2>NUL | find /I /N "GitPusher.exe">NUL
if "%ERRORLEVEL%"=="0" (
  echo GitPusher.exe is running. Attempting to close it...
  taskkill /F /IM GitPusher.exe >nul 2>&1
  timeout /t 2 /nobreak >nul
)

REM Try to remove old EXE if it exists
if exist "%PROJ%dist\GitPusher.exe" (
  echo Removing old EXE...
  del /f /q "%PROJ%dist\GitPusher.exe" >nul 2>&1
  if exist "%PROJ%dist\GitPusher.exe" (
    echo WARNING: Could not delete old EXE. It may be locked.
    echo Please close GitPusher.exe manually and try again.
    pause
    exit /b 1
  )
)

"%PY%" -m PyInstaller ^
  --noconsole --onefile ^
  --name GitPusher ^
  --add-data "base\push_it.sh;base" ^
  gui\main.py

echo.
echo Build complete. Find your EXE here:
echo   %PROJ%dist\GitPusher.exe
echo.
pause
