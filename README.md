<div align="center">

```
  ____        _        __  __                  _
 |  _ \  __ _| |_ __ _|  \/  | ___  _ __ _ __ | |__
 | | | |/ _` | __/ _` | |\/| |/ _ \| '__| '_ \| '_ \
 | |_| | (_| | || (_| | |  | | (_) | |  | |_) | | | |
 |____/ \__,_|\__\__,_|_|  |_|\___/|_|  | .__/|_| |_|
                                         |_|
```

**Convert between CSV, TSV, JSON, NDJSON, XML, YAML, TOML, Excel, and HTML tables — desktop app, CLI, and web.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-0a1628?style=flat-square&logo=python&logoColor=00f0ff)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-0a1628?style=flat-square&logo=opensourceinitiative&logoColor=00f0ff)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-91%20Passing-0a1628?style=flat-square&logo=pytest&logoColor=00f0ff)]()
[![Formats](https://img.shields.io/badge/Formats-9-0a1628?style=flat-square&logoColor=00f0ff)]()
[![By The Lazy Dragon](https://img.shields.io/badge/怠竜-Teary%C5%AB-0a1628?style=flat-square&logoColor=ff3a3a)](https://github.com/The-Lazy-Dragon)

*怠竜 Tearyū / The Lazy Dragon — [`github.com/The-Lazy-Dragon`](https://github.com/The-Lazy-Dragon)*

</div>

---

## 📖 What is tearyu-datamorph?

**tearyu-datamorph** is a data format converter that comes in three forms — pick whichever fits how you work:

| Mode | What it is | Who it's for |
|------|-----------|-------------|
| 🖥️ **Desktop App** | GUI with split panes, import/export | Anyone — no terminal needed |
| ⌨️ **CLI** | Terminal command, pipes, scripting | Developers and power users |
| 🌐 **Web** | Live converter in the browser | Quick conversions, no install |

All three share the same engine. Same results, different interface.

> 🔧 **Full technical docs** → [INSTRUCTIONS.md](INSTRUCTIONS.md)

---

## 🗺️ Conversion Map

### Text formats — fully bidirectional

```
CSV  ◄──►  TSV       CSV  ◄──►  JSON      CSV  ◄──►  NDJSON
CSV  ◄──►  XML       CSV  ◄──►  YAML      CSV  ◄──►  TOML
TSV  ◄──►  JSON      TSV  ◄──►  XML       TSV  ◄──►  YAML
JSON ◄──►  XML       JSON ◄──►  YAML      JSON ◄──►  TOML
JSON ◄──►  NDJSON    XML  ◄──►  YAML      YAML ◄──►  TOML
```

### Source-only formats (read in, convert to any text format)

| Source | → CSV | → TSV | → JSON | → NDJSON | → XML | → YAML | → TOML |
|--------|:-----:|:-----:|:------:|:--------:|:-----:|:------:|:------:|
| **XLSX** (Excel) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **HTML** table | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

> XLSX and HTML are **read-only sources** — tearyu-datamorph reads them and converts to any text format. Writing back to Excel or HTML is not supported.

---

## 🖥️ Desktop App (Recommended)

The desktop app is the main way to use tearyu-datamorph. No Python required — just download and run.

> ⚠️ **Important:** The prebuilt binary in `dist/` was compiled on **Linux**. Windows and Mac users need to build it once or run from source — both are covered below.

---

### 🪟 Windows

**Option A — Build the .exe yourself** *(one-time setup)*

1. Install Python 3.10+ from [python.org](https://www.python.org/downloads/) — tick **"Add Python to PATH"** during install
2. Download or clone this repo
3. Open **Command Prompt** or **PowerShell** in the project folder
4. Run:

```cmd
pip install pyinstaller pyyaml openpyxl
python build.py
```

5. Find your `.exe` at `dist\tearyu-datamorph.exe` — double-click to launch

**Option B — Run from source** *(no build step)*

```cmd
pip install pyyaml openpyxl
python gui\tearyu_datamorph_gui.py
```

---

### 🍎 Mac

**Option A — Build the binary yourself**

```bash
brew install python   # or download from python.org

git clone https://github.com/The-Lazy-Dragon/tearyu-datamorph.git
cd tearyu-datamorph
pip3 install pyinstaller pyyaml openpyxl
python3 build.py
# Output: dist/tearyu-datamorph
```

> First run may show a security warning. Go to **System Settings → Privacy & Security → Open Anyway**.

**Option B — Run from source**

```bash
pip3 install pyyaml openpyxl
python3 gui/tearyu_datamorph_gui.py
```

---

### 🐧 Linux

The prebuilt binary in `dist/` was built on Linux — try it first:

```bash
chmod +x dist/tearyu-datamorph
./dist/tearyu-datamorph
```

If it doesn't run (wrong distro/arch):

```bash
pip3 install pyinstaller pyyaml openpyxl
python3 build.py
./dist/tearyu-datamorph
```

Or run from source:

```bash
pip3 install pyyaml openpyxl
python3 gui/tearyu_datamorph_gui.py
```

---

### ❓ Just want it to work on any OS

```bash
# 1. Install Python 3.10+ from https://www.python.org/downloads/
# 2. Extract this repo
# 3. Open terminal in the tearyu-datamorph folder
pip install pyyaml openpyxl
python gui/tearyu_datamorph_gui.py    # Mac/Linux
python gui\tearyu_datamorph_gui.py   # Windows
```

---

### Using the GUI

```
┌─────────────────────────────────────────────────────────────────┐
│  怠竜  Tearyū DataMorph  v1.1.0                                  │
├──────────────────────────────────────────────────────────────────│
│  FROM [csv ▼]  ⟶  TO [json ▼]  │ SAMPLE: CSV JSON XML │ CONVERT │
├───────────────────────┬──────────────────────────────────────────│
│  INPUT           CSV  │  OUTPUT                           JSON   │
│                       │                                          │
│  ← paste or IMPORT    │  converted output appears here           │
│                       │                                          │
├───────────────────────┴──────────────────────────────────────────│
│  // status bar                                                   │
└──────────────────────────────────────────────────────────────────┘
```

1. Paste data or click **IMPORT** to load a file
2. Set FROM and TO formats (auto-detected from extension on import)
3. Hit **CONVERT**
4. **EXPORT FILE** to save, or **COPY** to clipboard

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` | Convert |
| `Ctrl+O` | Import file |
| `Ctrl+S` | Export output |
| `Ctrl+L` | Clear |

> **Note:** XLSX and HTML imports work via CLI only right now. GUI support coming in v1.2.0.

---

## 🌐 Web Version

**[https://the-lazy-dragon.github.io/tearyu-datamorph](https://the-lazy-dragon.github.io/tearyu-datamorph)**

Full converter in the browser. No install, no data leaves your machine. Import/export buttons included.

> Web version currently supports CSV, JSON, XML (the original six paths). YAML/TOML/TSV/NDJSON/XLSX/HTML coming in the next web update.

---

## ⌨️ CLI

The binary doubles as a CLI when called with file arguments. Same binary, two modes.

```bash
# All text format conversions
python src/datamorph_cli.py data.csv       output.json
python src/datamorph_cli.py data.json      output.yaml
python src/datamorph_cli.py data.yaml      output.toml
python src/datamorph_cli.py data.tsv       output.xml
python src/datamorph_cli.py data.ndjson    output.csv

# Excel — source only
python src/datamorph_cli.py report.xlsx    output.json
python src/datamorph_cli.py report.xlsx    output.csv
python src/datamorph_cli.py report.xlsx    output.yaml

# HTML table — source only (works with Excel "Save as HTML" exports!)
python src/datamorph_cli.py table.html     output.csv
python src/datamorph_cli.py table.html     output.json

# Force formats manually
datamorph data.txt out.txt --from csv --to yaml

# Verbose
datamorph large.json out.csv --verbose
#   → JSON  ⟶  CSV
#   ✔ Done in 8.2 ms  |  42 KB → 31 KB

# Pipe via stdin/stdout
cat data.csv | python src/datamorph_cli.py --from csv --to json > out.json
```

**CLI flags:**

| Flag | Description |
|------|-------------|
| `--from FORMAT` | Force source format |
| `--to FORMAT` | Force target format |
| `-v` / `--verbose` | Show timing and size stats |
| `--no-banner` | Hide the ASCII art |
| `--version` | Print version |
| `--help` | Show help |

**Supported FORMAT values:** `csv` `tsv` `json` `ndjson` `xml` `yaml` `toml` `xlsx` `html`

---

## 📐 What Gets Handled

### CSV / TSV
| Feature | |
|---------|--|
| First row as headers | ✅ |
| Quoted fields with commas or newlines | ✅ |
| Empty fields preserved | ✅ |
| UTF-8 and multibyte characters | ✅ |
| BOM prefix from Excel exports | ✅ stripped |
| Tab delimiter (TSV) | ✅ |

### JSON / NDJSON
| Feature | |
|---------|--|
| Arrays of objects | ✅ |
| Nested objects and arrays | ✅ |
| `null` → empty string | ✅ |
| Unicode (ensure_ascii=False) | ✅ |
| Pretty-printed output | ✅ 2-space indent |
| Newline-delimited (`.ndjson`, `.jsonl`) | ✅ |

### XML
| Feature | |
|---------|--|
| Element attributes → `@attributes` | ✅ |
| Nested elements | ✅ |
| Repeated tags → array | ✅ |
| Special char escaping | ✅ |
| Tag sanitization | ✅ |
| Pretty-printed output | ✅ |

### YAML
| Feature | |
|---------|--|
| Lists and mappings | ✅ |
| Nested structures | ✅ |
| Unicode preserved | ✅ |
| Output: block style, allow_unicode | ✅ |
| Requires `pyyaml` | ✅ |

### TOML
| Feature | |
|---------|--|
| Key/value tables | ✅ |
| Array of tables (`[[records]]`) | ✅ |
| Output as `[[records]]` blocks | ✅ |
| Stdlib `tomllib` (Python 3.11+) | ✅ no install |

### Excel (.xlsx) — source only
| Feature | |
|---------|--|
| Reads first sheet by default | ✅ |
| Specify sheet by name or index | ✅ |
| Empty cells → `""` | ✅ |
| Duplicate/blank headers deduplicated | ✅ |
| Requires `openpyxl` | ✅ |

### HTML table — source only
| Feature | |
|---------|--|
| Extracts first `<table>` by default | ✅ |
| `<th>` or `<td>` first row as headers | ✅ |
| Excel "Save as HTML" exports | ✅ |
| Webpage copy-paste tables | ✅ |
| UTF-8 and HTML entities decoded | ✅ |
| No external dependencies | ✅ stdlib only |

---

## ⚠️ Limitations

| Limitation | Detail |
|-----------|--------|
| All CSV/TSV values are strings | No type system — `42` stays `"42"` |
| Deep nesting flattens in CSV/TSV | `user.address.city` becomes a column header |
| XLSX and HTML are source-only | Can read them, can't write back to Excel or HTML |
| No streaming | Full file loaded into memory — fine up to ~100 MB |
| No schema validation | Format converter only |
| CSV must have a header row | First row always treated as headers |
| TOML output is flat `[[records]]` | Deep nesting becomes dotted keys |
| HTML: first table only by default | Multi-table HTML needs `--table-index` (coming soon) |
| Round-trips are data-safe, not byte-identical | Values survive; key order and whitespace may differ |

---

## 📦 Dependencies

| Package | Required for | Install |
|---------|-------------|---------|
| `pyyaml` | YAML conversions | `pip install pyyaml` |
| `openpyxl` | Excel (.xlsx) reading | `pip install openpyxl` |
| `tomllib` | TOML reading | stdlib (Python 3.11+), or `pip install tomli` |

Everything else is Python stdlib — `csv`, `json`, `xml`, `html.parser`, `re`, `io`.

---

## 📁 Project Structure

```
tearyu-datamorph/
├── dist/
│   └── tearyu-datamorph(.exe)  ← Prebuilt binary — run this
├── gui/
│   └── tearyu_datamorph_gui.py ← Desktop app source (tkinter)
├── src/
│   ├── datamorph.py            ← Core conversion engine (9 formats)
│   ├── datamorph_cli.py        ← CLI entry point  (command: datamorph)
│   └── __init__.py             ← Python API exports
├── docs/
│   └── index.html              ← Web version (GitHub Pages)
├── tests/
│   └── test_datamorph.py       ← 91 tests, all passing
├── examples/
│   ├── squad.csv               ← Sample CSV
│   ├── colonists.json          ← Sample JSON (nested + arrays)
│   └── films.xml               ← Sample XML (with attributes)
├── build.py                    ← Builds the .exe
├── tearyu-datamorph.spec       ← PyInstaller config
├── INSTRUCTIONS.md             ← Full technical reference
├── setup.py                    ← pip install support
├── requirements.txt            ← Runtime + dev deps
├── LICENSE                     ← MIT
└── README.md                   ← You are here
```

---

## 🧪 Tests

```bash
pip install pytest pyyaml openpyxl
python -m pytest tests/ -v
# 91 passed
```

---

## 📋 Changelog

### v1.1.0
- ➕ Added **TSV** (Tab-Separated Values) — bidirectional with all formats
- ➕ Added **NDJSON** (Newline-Delimited JSON / `.jsonl`) — bidirectional
- ➕ Added **YAML** — bidirectional with all formats (requires `pyyaml`)
- ➕ Added **TOML** — bidirectional with all formats (stdlib `tomllib`)
- ➕ Added **Excel (.xlsx)** — source-only, reads any sheet, converts to all text formats (requires `openpyxl`)
- ➕ Added **HTML table extraction** — source-only, extracts `<table>` tags including Excel "Save as HTML" exports
- 🔧 Fixed GUI crash on Windows/Mac (`<Drop>` TclError without `tkinterdnd2`)
- 🔧 Updated CLI format detection and auto-routing for all new formats
- 📈 Test suite expanded from 56 → 91 tests

### v1.0.0
- 🎉 Initial release
- ➕ CSV, JSON, XML — all six bidirectional paths
- ➕ Desktop GUI (tkinter) with import/export
- ➕ CLI with stdin/stdout piping
- ➕ Web version (GitHub Pages)
- ➕ PyInstaller `.exe` build pipeline

---

## 🗺️ Roadmap

- [ ] XLSX/HTML support in GUI dropdowns
- [ ] YAML/TOML/TSV/NDJSON in web version
- [ ] Multi-table HTML (`--table-index` flag)
- [ ] Batch conversion (whole folder at once)
- [ ] Syntax highlighting in GUI panes
- [ ] Column filtering before export
- [ ] Drag & drop via `tkinterdnd2`

---

## 🔗 tearyu Ecosystem

Part of the **怠竜 Tearyū** project family.

| Project | What it is |
|---------|-----------|
| **[tearyu-datamorph](https://github.com/The-Lazy-Dragon/tearyu-datamorph)** | ← You are here — desktop app + CLI + web converter |
| **[tearyu-datashift](https://github.com/The-Lazy-Dragon/tearyu-datashift)** | Claude Code skill edition — single file, type inference, drops into `~/.claude/skills/` |
| **[tearyu-humanizer](https://github.com/The-Lazy-Dragon/tearyu-humanizer)** | Claude Code skill — strips AI texture from writing |

> **tearyu-datashift** is the sibling repo — same conversion engine, rebuilt as a Claude Code skill. If you want Claude Code to handle your file conversions automatically, that's the one.

---

## 🤝 Contributing

Open an issue first for major changes. PRs welcome.

```bash
git clone https://github.com/The-Lazy-Dragon/tearyu-datamorph.git
cd tearyu-datamorph
pip install -e ".[dev]"
python -m pytest tests/ -v
```

---

## 📄 License

MIT © [The Lazy Dragon (怠竜 Tearyū)](https://github.com/The-Lazy-Dragon)

---

<div align="center">

*Built by The Lazy Dragon — 🇳🇵*
*怠竜 Tearyū · github.com/The-Lazy-Dragon*

</div>
