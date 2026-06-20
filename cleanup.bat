@echo off
REM Clean up virtual environment and cached files on Windows

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0

echo 🧹 Cleaning up project...

REM Remove virtual environment
if exist "%SCRIPT_DIR%venv" (
    echo 🗑️  Removing virtual environment...
    rmdir /s /q "%SCRIPT_DIR%venv"
)

REM Remove Python cache files
echo 🗑️  Removing Python cache...
for /d /r "%SCRIPT_DIR%" %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
del /s /q "%SCRIPT_DIR%*.pyc" 2>nul
del /s /q "%SCRIPT_DIR%*.pyo" 2>nul

REM Remove pytest cache
if exist "%SCRIPT_DIR%.pytest_cache" rmdir /s /q "%SCRIPT_DIR%.pytest_cache" 2>nul

echo ✓ Cleanup complete!
echo.
echo To rebuild from scratch:
echo   setup.bat

endlocal
