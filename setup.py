# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name="maestral-qt",
    author="Sam Schott",
    author_email="ss2151@cam.ac.uk",
    version="v1.2.1.dev0",
    description="A Qt GUI for the Maestral daemon",
    url="https://github.com/SamSchott/maestral",
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
        "bugsnag>=3.4.0",
        "click>=7.1.1",
        "maestral>=1.2.0",
        "markdown2",
        "packaging",
        "PyQt5>=5.9",
    ],
    zip_safe=False,
    entry_points={
        "console_scripts": ["maestral_qt=maestral_qt.cli:main"],
        "maestral_gui": ["maestral_qt=maestral_qt.main:run"],
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ],
    data_files=[("share/applications", ["maestral_qt/resources/maestral.desktop"])],
)
