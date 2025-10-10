@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Git Pusher App - Bash Backend
set "BASH_EXE=C:\Program Files\Git\git-bash.exe"
set "SH=%~dp0push_it.sh"
if not exist "%BASH_EXE%" (echo [ERROR] Git Bash not found at "%BASH_EXE%". & pause & exit /b 1)
if not exist "%SH%" (echo [ERROR] Missing push_it.sh at "%SH%". & pause & exit /b 1)
set /p "PROJECT_DIR=Drag or enter project folder: "
set /p "VERSION=Version tag [default v1.0]: "
if "%VERSION%"=="" set "VERSION=v1.0"
:askrepo
set /p "REPO_URL=Repo URL (https://github.com/user/repo.git): "
if "%REPO_URL%"=="" goto askrepo
set /p "BRANCH=Branch [default main]: "
if "%BRANCH%"=="" set "BRANCH=main"
set "CHERE_INVOKING=1"
set "MSYS2_ARG_CONV_EXCL=*"
echo.
echo 📂 Project : %PROJECT_DIR%
echo 🏷  Version : %VERSION%
echo 🌐 Repo    : %REPO_URL%
echo 🌿 Branch  : %BRANCH%
echo.
"%BASH_EXE%" -c "/usr/bin/env bash \"$(cygpath -u '%SH%')\" \"$(cygpath -u '%PROJECT_DIR%')\" \"%VERSION%\" \"%REPO_URL%\" \"%BRANCH%\""
set "ERR=%ERRORLEVEL%"
echo.
if not "%ERR%"=="0" (echo [ERROR] push_it.sh exited with code %ERR%) else (echo [OK] Completed successfully.)
echo.
pause
exit /b %ERR%
