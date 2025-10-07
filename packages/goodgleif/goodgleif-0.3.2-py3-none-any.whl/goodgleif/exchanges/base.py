"""Base exchange loader functionality."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
import pandas as pd


class ExchangeLoader(ABC):
    """Base class for exchange data loaders."""
    
    def __init__(self, exchange_name: str, country_code: str):
        self.exchange_name = exchange_name
        self.country_code = country_code
    
    @abstractmethod
    def load_data(self, cache_dir: Optional[str] = None) -> pd.DataFrame:
        """Load company data from the exchange.
        
        Args:
            cache_dir: Optional cache directory for storing data
            
        Returns:
            DataFrame with columns: ticker, name, country, exchange
        """
        pass
    
    @abstractmethod
    def get_sample_data(self) -> pd.DataFrame:
        """Get sample data for testing when live data isn't available.
        
        Returns:
            DataFrame with sample companies from this exchange
        """
        pass
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize DataFrame columns to expected format.
        
        Args:
            df: Raw DataFrame from exchange
            
        Returns:
            Standardized DataFrame with columns: ticker, name, country, exchange
        """
        # Ensure required columns exist
        required_cols = ['ticker', 'name', 'country', 'exchange']
        
        # Add standard columns if missing
        if 'country' not in df.columns:
            df['country'] = self.country_code
        if 'exchange' not in df.columns:
            df['exchange'] = self.exchange_name
            
        # Select and order columns
        available_cols = [col for col in required_cols if col in df.columns]
        if 'industry' in df.columns:
            available_cols.append('industry')
            
        return df[available_cols].copy()
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean the DataFrame by removing invalid entries.
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        # Remove rows with missing essential data
        df = df.dropna(subset=['ticker', 'name'])
        df = df[df['ticker'].str.strip() != '']
        df = df[df['name'].str.strip() != '']
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['ticker'])
        
        return df.reset_index(drop=True)
