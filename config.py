"""Shared configuration for the OneDrive toolkit scripts."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

DEFAULT_ROOT = r"C:\Users\codya\OneDrive"


def get_root(override: Optional[str] = None) -> Path:
    """Resolve the OneDrive root directory.

    Precedence: an explicit override (e.g. a --root CLI argument) wins,
    then the ONEDRIVE_ROOT environment variable, then DEFAULT_ROOT.
    """
    return Path(override or os.environ.get("ONEDRIVE_ROOT", DEFAULT_ROOT))


ROOT = get_root()
