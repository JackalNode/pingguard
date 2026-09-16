# -*- mode: python ; coding: utf-8 -*-

import sys

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets/icon.ico', 'assets'),   # bundle icon so get_app_icon() finds it at runtime
        ('assets/icon_header.png', 'assets'),   # in-app header logo (MainWindow title bar)
        ('LICENSE.txt', '.'),
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
    upx=False,  # disabled Session 28 - UPX compression is a well-documented AV false-positive
                # trigger; v2.2.4's Windows installer picked up 3 new "trojan" flags (Avira,
                # Cynet, WithSecure) on VirusTotal that v2.2.3 didn't have. Testing this as the
                # first, cheapest mitigation before touching PyInstaller's own version.
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
        upx=False,  # see upx=False note above (Session 28 AV false-positive mitigation)
        upx_exclude=[],
        name='PingGuard',
    )
