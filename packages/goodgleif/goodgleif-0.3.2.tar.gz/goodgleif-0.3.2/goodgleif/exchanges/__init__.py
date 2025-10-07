"""Exchange data loaders for major stock exchanges.

This module provides loaders for company lists from major stock exchanges.
Each exchange has its own loader with a consistent interface.

Available exchanges:
- ASX (Australian Securities Exchange)
- LSE (London Stock Exchange)
- TSX (Toronto Stock Exchange)

Usage:
    from goodgleif.exchanges import load_asx, load_lse, load_tsx
    from goodgleif.exchanges import sample_asx_data, sample_lse_data, sample_tsx_data
"""

from .base import ExchangeLoader
from .asx import ASXLoader
from .lse import LSELoader
from .tsx import TSXLoader

__all__ = [
    "ExchangeLoader",
    "ASXLoader",
    "LSELoader",
    "TSXLoader",
]
