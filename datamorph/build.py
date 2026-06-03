#!/usr/bin/env python3
"""
build.py — tearyu-datamorph .exe builder
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Run: python build.py

Produces: dist/tearyu-datamorph.exe  (Windows)
          dist/tearyu-datamorph      (Linux/Mac)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))

def run(cmd):
    print(f"\n  $ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=ROOT)
    if result.returncode != 0:
        print(f"\n  ✘ Command failed with code {result.returncode}")
        sys.exit(result.returncode)

def main():
    print("""
  ____        _        __  __                  _
 |  _ \\  __ _| |_ __ _|  \\/  | ___  _ __ _ __ | |__
 | | | |/ _` | __/ _` | |\\/| |/ _ \\| '__| '_ \\| '_ \\
 | |_| | (_| | || (_| | |  | | (_) | |  | |_) | | | |
 |____/ \\__,_|\\__\\__,_|_|  |_|\\___/|_|  | .__/|_| |_|
                                          |_|

  tearyu-datamorph — .exe build script
  怠竜 Tearyū / The Lazy Dragon
""")

    # Step 1: Install PyInstaller if needed
    try:
        import PyInstaller
        print("  ✔ PyInstaller already installed")
    except ImportError:
        print("  Installing PyInstaller...")
        run("pip install pyinstaller")

    # Step 2: Clean previous build
    import shutil
    for d in ["dist", "build"]:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"  ✔ Cleaned {d}/")

    # Step 3: Build
    print("\n  Building .exe...")
    run("pyinstaller tearyu-datamorph.spec --noconfirm")

    # Step 4: Verify
    exe_name = "tearyu-datamorph.exe" if sys.platform == "win32" else "tearyu-datamorph"
    exe_path = os.path.join("dist", exe_name)

    if os.path.isfile(exe_path):
        size = os.path.getsize(exe_path)
        size_mb = size / 1024 / 1024
        print(f"""
  ✔ Build complete!
    Output : dist/{exe_name}
    Size   : {size_mb:.1f} MB

  Usage:
    GUI mode : dist/{exe_name}
    CLI mode : dist/{exe_name} input.csv output.json
    CLI mode : dist/{exe_name} input.json output.xml --verbose
""")
    else:
        print("\n  ✘ Build may have failed — check output above")
        sys.exit(1)

if __name__ == "__main__":
    main()
