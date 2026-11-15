@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PYEXE="
call :try "C:\Users\tingz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
call :try "D:\apps\python\python.exe"
call :try "python"
if "%PYEXE%"=="" set "PYEXE=python"
echo [interpreter] %PYEXE%
echo.
"%PYEXE%" build_log.py
echo.
pause
exit /b

:try
if "%~1"=="" exit /b
"%~1" -c "import openpyxl, fitparse" >nul 2>&1
if errorlevel 1 exit /b
if not "%PYEXE%"=="" exit /b
set "PYEXE=%~1"
exit /b
