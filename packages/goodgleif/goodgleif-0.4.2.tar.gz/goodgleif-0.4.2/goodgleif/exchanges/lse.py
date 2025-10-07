"""LSE (London Stock Exchange) data loader."""

from __future__ import annotations
from typing import Optional
import pandas as pd
import requests
from io import StringIO

from .base import ExchangeLoader


class LSELoader(ExchangeLoader):
    """Loader for LSE (London Stock Exchange) data."""
    
    def __init__(self):
        super().__init__("LSE", "GB")
        self.url = "https://www.londonstockexchange.com/indices/ftse-100/constituents"
    
    def load_data(self, cache_dir: Optional[str] = None) -> pd.DataFrame:
        """Load LSE listed companies from official website.
        
        Data source: LSE official website
        Format: HTML tables, updated regularly
        
        Returns:
            DataFrame with columns:
            - ticker: LSE ticker code (EPIC)
            - name: Company name
            - country: Always 'GB'
            - exchange: Always 'LSE'
        """
        try:
            response = requests.get(self.url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            # Parse HTML tables
            tables = pd.read_html(StringIO(response.text))
            
            all_companies = []
            
            for table in tables:
                # Look for tables with company information
                if len(table.columns) >= 2:
                    # Try to identify company columns
                    potential_name_cols = []
                    potential_ticker_cols = []
                    
                    for col in table.columns:
                        col_lower = str(col).lower().strip()
                        if any(word in col_lower for word in ['company', 'name', 'title']):
                            potential_name_cols.append(col)
                        elif any(word in col_lower for word in ['ticker', 'epic', 'symbol', 'code']):
                            potential_ticker_cols.append(col)
                    
                    # Use first available columns
                    name_col = potential_name_cols[0] if potential_name_cols else table.columns[0]
                    ticker_col = potential_ticker_cols[0] if potential_ticker_cols else table.columns[1]
                    
                    if len(table) > 0:
                        # Extract companies
                        for _, row in table.iterrows():
                            name = str(row[name_col]).strip()
                            ticker = str(row[ticker_col]).strip()
                            
                            if name and ticker and name != 'nan' and ticker != 'nan':
                                all_companies.append({
                                    'ticker': ticker,
                                    'name': name,
                                    'country': 'GB',
                                    'exchange': 'LSE'
                                })
            
            if all_companies:
                df = pd.DataFrame(all_companies)
                df = self._standardize_columns(df)
                df = self._clean_data(df)
                print(f"Loaded {len(df)} LSE companies")
                return df
            else:
                raise ValueError("No companies found in LSE data")
                
        except Exception as e:
            print(f"Failed to load LSE data: {e}")
            print("Falling back to sample data...")
            return self.get_sample_data()
    
    def get_sample_data(self) -> pd.DataFrame:
        """Get sample LSE companies for testing."""
        data = [
            {'ticker': 'AAL', 'name': 'Anglo American plc', 'country': 'GB', 'exchange': 'LSE'},
            {'ticker': 'GLEN', 'name': 'Glencore plc', 'country': 'GB', 'exchange': 'LSE'},
            {'ticker': 'ANTO', 'name': 'Antofagasta plc', 'country': 'GB', 'exchange': 'LSE'},
            {'ticker': 'VOD', 'name': 'Vodafone Group plc', 'country': 'GB', 'exchange': 'LSE'},
            {'ticker': 'BP', 'name': 'BP plc', 'country': 'GB', 'exchange': 'LSE'},
        ]
        return pd.DataFrame(data)


# Convenience functions
def load_lse(cache_dir: Optional[str] = None) -> pd.DataFrame:
    """Load LSE companies."""
    loader = LSELoader()
    return loader.load_data(cache_dir)


def sample_lse_data() -> pd.DataFrame:
    """Get sample LSE companies."""
    loader = LSELoader()
    return loader.get_sample_data()
