from setuptools import setup

APP = ['main.py']
DATA_FILES = [('', ['cert.pem', 'config.json', 'cookiejar.json', 'crash_reports.json'])]
OPTIONS = {
    'argv_emulation': False,
    'includes': ['backend'],
    'packages': ['PySimpleGUI.py'],
    'resources': ['.git'],
    'iconfile': None,  # Optional: add an .icns icon
    'plist': {
        'CFBundleName': 'KasgeldApp',
        'CFBundleShortVersionString': 'v5.44.0-dev',
        'CFBundleIdentifier': 'com.camillodejong.kasgeldapp',
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
