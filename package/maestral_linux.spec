# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


from maestral import __version__, __author__


a = Analysis(['../maestral_qt/main.py'],
             binaries=[],
             datas= [
                ('../maestral_qt/resources/tray-icons-svg/*.svg', './tray-icons-svg'),
                ('../maestral_qt/resources/tray-icons-png/*.png', './tray-icons-png'),
                ('../maestral_qt/resources/*.ui', '.'),
                ('../../maestral-dropbox/maestral/resources/*', '.'),
             ],
             hiddenimports=[
                'pkg_resources.py2_warn',
                'keyring.backends.SecretService',
                'keyrings.alt.file',
             ],
             hookspath=['hooks'],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
