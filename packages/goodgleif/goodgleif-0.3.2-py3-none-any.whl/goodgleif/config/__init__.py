"""Configuration management for GoodGleif.

This module provides access to YAML configuration files used throughout the package.
"""

from pathlib import Path
from typing import Dict, List, Any
import yaml


def get_config_dir() -> Path:
    """Get the configuration directory path."""
    return Path(__file__).parent


def load_abbreviation_config() -> Dict[str, List[str]]:
    """Load abbreviation standardizations from config file."""
    config_path = get_config_dir() / "abbreviation_standardizations.yaml"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Fallback to hardcoded patterns if config file doesn't exist
        return {
            'llc': ['l l c', 'l.l.c', 'l l c.', 'l.l.c.'],
            'sro': ['s r o', 's.r.o', 's r o.', 's.r.o.'],
            'as': ['a s', 'a.s', 'a s.', 'a.s.'],
            'ab': ['a b', 'a.b', 'a b.', 'a.b.'],
            'ag': ['a g', 'a.g', 'a g.', 'a.g.'],
            'sa': ['s a', 's.a', 's a.', 's.a.'],
            'srl': ['s r l', 's.r.l', 's r l.', 's.r.l.'],
            'spa': ['s p a', 's.p.a', 's p a.', 's.p.a.'],
            'doo': ['d o o', 'd.o.o', 'd o o.', 'd.o.o.'],
            'sarl': ['s a r l', 's.a.r.l', 's a r l.', 's.a.r.l.'],
            'kft': ['k f t', 'k.f.t', 'k f t.', 'k.f.t.'],
            'inc': ['i n c', 'i.n.c', 'i n c.', 'i.n.c.'],
            'corp': ['c o r p', 'c.o.r.p', 'c o r p.', 'c.o.r.p.'],
            'ltd': ['l t d', 'l.t.d', 'l t d.', 'l.t.d.'],
            'gmbh': ['g m b h', 'g.m.b.h', 'g m b h.', 'g.m.b.h.'],
            'bv': ['b v', 'b.v', 'b v.', 'b.v.'],
            'nv': ['n v', 'n.v', 'n v.', 'n.v.'],
            'plc': ['p l c', 'p.l.c', 'p l c.', 'p.l.c.'],
            'pvt': ['p v t', 'p.v.t', 'p v t.', 'p.v.t.'],
            'sl': ['s l', 's.l', 's l.', 's.l.'],
            'ltda': ['l t d a', 'l.t.d.a', 'l t d a.', 'l.t.d.a.'],
            'ao': ['a o', 'a.o', 'a o.', 'a.o.'],
            'ooo': ['o o o', 'o.o.o', 'o o o.', 'o.o.o.'],
            'kk': ['k k', 'k.k', 'k k.', 'k.k.'],
            'yk': ['y k', 'y.k', 'y k.', 'y.k.'],
            'yxgs': ['y x g s', 'y.x.g.s', 'y x g s.', 'y.x.g.s.']
        }


def load_classification_config() -> Dict[str, List[str]]:
    """Load classification flags configuration from config file."""
    config_path = get_config_dir() / "classification_flags.yaml"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Fallback to default classification patterns
        return {
            'probably_metals_and_mining': [
                'mining', 'mine', 'gold', 'silver', 'copper', 'iron', 'steel',
                'coal', 'oil', 'gas', 'petroleum', 'energy', 'metals', 'ore',
                'mineral', 'extraction', 'drilling', 'exploration'
            ],
            'probably_financial': [
                'bank', 'financial', 'investment', 'capital', 'fund', 'trust',
                'insurance', 'credit', 'finance', 'securities', 'trading',
                'asset', 'wealth', 'advisory', 'brokerage'
            ],
            'probably_technology': [
                'technology', 'software', 'tech', 'digital', 'computer',
                'internet', 'data', 'cloud', 'ai', 'artificial intelligence',
                'machine learning', 'cyber', 'information', 'systems'
            ],
            'probably_healthcare': [
                'health', 'medical', 'pharmaceutical', 'biotech', 'drug',
                'medicine', 'hospital', 'clinic', 'therapy', 'treatment',
                'diagnostic', 'healthcare', 'wellness'
            ],
            'probably_automotive': [
                'automotive', 'auto', 'vehicle', 'car', 'truck', 'motor',
                'transportation', 'mobility', 'electric vehicle', 'ev'
            ],
            'probably_transportation': [
                'transport', 'shipping', 'logistics', 'freight', 'cargo',
                'airline', 'airways', 'railway', 'railroad', 'delivery'
            ],
            'probably_real_estate': [
                'real estate', 'property', 'construction', 'building',
                'development', 'housing', 'commercial', 'residential'
            ],
            'probably_manufacturing': [
                'manufacturing', 'production', 'industrial', 'factory',
                'assembly', 'machinery', 'equipment', 'tools'
            ],
            'probably_retail_consumer': [
                'retail', 'consumer', 'shopping', 'store', 'market',
                'commerce', 'ecommerce', 'fashion', 'apparel'
            ]
        }


def get_config_path(config_name: str) -> Path:
    """Get the path to a configuration file.
    
    Args:
        config_name: Name of the config file (without .yaml extension)
        
    Returns:
        Path to the configuration file
    """
    return get_config_dir() / f"{config_name}.yaml"


__all__ = [
    'get_config_dir',
    'load_abbreviation_config',
    'load_classification_config', 
    'get_config_path'
]
