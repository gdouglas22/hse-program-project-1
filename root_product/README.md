# Root Product

Python desktop app for computing square roots and n-th roots with a multilingual UI.

## Setup

- Python 3.11+
- Install deps:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python -m src.app
```

Run tests:

```bash
pytest
```

Optional coverage (install `pytest-cov` first):

```bash
pip install pytest-cov
pytest --cov=src --cov-report=term-missing
```

## Add a new language

Drop a new JSON file into `src/resources/i18n`, e.g. `de.json`:

```json
{
  "language_name": "Deutsch",
  "app_title": "Wurzelrechner",
  "label_number": "Zahl",
  "label_degree": "Grad n",
  "label_precision": "Genauigkeit",
  "label_mode": "Modus",
  "mode_principal": "Hauptwurzel",
  "mode_all": "Alle Wurzeln",
  "button_compute": "Berechnen",
  "button_clear": "Löschen",
  "button_copy": "Kopieren",
  "status_ready": "Bereit",
  "status_error": "Eingabefehler",
  "status_copied": "In die Zwischenablage kopiert",
  "result_header": "Ergebnis"
}
```

Then select it from the language drop-down. No restart required.

## Quick scripts

- Windows: `install.bat`, `build.bat`
- macOS/Linux: `bash install.sh`

## Packaging

Builds must be created on the target OS (PyInstaller limitation).

PyInstaller examples (include i18n resources):

Windows:

```bash
pyinstaller --noconfirm --onefile --windowed src/app.py --name RootProduct --add-data "src/resources/i18n;resources/i18n"
```

macOS:

```bash
pyinstaller --noconfirm --windowed src/app.py --name RootProduct --add-data "src/resources/i18n:resources/i18n"
```

Linux:

```bash
pyinstaller --noconfirm --onefile --windowed src/app.py --name RootProduct --add-data "src/resources/i18n:resources/i18n"
```

Optional: use the provided `RootProduct.spec` to include resources consistently:

```bash
pyinstaller --noconfirm RootProduct.spec
```

Briefcase (optional alternative):

```bash
pip install briefcase
briefcase new
briefcase create
briefcase build
```
