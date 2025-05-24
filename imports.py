# client/imports.py
# gemene dependencies
from __future__ import annotations

from local_deps import PySimpleGUI as pysg
import json
import os
import sys

DEFAULT_CONFIG = """{
  "request_url": "http://localhost:8000/",
  "cookiejar_location": "cookiejar.json",
  "window_size": [1000, 600],
  "window_edge_margin": [15, 15],
  "theme": "SystemDefaultForReal",
  "font": ["Helvetica", 35],
  "item_separation": ["-", 80],
  "catch_handled_http_exceptions": true,
  "catch_connectivity_error_exceptions": true,
  "use_global_exception_handler": true
}"""


def resource_path(relative_path):  # belangrijk voor wanneer ge-compiled als executable of app.
    """ Get the absolute path to a resource, works for development and for PyInstaller packaged builds """
    if hasattr(sys, '_MEIPASS'):
        # If the script is bundled, _MEIPASS is set by PyInstaller to point to the temporary folder
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def load_config(path="config.json", fallback_restore: str | dict = "{}", except_decode_error=False):
    print(path)

    try:
        with open(path) as f:
            conf = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        if not except_decode_error and e.__class__ is json.JSONDecodeError:
            raise ValueError(f"Could not decode {path}")
        print(f"{e.__class__ is json.JSONDecodeError}\nRestoring {path}")

        # maakt nieuwe configfile aan als het niet te vinden is
        with open(path, "w") as f:
            json.dump(fallback_restore, f, indent=2) if type(fallback_restore) is dict else f.write(fallback_restore)
        conf = fallback_restore if type(fallback_restore) is dict else json.loads(fallback_restore)

    print(f"Config at `{path}` loaded.")
    return conf

config = load_config(fallback_restore=DEFAULT_CONFIG, except_decode_error=True)
