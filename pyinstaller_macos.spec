# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


import time
from maestral import __version__, __author__


with open('bundle_version.txt', 'r') as f:
    bundle_version = str(int(f.read()) + 1)

with open('bundle_version.txt', 'w') as f:
    f.write(bundle_version)


a = Analysis(['maestral_qt/main.py'],
             binaries=[],
             datas= [
                ('maestral_qt/resources/tray-icons-svg/*.svg', './tray-icons-svg'),
                ('maestral_qt/resources/maestral.png', '.'),
                ('maestral_qt/resources/faceholder.png', '.'),
                ('maestral_qt/resources/*.ui', '.'),
                ('../maestral-dropbox/maestral/resources/*', '.'),
             ],
             hiddenimports=['pkg_resources.py2_warn', 'keyring.backends.OS_X',],
             hookspath=[],
             runtime_hooks=[],
             excludes=['_tkinter'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
app = BUNDLE(coll,
             name='Maestral.app',
             icon='maestral_qt/resources/maestral.icns',
             bundle_identifier='com.samschott.maestral',
             info_plist={
                'NSHighResolutionCapable': 'True',
                'NSRequiresAquaSystemAppearance': 'False',
                'LSUIElement': '1',
                'CFBundleVersion': bundle_version,
                'CFBundleShortVersionString': __version__,
                'NSHumanReadableCopyright': 'Copyright © {} {}. All rights reserved.'.format(time.strftime('%Y'), __author__),
                'LSMinimumSystemVersion': '10.13.0',
                },
)
