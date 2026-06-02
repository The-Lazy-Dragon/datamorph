<div align="center">

```
  ____        _        __  __                  _
 |  _ \  __ _| |_ __ _|  \/  | ___  _ __ _ __ | |__
 | | | |/ _` | __/ _` | |\/| |/ _ \| '__| '_ \| '_ \
 | |_| | (_| | || (_| | |  | | (_) | |  | |_) | | | |
 |____/ \__,_|\__\__,_|_|  |_|\___/|_|  | .__/|_| |_|
                                         |_|
```

**Convert between CSV, JSON, and XML — zero dependencies, production-ready.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-0a1628?style=flat-square&logo=python&logoColor=00f0ff)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-0a1628?style=flat-square&logo=opensourceinitiative&logoColor=00f0ff)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-0a1628?style=flat-square&logoColor=00f0ff)](requirements.txt)
[![Tests](https://img.shields.io/badge/Tests-Pytest-0a1628?style=flat-square&logo=pytest&logoColor=00f0ff)]()
[![By The Lazy Dragon](https://img.shields.io/badge/怠竜-Teary%C5%AB-0a1628?style=flat-square&logoColor=ff3a3a)](https://github.com/The-Lazy-Dragon)

*怠竜 Tearyū / The Lazy Dragon — [`github.com/The-Lazy-Dragon`](https://github.com/The-Lazy-Dragon)*

</div>

---

## 📖 What is DataMorph?

DataMorph is a **Python library and CLI tool** for converting data between the three most common structured text formats: **CSV, JSON, and XML**.

It was built to be:
- **Simple** — one function call or one terminal command
- **Robust** — handles nested structures, UTF-8, attributes, arrays
- **Zero-dependency** — pure Python stdlib, no pip bloat
- **Production-ready** — meaningful error messages, round-trip safe where possible

---

## 🗺️ Conversion Map

All six paths are fully supported:

```
CSV  ──►  JSON     JSON  ──►  CSV     XML  ──►  JSON
CSV  ──►  XML      JSON  ──►  XML     XML  ──►  CSV
```

---

## ⚡ Quick Install

### Option 1 — Run directly (no install needed)

```bash
git clone https://github.com/The-Lazy-Dragon/datamorph.git
cd datamorph
python src/cli.py input.csv output.json
```

### Option 2 — Install as a package

```bash
git clone https://github.com/The-Lazy-Dragon/datamorph.git
cd datamorph
pip install -e .
datamorph input.csv output.json
```

### Option 3 — Install from PyPI *(coming soon)*

```bash
pip install datamorph
```

**Requirements:** Python 3.10+ — no third-party packages needed.

---

## 🖥️ CLI Usage

```
usage: datamorph [input] [output] [--from FORMAT] [--to FORMAT] [-v]
```

### Basic file-to-file conversion

```bash
# Auto-detect formats from file extensions
datamorph squad.csv squad.json
datamorph squad.json squad.xml
datamorph films.xml films.json
```

### Override format detection

```bash
# File extensions don't match? Force the formats
datamorph mydata.txt result.txt --from csv --to json
```

### Pipe via stdin / stdout

```bash
# Read from stdin, write to stdout
cat data.csv | datamorph --from csv --to json > data.json

# Chain conversions
cat data.json | datamorph --from json --to xml | datamorph --from xml --to csv
```

### Verbose mode

```bash
datamorph large.json out.csv --verbose
# Output:
#   → JSON  ⟶  CSV
#   input : large.json
#   output: out.csv
#   ✔ Done in 12.4 ms  |  84.2 KB → 61.0 KB
```

### Full flag reference

| Flag | Short | Description |
|------|-------|-------------|
| `--from FORMAT` | | Override source format (`csv`, `json`, `xml`) |
| `--to FORMAT` | | Override target format (`csv`, `json`, `xml`) |
| `--verbose` | `-v` | Print summary stats to stderr |
| `--no-banner` | | Suppress the ASCII art banner |
| `--version` | | Print version and exit |
| `--help` | `-h` | Show help message and exit |

---

## 🐍 Python API

Import and use DataMorph as a library in your own code.

### `convert(data, source_fmt, target_fmt)` → `str`

Convert a raw string from one format to another.

```python
from datamorph import convert

# CSV → JSON
csv_data = "name,score\nAlice,99\nBob,42"
json_out = convert(csv_data, "csv", "json")
print(json_out)
# [
#   {"name": "Alice", "score": "99"},
#   {"name": "Bob",   "score": "42"}
# ]

# JSON → XML
json_data = '[{"player": "Gorrotxategi", "goals": 18}]'
xml_out = convert(json_data, "json", "xml")
print(xml_out)
# <?xml version="1.0" ?>
# <records>
#   <record>
#     <player>Gorrotxategi</player>
#     <goals>18</goals>
#   </record>
# </records>

# XML → CSV
xml_data = open("films.xml").read()
csv_out = convert(xml_data, "xml", "csv")
print(csv_out)
```

---

### `convert_file(input_path, output_path)` → `None`

Convert a file on disk, auto-detecting formats from extensions.

```python
from datamorph import convert_file

# Auto-detect: .csv → .json
convert_file("squad.csv", "output/squad.json")

# Auto-detect: .json → .xml
convert_file("colonists.json", "output/colonists.xml")

# Override formats explicitly
convert_file("data.txt", "out.txt", source_fmt="json", target_fmt="csv")
```

---

### `detect_format(path_or_content)` → `str`

Detect the format of a file path or raw content string.

```python
from datamorph import detect_format

detect_format("data.csv")                  # → "csv"
detect_format('{"name":"Dragon"}')         # → "json"
detect_format("<root><x>1</x></root>")     # → "xml"
detect_format("a,b,c\n1,2,3\n4,5,6")      # → "csv"  (content sniff)
```

---

### `DataMorphError`

All conversion and validation errors raise `DataMorphError` (a `ValueError` subclass).

```python
from datamorph import convert, DataMorphError

try:
    result = convert("{bad json", "json", "csv")
except DataMorphError as e:
    print(f"Conversion failed: {e}")
    # → Malformed JSON at line 1, col 10: Expecting property name enclosed in double quotes
```

---

## 📐 Format Handling Details

### CSV

| Feature | Handled |
|---------|---------|
| Headers (first row as keys) | ✅ |
| Quoted fields with commas | ✅ |
| Quoted fields with newlines | ✅ |
| Empty fields | ✅ (preserved as `""`) |
| UTF-8 / multibyte characters | ✅ |
| BOM prefix (Excel exports) | ✅ (stripped) |
| Multiple rows | ✅ |

When converting **to CSV from nested data** (JSON or XML), nested structures are flattened using dot notation:

```
{"user": {"name": "Alice", "score": 99}}
→ column: user.name = "Alice", user.score = "99"

{"tags": ["a", "b"]}
→ column: tags.0 = "a", tags.1 = "b"
```

---

### JSON

| Feature | Handled |
|---------|---------|
| Arrays of objects | ✅ |
| Nested objects | ✅ |
| Nested arrays | ✅ |
| `null` values | ✅ (→ empty string in CSV/XML) |
| UTF-8 strings | ✅ (ensure_ascii=False) |
| Single root object | ✅ (wrapped in list for CSV) |
| Output: pretty-printed (2-space indent) | ✅ |

---

### XML

| Feature | Handled |
|---------|---------|
| Element attributes (`@attributes`) | ✅ |
| Nested child elements | ✅ |
| Repeated sibling tags → JSON array | ✅ |
| Text content (`#text`) | ✅ |
| Mixed content (text + children) | ✅ |
| UTF-8 declaration in output | ✅ |
| Special char escaping (`&lt;`, `&amp;`) | ✅ (via ElementTree) |
| Tag sanitization (invalid chars → `_`) | ✅ |
| Output: pretty-printed | ✅ |

---

## ⚠️ Limitations

These are known limitations by design or by the nature of the formats:

| Limitation | Detail |
|-----------|--------|
| **All values are strings in CSV** | CSV has no type system. `42` becomes `"42"`. Type inference is not performed. |
| **Deep nesting survives JSON/XML but flattens in CSV** | `user.address.city` becomes a dotted column header. |
| **XML attribute names must be valid XML identifiers** | Column headers with spaces or leading digits are sanitized with `_`. |
| **No schema validation** | DataMorph is a format converter, not a schema validator. |
| **Round-trips are data-safe, not byte-identical** | JSON→XML→JSON preserves values but may change key ordering, whitespace, or wrapping. |
| **Binary data** | Not supported. DataMorph is for text/structured data only. |
| **Very large files (>100 MB)** | Works, but the whole file is loaded into memory. Consider streaming for huge datasets. |
| **CSV with no header row** | Not supported — first row is always treated as headers. |
| **XML namespaces** | Namespaces are preserved as-is in tag names but not specially handled. |
| **JSON number/boolean types** | Preserved in JSON→JSON but stringified when going through CSV. |

---

## 🧪 Running Tests

```bash
cd datamorph
pip install pytest
python -m pytest tests/ -v
```

Expected output:

```
tests/test_converter.py::TestDetectFormat::test_csv_extension PASSED
tests/test_converter.py::TestDetectFormat::test_json_extension PASSED
...
tests/test_converter.py::TestRoundTrip::test_csv_xml_csv PASSED

======= 47 passed in 0.18s =======
```

With coverage report:

```bash
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## 📁 Project Structure

```
datamorph/
├── src/
│   ├── __init__.py         ← Public API exports
│   ├── converter.py        ← Core conversion library
│   └── cli.py              ← Command-line interface
├── tests/
│   └── test_converter.py   ← Full test suite (47 tests)
├── examples/
│   ├── squad.csv           ← Sample CSV (football squad data)
│   ├── colonists.json      ← Sample JSON (nested + arrays)
│   └── films.xml           ← Sample XML (with attributes)
├── conftest.py             ← Pytest path config
├── setup.py                ← pip install support
├── requirements.txt        ← Dev dependencies only
├── LICENSE                 ← MIT
└── README.md               ← You are here
```

---

## 🗺️ Roadmap / Future Expansion

DataMorph is designed for easy extension. Adding new formats means:
1. Add a parser function `_parse_<fmt>(text) → object`
2. Add converter functions `_<fmt>_to_<target>(data) → str`
3. Register in the `convert()` dispatch table
4. Add to `detect_format()` sniffing logic

**Planned future formats:**
- [ ] YAML ↔ CSV / JSON / XML
- [ ] TOML ↔ JSON
- [ ] Excel (`.xlsx`) → CSV / JSON
- [ ] TSV (Tab-Separated Values)
- [ ] NDJSON (Newline-delimited JSON)
- [ ] Streaming mode for large files

---

## 🤝 Contributing

Pull requests are welcome. Open an issue first for major changes.

```bash
git clone https://github.com/The-Lazy-Dragon/datamorph.git
cd datamorph
pip install -e ".[dev]"
python -m pytest tests/ -v
```

---

## 📄 License

MIT © [The Lazy Dragon (怠竜 Tearyū)](https://github.com/The-Lazy-Dragon)

---

<div align="center">

*Built by The Lazy Dragon — Biratnagar, Nepal 🇳🇵*
*怠竜 Tearyū · github.com/The-Lazy-Dragon*

</div>
