# tearyu-datamorph.spec
# PyInstaller build spec
# Run: pyinstaller tearyu-datamorph.spec

import os
block_cipher = None

a = Analysis(
    ['gui/tearyu_datamorph_gui.py'],
    pathex=[os.path.abspath('src')],
    binaries=[],
    datas=[
        ('examples/', 'examples/'),
    ],
    hiddenimports=[
        'datamorph',
        'csv', 'json', 'xml', 'xml.etree',
        'xml.etree.ElementTree', 'xml.dom', 'xml.dom.minidom',
        're', 'io', 'os', 'sys', 'tkinter', 'tkinter.ttk',
        'tkinter.filedialog', 'tkinter.messagebox',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'PIL', 'scipy', 'pandas'],
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
    name='tearyu-datamorph',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,      # True = also works as CLI from terminal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
