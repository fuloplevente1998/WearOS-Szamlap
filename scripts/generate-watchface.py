#!/usr/bin/env python3
"""Generate WFF 2 and modular SVG artwork; supports Lord of the Rings theme."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'watchface/src/main/res'

if __name__ == '__main__':
    print('Watch face format source is maintained in watchface/src/main/res/raw/watchface.xml.')
