# Building the Windows .exe

BTCZ Tools can be packaged into a single standalone `BTCZ Tools.exe` with
[PyInstaller](https://pyinstaller.org/). The build must run **on Windows**.

## Quick build

Double-click **`build_exe.bat`**, or from Git Bash:

```bash
./build_exe.sh
```

The script creates a virtualenv, installs the dependencies and PyInstaller,
then builds the executable. The result is:

```
dist/BTCZ-Tools.exe
```

## Manual build

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt pyinstaller
pyinstaller btcz_tools.spec --noconfirm --clean
```

## Notes

- **Data location** — when frozen, the app stores its `data/` folder (addresses,
  settings, logo, logs, history) next to the `.exe`, so everything persists between runs.
- **Application icon** — place a `btcz_logo.ico` at the project root before building and
  it will be used as the executable icon. After the app has run once, a ready-made icon
  is available at `data/btcz_logo.ico` — copy it to the root. Without it the build uses
  the default PyInstaller icon.
- **No console window** — the build runs in windowed mode (`console=False`).
- **customtkinter assets** are bundled automatically via `collect_all` in the spec.
- The first launch of the `.exe` still needs an internet connection to download the BTCZ
  logo and fetch live data.