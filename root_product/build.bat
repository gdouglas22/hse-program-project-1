@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found in PATH.
  echo Install Python 3.11+ to build the package.
  pause
  exit /b 1
)

python -m pip show pyinstaller >nul 2>nul
if errorlevel 1 (
  echo PyInstaller is not installed.
  echo Run: python -m pip install pyinstaller
  pause
  exit /b 1
)

python -m PyInstaller --noconfirm RootProduct.spec
if errorlevel 1 (
  echo Build failed.
  pause
  exit /b 1
)

echo Build finished. See dist\RootProduct
pause
endlocal
