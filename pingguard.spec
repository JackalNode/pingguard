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
    upx=True,   # re-enabled Session 28 - disabling UPX (tested as v2.2.5) did NOT reduce AV
                # flags: Avira, DeepInstinct, and WithSecure all still flagged the UPX-off build
                # exactly as they flagged v2.2.4 (UPX-on). Ruled out as the cause; reverted rather
                # than carry the size/perf cost of no compression for nothing. Next theory:
                # unpinned pyinstaller>=6.0.0 in requirements.txt (see pyinstaller/pyinstaller#8164).
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
        upx=True,   # see note above - UPX-disable tested and ruled out (Session 28)
        upx_exclude=[],
        name='PingGuard',
    )
