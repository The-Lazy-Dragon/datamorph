"""
tests/test_datamorph.py
─────────────────────────────────────────────────────────────────────────────
Test suite for tearyu-datamorph
─────────────────────────────────────────────────────────────────────────────
Run:
    cd tearyu-datamorph
    python -m pytest tests/ -v
─────────────────────────────────────────────────────────────────────────────
"""

import json
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datamorph import (
    DataMorphError,
    convert,
    detect_format,
    _flatten,
    _safe_tag,
)


# ─────────────────────────────────────────────────────────────────────────────
# FORMAT DETECTION
# ─────────────────────────────────────────────────────────────────────────────

class TestDetectFormat:
    def test_csv_extension(self):
        assert detect_format("data.csv") == "csv"

    def test_json_extension(self):
        assert detect_format("data.json") == "json"

    def test_xml_extension(self):
        assert detect_format("data.xml") == "xml"

    def test_csv_content_sniff(self):
        csv_content = "name,age,city\nAlice,30,NY\nBob,25,LA"
        assert detect_format(csv_content) == "csv"

    def test_json_content_sniff_array(self):
        assert detect_format('[{"a":1}]') == "json"

    def test_json_content_sniff_object(self):
        assert detect_format('{"key":"val"}') == "json"

    def test_xml_content_sniff(self):
        assert detect_format("<root><item>x</item></root>") == "xml"

    def test_unknown_raises(self):
        with pytest.raises(DataMorphError):
            detect_format("this is just random unstructured text")


# ─────────────────────────────────────────────────────────────────────────────
# CSV → JSON
# ─────────────────────────────────────────────────────────────────────────────

class TestCsvToJson:
    def test_basic(self):
        csv = "name,age\nAlice,30\nBob,25"
        result = json.loads(convert(csv, "csv", "json"))
        assert result == [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]

    def test_utf8_characters(self):
        csv = "名前,役職\n竜炎,竜王\n黒影,滅竜"
        result = json.loads(convert(csv, "csv", "json"))
        assert result[0]["名前"] == "竜炎"
        assert result[1]["役職"] == "滅竜"

    def test_quoted_fields_with_commas(self):
        csv = 'name,description\nAlice,"loves cats, dogs"\nBob,simple'
        result = json.loads(convert(csv, "csv", "json"))
        assert result[0]["description"] == "loves cats, dogs"

    def test_empty_field_preserved(self):
        csv = "a,b,c\n1,,3"
        result = json.loads(convert(csv, "csv", "json"))
        assert result[0]["b"] == ""

    def test_single_row(self):
        csv = "x,y\n10,20"
        result = json.loads(convert(csv, "csv", "json"))
        assert len(result) == 1

    def test_empty_csv_raises(self):
        with pytest.raises(DataMorphError, match="empty"):
            convert("name,age\n", "csv", "json")

    def test_bom_stripped(self):
        csv = "\ufeffname,val\ntest,1"
        result = json.loads(convert(csv, "csv", "json"))
        assert "name" in result[0]


# ─────────────────────────────────────────────────────────────────────────────
# CSV → XML
# ─────────────────────────────────────────────────────────────────────────────

class TestCsvToXml:
    def test_basic_structure(self):
        csv = "name,age\nAlice,30"
        result = convert(csv, "csv", "xml")
        assert "<records>" in result
        assert "<record>" in result
        assert "<name>Alice</name>" in result
        assert "<age>30</age>" in result

    def test_multiple_rows(self):
        csv = "id,val\n1,a\n2,b\n3,c"
        result = convert(csv, "csv", "xml")
        assert result.count("<record>") == 3

    def test_special_chars_in_values(self):
        csv = "note\n<test>&value"
        result = convert(csv, "csv", "xml")
        # XML escaping should be applied
        assert "&lt;" in result or "<note>" in result  # ElementTree escapes


# ─────────────────────────────────────────────────────────────────────────────
# JSON → CSV
# ─────────────────────────────────────────────────────────────────────────────

