"""Test path setup for chapter05 samples."""
from __future__ import annotations

import sys
from pathlib import Path


CHAPTER_ROOT = Path(__file__).resolve().parents[1]
if str(CHAPTER_ROOT) not in sys.path:
    sys.path.insert(0, str(CHAPTER_ROOT))
