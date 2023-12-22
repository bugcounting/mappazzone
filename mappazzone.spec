# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main-pyinstaller.py'],
    pathex=[],
    binaries=[],
    # https://pyinstaller.org/en/stable/runtime-information.html#using-file
    datas= [
        ('src/mappazzone/data/*.csv', './src/mappazzone/data'),
        ('src/mappazzone/flags/*.png', './src/mappazzone/flags'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
    ],
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
    [],
    exclude_binaries=True,
    name='mappazzone',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='mappazzone',
)
