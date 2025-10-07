"""Template for adding new exchange loaders.

This file shows how to add a new exchange loader to the system.
Copy this file and modify it for your new exchange.

Example usage:
    from goodgleif.exchanges import load_nasdaq, sample_nasdaq_data
    nasdaq_companies = load_nasdaq()
"""

from __future__ import annotations
from typing import Optional
import pandas as pd
import requests  # Add other imports as needed

from .base import ExchangeLoader


class NewExchangeLoader(ExchangeLoader):
    """Loader for [Exchange Name] data."""
    
    def __init__(self):
        super().__init__("EXCHANGE_CODE", "COUNTRY_CODE")
        self.url = "https://example.com/companies.csv"  # Replace with actual URL
    
    def load_data(self, cache_dir: Optional[str] = None) -> pd.DataFrame:
        """Load companies from [Exchange Name].
        
        Args:
            cache_dir: Optional cache directory for storing data
            
        Returns:
            DataFrame with columns: ticker, name, country, exchange
        """
        try:
            # Add your data loading logic here
            response = requests.get(self.url, timeout=30)
            response.raise_for_status()
            
            # Parse the response data
            # This depends on the format (CSV, JSON, HTML, etc.)
            df = pd.read_csv(response.text)  # or pd.read_json(), etc.
            
            # Standardize column names to match expected format
            # df = df.rename(columns={'symbol': 'ticker', 'company_name': 'name'})
            
            # Standardize and clean the data
            df = self._standardize_columns(df)
            df = self._clean_data(df)
            
            print(f"Loaded {len(df)} [Exchange Name] companies")
            return df
            
        except Exception as e:
            print(f"Failed to load [Exchange Name] data: {e}")
            print("Falling back to sample data...")
            return self.get_sample_data()
    
    def get_sample_data(self) -> pd.DataFrame:
        """Get sample companies for testing.
        
        Returns:
            DataFrame with sample companies from this exchange
        """
        data = [
            {'ticker': 'TICKER1', 'name': 'Company One Inc.', 'country': 'COUNTRY_CODE', 'exchange': 'EXCHANGE_CODE'},
            {'ticker': 'TICKER2', 'name': 'Company Two Ltd.', 'country': 'COUNTRY_CODE', 'exchange': 'EXCHANGE_CODE'},
            # Add more sample companies as needed
        ]
        return pd.DataFrame(data)


# Convenience functions
def load_new_exchange(cache_dir: Optional[str] = None) -> pd.DataFrame:
    """Load companies from [Exchange Name]."""
    loader = NewExchangeLoader()
    return loader.load_data(cache_dir)


def sample_new_exchange_data() -> pd.DataFrame:
    """Get sample companies from [Exchange Name]."""
    loader = NewExchangeLoader()
    return loader.get_sample_data()


# Steps to add a new exchange:
# 1. Copy this file to goodgleif/exchanges/your_exchange.py
# 2. Replace [Exchange Name] with the actual exchange name
# 3. Replace EXCHANGE_CODE with the exchange code (e.g., 'NASDAQ')
# 4. Replace COUNTRY_CODE with the country code (e.g., 'US')
# 5. Update the URL to the actual data source
# 6. Implement the load_data() method with your data loading logic
# 7. Update get_sample_data() with real sample companies
# 8. Update the function names (load_new_exchange -> load_your_exchange)
# 9. Add your exchange to goodgleif/exchanges/__init__.py
# 10. Add tests for your exchange in tests/test_exchanges.py
