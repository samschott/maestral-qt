from setuptools import setup, find_packages
from maestral_qt import __author__, __version__


setup(
    name='maestral-qt',
    version=__version__,
    description='A Qt GUI for the Maestral daemon',
    url='https://github.com/SamSchott/maestral',
    author=__author__,
    author_email='ss2151@cam.ac.uk',
    license='MIT',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    package_data={
        'maestral_qt': [
            'resources/*.ui',
            'resources/*.icns',
            'resources/*.png',
            'resources/*.svg',
            'resources/*.desktop',
            'resources/*/*.svg',
            'resources/*/*.png',
            ],
        },
    setup_requires=['wheel'],
    install_requires=[
        'bugsnag',
        'click>=7.1.1',
        'maestral==0.6.3',
        'markdown2',
        'PyQt5>=5.9',
    ],
    zip_safe=False,
    entry_points={
      'console_scripts': ['maestral_qt=maestral_qt.main:run'],
    },
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
    data_files=[
        ('share/icons/hicolor/scalable/status', [
            'maestral_qt/resources/tray-icons-gnome/maestral-icon-disconnected-symbolic.svg',
            'maestral_qt/resources/tray-icons-gnome/maestral-icon-error-symbolic.svg',
            'maestral_qt/resources/tray-icons-gnome/maestral-icon-idle-symbolic.svg',
            'maestral_qt/resources/tray-icons-gnome/maestral-icon-info-symbolic.svg',
            'maestral_qt/resources/tray-icons-gnome/maestral-icon-paused-symbolic.svg',
            'maestral_qt/resources/tray-icons-gnome/maestral-icon-syncing-symbolic.svg',
        ]),
        ('share/applications', ['maestral_qt/resources/maestral.desktop']),
    ],
)
