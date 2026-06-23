@echo off
chcp 65001 >nul
set "PROJECT_DIR=%~dp0"
set "VENV_PY=%PROJECT_DIR%.venv\Scripts\python.exe"

if exist "%VENV_PY%" (
    "%VENV_PY%" "%PROJECT_DIR%asclepio.py" %*
    exit /b %ERRORLEVEL%
)

py "%PROJECT_DIR%asclepio.py" %* 2>nul
if not errorlevel 9009 exit /b %ERRORLEVEL%

python "%PROJECT_DIR%asclepio.py" %*
