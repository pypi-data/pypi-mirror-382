"""
Canonical name standardization for company name fuzzy matching.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Dict, List

import pandas as pd
import yaml


# Use centralized config - no local duplication


def create_canonical_name(name: str) -> str:
    """
    Create a canonical version of a company name for fuzzy matching.
    
    Standardizes:
    - Case (to lowercase)
    - Unicode normalization (NFD)
    - Removes non-ASCII characters
    - Removes extra whitespace
    - Standardizes common punctuation
    - KEEPS all legal suffixes (Inc., Corp., LLC, etc.)
    """
    if pd.isna(name) or name == '':
        return ''
    
    # Convert to string and strip
    canonical = str(name).strip()
    
    # Unicode normalization (decompose accented characters)
    canonical = unicodedata.normalize('NFD', canonical)
    
    # Remove non-ASCII characters (keep only ASCII letters, numbers, spaces, and basic punctuation)
    canonical = ''.join(char for char in canonical if ord(char) < 128)
    
    # Convert to lowercase
    canonical = canonical.lower()
    
    # Remove extra whitespace
    canonical = re.sub(r'\s+', ' ', canonical)
    
    # Standardize common punctuation (be conservative)
    canonical = re.sub(r'[.,;:!?]+', ' ', canonical)  # Multiple punctuation -> space
    canonical = re.sub(r'[&]', ' and ', canonical)   # & -> and
    canonical = re.sub(r'[+]', ' plus ', canonical)  # + -> plus
    canonical = re.sub(r'[@]', ' at ', canonical)     # @ -> at
    canonical = re.sub(r'[%]', ' percent ', canonical) # % -> percent
    canonical = re.sub(r'[$]', ' dollar ', canonical) # $ -> dollar
    
    # Remove periods from abbreviations (S.R.O. -> SRO, L.L.C. -> LLC)
    canonical = re.sub(r'\.', '', canonical)  # Remove all periods
    
    # Load abbreviations once
    if not hasattr(create_canonical_name, 'abbreviations'):
        from goodgleif.config import load_abbreviation_config
        create_canonical_name.abbreviations = load_abbreviation_config()

    # Apply abbreviation standardizations
    for std_form, patterns in create_canonical_name.abbreviations.items():
        for pattern in patterns:
            # Convert pattern to regex, handling spaces and periods flexibly
            # \b ensures word boundaries, \s* allows zero or more spaces
            regex_pattern = r'\b' + r'\s*'.join(re.escape(c) for c in pattern) + r'\b'
            canonical = re.sub(regex_pattern, std_form, canonical, flags=re.IGNORECASE)
    
    # Clean up extra spaces but KEEP all legal suffixes
    canonical = re.sub(r'\s+', ' ', canonical)      # Multiple spaces -> single space
    canonical = canonical.strip()
    
    return canonical.strip()


def create_brief_name(name: str) -> str:
    """
    Create a brief version of a company name by removing legal suffixes.
    
    This is more aggressive than canonical_name and removes common legal suffixes
    to get to the core business name.
    """
    if pd.isna(name) or name == '':
        return ''
    
    # Start with canonical name
    brief = create_canonical_name(name)
    
    # Remove common legal suffixes (more aggressive)
    legal_suffixes = [
        r'\b(inc|incorporated|corp|corporation|llc|ltd|limited|l\.l\.c\.|l\.p\.|lp|llp|l\.l\.p\.)\b',
        r'\b(sa|s\.a\.|srl|s\.r\.l\.|sro|s\.r\.o\.|gmbh|ag|a\.g\.|bv|b\.v\.|nv|n\.v\.)\b',
        r'\b(plc|p\.l\.c\.|pte|p\.t\.e\.|pvt|p\.v\.t\.|private|public)\b',
        r'\b(co|company|comp|companies|group|holdings|holding|enterprises|enterprise)\b',
    ]
    
    for suffix_pattern in legal_suffixes:
        brief = re.sub(suffix_pattern, '', brief, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    brief = re.sub(r'\s+', ' ', brief)
    brief = brief.strip()
    
    return brief
