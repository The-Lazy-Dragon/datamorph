"""conftest.py — adds src/ to sys.path for tearyu-datamorph tests."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
