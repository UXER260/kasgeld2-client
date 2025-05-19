# Created by camillodejong at 16/05/2025 18:22
from setuptools import setup

APP = ['main.py']
DATA_FILES = ['config.json', 'cookiejar.json']  # Add any other needed files
OPTIONS = {
    'argv_emulation': False,
    'includes': [],
    'packages': [],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
