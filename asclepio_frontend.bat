@echo off
setlocal
cd /d "%~dp0"

set PYTHON_CMD=

if "%PYTHON_CMD%"=="" (
    where py >nul 2>nul
    if not errorlevel 1 set PYTHON_CMD=py
)

if "%PYTHON_CMD%"=="" (
    where python >nul 2>nul
    if not errorlevel 1 set PYTHON_CMD=python
)

if "%PYTHON_CMD%"=="" (
    if exist ".venv\Scripts\python.exe" set PYTHON_CMD=.venv\Scripts\python.exe
)

if "%PYTHON_CMD%"=="" (
    echo.
    echo [ERRO] Python nao encontrado.
    echo Instale o Python ou crie um ambiente virtual em .venv.
    echo.
    pause
    exit /b 1
)

"%PYTHON_CMD%" site_server.py 8001
