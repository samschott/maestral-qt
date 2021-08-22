# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name="maestral-qt",
    author="Sam Schott",
    author_email="sam.schott@outlook.com",
    version="1.4.8.post0",
    description="A Qt GUI for the Maestral daemon",
    url="https://maestral.app",
    license="MIT",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={
        "maestral_qt": [
            "resources/*.ui",
            "resources/*.icns",
            "resources/*.png",
            "resources/*.svg",
            "resources/*.desktop",
        ],
    },
    python_requires=">=3.6",
    setup_requires=["wheel"],
    install_requires=[
        "click>=7.1.1",
        "importlib_resources;python_version<'3.9'",
        "maestral>=1.4.8",
        "markdown2",
        "packaging",
        "PyQt5>=5.9",
    ],
    zip_safe=False,
    entry_points={
        "console_scripts": ["maestral_qt=maestral_qt.__main__:main"],
        "maestral_gui": ["maestral_qt=maestral_qt.main:run"],
        "pyinstaller40": ["hook-dirs=maestral_qt.__pyinstaller:get_hook_dirs"],
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    data_files=[("share/applications", ["maestral_qt/resources/maestral.desktop"])],
)
