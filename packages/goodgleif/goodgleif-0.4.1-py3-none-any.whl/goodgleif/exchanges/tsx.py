"""TSX (Toronto Stock Exchange) data loader."""

from __future__ import annotations
from typing import Optional
import pandas as pd
import requests
from io import StringIO
import time

from .base import ExchangeLoader


class TSXLoader(ExchangeLoader):
    """Loader for TSX (Toronto Stock Exchange) data."""
    
    def __init__(self):
        super().__init__("TSX", "CA")
        self.urls = [
            "https://en.wikipedia.org/wiki/S%26P/TSX_Composite_Index",  # TSX Composite (~250 companies)
            "https://en.wikipedia.org/wiki/S%26P/TSX_60",  # TSX 60 (largest companies)
        ]
    
    def load_data(self, cache_dir: Optional[str] = None) -> pd.DataFrame:
        """Load TSX listed companies from Wikipedia indices.
        
        Data source: Wikipedia S&P/TSX indices
        Format: HTML tables, updated regularly
        
        Returns:
            DataFrame with columns:
            - ticker: TSX ticker code
            - name: Company name
            - country: Always 'CA'
            - exchange: 'TSX'
        """
        all_companies = []
        
        for url in self.urls:
            try:
                response = requests.get(url, timeout=30, headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                })
                response.raise_for_status()
                
                # Wikipedia tables are well-structured
                tables = pd.read_html(StringIO(response.text))
                
                # Find the constituents table
                for table in tables:
                    if 'Company' in table.columns or 'Symbol' in table.columns or 'Ticker' in table.columns:
                        df = table.copy()
                        
                        # Normalize columns
                        column_mapping = {}
                        for col in df.columns:
                            col_lower = str(col).lower().strip()
                            if 'symbol' in col_lower or 'ticker' in col_lower:
                                column_mapping[col] = 'ticker'
                            elif 'company' in col_lower or 'name' in col_lower:
                                column_mapping[col] = 'name'
                            elif 'sector' in col_lower or 'industry' in col_lower:
                                column_mapping[col] = 'industry'
                        
                        df = df.rename(columns=column_mapping)
                        
                        if 'ticker' in df.columns and 'name' in df.columns:
                            # Reset index to avoid issues
                            df = df.reset_index(drop=True)
                            df['country'] = 'CA'
                            df['exchange'] = 'TSX'
                            
                            cols = ['ticker', 'name', 'country', 'exchange']
                            if 'industry' in df.columns:
                                cols.append('industry')
                            
                            df = df[cols].copy()
                            df = df.dropna(subset=['ticker', 'name'])
                            df = df[df['ticker'].str.strip() != '']
                            df = df[df['name'].str.strip() != '']
                            
                            all_companies.extend(df.to_dict('records'))
                            break
                
                # Small delay between requests
                time.sleep(1)
                
            except Exception as e:
                print(f"Failed to load from {url}: {e}")
                continue
        
        if all_companies:
            df = pd.DataFrame(all_companies)
            df = self._standardize_columns(df)
            df = self._clean_data(df)
            print(f"Loaded {len(df)} TSX companies")
            return df
        else:
            print("Failed to load TSX data, falling back to sample data...")
            return self.get_sample_data()
    
    def get_sample_data(self) -> pd.DataFrame:
        """Get sample TSX companies for testing."""
        data = [
            {'ticker': 'ABX', 'name': 'Barrick Gold Corporation', 'country': 'CA', 'exchange': 'TSX'},
            {'ticker': 'FNV', 'name': 'Franco-Nevada Corporation', 'country': 'CA', 'exchange': 'TSX'},
            {'ticker': 'WPM', 'name': 'Wheaton Precious Metals Corp.', 'country': 'CA', 'exchange': 'TSX'},
            {'ticker': 'RY', 'name': 'Royal Bank of Canada', 'country': 'CA', 'exchange': 'TSX'},
            {'ticker': 'TD', 'name': 'Toronto-Dominion Bank', 'country': 'CA', 'exchange': 'TSX'},
        ]
        return pd.DataFrame(data)


# Convenience functions
def load_tsx(cache_dir: Optional[str] = None) -> pd.DataFrame:
    """Load TSX companies."""
    loader = TSXLoader()
    return loader.load_data(cache_dir)


def sample_tsx_data() -> pd.DataFrame:
    """Get sample TSX companies."""
    loader = TSXLoader()
    return loader.get_sample_data()
