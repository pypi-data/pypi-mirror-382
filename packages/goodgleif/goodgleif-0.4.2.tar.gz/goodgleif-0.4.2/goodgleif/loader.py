from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from goodgleif.paths import default_parquet_path, default_download_csv_path, resolve_input_csv


def load_gleif_csv(csv_path: Path | str | None = None, nrows: Optional[int] = None) -> pd.DataFrame:
    """Load the local raw GLEIF CSV.

    Args:
        csv_path: Path to the raw CSV. Defaults to repo-local data at `data_local/gleif.csv`.
        nrows: Optional row limit for faster dev/testing.

    Returns:
        DataFrame with the raw columns from GLEIF (no normalization here).
    """
    path = Path(csv_path) if csv_path is not None else None
    resolved = resolve_input_csv(path)
    return pd.read_csv(resolved, nrows=nrows)


def write_parquet(df: pd.DataFrame, out_path: Path | str | None = None) -> None:
    """Write a DataFrame to Parquet using pyarrow.

    Args:
        df: Frame to save
        out_path: Output parquet file path
    """
    out = Path(out_path) if out_path is not None else default_parquet_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, engine="pyarrow", index=False)


def build_small_csv(
    csv_path: Path | str | None = None,
    out_path: Path | str | None = None,
    n: int = 2000,
) -> Path:
    """Create a smaller CSV sample for tests/debugging.

    Args:
        csv_path: Source CSV path
        out_path: Destination sample CSV path
        n: Number of rows to include

    Returns:
        The path to the created sample CSV
    """
    src = Path(csv_path) if csv_path is not None else default_download_csv_path()
    
    if not src.exists():
        raise FileNotFoundError(f"Source CSV not found: {src}")
    df = load_gleif_csv(src, nrows=n)
    out = Path(out_path) if out_path is not None else (src.with_name("gleif_small.csv"))
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    return out


