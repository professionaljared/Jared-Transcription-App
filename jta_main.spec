# jta_main.spec

block_cipher = None

a = Analysis(
    ['jta_main.py'],
    pathex=['/Users/joeroberts/Documents/MarcyLabWorld/environment/Converter App'],
    binaries=[],
    datas=[
        ('/Users/joeroberts/Documents/MarcyLabWorld/environment/Converter App/venv310/lib/python3.10/site-packages/vosk', 'vosk'),
        ('/Users/joeroberts/Documents/MarcyLabWorld/environment/Converter App/model', 'model'),
        ('/Users/joeroberts/Documents/MarcyLabWorld/environment/Converter App/ffmpeg', 'ffmpeg'),
    ],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='jta_main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=None,  # Specify an icon if needed, or leave as None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='jta_main',
)
