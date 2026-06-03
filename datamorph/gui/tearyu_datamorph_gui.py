"""
tearyu-datamorph — Desktop GUI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Author : The Lazy Dragon (怠竜 Tearyū)
GitHub : https://github.com/The-Lazy-Dragon/tearyu-datamorph
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Run standalone:   python tearyu_datamorph_gui.py
Run as CLI:       python tearyu_datamorph_gui.py --cli input.csv output.json
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from __future__ import annotations
import os
import sys
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ── Allow running from the gui/ subfolder OR from project root ────────────────
_here = os.path.dirname(os.path.abspath(__file__))
_src  = os.path.join(_here, "..", "src")
if os.path.isdir(_src):
    sys.path.insert(0, os.path.abspath(_src))

from datamorph import convert, detect_format, DataMorphError   # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
# THEME CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

C = {
    "bg":        "#04080f",
    "bg2":       "#080f1c",
    "bg3":       "#0d1829",
    "bg4":       "#111f36",
    "cyan":      "#00f0ff",
    "cyan_dim":  "#00b8cc",
    "red":       "#ff3a3a",
    "gold":      "#ffc947",
    "white":     "#e8f4f8",
    "muted":     "#4a6a80",
    "border":    "#0d2640",
    "green":     "#28c840",
}

FONT_MONO  = ("Courier New", 10)
FONT_MONO_S= ("Courier New", 9)
FONT_MONO_L= ("Courier New", 11, "bold")
FONT_UI    = ("Segoe UI", 10)
FONT_UI_B  = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_JP    = ("Segoe UI", 9)

FORMATS    = ["csv", "json", "xml"]

SAMPLES = {
    "csv": (
        "id,name,role,nationality,goals,rating\n"
        "1,Iker Gorrotxategi,ST,ESP,18,9.1\n"
        "2,Luca Iannone,SS,ITA,13,8.8\n"
        "3,Luka Modrić,CM,CRO,2,8.5\n"
        "4,Toni Kroos,CM,GER,3,8.3\n"
        "5,Hari Gurung,LM,NEP,4,7.9"
    ),
    "json": (
        '[\n'
        '  {\n'
        '    "colonist": "竜炎 古竜",\n'
        '    "alias": "Ryūen",\n'
        '    "rank": "竜王",\n'
        '    "level": 120,\n'
        '    "stats": { "shooting": 20, "melee": 20 },\n'
        '    "bionics": ["archotech_legs", "archotech_eyes"]\n'
        '  },\n'
        '  {\n'
        '    "colonist": "黒影 滅竜",\n'
        '    "alias": "MiraMetsuryū",\n'
        '    "rank": "Fatalis",\n'
        '    "level": 99,\n'
        '    "stats": { "shooting": 12, "melee": 18 },\n'
        '    "bionics": []\n'
        '  }\n'
        ']'
    ),
    "xml": (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<films>\n'
        '  <film id="1" tier="S">\n'
        '    <title>Train to Busan</title>\n'
        '    <year>2016</year>\n'
        '    <country>South Korea</country>\n'
        '    <score>9.2</score>\n'
        '  </film>\n'
        '  <film id="2" tier="A">\n'
        '    <title>One Cut of the Dead</title>\n'
        '    <year>2017</year>\n'
        '    <country>Japan</country>\n'
        '    <score>8.8</score>\n'
        '  </film>\n'
        '</films>'
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _fmt_size(n: int) -> str:
    if n < 1024:        return f"{n} B"
    if n < 1024 ** 2:   return f"{n/1024:.1f} KB"
    return f"{n/1024**2:.2f} MB"


def _fmt_ext(fmt: str) -> str:
    return {"csv": ".csv", "json": ".json", "xml": ".xml"}.get(fmt, f".{fmt}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class TearYuDataMorph(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tearyū DataMorph")
        self.geometry("1100x720")
        self.minsize(820, 560)
        self.configure(bg=C["bg"])
        self._setup_icon()
        self._build_ui()
        self._bind_shortcuts()
        self._set_status("// ready — paste data, import a file, or load a sample", C["muted"])

    # ── Icon (dragon emoji rendered via canvas) ───────────────────────────────
    def _setup_icon(self):
        try:
            img = tk.PhotoImage(width=32, height=32)
            # Simple pixel icon: neon cyan square
            img.put(C["cyan"], to=(0, 0, 31, 31))
            img.put(C["bg"],   to=(3, 3, 28, 28))
            img.put(C["cyan"], to=(8, 8, 23, 23))
            self.iconphoto(True, img)
        except Exception:
            pass

    # ── TOP BAR ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Title bar
        title_frame = tk.Frame(self, bg=C["bg2"], height=52)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)

        tk.Label(
            title_frame, text="怠竜", font=("Segoe UI", 16, "bold"),
            fg=C["cyan"], bg=C["bg2"]
        ).pack(side="left", padx=(16, 4), pady=10)

        tk.Label(
            title_frame, text="Tearyū DataMorph",
            font=("Segoe UI", 13, "bold"), fg=C["white"], bg=C["bg2"]
        ).pack(side="left", pady=10)

        tk.Label(
            title_frame, text="v1.0.0",
            font=FONT_MONO_S, fg=C["muted"], bg=C["bg2"]
        ).pack(side="left", padx=(8, 0), pady=14)

        tk.Label(
            title_frame,
            text="CSV ↔ JSON ↔ XML  ·  zero dependencies  ·  github.com/The-Lazy-Dragon",
            font=FONT_MONO_S, fg=C["muted"], bg=C["bg2"]
        ).pack(side="right", padx=16, pady=14)

        # ── Separator
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")

        # ── Controls row
        ctrl = tk.Frame(self, bg=C["bg3"], pady=8)
        ctrl.pack(fill="x")

        tk.Label(ctrl, text="FROM", font=FONT_MONO_S, fg=C["muted"], bg=C["bg3"]).pack(side="left", padx=(16, 4))
        self.src_var = tk.StringVar(value="csv")
        src_menu = ttk.Combobox(ctrl, textvariable=self.src_var, values=FORMATS,
                                state="readonly", width=6, font=FONT_MONO)
        src_menu.pack(side="left", padx=(0, 8))

        tk.Label(ctrl, text="⟶", font=("Segoe UI", 14), fg=C["red"], bg=C["bg3"]).pack(side="left", padx=4)

        tk.Label(ctrl, text="TO", font=FONT_MONO_S, fg=C["muted"], bg=C["bg3"]).pack(side="left", padx=(8, 4))
        self.tgt_var = tk.StringVar(value="json")
        tgt_menu = ttk.Combobox(ctrl, textvariable=self.tgt_var, values=FORMATS,
                                state="readonly", width=6, font=FONT_MONO)
        tgt_menu.pack(side="left", padx=(0, 16))

        # Separator
        tk.Frame(ctrl, bg=C["border"], width=1, height=28).pack(side="left", padx=8)

        # Sample buttons
        tk.Label(ctrl, text="SAMPLE:", font=FONT_MONO_S, fg=C["muted"], bg=C["bg3"]).pack(side="left", padx=(8, 4))
        for fmt in FORMATS:
            b = tk.Button(
                ctrl, text=fmt.upper(),
                font=FONT_MONO_S, fg=C["gold"], bg=C["bg4"],
                activebackground=C["bg3"], activeforeground=C["gold"],
                relief="flat", bd=0, padx=8, pady=3, cursor="hand2",
                command=lambda f=fmt: self._load_sample(f)
            )
            b.pack(side="left", padx=2)

        # Right side buttons
        self.btn_convert = tk.Button(
            ctrl, text="  CONVERT  ⟶  ",
            font=("Courier New", 10, "bold"), fg=C["bg"], bg=C["cyan"],
            activebackground=C["cyan_dim"], activeforeground=C["bg"],
            relief="flat", bd=0, padx=12, pady=5, cursor="hand2",
            command=self._run_convert
        )
        self.btn_convert.pack(side="right", padx=16)

        tk.Frame(ctrl, bg=C["border"], width=1, height=28).pack(side="right", padx=4)

        btn_import = tk.Button(
            ctrl, text="IMPORT",
            font=FONT_MONO_S, fg=C["gold"], bg=C["bg4"],
            activebackground=C["bg3"], activeforeground=C["gold"],
            relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
            command=self._import_file
        )
        btn_import.pack(side="right", padx=2)

        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")

        # ── Main pane area
        panes = tk.Frame(self, bg=C["bg"])
        panes.pack(fill="both", expand=True)

        # Input pane
        self._build_pane(panes, side="left", label="INPUT", badge_text="CSV",
                         badge_color=C["gold"], is_input=True)

        # Divider
        tk.Frame(panes, bg=C["border"], width=1).pack(side="left", fill="y")

        # Output pane
        self._build_pane(panes, side="left", label="OUTPUT", badge_text="JSON",
                         badge_color=C["cyan"], is_input=False)

        # ── Status bar
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")
        status_bar = tk.Frame(self, bg=C["bg2"], height=30)
        status_bar.pack(fill="x")
        status_bar.pack_propagate(False)

        self.status_var = tk.StringVar()
        self.status_lbl = tk.Label(
            status_bar, textvariable=self.status_var,
            font=FONT_MONO_S, fg=C["muted"], bg=C["bg2"], anchor="w"
        )
        self.status_lbl.pack(side="left", padx=16, fill="x", expand=True)

        tk.Label(
            status_bar,
            text="怠竜 Tearyū · The Lazy Dragon · github.com/The-Lazy-Dragon/tearyu-datamorph",
            font=FONT_MONO_S, fg=C["border"], bg=C["bg2"]
        ).pack(side="right", padx=16)

        # Style the comboboxes
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox",
            fieldbackground=C["bg4"], background=C["bg3"],
            foreground=C["cyan"], selectbackground=C["bg4"],
            selectforeground=C["cyan"], borderwidth=1,
            relief="flat"
        )
        style.map("TCombobox", fieldbackground=[("readonly", C["bg4"])])

    def _build_pane(self, parent, side, label, badge_text, badge_color, is_input):
        frame = tk.Frame(parent, bg=C["bg"])
        frame.pack(side=side, fill="both", expand=True)

        # Pane header
        header = tk.Frame(frame, bg=C["bg3"], height=32)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text=label, font=FONT_MONO_S,
                 fg=C["muted"], bg=C["bg3"]).pack(side="left", padx=12, pady=6)

        badge = tk.Label(header, text=badge_text, font=FONT_MONO_S,
                         fg=badge_color, bg=C["bg4"], padx=6, pady=1)
        badge.pack(side="right", padx=8, pady=5)

        tk.Frame(frame, bg=C["border"], height=1).pack(fill="x")

        # Textarea
        txt_frame = tk.Frame(frame, bg=C["bg"])
        txt_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(txt_frame, bg=C["bg2"], troughcolor=C["bg3"],
                                 activebackground=C["cyan_dim"], width=8)
        scrollbar.pack(side="right", fill="y")

        txt = tk.Text(
            txt_frame,
            font=FONT_MONO, bg=C["bg"], fg=C["white"],
            insertbackground=C["cyan"], selectbackground=C["bg4"],
            selectforeground=C["cyan"], relief="flat", bd=0,
            wrap="none", undo=True, padx=10, pady=8,
            yscrollcommand=scrollbar.set,
            state="normal" if is_input else "disabled"
        )
        txt.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=txt.yview)

        # Footer
        tk.Frame(frame, bg=C["border"], height=1).pack(fill="x")
        footer = tk.Frame(frame, bg=C["bg3"], height=30)
        footer.pack(fill="x")
        footer.pack_propagate(False)

        stats_var = tk.StringVar(value="0 chars")
        tk.Label(footer, textvariable=stats_var, font=FONT_MONO_S,
                 fg=C["muted"], bg=C["bg3"]).pack(side="left", padx=10, pady=5)

        if is_input:
            btn_clear = tk.Button(
                footer, text="CLEAR",
                font=FONT_MONO_S, fg=C["red"], bg=C["bg3"],
                activebackground=C["bg4"], activeforeground=C["red"],
                relief="flat", bd=0, padx=8, pady=2, cursor="hand2",
                command=self._clear_input
            )
            btn_clear.pack(side="right", padx=6, pady=4)

            self.input_txt   = txt
            self.in_stats    = stats_var
            self.in_badge    = badge
            # Placeholder hint text
            txt.insert("1.0",
                "← Paste your data here, or click IMPORT to load a file\n"
                "   Supports: .csv  .json  .xml\n\n"
                "   Ctrl+Enter  to convert\n"
                "   Ctrl+O      to import file\n"
                "   Ctrl+S      to export output\n"
                "   Ctrl+L      to clear\n"
            )
            txt.config(fg=C["muted"])
            txt.bind("<FocusIn>", self._clear_placeholder)
            txt.bind("<<Modified>>", lambda e: self._update_in_stats())

            # Drag and drop — only works if tkinterdnd2 is installed.
            # Without it, <Drop> is an unknown event type and tkinter crashes.
            # Wrap in try/except so it degrades gracefully — IMPORT still works.
            try:
                txt.bind("<Drop>", self._on_drop)
            except tk.TclError:
                pass  # tkinterdnd2 not available — drag & drop disabled

        else:
            btn_export = tk.Button(
                footer, text="EXPORT FILE",
                font=FONT_MONO_S, fg=C["cyan"], bg=C["bg3"],
                activebackground=C["bg4"], activeforeground=C["cyan"],
                relief="flat", bd=0, padx=8, pady=2, cursor="hand2",
                command=self._export_file
            )
            btn_export.pack(side="right", padx=2, pady=4)

            btn_copy = tk.Button(
                footer, text="COPY",
                font=FONT_MONO_S, fg=C["cyan"], bg=C["bg3"],
                activebackground=C["bg4"], activeforeground=C["cyan"],
                relief="flat", bd=0, padx=8, pady=2, cursor="hand2",
                command=self._copy_output
            )
            btn_copy.pack(side="right", padx=2, pady=4)

            self.output_txt  = txt
            self.out_stats   = stats_var
            self.out_badge   = badge

    # ── SHORTCUTS ─────────────────────────────────────────────────────────────
    def _bind_shortcuts(self):
        self.bind("<Control-Return>", lambda e: self._run_convert())
        self.bind("<Control-o>",      lambda e: self._import_file())
        self.bind("<Control-s>",      lambda e: self._export_file())
        self.bind("<Control-l>",      lambda e: self._clear_input())

    # ── PLACEHOLDER ───────────────────────────────────────────────────────────
    def _clear_placeholder(self, event=None):
        if self.input_txt.cget("fg") == C["muted"]:
            self.input_txt.delete("1.0", "end")
            self.input_txt.config(fg=C["white"])

    # ── STATS ─────────────────────────────────────────────────────────────────
    def _update_in_stats(self):
        try:
            n = len(self.input_txt.get("1.0", "end-1c"))
            self.in_stats.set(f"{n:,} chars")
            self.input_txt.edit_modified(False)
        except Exception:
            pass

    def _update_out_stats(self, text: str):
        self.out_stats.set(f"{len(text):,} chars")

    # ── STATUS ────────────────────────────────────────────────────────────────
    def _set_status(self, msg: str, color: str = None):
        self.status_var.set(msg)
        self.status_lbl.config(fg=color or C["muted"])

    # ── CONVERT ───────────────────────────────────────────────────────────────
    def _run_convert(self):
        raw = self.input_txt.get("1.0", "end-1c")
        if self.input_txt.cget("fg") == C["muted"] or not raw.strip():
            self._set_status("✘  Input is empty — paste data or load a sample", C["red"])
            return

        src = self.src_var.get()
        tgt = self.tgt_var.get()

        self.btn_convert.config(text="  CONVERTING…  ", state="disabled")
        self._set_status("// converting…", C["cyan_dim"])
        self.update_idletasks()

        def _work():
            t0 = time.perf_counter()
            try:
                result = convert(raw, src, tgt)
                ms = (time.perf_counter() - t0) * 1000
                self.after(0, lambda: self._show_result(result, src, tgt, ms))
            except DataMorphError as e:
                self.after(0, lambda: self._show_error(str(e)))
            except Exception as e:
                self.after(0, lambda: self._show_error(f"Unexpected error: {e}"))

        threading.Thread(target=_work, daemon=True).start()

    def _show_result(self, result: str, src: str, tgt: str, ms: float):
        self.output_txt.config(state="normal")
        self.output_txt.delete("1.0", "end")
        self.output_txt.insert("1.0", result)
        self.output_txt.config(state="disabled")
        self._update_out_stats(result)
        self.out_badge.config(text=tgt.upper())
        self.in_badge.config(text=src.upper())
        in_kb  = len(self.input_txt.get("1.0","end-1c")) / 1024
        out_kb = len(result) / 1024
        self._set_status(
            f"✔  Done in {ms:.1f} ms  ·  {in_kb:.1f} KB → {out_kb:.1f} KB  ·  {src.upper()} → {tgt.upper()}",
            C["green"]
        )
        self.btn_convert.config(text="  CONVERT  ⟶  ", state="normal")

    def _show_error(self, msg: str):
        self._set_status(f"✘  {msg}", C["red"])
        self.btn_convert.config(text="  CONVERT  ⟶  ", state="normal")

    # ── IMPORT ────────────────────────────────────────────────────────────────
    def _import_file(self):
        path = filedialog.askopenfilename(
            title="Import file — tearyu-datamorph",
            filetypes=[
                ("Data files", "*.csv *.json *.xml"),
                ("CSV", "*.csv"), ("JSON", "*.json"), ("XML", "*.xml"),
                ("All files", "*.*")
            ]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
        except UnicodeDecodeError:
            try:
                with open(path, "r", encoding="latin-1") as f:
                    data = f.read()
            except Exception as e:
                self._set_status(f"✘  Could not read file: {e}", C["red"])
                return

        # Auto-detect format
        ext = os.path.splitext(path)[-1].lower().lstrip(".")
        if ext in FORMATS:
            self.src_var.set(ext)
            self.in_badge.config(text=ext.upper())
            auto = {"csv": "json", "json": "xml", "xml": "json"}
            self.tgt_var.set(auto[ext])
            self.out_badge.config(text=auto[ext].upper())

        self._clear_placeholder()
        self.input_txt.delete("1.0", "end")
        self.input_txt.insert("1.0", data)
        self.input_txt.config(fg=C["white"])
        self._update_in_stats()

        fname = os.path.basename(path)
        size  = _fmt_size(len(data.encode("utf-8")))
        self._set_status(f"// imported: {fname}  ({size})  — hit CONVERT or Ctrl+Enter", C["gold"])

    def _on_drop(self, event):
        """Handle drag-and-drop if tkinterdnd2 is available."""
        path = event.data.strip().strip("{}")
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = f.read()
                self._clear_placeholder()
                self.input_txt.delete("1.0", "end")
                self.input_txt.insert("1.0", data)
                self.input_txt.config(fg=C["white"])
                ext = os.path.splitext(path)[-1].lower().lstrip(".")
                if ext in FORMATS:
                    self.src_var.set(ext)
                self._set_status(f"// dropped: {os.path.basename(path)}", C["gold"])
            except Exception as e:
                self._set_status(f"✘  Drop failed: {e}", C["red"])

    # ── EXPORT ────────────────────────────────────────────────────────────────
    def _export_file(self):
        self.output_txt.config(state="normal")
        data = self.output_txt.get("1.0", "end-1c")
        self.output_txt.config(state="disabled")

        if not data.strip():
            self._set_status("✘  Nothing to export — convert something first", C["red"])
            return

        tgt = self.tgt_var.get()
        path = filedialog.asksaveasfilename(
            title="Export output — tearyu-datamorph",
            defaultextension=_fmt_ext(tgt),
            initialfile=f"tearyu_output{_fmt_ext(tgt)}",
            filetypes=[
                ("CSV", "*.csv"), ("JSON", "*.json"), ("XML", "*.xml"),
                ("All files", "*.*")
            ]
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)
            fname = os.path.basename(path)
            size  = _fmt_size(len(data.encode("utf-8")))
            self._set_status(f"✔  Exported: {fname}  ({size})", C["green"])
        except Exception as e:
            self._set_status(f"✘  Export failed: {e}", C["red"])

    # ── COPY ─────────────────────────────────────────────────────────────────
    def _copy_output(self):
        self.output_txt.config(state="normal")
        data = self.output_txt.get("1.0", "end-1c")
        self.output_txt.config(state="disabled")
        if not data.strip():
            self._set_status("✘  Nothing to copy", C["red"])
            return
        self.clipboard_clear()
        self.clipboard_append(data)
        self._set_status("✔  Copied to clipboard", C["green"])

    # ── CLEAR ─────────────────────────────────────────────────────────────────
    def _clear_input(self):
        self.input_txt.delete("1.0", "end")
        self.input_txt.config(fg=C["white"])
        self.output_txt.config(state="normal")
        self.output_txt.delete("1.0", "end")
        self.output_txt.config(state="disabled")
        self._update_in_stats()
        self._update_out_stats("")
        self._set_status("// cleared — ready", C["muted"])

    # ── SAMPLE ────────────────────────────────────────────────────────────────
    def _load_sample(self, fmt: str):
        auto = {"csv": "json", "json": "xml", "xml": "json"}
        self.src_var.set(fmt)
        self.tgt_var.set(auto[fmt])
        self.in_badge.config(text=fmt.upper())
        self.out_badge.config(text=auto[fmt].upper())
        self._clear_placeholder()
        self.input_txt.delete("1.0", "end")
        self.input_txt.insert("1.0", SAMPLES[fmt])
        self.input_txt.config(fg=C["white"])
        self._update_in_stats()
        self.output_txt.config(state="normal")
        self.output_txt.delete("1.0", "end")
        self.output_txt.config(state="disabled")
        self._set_status(f"// sample loaded: {fmt.upper()} — hit CONVERT or Ctrl+Enter", C["gold"])


# ─────────────────────────────────────────────────────────────────────────────
# CLI PASSTHROUGH
# ─────────────────────────────────────────────────────────────────────────────

def _cli_mode(argv):
    """
    Minimal CLI passthrough when --cli flag is present or when
    called with file arguments from terminal.
    Full CLI: use src/tearyu_datamorph.py directly.
    """
    import argparse
    parser = argparse.ArgumentParser(
        prog="datamorph",
        description="datamorph — CSV/TSV/JSON/NDJSON/XML/YAML/TOML/XLSX/HTML converter"
    )
    parser.add_argument("input",  help="Input file path")
    parser.add_argument("output", help="Output file path")
    parser.add_argument("--from", dest="src", choices=FORMATS,
                        help="Force source format")
    parser.add_argument("--to",   dest="tgt", choices=FORMATS,
                        help="Force target format")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    if not os.path.isfile(args.input):
        print(f"  ✘ File not found: {args.input}", file=sys.stderr)
        sys.exit(2)

    with open(args.input, "r", encoding="utf-8") as f:
        data = f.read()

    src = args.src or detect_format(args.input)
    tgt = args.tgt or detect_format(args.output)

    t0 = time.perf_counter()
    try:
        result = convert(data, src, tgt)
    except DataMorphError as e:
        print(f"  ✘ {e}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(result)

    if args.verbose:
        ms = (time.perf_counter() - t0) * 1000
        print(f"  ✔ {src.upper()} → {tgt.upper()}  "
              f"in {ms:.1f} ms  "
              f"({_fmt_size(len(data.encode()))} → {_fmt_size(len(result.encode()))})",
              file=sys.stderr)


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # If called with file args or --cli, run CLI mode (no GUI)
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-h"):
        # Looks like a CLI call: tearyu-datamorph input.csv output.json
        if len(sys.argv) >= 3 and not sys.argv[1].startswith("--"):
            _cli_mode(sys.argv[1:])
            return

    # Otherwise launch GUI
    app = TearYuDataMorph()
    app.mainloop()


if __name__ == "__main__":
    main()