class TestJsonToCsv:
    def test_flat_array(self):
        data = '[{"name":"Alice","age":"30"},{"name":"Bob","age":"25"}]'
        result = convert(data, "json", "csv")
        lines = result.strip().splitlines()
        assert lines[0] == "name,age"
        assert lines[1] == "Alice,30"
        assert lines[2] == "Bob,25"

    def test_nested_flattened(self):
        data = '[{"user":{"name":"Alice","score":99}}]'
        result = convert(data, "json", "csv")
        assert "user.name" in result
        assert "user.score" in result
        assert "Alice" in result

    def test_nested_array_flattened(self):
        data = '[{"tags":["a","b","c"]}]'
        result = convert(data, "json", "csv")
        assert "tags.0" in result
        assert "tags.1" in result

    def test_single_object_converted(self):
        data = '{"name":"Dragon","type":"lazy"}'
        result = convert(data, "json", "csv")
        assert "name" in result
        assert "Dragon" in result

    def test_invalid_root_type_raises(self):
        with pytest.raises(DataMorphError):
            convert('"just a string"', "json", "csv")


# ─────────────────────────────────────────────────────────────────────────────
# JSON → XML
# ─────────────────────────────────────────────────────────────────────────────

class TestJsonToXml:
    def test_array_becomes_records(self):
        data = '[{"id":"1"},{"id":"2"}]'
        result = convert(data, "json", "xml")
        assert "<records>" in result
        assert result.count("<record>") == 2

    def test_dict_becomes_root_children(self):
        data = '{"name":"Dragon","level":99}'
        result = convert(data, "json", "xml")
        assert "<name>Dragon</name>" in result
        assert "<level>99</level>" in result

    def test_nested_dict(self):
        data = '{"player":{"name":"Ryūen","rank":"S"}}'
        result = convert(data, "json", "xml")
        assert "<player>" in result
        assert "<name>Ryūen</name>" in result

    def test_null_value(self):
        data = '[{"name":null}]'
        result = convert(data, "json", "xml")
        # ElementTree may emit self-closing <name/> or <name></name> — both valid
        assert "<name" in result


# ─────────────────────────────────────────────────────────────────────────────
# XML → JSON
# ─────────────────────────────────────────────────────────────────────────────

class TestXmlToJson:
    def test_basic(self):
        xml = "<root><name>Alice</name><age>30</age></root>"
        result = json.loads(convert(xml, "xml", "json"))
        assert result["root"]["name"] == "Alice"
        assert result["root"]["age"] == "30"

    def test_attributes_preserved(self):
        xml = '<root><item id="1" class="hero">Dragon</item></root>'
        result = json.loads(convert(xml, "xml", "json"))
        item = result["root"]["item"]
        assert item["@attributes"]["id"] == "1"
        assert item["@attributes"]["class"] == "hero"
        assert item["#text"] == "Dragon"

    def test_repeated_tags_become_list(self):
        xml = "<root><item>a</item><item>b</item><item>c</item></root>"
        result = json.loads(convert(xml, "xml", "json"))
        assert isinstance(result["root"]["item"], list)
        assert len(result["root"]["item"]) == 3

    def test_nested_elements(self):
        xml = "<roster><player><name>Gorrotxategi</name><goals>18</goals></player></roster>"
        result = json.loads(convert(xml, "xml", "json"))
        player = result["roster"]["player"]
        assert player["name"] == "Gorrotxategi"

    def test_leaf_text(self):
        xml = "<root><val>42</val></root>"
        result = json.loads(convert(xml, "xml", "json"))
        assert result["root"]["val"] == "42"


# ─────────────────────────────────────────────────────────────────────────────
# XML → CSV
# ─────────────────────────────────────────────────────────────────────────────

class TestXmlToCsv:
    def test_uniform_children(self):
        xml = (
            "<records>"
            "<record><name>Alice</name><age>30</age></record>"
            "<record><name>Bob</name><age>25</age></record>"
            "</records>"
        )
        result = convert(xml, "xml", "csv")
        lines = result.strip().splitlines()
        assert lines[0] == "name,age"
        assert "Alice" in result
        assert "Bob" in result

    def test_no_children_raises(self):
        with pytest.raises(DataMorphError):
            convert("<root/>", "xml", "csv")

    def test_flattened_nested(self):
        xml = (
            "<records>"
            "<record><player><name>Ryūen</name></player></record>"
            "</records>"
        )
        result = convert(xml, "xml", "csv")
        assert "player.name" in result or "name" in result


