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
### Full Technical Usage Guide

*怠竜 Tearyū / The Lazy Dragon — [`github.com/The-Lazy-Dragon`](https://github.com/The-Lazy-Dragon)*

</div>

---

## Table of Contents

1. [Installation](#1-installation)
2. [CLI Usage — Full Reference](#2-cli-usage--full-reference)
3. [Python API — Full Reference](#3-python-api--full-reference)
4. [Format Behaviour In Depth](#4-format-behaviour-in-depth)
5. [How Nested Data Is Handled](#5-how-nested-data-is-handled)
6. [Error Handling](#6-error-handling)
7. [Limitations](#7-limitations)
8. [Running the Test Suite](#8-running-the-test-suite)
9. [Extending DataMorph](#9-extending-datamorph)

---

## 1. Installation

### Requirements

- Python **3.10 or higher**
- No external runtime packages — stdlib only (`csv`, `json`, `xml.etree`, `re`, `io`, `os`)

### Option A — Run directly without installing

Clone or download, then call the CLI via `python src/cli.py`:

```bash
git clone https://github.com/The-Lazy-Dragon/datamorph.git
cd datamorph
python src/cli.py input.csv output.json
```

The library is importable the same way:

```python
import sys
sys.path.insert(0, "path/to/datamorph/src")
from converter import convert
```

### Option B — Install as an editable package (recommended for dev)

```bash
git clone https://github.com/The-Lazy-Dragon/datamorph.git
cd datamorph
pip install -e .
```

This registers the `datamorph` CLI command globally and makes `from datamorph import ...` work from anywhere.

### Option C — PyPI *(coming soon)*

```bash
pip install datamorph
```

---

## 2. CLI Usage — Full Reference

### Syntax

```
python src/cli.py [INPUT] [OUTPUT] [--from FORMAT] [--to FORMAT] [-v] [--no-banner]
```

Or, if installed via pip:

```
datamorph [INPUT] [OUTPUT] [--from FORMAT] [--to FORMAT] [-v] [--no-banner]
```

---

### 2.1 File-to-File Conversion

The most common usage. Formats are auto-detected from file extensions:

```bash
datamorph data.csv   output.json   # CSV  → JSON
datamorph data.json  output.xml    # JSON → XML
datamorph data.xml   output.csv    # XML  → CSV
datamorph data.csv   output.xml    # CSV  → XML
datamorph data.json  output.csv    # JSON → CSV
datamorph data.xml   output.json   # XML  → JSON
```

---

### 2.2 Overriding Format Detection

If your file doesn't have a standard extension (or has the wrong one), use `--from` and `--to`:

```bash
datamorph raw_export.txt result.txt --from csv --to json
datamorph dump --from xml --to json > parsed.json
```

`--from` and `--to` accept: `csv`, `json`, `xml`

---

### 2.3 stdin / stdout Piping

Omit the input file to read from stdin. Omit the output file to write to stdout.
You **must** use `--from` / `--to` when piping since there's no filename to detect from.

```bash
# Pipe from file
cat data.csv | datamorph --from csv --to json > data.json

# Chain two conversions
cat data.json | datamorph --from json --to xml | datamorph --from xml --to csv > final.csv

# Use in a shell pipeline with other tools
curl https://example.com/data.csv | datamorph --from csv --to json | jq '.[] | .name'
```

---

### 2.4 Verbose Mode

```bash
datamorph data.json out.csv --verbose
```

Prints to `stderr` (so it doesn't pollute stdout when piping):

```
  → JSON  ⟶  CSV
  input : data.json
  output: out.csv
  ✔ Done in 8.2 ms  |  42.1 KB → 31.5 KB
```

---

### 2.5 All Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--from FORMAT` | | Force source format: `csv`, `json`, `xml` |
| `--to FORMAT` | | Force target format: `csv`, `json`, `xml` |
| `--verbose` | `-v` | Print conversion summary to stderr |
| `--no-banner` | | Suppress the ASCII art banner |
| `--version` | | Print `datamorph 1.0.0` and exit |
| `--help` | `-h` | Show help and exit |

---

### 2.6 Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Conversion error (malformed input, unsupported path, etc.) |
| `2` | File not found |
| `130` | Interrupted (`Ctrl+C`) |

---

## 3. Python API — Full Reference

Import from `datamorph` (if pip-installed) or directly from `converter`:

```python
from datamorph import convert, convert_file, detect_format, DataMorphError
# or
from converter import convert, convert_file, detect_format, DataMorphError
```

---

### 3.1 `convert(data, source_fmt, target_fmt)` → `str`

Converts a raw string from one format to another. Returns the converted string.

```python
convert(data: str, source_fmt: str, target_fmt: str) -> str
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `str` | Raw text content of the source data |
| `source_fmt` | `str` | `"csv"`, `"json"`, or `"xml"` |
| `target_fmt` | `str` | `"csv"`, `"json"`, or `"xml"` |

**Returns:** converted text as a `str`

**Raises:** `DataMorphError` on any parse or conversion failure

**Examples:**

```python
from datamorph import convert

# ── CSV → JSON ──────────────────────────────────────────────────────────────
csv = "name,goals,nationality\nGorrotxategi,18,ESP\nIannone,13,ITA"
json_out = convert(csv, "csv", "json")
# [
#   {"name": "Gorrotxategi", "goals": "18", "nationality": "ESP"},
#   {"name": "Iannone",      "goals": "13", "nationality": "ITA"}
# ]

# ── JSON → XML ──────────────────────────────────────────────────────────────
import json
data = json.dumps([{"player": "Ryūen", "rank": "竜王", "level": 120}])
xml_out = convert(data, "json", "xml")
# <?xml version="1.0" ?>
# <records>
#   <record>
#     <player>Ryūen</player>
#     <rank>竜王</rank>
#     <level>120</level>
#   </record>
# </records>

# ── XML → JSON ──────────────────────────────────────────────────────────────
xml = "<squad><player><name>Modrić</name><age>39</age></player></squad>"
json_out = convert(xml, "xml", "json")

# ── XML → CSV ───────────────────────────────────────────────────────────────
xml = """
<records>
  <record><name>Alice</name><score>99</score></record>
  <record><name>Bob</name><score>42</score></record>
</records>
"""
csv_out = convert(xml, "xml", "csv")
# name,score
# Alice,99
# Bob,42

# ── Same-format no-op ────────────────────────────────────────────────────────
# Passing the same format returns the input unchanged
result = convert('{"a":1}', "json", "json")  # → '{"a":1}'
```

---

### 3.2 `convert_file(input_path, output_path, source_fmt=None, target_fmt=None)` → `None`

Reads a file, converts it, and writes the result to another file.
Formats are auto-detected from extensions unless overridden.

```python
convert_file(
    input_path: str,
    output_path: str,
    source_fmt: str | None = None,
    target_fmt: str | None = None
) -> None
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `input_path` | `str` | Path to source file |
| `output_path` | `str` | Path to write output (directories created if needed) |
| `source_fmt` | `str \| None` | Override source format. Defaults to extension detection. |
| `target_fmt` | `str \| None` | Override target format. Defaults to extension detection. |

**Raises:**
- `FileNotFoundError` if `input_path` doesn't exist
- `DataMorphError` on conversion failure

**Examples:**

```python
from datamorph import convert_file

# Auto-detect from extensions
convert_file("squad.csv", "squad.json")
convert_file("colonists.json", "colonists.xml")
convert_file("films.xml", "films.csv")

# Override formats (useful for non-standard extensions)
convert_file("export.dat", "result.dat", source_fmt="json", target_fmt="csv")

# Output directory is created automatically
convert_file("data.csv", "output/subdir/data.json")

# Batch convert in a loop
import os
for fname in os.listdir("data/"):
    if fname.endswith(".csv"):
        stem = fname[:-4]
        convert_file(f"data/{fname}", f"output/{stem}.json")
```

---

### 3.3 `detect_format(path_or_content)` → `str`

Returns `"csv"`, `"json"`, or `"xml"`. Accepts either a filesystem path or raw content.

**Detection priority:**
1. File extension (`.csv`, `.json`, `.xml`) — fastest
2. Content sniffing:
   - Starts with `<` → XML
   - Starts with `{` or `[` and parses as valid JSON → JSON
   - Multiple lines with consistent comma counts → CSV

```python
from datamorph import detect_format

# By extension
detect_format("data.csv")              # → "csv"
detect_format("data.json")             # → "json"
detect_format("data.xml")              # → "xml"

# By content
detect_format('{"key": "value"}')      # → "json"
detect_format('[{"a":1},{"a":2}]')     # → "json"
detect_format("<root><x>1</x></root>") # → "xml"
detect_format("a,b,c\n1,2,3\n4,5,6")  # → "csv"

# Raises DataMorphError if undetectable
detect_format("this is just prose")    # ✘ DataMorphError
```

---

### 3.4 `DataMorphError`

All user-facing errors are `DataMorphError`, a subclass of `ValueError`.

```python
from datamorph import convert, DataMorphError

try:
    result = convert("{not valid json!!", "json", "csv")
except DataMorphError as e:
    print(e)
    # Malformed JSON at line 1, col 18: Expecting ',' delimiter

try:
    convert("", "csv", "json")
except DataMorphError as e:
    print(e)
    # Input is empty.

try:
    convert("name,age\n", "csv", "json")
except DataMorphError as e:
    print(e)
    # CSV is empty or has no data rows.
```

**All error messages are human-readable** and include position info where applicable (JSON line/col, XML parse position).

---

## 4. Format Behaviour In Depth

### 4.1 CSV

- **First row is always the header row.** DataMorph does not support headerless CSV.
- **All values are strings.** CSV has no type system. `99` stays `"99"` — no coercion.
- **BOM is stripped.** Excel often exports UTF-8-with-BOM. DataMorph strips `\ufeff` silently.
- **Quoted fields are fully handled.** Commas inside quotes, newlines inside quotes, escaped quotes (`""`) all work.
- **Empty fields are preserved** as empty strings `""`, not `null`.
- **Empty rows are skipped** silently.

---

### 4.2 JSON

- **Root must be an array or object** to convert to CSV. A bare string or number will throw.
- **Output is always pretty-printed** with 2-space indentation.
- **`null` values** → empty string in CSV, self-closing tag (`<field/>`) in XML.
- **`ensure_ascii=False`** — Unicode characters are preserved as-is (no `\uXXXX` escaping).
- **Arrays of objects** → one row per object in CSV, one `<record>` per object in XML.
- **Single root object** → wrapped in a list for CSV conversion purposes.

---

### 4.3 XML

- **Attributes** are preserved under `@attributes` in JSON output.
- **Text content** of elements with children is stored under `#text`.
- **Repeated sibling tags** are automatically converted to a JSON array.
- **Output is pretty-printed** via `xml.dom.minidom`.
- **Tag sanitization:** invalid XML tag names (leading digits, spaces, slashes) are cleaned automatically using `_safe_tag()`. Example: `my field` → `my_field`, `1data` → `_1data`.
- **Special characters** in values (`<`, `>`, `&`) are escaped by ElementTree automatically.

---

## 5. How Nested Data Is Handled

### JSON/XML → CSV (Flattening)

CSV is a flat format. Nested structures are flattened using **dot notation**:

| Input (JSON) | CSV Column |
|---|---|
| `{"user": {"name": "Alice"}}` | `user.name` |
| `{"user": {"address": {"city": "NY"}}}` | `user.address.city` |
| `{"tags": ["a", "b", "c"]}` | `tags.0`, `tags.1`, `tags.2` |
| `{"scores": [{"val": 1}]}` | `scores.0.val` |

No data is lost — deeply nested values become long column names.

**Example:**

Input JSON:
```json
[
  {
    "name": "Ryūen",
    "stats": { "shooting": 20, "melee": 20 },
    "bionics": ["archotech_legs", "archotech_eyes"]
  }
]
```

Output CSV:
```
name,stats.shooting,stats.melee,bionics.0,bionics.1
Ryūen,20,20,archotech_legs,archotech_eyes
```

---

### XML → JSON (Structural Mapping)

| XML Pattern | JSON Output |
|---|---|
| `<name>Alice</name>` | `"name": "Alice"` |
| `<item id="1">text</item>` | `"item": {"@attributes": {"id": "1"}, "#text": "text"}` |
| `<item>a</item><item>b</item>` | `"item": ["a", "b"]` |
| `<player><name>X</name></player>` | `"player": {"name": "X"}` |

---

### XML → CSV (Row Detection)

DataMorph uses a heuristic to detect rows:

- If all direct children of the root share the **same tag name** → each child is a row
- Otherwise → each child becomes its own row, keyed by its tag

Then each row's sub-elements are flattened the same way as JSON.

---

## 6. Error Handling

### All errors are `DataMorphError`

```python
from datamorph import DataMorphError

# Safe wrapper pattern
def safe_convert(data, src, tgt):
    try:
        return convert(data, src, tgt)
    except DataMorphError as e:
        print(f"[DataMorph] {e}")
        return None
```

### In CLI scripts

```bash
datamorph bad.json out.csv
# ✘ CONVERSION ERROR: Malformed JSON at line 3, col 5: ...
echo $?  # → 1
```

You can catch the exit code in shell scripts:

```bash
if datamorph input.csv output.json --no-banner; then
    echo "Converted successfully"
else
    echo "Conversion failed — check your input file"
fi
```

---

## 7. Limitations

| Limitation | Detail |
|---|---|
| **No type preservation through CSV** | Numbers and booleans become strings. `42` → `"42"`. Unavoidable — CSV has no type system. |
| **Round-trips are data-safe, not byte-identical** | JSON→XML→JSON preserves all values but may change key ordering, whitespace, and wrapping structure. |
| **No CSV without headers** | First row is always the header. There's no `--no-header` flag yet. |
| **No streaming** | The entire file is loaded into memory. Fine for files up to ~100 MB; large datasets should be chunked externally. |
| **Binary data** | Not supported. Text/UTF-8 only. |
| **XML namespaces** | Namespace prefixes are kept as-is in tag names (e.g. `ns:element` → tag `ns:element`), not specially resolved. |
| **JSON number/boolean coercion** | `true` → `"True"`, `false` → `"False"`, `null` → `""` when going through CSV. |
| **No schema validation** | DataMorph converts structure, not semantics. It won't validate against XSD or JSON Schema. |
| **CSV with multi-line headers** | Not supported — header is strictly the first row. |

---

## 8. Running the Test Suite

### Install pytest

```bash
pip install pytest pytest-cov
```

### Run all 56 tests

```bash
cd datamorph
python -m pytest tests/ -v
```

### With coverage report

```bash
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

### Run a specific test class

```bash
python -m pytest tests/ -v -k "TestCsvToJson"
python -m pytest tests/ -v -k "TestRoundTrip"
python -m pytest tests/ -v -k "TestErrors"
```

### Test structure

| Class | What it covers |
|---|---|
| `TestDetectFormat` | Format detection by extension and content sniffing |
| `TestCsvToJson` | CSV → JSON: basic, UTF-8, quoted fields, BOM, empty rows |
| `TestCsvToXml` | CSV → XML: structure, multi-row, special chars |
| `TestJsonToCsv` | JSON → CSV: flat, nested, arrays, single object, error |
| `TestJsonToXml` | JSON → XML: arrays, dicts, nested, null values |
| `TestXmlToJson` | XML → JSON: basic, attributes, repeated tags, nesting |
| `TestXmlToCsv` | XML → CSV: uniform children, flattened nested, error |
| `TestNoOp` | Same-format conversions return input unchanged |
| `TestErrors` | All error paths: empty input, malformed JSON/XML, bad formats |
| `TestFlatten` | Internal `_flatten()` helper |
| `TestSafeTag` | Internal `_safe_tag()` helper |
| `TestRoundTrip` | CSV→JSON→CSV, JSON→XML→JSON, CSV→XML→CSV |

---

## 9. Extending DataMorph

DataMorph is designed to be extended. Adding a new format (e.g. YAML) requires 4 steps:

### Step 1 — Add a parser

```python
# In converter.py
def _parse_yaml(text: str) -> Any:
    try:
        import yaml  # or use a stdlib alternative
        return yaml.safe_load(text)
    except Exception as exc:
        raise DataMorphError(f"Malformed YAML: {exc}") from exc
```

### Step 2 — Add converter functions

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
# In the convert() dispatch block:
if source_fmt == "yaml":
    parsed = _parse_yaml(data)
    if target_fmt == "json": return _yaml_to_json(parsed)
    if target_fmt == "csv":  return _yaml_to_csv(parsed)
    if target_fmt == "xml":  return _json_to_xml(parsed)

if target_fmt == "yaml":
    if source_fmt == "json": return _json_to_yaml(_parse_json(data))
    if source_fmt == "csv":  return _json_to_yaml(_parse_csv(data))
    if source_fmt == "xml":  return _json_to_yaml(_element_to_dict(_parse_xml(data)))
```

### Step 4 — Add detection

```python
# In detect_format():
_EXTENSION_MAP[".yaml"] = "yaml"
_EXTENSION_MAP[".yml"] = "yaml"

# Content sniff:
if sample.startswith("---") or re.match(r"^\w+:\s", sample):
    return "yaml"
```

That's all. Write tests for the new paths in `tests/test_converter.py` and you're done.

---

<div align="center">
Try it Live: https://the-lazy-dragon.github.io/datamorph/
*Built by The Lazy Dragon — 🇳🇵*
*怠竜 Tearyū · github.com/The-Lazy-Dragon*

</div>
