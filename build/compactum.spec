# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — single-file GUI bundle for Capsa."""

import sys
from pathlib import Path

block_cipher = None

ROOT = Path(SPECPATH).resolve().parent
SRC = ROOT / "src" / "capsapdf"

datas = [
    (str(SRC / "webui"), "capsa/webui"),
]

# pywebview platform-specific hidden imports
hidden = [
    "pypdfium2_raw",
    "PIL._tkinter_finder",
]
if sys.platform == "darwin":
    hidden += ["webview.platforms.cocoa"]
elif sys.platform == "win32":
    hidden += ["webview.platforms.edgechromium", "webview.platforms.mshtml", "clr_loader"]
else:
    hidden += ["webview.platforms.gtk", "webview.platforms.qt"]

a = Analysis(
    [str(SRC / "__main__.py")],
    pathex=[str(ROOT / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "test", "unittest"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Compactum",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "build" / "icon.icns") if (ROOT / "build" / "icon.icns").exists() else None,
)

# macOS .app bundle
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="Compactum.app",
        icon=str(ROOT / "build" / "icon.icns") if (ROOT / "build" / "icon.icns").exists() else None,
        bundle_identifier="com.vivesieg.compactum",
        info_plist={
            "CFBundleName": "Compactum",
            "CFBundleDisplayName": "Compactum",
            "CFBundleShortVersionString": "1.0.0",
            "CFBundleVersion": "1.0.0",
            "NSHighResolutionCapable": True,
            "NSRequiresAquaSystemAppearance": False,
            "LSMinimumSystemVersion": "10.13",
        },
    )
