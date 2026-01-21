@echo off
setlocal

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found in PATH.
  echo Install Python 3.11+ and rerun this installer.
  pause
  exit /b 1
)

python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed.
  pause
  exit /b 1
)

python -m pip install pyinstaller
if errorlevel 1 (
  echo PyInstaller installation failed.
  pause
  exit /b 1
)

python -m src.app
endlocal
