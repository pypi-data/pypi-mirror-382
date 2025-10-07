from __future__ import annotations

from pathlib import Path
from typing import Optional


def get_project_root(start: Optional[Path] = None) -> Path:
    """Return the top-level project directory by walking upwards.

    We detect the root as the first directory containing `.git` or `pyproject.toml`.
    Falls back to two levels above this file, which is `.../goodgleif/` repo root.
    """
    here = Path(start) if start is not None else Path(__file__).resolve()
    cur = here if here.is_dir() else here.parent
    for parent in [cur] + list(cur.parents):
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
            return parent
    return here.parents[2]
