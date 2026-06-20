@echo off
REM Activate venv and run the application on Windows

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%venv

echo 🚀 AI Video Detection System
echo ============================

REM Check if venv exists
if not exist "%VENV_DIR%" (
    echo ⚠️  Virtual environment not found. Running setup first...
    call "%SCRIPT_DIR%setup.bat"
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"

echo ✓ Environment activated
echo.

REM Run the application
echo 🎯 Starting video detection...
python -m app.main %*

endlocal
