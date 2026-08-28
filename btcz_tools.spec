import os

from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all("customtkinter")

icon_path = os.path.join(SPECPATH, "btcz_logo.ico")
icon_file = icon_path if os.path.exists(icon_path) else None
print("BTCZ Tools build icon:", icon_file or "DEFAULT (btcz_logo.ico introuvable a cote du .spec)")

a = Analysis(
    ["run.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="BTCZ-Tools",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)