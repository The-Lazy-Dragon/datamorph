"""
setup.py — DataMorph package installer
"""

from setuptools import setup, find_packages
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="tearyu-datamorph",
    version="1.0.0",
    description="Convert between CSV, JSON, and XML — zero dependencies.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="The Lazy Dragon (怠竜 Tearyū)",
    author_email="contact@the-lazy-dragon.dev",
    url="https://github.com/The-Lazy-Dragon/tearyu-datamorph",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "datamorph=datamorph_cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    keywords="csv json xml convert transform data morph cli",
    project_urls={
        "Bug Reports": "https://github.com/The-Lazy-Dragon/tearyu-datamorph/issues",
        "Source":      "https://github.com/The-Lazy-Dragon/tearyu-datamorph",
    },
)
