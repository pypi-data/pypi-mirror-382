from __future__ import annotations

import os
import tempfile
from contextlib import contextmanager
from importlib.resources import as_file, files
from pathlib import Path
from typing import Iterator, Optional

from platformdirs import user_cache_dir



APP_NAME = "goodgleif"
ENV_DATA_DIR = "GOODGLEIF_DATA_DIR"
RESOURCE_PKG = "goodgleif.data"


@contextmanager
def open_resource_path(relpath: str | Path) -> Iterator[Path]:
    resource = files(RESOURCE_PKG).joinpath(str(relpath))
    if not resource.is_file():
        raise FileNotFoundError(f"Resource not found: {relpath!s}")
    with as_file(resource) as p:
        yield p


def read_resource_bytes(relpath: str | Path) -> bytes:
    resource = files(RESOURCE_PKG).joinpath(str(relpath))
    if not resource.is_file():
        raise FileNotFoundError(f"Resource not found: {relpath!s}")
    return resource.read_bytes()


def get_writable_dir() -> Path:
    candidates = []
    env = os.getenv(ENV_DATA_DIR)
    if env:
        candidates.append(Path(env).expanduser())
    candidates.append(Path(user_cache_dir(APP_NAME)))
    candidates.append(Path(tempfile.gettempdir()) / APP_NAME)

    for d in candidates:
        try:
            d.mkdir(parents=True, exist_ok=True)
            probe = d / ".write_test"
            probe.touch(exist_ok=True)
            probe.unlink(missing_ok=True)
            return d
        except Exception:
            continue
    raise RuntimeError("No writable directory available")


def default_parquet_path() -> Path:
    return get_writable_dir() / "gleif.parquet"


def default_download_csv_path() -> Path:
    return get_writable_dir() / "gleif.csv"


def resolve_input_csv(user_path: Optional[Path] = None) -> Path:
    if user_path:
        p = Path(user_path).expanduser()
        if p.exists():
            return p
        raise FileNotFoundError(p)

    env_dir = os.getenv(ENV_DATA_DIR)
    if env_dir:
        p = Path(env_dir).expanduser() / "gleif.csv"
        if p.exists():
            return p

    # Check default writable location created by debug helpers
    default_csv = default_download_csv_path()
    if default_csv.exists():
        return default_csv

    try:
        with open_resource_path("seed/gleif.csv") as p:
            return p
    except FileNotFoundError:
        pass

    raise FileNotFoundError(
        "No input CSV found. Provide --csv PATH, set GOODGLEIF_DATA_DIR, or ship seed/gleif.csv."
    )



