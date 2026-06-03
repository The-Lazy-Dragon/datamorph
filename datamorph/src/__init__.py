"""
datamorph
─────────────────────────────────────────────────────────────────────────────
The Lazy Dragon's DataMorph
Convert between CSV, JSON, and XML — production-grade, zero dependencies.

Author : The Lazy Dragon (怠竜 Tearyū)
GitHub : https://github.com/The-Lazy-Dragon
─────────────────────────────────────────────────────────────────────────────

Quick start
-----------
>>> from datamorph import convert, convert_file, detect_format
>>> result = convert('[{"name":"Ryūen","role":"竜王"}]', "json", "csv")
>>> print(result)
name,role
Ryūen,竜王

>>> convert_file("records.json", "records.xml")
"""

from datamorph import (
    DataMorphError,
    convert,
    convert_file,
    detect_format,
)

__all__ = [
    "convert",
    "convert_file",
    "detect_format",
    "DataMorphError",
]

__version__ = "1.0.0"
__author__  = "The Lazy Dragon (怠竜 Tearyū)"
__url__     = "https://github.com/The-Lazy-Dragon/tearyu-datamorph"
