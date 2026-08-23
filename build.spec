# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for 枢纽台 / NexusDeck (跨平台桌面化打包)。

产物：单文件可执行 NexusDeck（macOS 为 .app via --windowed，Windows 为 .exe）。
运行时 server.py 通过 __file__ 定位 static/ 与 VERSION，PyInstaller 会把它们
作为 datas 解压到同一临时目录，因此无需任何路径改造。
"""

import os

block_cipher = None

app_name = "NexusDeck"
here = os.path.abspath(SPECPATH)

# 需要随可执行一起打包的资源（相对 SPECPATH）
datas = [
    (os.path.join(here, "static"), "static"),
    (os.path.join(here, "VERSION"), "VERSION"),
]

# server.py 用到 msvcrt（Windows）/ fcntl（POSIX），均为标准库，无需额外 hiddenimport

a = Analysis(
    [os.path.join(here, "server.py")],
    pathex=[here],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 无终端窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)

# macOS 额外产出 .app 包（windowed）
app = BUNDLE(
    coll,
    name=app_name + ".app",
    icon=None,
    bundle_identifier="com.nexusdeck.desktop",
    info_plist={
        "CFBundleDisplayName": "枢纽台",
        "CFBundleName": "NexusDeck",
        "CFBundleExecutable": app_name,
        "CFBundleIdentifier": "com.nexusdeck.desktop",
        "CFBundleShortVersionString": open(os.path.join(here, "VERSION")).read().strip(),
        "CFBundleVersion": "100",
        "CFBundleDevelopmentRegion": "zh_CN",
        "LSMinimumSystemVersion": "12.0",
        "LSUIElement": True,
        "NSHighResolutionCapable": True,
        "NSPrincipalClass": "NSApplication",
    },
    windowed=True,
)
