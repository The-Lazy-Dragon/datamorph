#!/usr/bin/env python3
"""
tearyu-datamorph/datamorph_cli.py
─────────────────────────────────────────────────────────────────────────────
The Lazy Dragon's DataMorph — CLI
Author : The Lazy Dragon (怠竜 Tearyū)
GitHub : https://github.com/The-Lazy-Dragon
─────────────────────────────────────────────────────────────────────────────
Usage:
  datamorph input.csv output.json
  datamorph input.json output.xml --verbose
  datamorph --from json --to csv < input.json > output.csv
  datamorph input.xml output.json --verbose
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from datamorph import DataMorphError, convert, convert_file, convert_xlsx, detect_format

# ─────────────────────────────────────────────────────────────────────────────
# ANSI colour helpers
# ─────────────────────────────────────────────────────────────────────────────

_USE_COLOUR = sys.stderr.isatty()


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOUR else text


def cyan(t: str) -> str:    return _c(t, "96")
def red(t: str) -> str:     return _c(t, "91")
def yellow(t: str) -> str:  return _c(t, "93")
def dim(t: str) -> str:     return _c(t, "2")
def bold(t: str) -> str:    return _c(t, "1")
def green(t: str) -> str:   return _c(t, "92")


# ─────────────────────────────────────────────────────────────────────────────
# BANNER
# ─────────────────────────────────────────────────────────────────────────────

BANNER = r"""
  ____        _        __  __                  _
 |  _ \  __ _| |_ __ _|  \/  | ___  _ __ _ __ | |__
 | | | |/ _` | __/ _` | |\/| |/ _ \| '__| '_ \| '_ \
 | |_| | (_| | || (_| | |  | | (_) | |  | |_) | | | |
 |____/ \__,_|\__\__,_|_|  |_|\___/|_|  | .__/|_| |_|
                                         |_|
"""


def print_banner() -> None:
    print(cyan(BANNER), file=sys.stderr)
    print(
        dim("  怠竜 Tearyū / The Lazy Dragon  ─  github.com/The-Lazy-Dragon\n"),
        file=sys.stderr,
    )


# ─────────────────────────────────────────────────────────────────────────────
# ARGUMENT PARSER
# ─────────────────────────────────────────────────────────────────────────────

_FMT_CHOICES = ["csv", "tsv", "json", "ndjson", "xml", "yaml", "toml", "xlsx", "html"]

EPILOG = """
examples:
  # File-to-file (formats auto-detected from extensions)
  datamorph data.csv out.json
  datamorph data.xml out.csv
  datamorph records.json output.xml

  # Override formats explicitly
  datamorph myfile.txt out.txt --from csv --to json

  # Read from stdin, write to stdout
  datamorph --from json --to xml < input.json > output.xml

  # Verbose mode shows a summary
  datamorph large.json out.csv --verbose
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="datamorph",
        description="datamorph — Convert CSV/TSV/JSON/NDJSON/XML/YAML/TOML/XLSX/HTML — by The Lazy Dragon (怠竜 Tearyū)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EPILOG,
    )

    parser.add_argument(
        "input",
        nargs="?",
        help="Input file path (omit to read from stdin)",
    )
    parser.add_argument(
        "output",
        nargs="?",
        help="Output file path (omit to write to stdout)",
    )
    parser.add_argument(
        "--from", dest="source_fmt",
        choices=_FMT_CHOICES,
        metavar="FORMAT",
        help="Force source format (csv|json|xml). Auto-detected if omitted.",
    )
    parser.add_argument(
        "--to", dest="target_fmt",
        choices=_FMT_CHOICES,
        metavar="FORMAT",
        help="Force target format (csv|json|xml). Auto-detected if omitted.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print conversion summary to stderr",
    )
    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Suppress the ASCII banner",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="datamorph 1.1.0",
    )
    return parser


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _fmt_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 ** 2:
        return f"{n / 1024:.1f} KB"
    return f"{n / 1024**2:.2f} MB"


def _detect_src(args: argparse.Namespace, raw: str) -> str:
    if args.source_fmt:
        return args.source_fmt
    if args.input:
        return detect_format(args.input)
    return detect_format(raw)


def _detect_tgt(args: argparse.Namespace) -> str:
    if args.target_fmt:
        return args.target_fmt
    if args.output:
        return detect_format(args.output)
    raise DataMorphError(
        "Cannot detect target format — no output file given and --to not specified."
    )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.no_banner:
        print_banner()

    try:
        t0 = time.perf_counter()

        # ── Determine I/O mode ──────────────────────────────────────────────
        reading_stdin = args.input is None
        writing_stdout = args.output is None

        # Detect source format early to handle xlsx (binary) specially
        src_fmt = args.source_fmt or (detect_format(args.input) if args.input else None)
        tgt_fmt = _detect_tgt(args)

        # ── Excel binary path ───────────────────────────────────────────────
        if src_fmt == "xlsx":
            if reading_stdin:
                raise DataMorphError("Excel (.xlsx) files cannot be read from stdin — provide a file path.")
            if not os.path.isfile(args.input):
                raise FileNotFoundError(f"Input file not found: {args.input}")

            if args.verbose:
                print(f"  {bold('→')} {cyan('XLSX')}  {bold('⟶')}  {cyan(tgt_fmt.upper())}", file=sys.stderr)
                print(f"  {dim('input :')} {args.input}", file=sys.stderr)

            result = convert_xlsx(args.input, tgt_fmt, output_path=args.output if not writing_stdout else None)

            if writing_stdout:
                sys.stdout.write(result)

            elapsed = (time.perf_counter() - t0) * 1000
            if args.verbose:
                out_label = args.output or "<stdout>"
                print(f"  {dim('output:')} {out_label}", file=sys.stderr)
                print(f"  {green('✔')} Done in {elapsed:.1f} ms", file=sys.stderr)

            return 0

        # ── Text path (all other formats) ───────────────────────────────────
        if reading_stdin:
            raw = sys.stdin.read()
        else:
            if not os.path.isfile(args.input):
                raise FileNotFoundError(f"Input file not found: {args.input}")
            with open(args.input, "r", encoding="utf-8") as fh:
                raw = fh.read()

        if src_fmt is None:
            src_fmt = detect_format(raw)

        if args.verbose:
            src_label = args.input or "<stdin>"
            print(
                f"  {bold('→')} {cyan(src_fmt.upper())}  {bold('⟶')}  {cyan(tgt_fmt.upper())}",
                file=sys.stderr,
            )
            print(f"  {dim('input :')} {src_label}", file=sys.stderr)

        result = convert(raw, src_fmt, tgt_fmt)

        if writing_stdout:
            sys.stdout.write(result)
        else:
            os.makedirs(
                os.path.dirname(os.path.abspath(args.output)) or ".", exist_ok=True
            )
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(result)

        elapsed = (time.perf_counter() - t0) * 1000

        if args.verbose:
            out_label = args.output or "<stdout>"
            print(f"  {dim('output:')} {out_label}", file=sys.stderr)
            print(
                f"  {green('✔')} Done in {elapsed:.1f} ms"
                f"  {dim('|')} {_fmt_size(len(raw.encode()))} → {_fmt_size(len(result.encode()))}",
                file=sys.stderr,
            )

        return 0

    except FileNotFoundError as exc:
        print(f"  {red('✘ FILE ERROR:')} {exc}", file=sys.stderr)
        return 2
    except DataMorphError as exc:
        print(f"  {red('✘ CONVERSION ERROR:')} {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(f"\n  {yellow('⚠')} Interrupted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