# ─────────────────────────────────────────────────────────────────────────────
# SAME-FORMAT NO-OP
# ─────────────────────────────────────────────────────────────────────────────

class TestNoOp:
    def test_json_to_json(self):
        data = '[{"a":1}]'
        assert convert(data, "json", "json") == data

    def test_csv_to_csv(self):
        data = "a,b\n1,2"
        assert convert(data, "csv", "csv") == data

    def test_xml_to_xml(self):
        data = "<root><x>1</x></root>"
        assert convert(data, "xml", "xml") == data


# ─────────────────────────────────────────────────────────────────────────────
# ERROR HANDLING
# ─────────────────────────────────────────────────────────────────────────────

class TestErrors:
    def test_empty_input(self):
        with pytest.raises(DataMorphError, match="empty"):
            convert("", "csv", "json")

    def test_whitespace_only(self):
        with pytest.raises(DataMorphError, match="empty"):
            convert("   \n\t  ", "json", "csv")

    def test_malformed_json(self):
        with pytest.raises(DataMorphError, match="Malformed JSON"):
            convert("{bad json!!}", "json", "csv")

    def test_malformed_xml(self):
        with pytest.raises(DataMorphError, match="Malformed XML"):
            convert("<unclosed>", "xml", "json")

    def test_bad_source_format(self):
        with pytest.raises(DataMorphError, match="Unsupported source"):
            convert("data", "parquet", "json")

    def test_bad_target_format(self):
        with pytest.raises(DataMorphError, match="Unsupported target"):
            convert('{"a":1}', "json", "avro")


# ─────────────────────────────────────────────────────────────────────────────
# INTERNAL HELPERS
# ─────────────────────────────────────────────────────────────────────────────

class TestFlatten:
    def test_simple(self):
        assert _flatten({"a": 1, "b": 2}) == {"a": "1", "b": "2"}

    def test_nested(self):
        result = _flatten({"a": {"b": {"c": "deep"}}})
        assert result == {"a.b.c": "deep"}

    def test_list(self):
        result = _flatten({"items": [1, 2, 3]})
        assert result["items.0"] == "1"
        assert result["items.2"] == "3"

    def test_none_value(self):
        assert _flatten({"x": None}) == {"x": ""}


class TestSafeTag:
    def test_valid_tag(self):
        assert _safe_tag("name") == "name"

    def test_leading_digit(self):
        assert _safe_tag("1field").startswith("_")

    def test_space_replaced(self):
        assert " " not in _safe_tag("my field")

    def test_empty_fallback(self):
        assert _safe_tag("") == "field"

    def test_slash_replaced(self):
        assert "/" not in _safe_tag("a/b")


# ─────────────────────────────────────────────────────────────────────────────
# ROUND-TRIP TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestRoundTrip:
    """
    These don't guarantee identical output (whitespace, ordering) but do
    guarantee that the data survives a two-hop conversion intact.
    """

    def test_csv_json_csv(self):
        original = "name,score\nAlice,99\nBob,42"
        as_json = convert(original, "csv", "json")
        back = convert(as_json, "json", "csv")
        # Row data should survive
        assert "Alice" in back
        assert "99" in back

    def test_json_xml_json(self):
        original = '[{"player":"Gorrotxategi","goals":"18"}]'
        as_xml = convert(original, "json", "xml")
        back = json.loads(convert(as_xml, "xml", "json"))
        # The data should be reachable somewhere in the tree
        raw = json.dumps(back)
        assert "Gorrotxategi" in raw
        assert "18" in raw

    def test_csv_xml_csv(self):
        original = "id,city\n1,Biratnagar\n2,Tokyo"
        as_xml = convert(original, "csv", "xml")
        back = convert(as_xml, "xml", "csv")
        assert "Biratnagar" in back
        assert "Tokyo" in back


