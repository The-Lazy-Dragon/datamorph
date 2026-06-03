<div align="center">

```
  ____        _        __  __                  _
 |  _ \  __ _| |_ __ _|  \/  | ___  _ __ _ __ | |__
 | | | |/ _` | __/ _` | |\/| |/ _ \| '__| '_ \| '_ \
 | |_| | (_| | || (_| | |  | | (_) | |  | |_) | | | |
 |____/ \__,_|\__\__,_|_|  |_|\___/|_|  | .__/|_| |_|
                                         |_|
```

# INSTRUCTIONS.md
### Full Technical Reference

*怠竜 Tearyū / The Lazy Dragon — [`github.com/The-Lazy-Dragon`](https://github.com/The-Lazy-Dragon)*

</div>

---

## Table of Contents

1. [Installation & Getting the App](#1-installation--getting-the-app)
2. [Desktop App — Full Reference](#2-desktop-app--full-reference)
3. [Web Version — Full Reference](#3-web-version--full-reference)
4. [CLI — Full Reference](#4-cli--full-reference)
5. [Python API — Full Reference](#5-python-api--full-reference)
6. [Format Behaviour In Depth](#6-format-behaviour-in-depth)
7. [How Nested Data Is Handled](#7-how-nested-data-is-handled)
8. [Error Handling](#8-error-handling)
9. [Limitations](#9-limitations)
10. [Building the .exe Yourself](#10-building-the-exe-yourself)
11. [Running the Test Suite](#11-running-the-test-suite)
12. [Extending datamorph](#12-extending-datamorph)

---

## 1. Installation & Getting the App

datamorph works on Windows, Mac, and Linux. Pick the method that fits your setup.

> ⚠️ **The prebuilt binary in `dist/` was compiled on Linux.** Windows and Mac users need to either build it (2 minutes) or run from source. Both are covered below.

---

### 🪟 Windows

**Option A — Build the .exe yourself** *(recommended — one-time setup)*

1. Install Python 3.10+ from [python.org](https://www.python.org/downloads/)
   - During install, tick **"Add Python to PATH"** — important
2. Download or clone this repo
3. Open **Command Prompt** or **PowerShell** inside the project folder
4. Run:

```cmd
pip install pyinstaller
python build.py
```

5. Your `.exe` is now at `dist	earyu-datamorph.exe` — double-click to launch the GUI

**Option B — Run from source** *(no build step needed)*

```cmd
python gui	earyu_datamorph_gui.py
```

**Option C — CLI only via pip**

```cmd
pip install -e .
datamorph input.csv output.json
```

---

### 🍎 Mac

**Option A — Build the binary yourself**

```bash
# Install Python if needed — either from python.org or via Homebrew
brew install python

git clone https://github.com/The-Lazy-Dragon/tearyu-datamorph.git
cd tearyu-datamorph
pip3 install pyinstaller
python3 build.py
```

Your binary is at `dist/tearyu-datamorph`. Run it:

```bash
./dist/tearyu-datamorph        # GUI
./dist/tearyu-datamorph input.csv output.json   # CLI
```

> **Mac security warning:** First run may show *"datamorph cannot be opened because it is from an unidentified developer"*. Go to **System Settings → Privacy & Security → scroll down → Open Anyway**. Only happens once.

**Option B — Run from source**

```bash
python3 gui/tearyu_datamorph_gui.py
```

**Option C — CLI only via pip**

```bash
pip3 install -e .
datamorph input.csv output.json
```

---

### 🐧 Linux

The prebuilt binary in `dist/` was built on Linux — try it first:

```bash
chmod +x dist/tearyu-datamorph
./dist/tearyu-datamorph              # GUI
./dist/tearyu-datamorph data.csv out.json   # CLI
```

If it doesn't run (wrong distro or architecture), build it:

```bash
pip3 install pyinstaller
python3 build.py
./dist/tearyu-datamorph
```

Or run from source directly:

```bash
python3 gui/tearyu_datamorph_gui.py
```

---

### 🌐 Web — No install at all (any OS)

Open `docs/index.html` in any browser. Or visit the GitHub Pages URL:

```
https://the-lazy-dragon.github.io/tearyu-datamorph
```

Full converter in the browser. No Python, no install, no data leaves your machine.

---

### Quick reference table

| OS | Easiest method | Requires |
|----|---------------|----------|
| Windows | `python build.py` → run `.exe` | Python 3.10+, one-time |
| Mac | `python3 build.py` → run binary | Python 3.10+, one-time |
| Linux | `./dist/tearyu-datamorph` | Nothing (prebuilt) |
| Any | `python gui/tearyu_datamorph_gui.py` | Python 3.10+ |
| Any | Open `docs/index.html` | Browser only |

---

## 2. Desktop App — Full Reference

### Launching

```bash
# Prebuilt binary
./dist/tearyu-datamorph          # Tearyū DataMorph GUI opens

# CLI via Python directly
python src/datamorph_cli.py input.csv output.json

# From source (GUI)
python gui/tearyu_datamorph_gui.py
```

The GUI/CLI split happens automatically: pass file arguments → `datamorph` CLI mode. No arguments → **Tearyū DataMorph** GUI opens.

---

### Interface layout

```
┌──────────────────────────────────────────────────────────────────────┐
│  [titlebar]  怠竜  datamorph  v1.0.0                          │
├──────────────────────────────────────────────────────────────────────│
│  [controls]  FROM [csv▼]  ⟶  TO [json▼]  │ SAMPLE: CSV JSON XML     │
│                                           │                 CONVERT  │
├─────────────────────────┬────────────────────────────────────────────│
│  INPUT            [CSV] │  OUTPUT                             [JSON] │
│                         │                                            │
│  (editable textarea)    │  (read-only textarea)                      │
│                         │                                            │
│  0 chars    [IMPORT][CLR│  0 chars              [EXPORT FILE] [COPY] │
├─────────────────────────┴────────────────────────────────────────────│
│  [statusbar]  // ready                    怠竜 Tearyū / github.com   │
└──────────────────────────────────────────────────────────────────────┘
```

---

### Controls reference

**FROM / TO dropdowns**
Select your source and target formats. Options: `csv`, `json`, `xml`. Auto-set on file import based on the file extension.

**SAMPLE buttons (CSV / JSON / XML)**
Loads real example data into the input pane and sets sensible defaults:
- CSV sample → converts to JSON
- JSON sample → converts to XML
- XML sample → converts to JSON

**CONVERT button**
Runs the conversion. Output appears in the right pane instantly. The status bar shows timing, file sizes, and the conversion path.

**IMPORT button (input pane footer)**
Opens a file picker. Accepted: `.csv`, `.json`, `.xml`, `.txt`. On import:
- File contents load into the input textarea
- FROM format auto-detected from extension
- TO format auto-set to a sensible default

**EXPORT FILE button (output pane footer)**
Opens a save-as dialog. Output is saved as a UTF-8 encoded file with the correct extension for the target format.

**COPY button (output pane footer)**
Copies the output to clipboard.

**CLEAR button (input pane footer)**
Clears both panes.

---

### Drag & drop

Drag a `.csv`, `.json`, or `.xml` file from your file manager directly onto the input textarea. Format auto-detects from extension, same as the import button.

> Note: Full native drag & drop requires `tkinterdnd2`. Without it, use the IMPORT button — same result.

---

### Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` | Convert |
| `Ctrl+O` | Import file |
| `Ctrl+S` | Export output |
| `Ctrl+L` | Clear input |

---

### Status bar messages

| Prefix | Meaning |
|--------|---------|
| `✔` green | Success — shows timing and size |
| `✘` red | Error — shows what went wrong |
| `//` muted | Idle / informational |

---

## 3. Web Version — Full Reference

The web version lives in `docs/index.html` and is hosted via GitHub Pages. It runs entirely in the browser — no server, no data sent anywhere.

**Live URL:** `https://the-lazy-dragon.github.io/tearyu-datamorph`

**Run locally:**
```bash
open docs/index.html       # Mac
start docs/index.html      # Windows
xdg-open docs/index.html   # Linux
```

### Features

- Full split-pane editor matching the desktop app
- **IMPORT FILE** button — file picker for `.csv`, `.json`, `.xml`
- **Drag & drop** onto the input textarea
- **EXPORT FILE** — downloads output with correct extension and MIME type
- **COPY** — clipboard copy
- Sample data loader (CSV / JSON / XML)
- `Ctrl+Enter` to convert
- Format auto-detected from file extension on import
- UTF-8 safe — Japanese, Nepali, Arabic all preserved

### Difference from the desktop app

The web version uses a JavaScript reimplementation of the conversion engine. It's functionally identical for all six paths but runs in-browser instead of Python. Large files (>5 MB) may be slower since it's JS not Python.

---

## 4. CLI — Full Reference

The CLI is built into the same binary as the GUI. Pass file arguments → runs headless as a converter. No arguments → GUI opens.

### Syntax

```bash
datamorph <input> <output> [options]

# or via Python
python src/datamorph_cli.py <input> <output> [options]
```

### All six conversion paths

```bash
datamorph data.csv   out.json   # CSV  → JSON
datamorph data.csv   out.xml    # CSV  → XML
datamorph data.json  out.csv    # JSON → CSV
datamorph data.json  out.xml    # JSON → XML
datamorph data.xml   out.json   # XML  → JSON
datamorph data.xml   out.csv    # XML  → CSV
```

### Force format (when extension doesn't match)

```bash
datamorph export.dat result.txt --from json --to csv
```

### stdin / stdout piping

```bash
cat data.csv | python src/datamorph_cli.py --from csv --to json > out.json

# Chain two conversions
cat data.json \
  | python src/datamorph_cli.py --from json --to xml \
  | python src/datamorph_cli.py --from xml --to csv \
  > final.csv
```

### Verbose mode

```bash
datamorph large.json out.csv --verbose
#   → JSON  ⟶  CSV
#   input : large.json
#   output: out.csv
#   ✔ Done in 8.2 ms  |  42.1 KB → 31.5 KB
```

### All flags

| Flag | Short | Description |
|------|-------|-------------|
| `--from FORMAT` | | Force source format: `csv`, `json`, `xml` |
| `--to FORMAT` | | Force target format: `csv`, `json`, `xml` |
| `--verbose` | `-v` | Print timing + size stats to stderr |
| `--no-banner` | | Suppress ASCII banner |
| `--version` | | Print `datamorph 1.0.0` |
| `--help` | `-h` | Show help |

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Conversion error |
| `2` | File not found |
| `130` | Interrupted (Ctrl+C) |

### Use in shell scripts

```bash
if datamorph input.csv output.json --no-banner; then
  echo "Converted OK"
else
  echo "Failed — code $?"
fi
```

---

## 5. Python API — Full Reference

Import directly from `datamorph` (after `pip install -e .` or with src on the path):

```python
import sys
sys.path.insert(0, "path/to/tearyu-datamorph/src")

from datamorph import convert, convert_file, detect_format, DataMorphError
```

---

### `convert(data, source_fmt, target_fmt)` → `str`

Converts a raw string from one format to another.

```python
from datamorph import convert

# CSV → JSON
result = convert("name,score\nAlice,99\nBob,42", "csv", "json")
# '[{"name": "Alice", "score": "99"}, ...]'

# JSON → XML
result = convert('[{"player": "Gorrotxategi", "goals": 18}]', "json", "xml")

# XML → CSV
result = convert(open("films.xml").read(), "xml", "csv")

# Same-format: no-op, returns input unchanged
result = convert('{"a":1}', "json", "json")
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `data` | `str` | Raw text content |
| `source_fmt` | `str` | `"csv"`, `"json"`, or `"xml"` |
| `target_fmt` | `str` | `"csv"`, `"json"`, or `"xml"` |

**Raises:** `DataMorphError` on any parse or conversion failure.

---

### `convert_file(input_path, output_path, source_fmt=None, target_fmt=None)` → `None`

Reads a file, converts it, writes result to output. Formats auto-detected from extensions.

```python
from datamorph import convert_file

convert_file("squad.csv", "squad.json")
convert_file("colonists.json", "colonists.xml")
convert_file("films.xml", "films.csv")

# Override formats
convert_file("data.dat", "out.dat", source_fmt="json", target_fmt="csv")

# Output directories created automatically
convert_file("data.csv", "output/sub/data.json")

# Batch convert
import os
for f in os.listdir("data/"):
    if f.endswith(".csv"):
        convert_file(f"data/{f}", f"output/{f[:-4]}.json")
```

---

### `detect_format(path_or_content)` → `str`

Detects `"csv"`, `"json"`, or `"xml"` from a path or raw content.

```python
from datamorph import detect_format

detect_format("data.csv")               # → "csv"  (extension)
detect_format('{"key":"val"}')          # → "json" (content sniff)
detect_format("<root><x>1</x></root>")  # → "xml"  (content sniff)
detect_format("a,b\n1,2\n3,4")         # → "csv"  (content sniff)
```

Raises `DataMorphError` if the format cannot be determined.

---

### `DataMorphError`

All user-facing errors. Subclass of `ValueError`.

```python
from datamorph import convert, DataMorphError

try:
    convert("{bad json", "json", "csv")
except DataMorphError as e:
    print(e)
    # Malformed JSON at line 1, col 10: Expecting property name ...

try:
    convert("", "csv", "json")
except DataMorphError as e:
    print(e)
    # Input is empty.
```

---

## 6. Format Behaviour In Depth

### CSV
- First row is always the header row — no headerless CSV support
- All values are strings — CSV has no type system, `42` → `"42"`
- BOM (`\uFEFF`) stripped silently — handles Excel exports
- Quoted fields fully handled — commas, newlines, and `""` escaping inside quotes
- Empty fields preserved as `""`
- Empty rows skipped silently

### JSON
- Root must be an array or object for CSV conversion — bare strings/numbers throw
- Output always pretty-printed, 2-space indent
- `null` → empty string in CSV, self-closing tag in XML
- `ensure_ascii=False` — Unicode preserved as-is
- Single root object wrapped in a list for CSV

### XML
- Attributes preserved as `@attributes` dict in JSON
- Text content in elements with children stored as `#text`
- Repeated sibling tags auto-converted to JSON array
- Output pretty-printed via `xml.dom.minidom`
- Invalid tag names (spaces, leading digits, slashes) sanitized by `_safe_tag()`
- Special chars in values (`<`, `>`, `&`) escaped by ElementTree

---

## 7. How Nested Data Is Handled

### Flattening to CSV

CSV is flat. Nested structures are flattened with dot notation:

| Input (JSON) | CSV Column |
|---|---|
| `{"user": {"name": "Alice"}}` | `user.name` |
| `{"user": {"addr": {"city": "NY"}}}` | `user.addr.city` |
| `{"tags": ["a", "b"]}` | `tags.0`, `tags.1` |
| `{"scores": [{"v": 1}]}` | `scores.0.v` |

Nothing is dropped. Deep nesting = long column names.

### XML → JSON mapping

| XML Pattern | JSON Result |
|---|---|
| `<name>Alice</name>` | `"name": "Alice"` |
| `<item id="1">text</item>` | `"item": {"@attributes": {"id":"1"}, "#text":"text"}` |
| `<x>a</x><x>b</x>` | `"x": ["a", "b"]` |
| `<player><name>X</name></player>` | `"player": {"name": "X"}` |

### XML → CSV row detection

If all direct children of the root share the same tag → each child is a row. Otherwise each child becomes its own row keyed by its tag. Sub-elements are then flattened the same way as JSON.

---

## 8. Error Handling

### In the GUI

Errors appear in the status bar in red:
```
✘  Malformed JSON at line 3, col 5: Expecting ',' delimiter
✘  Input is empty — paste data or load a sample
✘  CSV is empty or has no data rows
```
The output pane stays blank on error. No crash.

### In the CLI

Errors print to stderr with exit code 1:
```bash
datamorph bad.json out.csv
# ✘ CONVERSION ERROR: Malformed JSON at line 3, col 5: ...
echo $?  # → 1
```

### In the Python API

All errors are `DataMorphError` (subclass of `ValueError`):
```python
try:
    result = convert(data, "json", "csv")
except DataMorphError as e:
    # handle it
```

---

## 9. Limitations

| Limitation | Detail |
|---|---|
| All CSV values are strings | `42` → `"42"`. No type coercion. |
| Deep nesting flattens in CSV | `user.address.city` becomes a long column name — no data lost |
| Round-trips are data-safe, not byte-identical | Values survive JSON→XML→JSON, structure may differ slightly |
| No streaming | Whole file loaded into memory — fine up to ~100 MB |
| No CSV without headers | First row always treated as headers |
| No schema validation | Format converter only — doesn't validate against XSD or JSON Schema |
| Binary data | Not supported — text/UTF-8 only |
| XML namespaces | Kept as-is in tag names (`ns:tag`), not specially resolved |
| JSON boolean/null through CSV | `true` → `"True"`, `null` → `""` when going through CSV |
| GUI drag & drop | Full native DnD needs `tkinterdnd2` — without it, use the IMPORT button |

---

## 10. Building the .exe Yourself

The included `build.py` handles everything:

```bash
cd tearyu-datamorph
pip install pyinstaller
python build.py
```

Output: `dist/tearyu-datamorph` (Linux/Mac) or `dist/tearyu-datamorph.exe` (Windows).

`build.py` does:
1. Checks / installs PyInstaller
2. Cleans `dist/` and `build/`
3. Runs `pyinstaller tearyu-datamorph.spec`
4. Prints the output path and file size

The `.spec` file is `tearyu-datamorph.spec` — edit it if you want to customize the build (icon, name, excluded modules, etc.).

The binary has `console=True` so it works both as a GUI and as a CLI from the terminal.

---

## 11. Running the Test Suite

Tests cover the core engine (`src/datamorph.py`) — all 56 pass.

```bash
pip install pytest
python -m pytest tests/ -v
```

Run a specific class:
```bash
python -m pytest tests/ -v -k "TestCsvToJson"
python -m pytest tests/ -v -k "TestRoundTrip"
python -m pytest tests/ -v -k "TestErrors"
```

With coverage:
```bash
pip install pytest-cov
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

Test classes:

| Class | Covers |
|---|---|
| `TestDetectFormat` | Extension and content-sniff detection |
| `TestCsvToJson` | CSV → JSON: basic, UTF-8, quoted, BOM |
| `TestCsvToXml` | CSV → XML: structure, rows, escaping |
| `TestJsonToCsv` | JSON → CSV: flat, nested, arrays, single object |
| `TestJsonToXml` | JSON → XML: arrays, dicts, nested, null |
| `TestXmlToJson` | XML → JSON: basic, attributes, repeated tags |
| `TestXmlToCsv` | XML → CSV: uniform children, nesting |
| `TestNoOp` | Same-format returns input unchanged |
| `TestErrors` | Empty input, malformed JSON/XML, bad format names |
| `TestFlatten` | Internal `_flatten()` helper |
| `TestSafeTag` | Internal `_safe_tag()` helper |
| `TestRoundTrip` | CSV→JSON→CSV, JSON→XML→JSON, CSV→XML→CSV |

---

## 12. Extending datamorph

Adding a new format (e.g. YAML) takes 4 steps in `src/datamorph.py`:

### Step 1 — Parser
```python
def _parse_yaml(text: str) -> Any:
    try:
        import yaml
        return yaml.safe_load(text)
    except Exception as exc:
        raise DataMorphError(f"Malformed YAML: {exc}") from exc
```

### Step 2 — Converters
```python
def _yaml_to_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)

def _yaml_to_csv(data: Any) -> str:
    return _json_to_csv(data)  # reuse existing logic

def _json_to_yaml(data: Any) -> str:
    import yaml
    return yaml.dump(data, allow_unicode=True, default_flow_style=False)
```

### Step 3 — Register in `convert()`
```python
if source_fmt == "yaml":
    parsed = _parse_yaml(data)
    if target_fmt == "json": return _yaml_to_json(parsed)
    if target_fmt == "csv":  return _yaml_to_csv(parsed)
    if target_fmt == "xml":  return _json_to_xml(parsed)
```

### Step 4 — Detection
```python
_EXTENSION_MAP[".yaml"] = "yaml"
_EXTENSION_MAP[".yml"]  = "yaml"
```

Then add it to the GUI dropdowns in `gui/tearyu_datamorph_gui.py`:
```python
FORMATS = ["csv", "json", "xml", "yaml"]   # add here
```

And to the web version's `<select>` elements in `docs/index.html`. That's the full chain.

---

<div align="center">

*Built by The Lazy Dragon — 🇳🇵*
*怠竜 Tearyū · github.com/The-Lazy-Dragon/tearyu-datamorph*

</div>
