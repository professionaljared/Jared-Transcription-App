# jta_main.spec
block_cipher = None

a = Analysis(
    ['jta_main_optimized.py'],
    pathex=['/path/to/your/project'],
    binaries=[],
    datas=[
        ('model', 'model'),  # Include the Vosk model folder
        ('ffmpeg/macos/ffmpeg', './ffmpeg')  # Include ffmpeg for macOS
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='JTA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False to hide the console window
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='JTA'
)