# ─────────────────────────────────────────────────────────────────────────────
# TSV
# ─────────────────────────────────────────────────────────────────────────────

class TestTsv:
    def test_tsv_to_json(self):
        tsv = "name\tscore\nAlice\t99\nBob\t42"
        result = json.loads(convert(tsv, "tsv", "json"))
        assert result[0]["name"] == "Alice"
        assert result[1]["score"] == "42"

    def test_tsv_to_csv(self):
        tsv = "name\tscore\nAlice\t99"
        result = convert(tsv, "tsv", "csv")
        assert "name,score" in result
        assert "Alice,99" in result

    def test_json_to_tsv(self):
        data = '[{"a":"1","b":"2"}]'
        result = convert(data, "json", "tsv")
        assert "\t" in result
        assert "a\tb" in result

    def test_csv_to_tsv(self):
        csv_data = "x,y\n1,2\n3,4"
        result = convert(csv_data, "csv", "tsv")
        assert "x\ty" in result
        assert "1\t2" in result


# ─────────────────────────────────────────────────────────────────────────────
# NDJSON
# ─────────────────────────────────────────────────────────────────────────────

class TestNdjson:
    def test_ndjson_to_json(self):
        ndjson = '{"a":1}\n{"a":2}\n{"a":3}'
        result = json.loads(convert(ndjson, "ndjson", "json"))
        assert len(result) == 3
        assert result[1]["a"] == 2

    def test_ndjson_to_csv(self):
        ndjson = '{"name":"Alice","score":99}\n{"name":"Bob","score":42}'
        result = convert(ndjson, "ndjson", "csv")
        assert "name,score" in result
        assert "Alice" in result

    def test_json_to_ndjson(self):
        data = '[{"x":1},{"x":2}]'
        result = convert(data, "json", "ndjson")
        lines = [l for l in result.splitlines() if l.strip()]
        assert len(lines) == 2
        assert json.loads(lines[0])["x"] == 1

    def test_ndjson_empty_lines_skipped(self):
        ndjson = '{"a":1}\n\n{"a":2}\n'
        result = json.loads(convert(ndjson, "ndjson", "json"))
        assert len(result) == 2

    def test_malformed_ndjson(self):
        with pytest.raises(DataMorphError, match="Malformed NDJSON"):
            convert('{"a":1}\n{bad}', "ndjson", "json")


# ─────────────────────────────────────────────────────────────────────────────
# YAML
# ─────────────────────────────────────────────────────────────────────────────

class TestYaml:
    def test_yaml_to_json(self):
        yaml_data = "- name: Alice\n  score: 99\n- name: Bob\n  score: 42\n"
        result = json.loads(convert(yaml_data, "yaml", "json"))
        assert result[0]["name"] == "Alice"

    def test_yaml_to_csv(self):
        yaml_data = "- name: Alice\n  score: 99\n"
        result = convert(yaml_data, "yaml", "csv")
        assert "name,score" in result
        assert "Alice" in result

    def test_json_to_yaml(self):
        data = '[{"player":"Gorrotxategi","goals":18}]'
        result = convert(data, "json", "yaml")
        assert "player:" in result or "Gorrotxategi" in result

    def test_yaml_to_xml(self):
        yaml_data = "- name: Alice\n  score: 99\n"
        result = convert(yaml_data, "yaml", "xml")
        assert "<name>Alice</name>" in result

    def test_yaml_to_tsv(self):
        yaml_data = "- name: Alice\n  score: 99\n"
        result = convert(yaml_data, "yaml", "tsv")
        assert "\t" in result
        assert "Alice" in result

    def test_malformed_yaml(self):
        with pytest.raises(DataMorphError, match="Malformed YAML"):
            convert("key: [unclosed", "yaml", "json")


# ─────────────────────────────────────────────────────────────────────────────
# TOML
# ─────────────────────────────────────────────────────────────────────────────

