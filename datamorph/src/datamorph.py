"""
tearyu-datamorph/datamorph.py
─────────────────────────────────────────────────────────────────────────────
The Lazy Dragon's tearyu-datamorph — Core Converter Library
Author : The Lazy Dragon (怠竜 Tearyū)
GitHub : https://github.com/The-Lazy-Dragon/tearyu-datamorph
─────────────────────────────────────────────────────────────────────────────
Supported formats
    csv   — Comma-Separated Values
    tsv   — Tab-Separated Values
    json  — JSON (arrays and nested objects)
    ndjson— Newline-Delimited JSON
    xml   — XML (attributes, nested elements)
    yaml  — YAML (requires pyyaml)
    toml  — TOML (stdlib tomllib, Python 3.11+; tomli fallback)
    xlsx  — Excel workbook (requires openpyxl) [source only]
    html  — HTML <table> extraction [source only]

Public API
    detect_format(path_or_content)              → str
    convert(data, source_fmt, target_fmt)       → str
    convert_file(in_path, out_path, ...)        → None
    convert_xlsx(path, sheet, target_fmt)       → str
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import csv
import io
import json
import os
import re
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from typing import Any
from xml.dom import minidom


# ─────────────────────────────────────────────────────────────────────────────
# OPTIONAL DEPENDENCY IMPORTS
# ─────────────────────────────────────────────────────────────────────────────

def _require(pkg: str, install: str | None = None) -> Any:
    """Import a package, raising DataMorphError with install hint if missing."""
    import importlib
    try:
        return importlib.import_module(pkg)
    except ImportError:
        hint = install or pkg
        raise DataMorphError(
            f"'{pkg}' is required for this conversion but isn't installed. "
            f"Run: pip install {hint}"
        )


def _load_yaml():
    return _require("yaml", "pyyaml")


def _load_tomllib():
    """tomllib is stdlib in Python 3.11+; fall back to tomli."""
    try:
        import tomllib
        return tomllib
    except ImportError:
        return _require("tomli", "tomli")


def _load_openpyxl():
    return _require("openpyxl", "openpyxl")


# ─────────────────────────────────────────────────────────────────────────────
# EXCEPTIONS
# ─────────────────────────────────────────────────────────────────────────────

class DataMorphError(ValueError):
    """Raised for all conversion / validation errors."""


# ─────────────────────────────────────────────────────────────────────────────
# FORMAT DETECTION
# ─────────────────────────────────────────────────────────────────────────────

_EXTENSION_MAP: dict[str, str] = {
    ".csv":    "csv",
    ".tsv":    "tsv",
    ".tab":    "tsv",
    ".json":   "json",
    ".ndjson": "ndjson",
    ".jsonl":  "ndjson",
    ".xml":    "xml",
    ".yaml":   "yaml",
    ".yml":    "yaml",
    ".toml":   "toml",
    ".xlsx":   "xlsx",
    ".html":   "html",
    ".htm":    "html",
}

# Formats that can be an output target
_OUTPUT_FORMATS = {"csv", "tsv", "json", "ndjson", "xml", "yaml", "toml"}

# Formats that are source-only (we read but can't write)
_SOURCE_ONLY = {"xlsx", "html"}


def detect_format(path_or_content: str) -> str:
    """
    Detect data format from a file path (extension) or raw content.

    Priority: file extension → content sniffing.

    Returns one of: csv, tsv, json, ndjson, xml, yaml, toml, xlsx, html
    Raises DataMorphError if format cannot be determined.
    """
    ext = os.path.splitext(path_or_content)[-1].lower()
    if ext in _EXTENSION_MAP:
        return _EXTENSION_MAP[ext]

    sample = path_or_content.strip()

    # XML / HTML
    if sample.startswith("<"):
        if re.search(r"<\s*table[\s>]", sample, re.IGNORECASE):
            return "html"
        return "xml"

    # JSON / NDJSON
    if sample.startswith(("{", "[")):
        try:
            json.loads(sample)
            return "json"
        except json.JSONDecodeError:
            pass

    # NDJSON — multiple lines each starting with { or [
    lines = [l for l in sample.splitlines() if l.strip()]
    if len(lines) >= 2 and all(l.strip().startswith(("{", "[")) for l in lines[:5]):
        return "ndjson"

    # YAML — key: value structure
    if re.match(r"^\w[\w\s]*:\s", sample):
        return "yaml"

    # TOML — [section] or key = value
    if re.match(r"^\[[\w.]+\]", sample) or re.match(r"^\w+\s*=\s*", sample):
        return "toml"

    # TSV — tabs as delimiter
    if "\t" in sample:
        tsv_lines = [l for l in lines if l.strip()]
        if len(tsv_lines) >= 2:
            tab_counts = [l.count("\t") for l in tsv_lines[:5]]
            if all(c == tab_counts[0] and c >= 1 for c in tab_counts):
                return "tsv"

    # CSV — consistent comma counts
    if len(lines) >= 2:
        comma_counts = [l.count(",") for l in lines[:5]]
        if all(c == comma_counts[0] and c >= 1 for c in comma_counts):
            return "csv"

    raise DataMorphError(
        "Cannot detect format. Use --from to specify it explicitly.\n"
        f"  Supported: {', '.join(sorted(_EXTENSION_MAP.values()))}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _safe_tag(name: str) -> str:
    name = re.sub(r"[\s/\\]", "_", name)
    name = re.sub(r"[^\w.\-]", "", name, flags=re.ASCII)
    if name and name[0].isdigit():
        name = f"_{name}"
    return name or "field"


def _flatten(obj: Any, prefix: str = "") -> dict[str, str]:
    items: dict[str, str] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            full_key = f"{prefix}.{k}" if prefix else k
            items.update(_flatten(v, full_key))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            full_key = f"{prefix}.{i}" if prefix else str(i)
            items.update(_flatten(v, full_key))
    else:
        items[prefix] = "" if obj is None else str(obj)
    return items


def _build_xml_element(parent: ET.Element, key: str, value: Any) -> None:
    tag = _safe_tag(key)
    child = ET.SubElement(parent, tag)
    if isinstance(value, dict):
        for k, v in value.items():
            _build_xml_element(child, k, v)
    elif isinstance(value, list):
        for item in value:
            _build_xml_element(child, "item", item)
    else:
        child.text = "" if value is None else str(value)


def _element_to_dict(element: ET.Element) -> Any:
    result: dict[str, Any] = {}
    if element.attrib:
        result["@attributes"] = dict(element.attrib)
    children = list(element)
    if not children:
        text = (element.text or "").strip()
        if result:
            if text:
                result["#text"] = text
            return result
        return text
    child_dict: dict[str, list[Any]] = {}
    for child in children:
        child_dict.setdefault(child.tag, []).append(_element_to_dict(child))
    for tag, items in child_dict.items():
        result[tag] = items[0] if len(items) == 1 else items
    text = (element.text or "").strip()
    if text:
        result["#text"] = text
    return result


def _pretty_xml(root: ET.Element) -> str:
    raw = ET.tostring(root, encoding="unicode")
    reparsed = minidom.parseString(raw)
    return "\n".join(reparsed.toprettyxml(indent="  ").splitlines())


def _rows_to_delimited(rows: list[dict], delimiter: str) -> str:
    """Shared writer for CSV and TSV."""
    all_keys: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for k in row:
            if k not in seen:
                all_keys.append(k)
                seen.add(k)
    out = io.StringIO()
    writer = csv.DictWriter(
        out, fieldnames=all_keys, extrasaction="ignore",
        lineterminator="\n", delimiter=delimiter
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row.get(k, "") for k in all_keys})
    return out.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# PARSERS  →  Python objects (rows / dicts / lists)
# ─────────────────────────────────────────────────────────────────────────────

def _parse_delimited(text: str, delimiter: str) -> list[dict[str, Any]]:
    text = text.lstrip("\ufeff")
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    try:
        rows = [dict(row) for row in reader if any(v for v in row.values())]
    except csv.Error as exc:
        fmt = "TSV" if delimiter == "\t" else "CSV"
        raise DataMorphError(f"Malformed {fmt}: {exc}") from exc
    if not rows:
        raise DataMorphError("File is empty or has no data rows.")
    return rows


def _parse_csv(text: str)  -> list[dict]: return _parse_delimited(text, ",")
def _parse_tsv(text: str)  -> list[dict]: return _parse_delimited(text, "\t")


def _parse_json(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise DataMorphError(
            f"Malformed JSON at line {exc.lineno}, col {exc.colno}: {exc.msg}"
        ) from exc


def _parse_ndjson(text: str) -> list[Any]:
    rows = []
    for i, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise DataMorphError(
                f"Malformed NDJSON at line {i}: {exc.msg}"
            ) from exc
    if not rows:
        raise DataMorphError("NDJSON file is empty.")
    return rows


def _parse_xml(text: str) -> ET.Element:
    try:
        return ET.fromstring(text.strip())
    except ET.ParseError as exc:
        raise DataMorphError(f"Malformed XML: {exc}") from exc


def _parse_yaml(text: str) -> Any:
    yaml = _load_yaml()
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise DataMorphError(f"Malformed YAML: {exc}") from exc
    if data is None:
        raise DataMorphError("YAML file is empty.")
    return data


def _parse_toml(text: str) -> Any:
    toml = _load_tomllib()
    try:
        # tomllib requires bytes
        return toml.loads(text) if hasattr(toml, "loads") else toml.loads(text)
    except Exception as exc:
        raise DataMorphError(f"Malformed TOML: {exc}") from exc


class _HTMLTableParser(HTMLParser):
    """Extract first <table> from HTML into list-of-row-lists."""

    def __init__(self):
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._in_table = False
        self._in_row   = False
        self._in_cell  = False
        self._cur_table: list[list[str]] = []
        self._cur_row:   list[str] = []
        self._cur_cell   = ""

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "table":
            self._in_table = True
            self._cur_table = []
        elif tag in ("tr",) and self._in_table:
            self._in_row = True
            self._cur_row = []
        elif tag in ("td", "th") and self._in_row:
            self._in_cell = True
            self._cur_cell = ""

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in ("td", "th") and self._in_cell:
            self._cur_row.append(self._cur_cell.strip())
            self._in_cell = False
        elif tag == "tr" and self._in_row:
            if self._cur_row:
                self._cur_table.append(self._cur_row)
            self._in_row = False
        elif tag == "table" and self._in_table:
            if self._cur_table:
                self.tables.append(self._cur_table)
            self._in_table = False

    def handle_data(self, data):
        if self._in_cell:
            self._cur_cell += data

    def handle_entityref(self, name):
        if self._in_cell:
            import html
            self._cur_cell += html.unescape(f"&{name};")

    def handle_charref(self, name):
        if self._in_cell:
            import html
            self._cur_cell += html.unescape(f"&#{name};")


def _parse_html_table(text: str, table_index: int = 0) -> list[dict[str, Any]]:
    """
    Extract a table from HTML into list-of-row-dicts.
    First row is used as headers.
    table_index: which <table> to extract (0 = first).
    """
    parser = _HTMLTableParser()
    parser.feed(text)

    if not parser.tables:
        raise DataMorphError(
            "No <table> elements found in HTML. "
            "Make sure your file contains an HTML table."
        )

    if table_index >= len(parser.tables):
        raise DataMorphError(
            f"Table index {table_index} out of range — "
            f"found {len(parser.tables)} table(s) (0-indexed)."
        )

    raw = parser.tables[table_index]
    if len(raw) < 2:
        raise DataMorphError(
            "HTML table must have at least a header row and one data row."
        )

    headers = raw[0]
    # Deduplicate blank/duplicate headers
    seen_h: dict[str, int] = {}
    clean_headers = []
    for h in headers:
        h = h.strip() or "column"
        count = seen_h.get(h, 0)
        seen_h[h] = count + 1
        clean_headers.append(h if count == 0 else f"{h}_{count}")

    rows = []
    for row in raw[1:]:
        # Pad short rows, trim long ones
        padded = list(row) + [""] * (len(clean_headers) - len(row))
        rows.append(dict(zip(clean_headers, padded[:len(clean_headers)])))
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# XLSX  (binary — separate entry point)
# ─────────────────────────────────────────────────────────────────────────────

def convert_xlsx(
    input_path: str,
    target_fmt: str,
    output_path: str | None = None,
    sheet: str | int | None = None,
) -> str:
    """
    Read an Excel workbook and convert a sheet to the target format.

    Parameters
    ----------
    input_path : str
        Path to the .xlsx file.
    target_fmt : str
        Output format: csv, tsv, json, ndjson, xml, yaml, toml
    output_path : str, optional
        If given, write output to this file as well as returning it.
    sheet : str or int, optional
        Sheet name or 0-based index. Defaults to the first sheet.

    Returns
    -------
    str
        Converted text.
    """
    openpyxl = _load_openpyxl()
    try:
        wb = openpyxl.load_workbook(input_path, read_only=True, data_only=True)
    except Exception as exc:
        raise DataMorphError(f"Cannot open Excel file: {exc}") from exc

    # Pick sheet
    if sheet is None:
        ws = wb.active
    elif isinstance(sheet, int):
        names = wb.sheetnames
        if sheet >= len(names):
            raise DataMorphError(
                f"Sheet index {sheet} out of range — "
                f"workbook has {len(names)} sheet(s)."
            )
        ws = wb[names[sheet]]
    else:
        if sheet not in wb.sheetnames:
            raise DataMorphError(
                f"Sheet '{sheet}' not found. "
                f"Available: {', '.join(wb.sheetnames)}"
            )
        ws = wb[sheet]

    rows_raw = list(ws.iter_rows(values_only=True))
    wb.close()

    if not rows_raw:
        raise DataMorphError("Excel sheet is empty.")

    # First row = headers
    headers = [str(h).strip() if h is not None else f"col_{i}"
               for i, h in enumerate(rows_raw[0])]

    # Deduplicate blank/duplicate headers
    seen_h: dict[str, int] = {}
    clean_headers = []
    for h in headers:
        h = h or "column"
        count = seen_h.get(h, 0)
        seen_h[h] = count + 1
        clean_headers.append(h if count == 0 else f"{h}_{count}")

    rows = []
    for raw_row in rows_raw[1:]:
        padded = list(raw_row) + [None] * (len(clean_headers) - len(raw_row))
        row = {}
        for k, v in zip(clean_headers, padded[:len(clean_headers)]):
            row[k] = "" if v is None else str(v)
        rows.append(row)

    if not rows:
        raise DataMorphError("Excel sheet has headers but no data rows.")

    result = _rows_to_target(rows, target_fmt)

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(result)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# CONVERTERS  →  output text
# ─────────────────────────────────────────────────────────────────────────────

def _rows_to_json(rows: list[dict]) -> str:
    return json.dumps(rows, ensure_ascii=False, indent=2)


def _rows_to_ndjson(rows: list[dict]) -> str:
    return "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)


def _rows_to_xml(rows: list[dict]) -> str:
    root = ET.Element("records")
    for row in rows:
        record = ET.SubElement(root, "record")
        for key, value in row.items():
            _build_xml_element(record, key, value)
    return _pretty_xml(root)


def _rows_to_yaml(rows: list[dict]) -> str:
    yaml = _load_yaml()
    return yaml.dump(rows, allow_unicode=True, default_flow_style=False, sort_keys=False)


def _rows_to_toml(rows: list[dict]) -> str:
    """
    TOML output: array of tables under [[records]].
    """
    lines = []
    for row in rows:
        lines.append("[[records]]")
        for k, v in row.items():
            tag = re.sub(r"[^\w]", "_", k) or "field"
            # TOML strings must be quoted; numbers stay bare if valid
            try:
                float(v)
                lines.append(f"{tag} = {v}")
            except (ValueError, TypeError):
                escaped = str(v).replace('"', '\\"')
                lines.append(f'{tag} = "{escaped}"')
        lines.append("")
    return "\n".join(lines)


def _json_to_csv(data: Any) -> str:
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise DataMorphError(
            "JSON root must be an array or object to convert to CSV. "
            "Got: " + type(data).__name__
        )
    flat_rows = [_flatten(row) for row in data]
    return _rows_to_delimited(flat_rows, ",")


def _json_to_tsv(data: Any) -> str:
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise DataMorphError("JSON root must be an array or object to convert to TSV.")
    flat_rows = [_flatten(row) for row in data]
    return _rows_to_delimited(flat_rows, "\t")


def _json_to_xml(data: Any) -> str:
    root = ET.Element("root")
    if isinstance(data, list):
        root.tag = "records"
        for item in data:
            _build_xml_element(root, "record", item)
    elif isinstance(data, dict):
        for k, v in data.items():
            _build_xml_element(root, k, v)
    else:
        root.text = str(data)
    return _pretty_xml(root)


def _json_to_yaml(data: Any) -> str:
    yaml = _load_yaml()
    return yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)


def _json_to_toml(data: Any) -> str:
    if isinstance(data, list):
        return _rows_to_toml([_flatten(r) for r in data])
    if isinstance(data, dict):
        return _rows_to_toml([_flatten(data)])
    raise DataMorphError("TOML output requires a JSON object or array at the root.")


def _json_to_ndjson(data: Any) -> str:
    if isinstance(data, list):
        return "\n".join(json.dumps(r, ensure_ascii=False) for r in data)
    return json.dumps(data, ensure_ascii=False)


def _xml_to_json(element: ET.Element) -> str:
    d = {element.tag: _element_to_dict(element)}
    return json.dumps(d, ensure_ascii=False, indent=2)


def _xml_to_csv(element: ET.Element) -> str:
    children = list(element)
    if not children:
        raise DataMorphError("XML root element has no children to convert to rows.")
    first_tag = children[0].tag
    if all(c.tag == first_tag for c in children):
        rows = [_flatten(_element_to_dict(c)) for c in children]
    else:
        rows = [_flatten({c.tag: _element_to_dict(c)}) for c in children]
    return _rows_to_delimited(rows, ",")


def _xml_to_tsv(element: ET.Element) -> str:
    children = list(element)
    if not children:
        raise DataMorphError("XML root element has no children to convert to rows.")
    first_tag = children[0].tag
    if all(c.tag == first_tag for c in children):
        rows = [_flatten(_element_to_dict(c)) for c in children]
    else:
        rows = [_flatten({c.tag: _element_to_dict(c)}) for c in children]
    return _rows_to_delimited(rows, "\t")


def _yaml_to_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def _yaml_to_csv(data: Any) -> str:
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise DataMorphError("YAML root must be a list or mapping to convert to CSV.")
    return _rows_to_delimited([_flatten(r) for r in data], ",")


def _yaml_to_tsv(data: Any) -> str:
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise DataMorphError("YAML root must be a list or mapping to convert to TSV.")
    return _rows_to_delimited([_flatten(r) for r in data], "\t")


def _yaml_to_xml(data: Any) -> str:
    return _json_to_xml(data)


def _yaml_to_ndjson(data: Any) -> str:
    return _json_to_ndjson(data)


def _yaml_to_toml(data: Any) -> str:
    return _json_to_toml(data)


def _toml_to_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def _toml_to_csv(data: Any) -> str:
    # TOML top-level is always a dict
    # If it has a single list value, use that as rows
    if isinstance(data, dict):
        lists = [(k, v) for k, v in data.items() if isinstance(v, list)]
        if len(lists) == 1:
            data = lists[0][1]
        else:
            data = [data]
    return _rows_to_delimited([_flatten(r) for r in data], ",")


def _toml_to_tsv(data: Any) -> str:
    if isinstance(data, dict):
        lists = [(k, v) for k, v in data.items() if isinstance(v, list)]
        if len(lists) == 1:
            data = lists[0][1]
        else:
            data = [data]
    return _rows_to_delimited([_flatten(r) for r in data], "\t")


def _toml_to_xml(data: Any) -> str:
    return _json_to_xml(data)


def _toml_to_yaml(data: Any) -> str:
    return _json_to_yaml(data)


def _toml_to_ndjson(data: Any) -> str:
    return _json_to_ndjson(data)


def _ndjson_to_json(rows: list) -> str:
    return json.dumps(rows, ensure_ascii=False, indent=2)


def _ndjson_to_csv(rows: list) -> str:
    return _rows_to_delimited([_flatten(r) for r in rows], ",")


def _ndjson_to_tsv(rows: list) -> str:
    return _rows_to_delimited([_flatten(r) for r in rows], "\t")


def _ndjson_to_xml(rows: list) -> str:
    return _json_to_xml(rows)


def _ndjson_to_yaml(rows: list) -> str:
    return _json_to_yaml(rows)


def _ndjson_to_toml(rows: list) -> str:
    return _json_to_toml(rows)


def _rows_to_target(rows: list[dict], target_fmt: str) -> str:
    """Shared helper — convert a list of row-dicts to any output format."""
    if target_fmt == "csv":    return _rows_to_delimited(rows, ",")
    if target_fmt == "tsv":    return _rows_to_delimited(rows, "\t")
    if target_fmt == "json":   return _rows_to_json(rows)
    if target_fmt == "ndjson": return _rows_to_ndjson(rows)
    if target_fmt == "xml":    return _rows_to_xml(rows)
    if target_fmt == "yaml":   return _rows_to_yaml(rows)
    if target_fmt == "toml":   return _rows_to_toml(rows)
    raise DataMorphError(f"Unsupported target format: '{target_fmt}'")


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

#: All formats accepted as source input
ALL_SOURCE_FORMATS = frozenset(_EXTENSION_MAP.values())

#: All formats accepted as output targets
ALL_TARGET_FORMATS = _OUTPUT_FORMATS


def convert(data: str, source_fmt: str, target_fmt: str) -> str:
    """
    Convert *data* (raw text) from *source_fmt* to *target_fmt*.

    Supported source formats : csv, tsv, json, ndjson, xml, yaml, toml, html
    Supported target formats : csv, tsv, json, ndjson, xml, yaml, toml

    xlsx is source-only — use convert_xlsx() for Excel files.

    Parameters
    ----------
    data : str
        Raw text content.
    source_fmt : str
        Source format name (case-insensitive).
    target_fmt : str
        Target format name (case-insensitive).

    Returns
    -------
    str
        Converted text.

    Raises
    ------
    DataMorphError
        On parse failures, unsupported paths, or empty input.
    """
    source_fmt = source_fmt.lower().strip()
    target_fmt = target_fmt.lower().strip()

    if source_fmt == "xlsx":
        raise DataMorphError(
            "Excel (.xlsx) files are binary — use convert_xlsx(path, target_fmt) instead."
        )
    if source_fmt not in ALL_SOURCE_FORMATS:
        raise DataMorphError(
            f"Unsupported source format: '{source_fmt}'.\n"
            f"  Supported: {', '.join(sorted(ALL_SOURCE_FORMATS))}"
        )
    if target_fmt not in ALL_TARGET_FORMATS:
        raise DataMorphError(
            f"Unsupported target format: '{target_fmt}'.\n"
            f"  Supported: {', '.join(sorted(ALL_TARGET_FORMATS))}"
        )
    if not data.strip():
        raise DataMorphError("Input is empty.")
    if source_fmt == target_fmt:
        return data

    # ── CSV ──────────────────────────────────────────────────────────────────
    if source_fmt == "csv":
        rows = _parse_csv(data)
        return _rows_to_target(rows, target_fmt)

    # ── TSV ──────────────────────────────────────────────────────────────────
    if source_fmt == "tsv":
        rows = _parse_tsv(data)
        return _rows_to_target(rows, target_fmt)

    # ── JSON ─────────────────────────────────────────────────────────────────
    if source_fmt == "json":
        parsed = _parse_json(data)
        if target_fmt == "csv":    return _json_to_csv(parsed)
        if target_fmt == "tsv":    return _json_to_tsv(parsed)
        if target_fmt == "xml":    return _json_to_xml(parsed)
        if target_fmt == "yaml":   return _json_to_yaml(parsed)
        if target_fmt == "toml":   return _json_to_toml(parsed)
        if target_fmt == "ndjson": return _json_to_ndjson(parsed)

    # ── NDJSON ───────────────────────────────────────────────────────────────
    if source_fmt == "ndjson":
        rows = _parse_ndjson(data)
        if target_fmt == "json":   return _ndjson_to_json(rows)
        if target_fmt == "csv":    return _ndjson_to_csv(rows)
        if target_fmt == "tsv":    return _ndjson_to_tsv(rows)
        if target_fmt == "xml":    return _ndjson_to_xml(rows)
        if target_fmt == "yaml":   return _ndjson_to_yaml(rows)
        if target_fmt == "toml":   return _ndjson_to_toml(rows)

    # ── XML ──────────────────────────────────────────────────────────────────
    if source_fmt == "xml":
        element = _parse_xml(data)
        if target_fmt == "json":   return _xml_to_json(element)
        if target_fmt == "csv":    return _xml_to_csv(element)
        if target_fmt == "tsv":    return _xml_to_tsv(element)
        # For yaml/ndjson/toml: convert via JSON as intermediate
        _xml_as_dict = json.loads(_xml_to_json(element))
        if target_fmt == "yaml":   return _json_to_yaml(_xml_as_dict)
        if target_fmt == "ndjson": return _json_to_ndjson(_xml_as_dict)
        if target_fmt == "toml":   return _json_to_toml(_xml_as_dict)

    # ── YAML ─────────────────────────────────────────────────────────────────
    if source_fmt == "yaml":
        parsed = _parse_yaml(data)
        if target_fmt == "json":   return _yaml_to_json(parsed)
        if target_fmt == "csv":    return _yaml_to_csv(parsed)
        if target_fmt == "tsv":    return _yaml_to_tsv(parsed)
        if target_fmt == "xml":    return _yaml_to_xml(parsed)
        if target_fmt == "ndjson": return _yaml_to_ndjson(parsed)
        if target_fmt == "toml":   return _yaml_to_toml(parsed)

    # ── TOML ─────────────────────────────────────────────────────────────────
    if source_fmt == "toml":
        parsed = _parse_toml(data)
        if target_fmt == "json":   return _toml_to_json(parsed)
        if target_fmt == "csv":    return _toml_to_csv(parsed)
        if target_fmt == "tsv":    return _toml_to_tsv(parsed)
        if target_fmt == "xml":    return _toml_to_xml(parsed)
        if target_fmt == "yaml":   return _toml_to_yaml(parsed)
        if target_fmt == "ndjson": return _toml_to_ndjson(parsed)

    # ── HTML table ───────────────────────────────────────────────────────────
    if source_fmt == "html":
        rows = _parse_html_table(data)
        return _rows_to_target(rows, target_fmt)

    raise DataMorphError(
        f"Conversion path {source_fmt} → {target_fmt} is not implemented."
    )


def convert_file(
    input_path: str,
    output_path: str,
    source_fmt: str | None = None,
    target_fmt: str | None = None,
    sheet: str | int | None = None,
) -> None:
    """
    Convert the file at *input_path* and write result to *output_path*.

    Formats are auto-detected from extensions unless overridden.
    For .xlsx files, uses convert_xlsx() automatically.

    Parameters
    ----------
    input_path : str
        Path to source file.
    output_path : str
        Path for output file (directories created if needed).
    source_fmt : str, optional
        Override source format detection.
    target_fmt : str, optional
        Override target format detection.
    sheet : str or int, optional
        For .xlsx files: sheet name or 0-based index.

    Raises
    ------
    FileNotFoundError
        If *input_path* does not exist.
    DataMorphError
        On any conversion error.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    src = source_fmt or detect_format(input_path)
    tgt = target_fmt or detect_format(output_path)

    # Excel is binary — special path
    if src == "xlsx":
        convert_xlsx(input_path, tgt, output_path=output_path, sheet=sheet)
        return

    with open(input_path, "r", encoding="utf-8") as fh:
        data = fh.read()

    result = convert(data, src, tgt)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(result)
