"""
gui/app.py
─────────────────────────────────────────────────────────────────────────────
tearyu-datamorph — Desktop GUI
Author : The Lazy Dragon (怠竜 Tearyū)
GitHub : https://github.com/The-Lazy-Dragon/tearyu-datamorph
─────────────────────────────────────────────────────────────────────────────
Launches the HTML converter in a native desktop window via pywebview.
Exposes a Python bridge so JS can call native file open/save dialogs.
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import os
import sys
import threading

# ── Path setup (works both dev and PyInstaller onefile) ─────────────────────
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add src/ to path so we can import the converter
SRC_DIR = os.path.join(os.path.dirname(BASE_DIR), 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from converter import convert, DataMorphError  # noqa: E402

import webview  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# PYTHON ↔ JS BRIDGE
# ─────────────────────────────────────────────────────────────────────────────

class DataMorphAPI:
    """
    Methods exposed to JavaScript via window.pywebview.api.*
    All methods must be synchronous and return JSON-serialisable values.
    """

    def __init__(self, window_ref: list):
        self._win = window_ref  # mutable reference — set after window created

    @property
    def win(self) -> webview.Window:
        return self._win[0]

    # ── File I/O ──────────────────────────────────────────────────────────────

    def open_file(self) -> dict:
        """
        Open a native file picker.
        Returns { ok: bool, content: str, filename: str, format: str }
        """
        result = self.win.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=('Data Files (*.csv;*.json;*.xml)', 'All Files (*.*)'),
        )
        if not result:
            return {'ok': False}

        path = result[0]
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                content = fh.read()
        except UnicodeDecodeError:
            try:
                with open(path, 'r', encoding='latin-1') as fh:
                    content = fh.read()
            except Exception as exc:
                return {'ok': False, 'error': str(exc)}
        except Exception as exc:
            return {'ok': False, 'error': str(exc)}

        ext = os.path.splitext(path)[-1].lower().lstrip('.')
        fmt = ext if ext in ('csv', 'json', 'xml') else 'unknown'
        return {
            'ok':       True,
            'content':  content,
            'filename': os.path.basename(path),
            'format':   fmt,
            'size':     len(content),
        }

    def save_file(self, content: str, suggested_fmt: str) -> dict:
        """
        Open a native save dialog.
        Returns { ok: bool, path: str }
        """
        ext_map = {
            'csv':  ('CSV Files (*.csv)', 'output.csv'),
            'json': ('JSON Files (*.json)', 'output.json'),
            'xml':  ('XML Files (*.xml)', 'output.xml'),
        }
        file_types, default_name = ext_map.get(suggested_fmt, ('All Files (*.*)', 'output.txt'))

        result = self.win.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename=default_name,
            file_types=(file_types, 'All Files (*.*)'),
        )
        if not result:
            return {'ok': False}

        path = result if isinstance(result, str) else result[0]
        try:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(content)
            return {'ok': True, 'path': path, 'filename': os.path.basename(path)}
        except Exception as exc:
            return {'ok': False, 'error': str(exc)}

    # ── Conversion (runs in Python, not JS) ───────────────────────────────────

    def convert(self, data: str, src: str, tgt: str) -> dict:
        """
        Run the Python converter directly.
        Returns { ok: bool, result: str } or { ok: false, error: str }
        """
        try:
            result = convert(data, src, tgt)
            return {'ok': True, 'result': result}
        except DataMorphError as exc:
            return {'ok': False, 'error': str(exc)}
        except Exception as exc:
            return {'ok': False, 'error': f'Unexpected error: {exc}'}

    # ── App info ──────────────────────────────────────────────────────────────

    def get_version(self) -> str:
        return '1.0.0'

    def get_platform(self) -> str:
        return sys.platform


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    html_path = os.path.join(BASE_DIR, 'ui', 'index.html')

    if not os.path.isfile(html_path):
        # Fallback: look relative to script location
        html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'index.html')

    if not os.path.isfile(html_path):
        print(f"[ERROR] Cannot find ui/index.html at: {html_path}", file=sys.stderr)
        sys.exit(1)

    window_ref: list = [None]
    api = DataMorphAPI(window_ref)

    window = webview.create_window(
        title        = 'tearyu-datamorph  ·  怠竜 Tearyū',
        url          = f'file:///{html_path.replace(os.sep, "/")}',
        js_api       = api,
        width        = 1280,
        height       = 820,
        min_size     = (900, 600),
        resizable    = True,
        text_select  = True,
        background_color = '#04080f',
    )
    window_ref[0] = window

    webview.start(debug=False)


if __name__ == '__main__':
    main()
