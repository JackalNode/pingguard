# -*- mode: python ; coding: utf-8 -*-

import sys

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/icon.ico', 'assets'),   # bundle icon so get_app_icon() finds it at runtime
    ],
    hiddenimports=[
        'updater',
        'packaging',
        'packaging.version',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries if sys.platform not in ('darwin', 'win32') else [],
    a.datas if sys.platform not in ('darwin', 'win32') else [],
    [],
    exclude_binaries=(sys.platform in ('darwin', 'win32')),
    name='PingGuard',
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
    icon='assets/icon.ico',
)

if sys.platform == 'darwin':
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='PingGuard',
    )
    app = BUNDLE(
        coll,
        name='PingGuard.app',
        icon=None,
        bundle_identifier=None,
    )
elif sys.platform == 'win32':
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='PingGuard',
    )
