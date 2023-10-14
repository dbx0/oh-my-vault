#!/usr/bin/env python
import sys

REQUIRED_PYVERSION = "3.9"
PYVERSION = f"{sys.version_info.major}.{sys.version_info.minor}"

if PYVERSION > REQUIRED_PYVERSION:
    sys.exit(f"[!] Incompatible Python version. Python {REQUIRED_PYVERSION}+ required, Python {PYVERSION} found.")

dependencies = [
    "requests",
    "colorama"
]

missing = []

for dependency in dependencies:    
    try:
        __import__(dependency)
    except ImportError:
        missing.append(dependency)

if missing:
    sys.exit(f"[!] Missing one or more core dependencies: {','.join(missing)}")