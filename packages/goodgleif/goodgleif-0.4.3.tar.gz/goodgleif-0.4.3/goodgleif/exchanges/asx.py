"""ASX (Australian Securities Exchange) data loader."""

from __future__ import annotations
from typing import Optional
import pandas as pd
import requests
from io import StringIO

from .base import ExchangeLoader


class ASXLoader(ExchangeLoader):
    """Loader for ASX (Australian Securities Exchange) data."""
    
    def __init__(self):
        super().__init__("ASX", "AU")
        self.url = "https://www.asx.com.au/asx/research/ASXListedCompanies.csv"
    
    def load_data(self, cache_dir: Optional[str] = None) -> pd.DataFrame:
        """Load ASX listed companies from official CSV.
        
        Data source: https://www.asx.com.au/asx/research/ASXListedCompanies.csv
        Format: CSV, updated regularly
        
        Returns:
            DataFrame with columns:
            - ticker: ASX ticker code
            - name: Company name
            - country: Always 'AU'
            - exchange: Always 'ASX'
            - industry: GICS industry classification (if available)
        """
        try:
            response = requests.get(self.url, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            
            # Parse CSV - skip first few metadata rows
            lines = response.text.split('\n')
            # Find the header line (starts with "ASX code" or "Company name")
            header_idx = 0
            for i, line in enumerate(lines):
                if 'ASX code' in line or 'Company name' in line:
                    header_idx = i
                    break
            
            # Read from header line onwards
            csv_content = '\n'.join(lines[header_idx:])
            df = pd.read_csv(StringIO(csv_content))
            
            # Normalize column names
            df.columns = df.columns.str.strip()
            column_mapping = {}
            for col in df.columns:
                col_lower = col.lower().strip()
                if 'asx code' in col_lower or 'code' in col_lower:
                    column_mapping[col] = 'ticker'
                elif 'company name' in col_lower or 'name' in col_lower:
                    column_mapping[col] = 'name'
                elif 'industry' in col_lower or 'sector' in col_lower:
                    column_mapping[col] = 'industry'
            
            df = df.rename(columns=column_mapping)
            
            # Ensure required columns exist
            if 'ticker' not in df.columns:
                raise ValueError("Could not find ticker column in ASX data")
            if 'name' not in df.columns:
                raise ValueError("Could not find name column in ASX data")
            
            # Standardize and clean
            df = self._standardize_columns(df)
            df = self._clean_data(df)
            
            print(f"Loaded {len(df)} ASX companies")
            return df
            
        except Exception as e:
            print(f"Failed to load ASX data: {e}")
            print("Falling back to sample data...")
            return self.get_sample_data()
    
    def get_sample_data(self) -> pd.DataFrame:
        """Get sample ASX companies for testing."""
        data = [
            {'ticker': 'BHP', 'name': 'BHP Group Limited', 'country': 'AU', 'exchange': 'ASX', 'industry': 'Materials'},
            {'ticker': 'RIO', 'name': 'Rio Tinto Limited', 'country': 'AU', 'exchange': 'ASX', 'industry': 'Materials'},
            {'ticker': 'FMG', 'name': 'Fortescue Metals Group Ltd', 'country': 'AU', 'exchange': 'ASX', 'industry': 'Materials'},
            {'ticker': 'NCM', 'name': 'Newcrest Mining Limited', 'country': 'AU', 'exchange': 'ASX', 'industry': 'Materials'},
            {'ticker': 'WBC', 'name': 'Westpac Banking Corporation', 'country': 'AU', 'exchange': 'ASX', 'industry': 'Financials'},
            {'ticker': 'CBA', 'name': 'Commonwealth Bank of Australia', 'country': 'AU', 'exchange': 'ASX', 'industry': 'Financials'},
        ]
        return pd.DataFrame(data)


# Convenience functions
def load_asx(cache_dir: Optional[str] = None) -> pd.DataFrame:
    """Load ASX companies."""
    loader = ASXLoader()
    return loader.load_data(cache_dir)


def sample_asx_data() -> pd.DataFrame:
    """Get sample ASX companies."""
    loader = ASXLoader()
    return loader.get_sample_data()
