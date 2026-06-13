"""RouterShell legacy library package."""

from __future__ import annotations

import sys
from pathlib import Path

_LIB_PATH = Path(__file__).resolve().parent
_LIB_PATH_STR = str(_LIB_PATH)

if _LIB_PATH_STR not in sys.path:
    sys.path.insert(0, _LIB_PATH_STR)
