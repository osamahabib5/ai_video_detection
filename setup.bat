@echo off
REM Setup Python virtual environment and install dependencies on Windows

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%venv

echo 🐍 Setting up Python Virtual Environment...
echo ============================================

REM Check Python
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ✗ Python not found! Please install Python 3.10+
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo 📌 Python version: !PYTHON_VERSION!

REM Create virtual environment
if not exist "%VENV_DIR%" (
    echo 🔧 Creating virtual environment at: %VENV_DIR%
    python -m venv "%VENV_DIR%"
    echo ✓ Virtual environment created
) else (
    echo ⚠️  Virtual environment already exists at: %VENV_DIR%
)

REM Activate and install dependencies
echo.
echo 📦 Activating environment and installing dependencies...
call "%VENV_DIR%\Scripts\activate.bat"

REM Upgrade pip
echo ⬆️  Upgrading pip...
pip install --upgrade pip

REM Install PyTorch (CPU version by default)
echo.
echo 🔥 Installing PyTorch (CPU version)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

REM Install remaining dependencies
echo.
echo 📚 Installing project dependencies...
pip install -r "%SCRIPT_DIR%requirements.txt"

REM Create necessary directories
echo.
echo 📁 Creating directory structure...
if not exist "%SCRIPT_DIR%data\models" mkdir "%SCRIPT_DIR%data\models"
if not exist "%SCRIPT_DIR%data\videos" mkdir "%SCRIPT_DIR%data\videos"
if not exist "%SCRIPT_DIR%logs\predictions" mkdir "%SCRIPT_DIR%logs\predictions"

echo.
echo ============================================
echo ✅ Setup complete!
echo.
echo To activate the environment:
echo   venv\Scripts\activate
echo.
echo To run the application:
echo   python -m app.main
echo.
echo To start the API server:
echo   uvicorn app.api:app --host 0.0.0.0 --port 8000
echo.

endlocal
