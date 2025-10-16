@echo off
setlocal

REM ===== Paths =====
set "PROJ=%~dp0"
set "PY=%PROJ%venv\Scripts\python.exe"

REM ===== Create venv if missing =====
if not exist "%PROJ%venv\" (
  py -3 -m venv "%PROJ%venv"
)

REM ===== Install deps =====
"%PY%" -m pip install --upgrade pip
"%PY%" -m pip install pyinstaller tkinterdnd2

REM ===== Build .exe (onefile, no console, include push_it.sh) =====
REM Note: --add-data "src;dst" uses semicolon on Windows
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
