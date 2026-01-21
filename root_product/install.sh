set -e

cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Python 3.11+ not found in PATH."
  exit 1
fi

if ! "$PY" -m pip install -r requirements.txt; then
  echo "Dependency installation failed."
  exit 1
fi

if ! "$PY" -m pip install pyinstaller; then
  echo "PyInstaller installation failed."
  exit 1
fi

"$PY" -m src.app