class TestToml:
    def test_toml_to_json(self):
        toml_data = '[server]\nhost = "localhost"\nport = 8080\n'
        result = json.loads(convert(toml_data, "toml", "json"))
        assert result["server"]["host"] == "localhost"

    def test_toml_to_csv(self):
        toml_data = '[[records]]\nname = "Alice"\nscore = "99"\n\n[[records]]\nname = "Bob"\nscore = "42"\n'
        result = convert(toml_data, "toml", "csv")
        assert "name" in result
        assert "Alice" in result

    def test_json_to_toml(self):
        data = '[{"name":"Alice","score":"99"}]'
        result = convert(data, "json", "toml")
        assert "[[records]]" in result
        assert "Alice" in result

    def test_toml_to_yaml(self):
        toml_data = 'title = "tearyu-datamorph"\nversion = "1.0.0"\n'
        result = convert(toml_data, "toml", "yaml")
        assert "tearyu-datamorph" in result


# ─────────────────────────────────────────────────────────────────────────────
# HTML TABLE
# ─────────────────────────────────────────────────────────────────────────────

class TestHtmlTable:
    def test_basic_table_to_csv(self):
        html = """<table>
          <tr><th>name</th><th>score</th></tr>
          <tr><td>Alice</td><td>99</td></tr>
          <tr><td>Bob</td><td>42</td></tr>
        </table>"""
        result = convert(html, "html", "csv")
        assert "name,score" in result
        assert "Alice,99" in result

    def test_basic_table_to_json(self):
        html = """<table>
          <tr><th>player</th><th>goals</th></tr>
          <tr><td>Gorrotxategi</td><td>18</td></tr>
        </table>"""
        result = json.loads(convert(html, "html", "json"))
        assert result[0]["player"] == "Gorrotxategi"
        assert result[0]["goals"] == "18"

    def test_table_to_xml(self):
        html = "<table><tr><th>x</th></tr><tr><td>1</td></tr></table>"
        result = convert(html, "html", "xml")
        assert "<x>1</x>" in result

    def test_no_table_raises(self):
        with pytest.raises(DataMorphError, match="No <table>"):
            convert("<html><body><p>no table here</p></body></html>", "html", "json")

    def test_utf8_in_table(self):
        html = "<table><tr><th>名前</th></tr><tr><td>竜炎</td></tr></table>"
        result = json.loads(convert(html, "html", "json"))
        assert result[0]["名前"] == "竜炎"

    def test_excel_style_html(self):
        # Simulates what Excel "Save as HTML" produces
        html = """<html><body>
        <table border=0 cellpadding=0>
        <tr><td>id</td><td>name</td><td>value</td></tr>
        <tr><td>1</td><td>Dragon</td><td>9000</td></tr>
        <tr><td>2</td><td>Ryūen</td><td>8500</td></tr>
        </table></body></html>"""
        result = json.loads(convert(html, "html", "json"))
        assert len(result) == 2
        assert result[0]["name"] == "Dragon"
        assert result[1]["name"] == "Ryūen"


# ─────────────────────────────────────────────────────────────────────────────
# FORMAT DETECTION — new formats
# ─────────────────────────────────────────────────────────────────────────────

class TestDetectFormatNew:
    def test_tsv_extension(self):
        assert detect_format("data.tsv") == "tsv"

    def test_ndjson_extension(self):
        assert detect_format("data.ndjson") == "ndjson"

    def test_jsonl_extension(self):
        assert detect_format("data.jsonl") == "ndjson"

    def test_yaml_extension(self):
        assert detect_format("data.yaml") == "yaml"

    def test_yml_extension(self):
        assert detect_format("data.yml") == "yaml"

    def test_toml_extension(self):
        assert detect_format("data.toml") == "toml"

    def test_xlsx_extension(self):
        assert detect_format("data.xlsx") == "xlsx"

    def test_html_extension(self):
        assert detect_format("data.html") == "html"

    def test_html_content_sniff(self):
        assert detect_format("<html><table><tr><td>x</td></tr></table></html>") == "html"

    def test_ndjson_content_sniff(self):
        assert detect_format('{"a":1}\n{"a":2}\n{"a":3}') == "ndjson"
