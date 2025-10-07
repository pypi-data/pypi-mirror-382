"""
GoodGleif class for fuzzy company name matching against GLEIF data.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import List, Optional, Tuple
import requests
import hashlib
import zipfile
import tempfile
import os

import pandas as pd
from rapidfuzz import fuzz, process

from .canonicalname import create_canonical_name, create_brief_name


class CompanyMatcher:
    """
    Fuzzy company name matching against GLEIF real companies data.
    """
    
    def __init__(self, parquet_path: Optional[Path] = None, category: Optional[str] = None):
        """
        Initialize with path to gleif_classified data or specific category.
        
        Args:
            parquet_path: Path to the classified parquet file. If None, uses default.
            category: Specific category to load (e.g., 'financial', 'metals_and_mining', 'real_companies')
        """
        self.category = category
        if category is not None:
            # Load specific category from package data
            from goodgleif.loader import load_category_data, list_available_categories
            try:
                self.df = load_category_data(category)
                self.parquet_path = None  # Not using file path for category loading
            except FileNotFoundError as e:
                # Provide helpful error message with available categories
                available_categories = list_available_categories()
                if available_categories:
                    available_list = ", ".join(available_categories[:10])  # Show first 10
                    if len(available_categories) > 10:
                        available_list += f" (and {len(available_categories) - 10} more)"
                    raise FileNotFoundError(
                        f"Category '{category}' not found.\n\n"
                        f"Available categories: {available_list}\n\n"
                        f"Use CompanyMatcher.show_available_categories() to see all options.\n"
                        f"Original error: {e}"
                    )
                else:
                    raise FileNotFoundError(
                        f"Category '{category}' not found.\n\n"
                        f"No category datasets are available. Please run the filter script first.\n"
                        f"Original error: {e}"
                    )
        elif parquet_path is None:
            # Default to metals_and_mining industry data
            from goodgleif.whereami import get_project_root
            parquet_path = get_project_root() / "goodgleif" / "data" / "gleif_metals_and_mining.parquet"
            self.parquet_path = Path(parquet_path)
        else:
            self.parquet_path = Path(parquet_path)
        
        self.df: Optional[pd.DataFrame] = None
        self.canonical_names: Optional[List[str]] = None
        
    def load_data(self) -> None:
        """Load the parquet data and canonical names."""
        # If category was specified, data is already loaded in __init__
        if self.category is not None:
            print(f"Loaded {len(self.df):,} companies from category: {self.category}")
            self._setup_canonical_names()
            return
            
        base_path = self.parquet_path.parent
        manifest_path = base_path / "gleif_classified_manifest.txt"
        
        # Try to load the default industry file first
        if self.parquet_path.exists():
            print(f"Loading GLEIF data from: {self.parquet_path}")
            self.df = pd.read_parquet(self.parquet_path)
        # Check for partitioned files in data_local (development)
        elif manifest_path.exists():
            print(f"Loading partitioned GLEIF data from: {base_path}")
            self._load_partitioned_data(base_path)
        # Check for package-distributed partitioned files
        elif self._load_package_partitioned_data():
            print("Loading partitioned GLEIF data from package...")
        else:
            print("GLEIF data not found locally. Attempting to download from GitHub...")
            self._download_dataset_from_github()
            if self.parquet_path.exists():
                print(f"Downloaded GLEIF data to: {self.parquet_path}")
                self.df = pd.read_parquet(self.parquet_path)
            else:
                raise FileNotFoundError("GLEIF data not found and could not be downloaded from GitHub. Please check your internet connection and try again.")
        
        # Use pre-computed canonical names - fail if not available
        if 'canonical_name' in self.df.columns:
            print("Using pre-computed canonical names...")
            self.canonical_names = self.df['canonical_name'].tolist()
        else:
            raise ValueError(
                "canonical_name column not found in dataset. "
                "Please regenerate the dataset using 'python scripts/filter_gleif.py' "
                "to include pre-computed canonical names for optimal performance."
            )
        
        print(f"Loaded {len(self.df):,} companies")
    
    def _load_partitioned_data(self, base_path: Path) -> None:
        """Load data from partitioned files."""
        partitions = []
        
        # Check if any partition files exist
        partition_files = [base_path / f"gleif_classified_part_{i}.parquet" for i in range(1, 6)]
        if not any(f.exists() for f in partition_files):
            print("No partition files found, downloading from GitHub...")
            self._download_dataset_from_github()
        
        # Load all partition files
        for i in range(1, 6):  # Parts 1-5
            partition_path = base_path / f"gleif_classified_part_{i}.parquet"
            if partition_path.exists():
                print(f"  Loading partition {i}...")
                partition_df = pd.read_parquet(partition_path)
                partitions.append(partition_df)
            else:
                print(f"  Warning: Partition {i} not found: {partition_path}")
        
        if not partitions:
            raise FileNotFoundError("No partition files found")
        
        # Combine all partitions
        print(f"  Combining {len(partitions)} partitions...")
        self.df = pd.concat(partitions, ignore_index=True)
        print(f"  Combined dataset: {len(self.df):,} companies")
    
    def _load_package_partitioned_data(self) -> bool:
        """Load data from package-distributed partitioned files."""
        try:
            from goodgleif.paths import open_resource_path
            
            partitions = []
            
            # Try to load all partition files from package resources
            for i in range(1, 6):  # Parts 1-5
                try:
                    with open_resource_path(f"gleif_classified_part_{i}.parquet") as partition_path:
                        print(f"  Loading partition {i} from package...")
                        partition_df = pd.read_parquet(partition_path)
                        partitions.append(partition_df)
                except FileNotFoundError:
                    # If any partition is missing, return False
                    return False
            
            if partitions:
                # Combine all partitions
                print(f"  Combining {len(partitions)} partitions...")
                self.df = pd.concat(partitions, ignore_index=True)
                print(f"  Combined dataset: {len(self.df):,} companies")
                return True
            
            return False
            
        except ImportError:
            # Package resources not available
            return False
    
    def search(self, query: str, limit: int = 10, min_score: int = 60) -> pd.DataFrame:
        """
        Search for companies matching the query using fuzzy matching.
        
        Args:
            query: Company name to search for
            limit: Maximum number of results to return
            min_score: Minimum fuzzy match score (0-100)
            
        Returns:
            DataFrame with matching companies and their scores
        """
        if self.df is None or self.canonical_names is None:
            self.load_data()
        
        # Create canonical version of query
        canonical_query = create_canonical_name(query)
        
        if not canonical_query:
            return pd.DataFrame()
        
        # Use rapidfuzz for fast fuzzy matching
        matches = process.extract(
            canonical_query,
            self.canonical_names,
            scorer=fuzz.ratio,
            limit=limit * 2  # Get more than needed to filter by score
        )
        
        # Filter by minimum score and get indices
        results = []
        for match_text, score, idx in matches:
            if score >= min_score:
                results.append({
                    'original_name': self.df.iloc[idx]['Entity.LegalName'],
                    'canonical_name': match_text,
                    'score': score,
                    'lei': self.df.iloc[idx]['LEI'],
                    'category': self.df.iloc[idx].get('Entity.EntityCategory', 'N/A'),
                    'subcategory': self.df.iloc[idx].get('Entity.EntitySubCategory', 'N/A'),
                    'country': self.df.iloc[idx].get('Entity.LegalAddress.Country', 'N/A'),
                    'real_flag': self.df.iloc[idx].get('REAL_FLAG', 0)
                })
        
        # Convert to DataFrame and sort by score
        results_df = pd.DataFrame(results)
        if not results_df.empty:
            results_df = results_df.sort_values('score', ascending=False).head(limit)
        
        return results_df
    
    def get_shortlist(self, query: str, limit: int = 10, min_score: int = 70) -> List[dict]:
        """
        Get a shortlist of the best matches for a company name.
        
        Args:
            query: Company name to search for
            limit: Maximum number of results to return
            min_score: Minimum fuzzy match score (0-100)
            
        Returns:
            List of dictionaries with match information
        """
        results_df = self.search(query, limit, min_score)
        
        if results_df.empty:
            return []
        
        return results_df.to_dict('records')
    
    def get_canonical_name(self, company_name: str) -> str:
        """
        Create a canonical name for a given company name.
        
        Args:
            company_name: Company name to standardize
            
        Returns:
            Canonical version of the company name
        """
        return create_canonical_name(company_name)
    
    def get_brief_name(self, company_name: str) -> str:
        """
        Create a brief name for a given company name (removes legal suffixes).
        
        Args:
            company_name: Company name to standardize
            
        Returns:
            Brief version of the company name
        """
        return create_brief_name(company_name)
    
    def match_canonical(self, query: str, limit: int = 10, min_score: int = 70, country: Optional[str] = None) -> List[dict]:
        """
        Match against canonical names (preserves legal suffixes).
        
        Args:
            query: Company name to search for
            limit: Maximum number of results
            min_score: Minimum fuzzy match score
            country: Optional country code to filter by (matches any .Country column)
            
        Returns:
            List of matching companies
        """
        if self.df is None or self.canonical_names is None:
            self.load_data()
        
        canonical_query = create_canonical_name(query)
        return self._perform_search(canonical_query, self.canonical_names, limit, min_score, country)
    
    def match_brief(self, query: str, limit: int = 10, min_score: int = 70, country: Optional[str] = None) -> List[dict]:
        """
        Match against brief names (removes legal suffixes).
        
        Args:
            query: Company name to search for
            limit: Maximum number of results
            min_score: Minimum fuzzy match score
            country: Optional country code to filter by (matches any .Country column)
            
        Returns:
            List of matching companies
        """
        if self.df is None or self.canonical_names is None:
            self.load_data()
        
        # Use pre-computed brief names - fail if not available
        if 'brief_name' not in self.df.columns:
            raise ValueError(
                "brief_name column not found in dataset. "
                "Please regenerate the dataset using 'python scripts/filter_gleif.py' "
                "to include pre-computed brief names for optimal performance."
            )
        
        brief_names = self.df['brief_name'].tolist()
        brief_query = create_brief_name(query)
        return self._perform_search(brief_query, brief_names, limit, min_score, country)
    
    def match_best(self, query: str, limit: int = 10, min_score: int = 70, country: Optional[str] = None) -> List[dict]:
        """
        Get the best matches using both canonical and brief name matching.
        
        Args:
            query: Company name to search for
            limit: Maximum number of results
            min_score: Minimum fuzzy match score
            country: Optional country code to filter by (matches any .Country column)
            
        Returns:
            List of matching companies with both canonical and brief scores
        """
        if self.df is None or self.canonical_names is None:
            self.load_data()
        
        canonical_query = create_canonical_name(query)
        brief_query = create_brief_name(query)
        
        # Use pre-computed brief names - fail if not available
        if 'brief_name' not in self.df.columns:
            raise ValueError(
                "brief_name column not found in dataset. "
                "Please regenerate the dataset using 'python scripts/filter_gleif.py' "
                "to include pre-computed brief names for optimal performance."
            )
        
        brief_names = self.df['brief_name'].tolist()
        
        # Get matches from both approaches
        canonical_matches = self._perform_search(canonical_query, self.canonical_names, limit * 2, min_score, country)
        brief_matches = self._perform_search(brief_query, brief_names, limit * 2, min_score, country)
        
        # Combine and deduplicate by LEI
        all_matches = {}
        
        for match in canonical_matches:
            lei = match['lei']
            if lei not in all_matches:
                all_matches[lei] = match
                all_matches[lei]['canonical_score'] = match['score']
                all_matches[lei]['brief_score'] = 0
            else:
                all_matches[lei]['canonical_score'] = match['score']
        
        for match in brief_matches:
            lei = match['lei']
            if lei not in all_matches:
                all_matches[lei] = match
                all_matches[lei]['canonical_score'] = 0
                all_matches[lei]['brief_score'] = match['score']
            else:
                all_matches[lei]['brief_score'] = match['score']
        
        # Calculate combined score and sort
        for lei, match in all_matches.items():
            canonical_score = match.get('canonical_score', 0)
            brief_score = match.get('brief_score', 0)
            match['combined_score'] = max(canonical_score, brief_score)  # Use the higher score
        
        # Sort by combined score and return top results
        sorted_matches = sorted(all_matches.values(), key=lambda x: x['combined_score'], reverse=True)
        return sorted_matches[:limit]
    
    def _perform_search(self, query: str, name_list: List[str], limit: int, min_score: int, country: Optional[str] = None) -> List[dict]:
        """Internal method to perform fuzzy search with optional country filtering."""
        if not query:
            return []
        
        matches = process.extract(
            query,
            name_list,
            scorer=fuzz.ratio,
            limit=limit * 2
        )
        
        results = []
        for match_text, score, idx in matches:
            if score >= min_score:
                # Check country filter if provided
                if country:
                    country_match = self._check_country_match(self.df.iloc[idx], country)
                    if not country_match:
                        continue
                
                results.append({
                    'original_name': self.df.iloc[idx]['Entity.LegalName'],
                    'canonical_name': self.df.iloc[idx].get('canonical_name', ''),
                    'brief_name': self.df.iloc[idx].get('brief_name', ''),
                    'score': score,
                    'lei': self.df.iloc[idx]['LEI'],
                    'category': self.df.iloc[idx].get('Entity.EntityCategory', 'N/A'),
                    'subcategory': self.df.iloc[idx].get('Entity.EntitySubCategory', 'N/A'),
                    'country': self.df.iloc[idx].get('Entity.LegalAddress.Country', 'N/A'),
                    'real_flag': self.df.iloc[idx].get('REAL_FLAG', 0)
                })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)[:limit]
    
    def _check_country_match(self, row: pd.Series, country: str) -> bool:
        """
        Check if a row matches the country filter by looking at any column ending in .Country.
        
        Args:
            row: DataFrame row to check
            country: Country code to match (case-insensitive)
            
        Returns:
            True if any .Country column matches the country code
        """
        if not country:
            return True
        
        country_upper = country.upper()
        
        # Find all columns ending in .Country
        country_columns = [col for col in row.index if col.endswith('.Country')]
        
        for col in country_columns:
            value = row.get(col, '')
            if pd.notna(value) and str(value).upper() == country_upper:
                return True
        
        return False
    
    def get_lei_by_name(self, company_name: str, exact_match: bool = False) -> Optional[str]:
        """
        Get LEI for a company by name.
        
        Args:
            company_name: Company name to search for
            exact_match: If True, requires exact match (case-insensitive)
            
        Returns:
            LEI string if found, None otherwise
        """
        if self.df is None:
            self.load_data()
        
        if exact_match:
            # Exact match (case-insensitive)
            mask = self.df['Entity.LegalName'].str.lower() == company_name.lower()
            if mask.any():
                return self.df[mask].iloc[0]['LEI']
        else:
            # Fuzzy match - get best match
            results = self.search(company_name, limit=1, min_score=90)
            if not results.empty:
                return results.iloc[0]['lei']
        
        return None
    
    def get_company_info(self, lei: str) -> Optional[dict]:
        """
        Get comprehensive company information by LEI.
        
        Args:
            lei: LEI to search for
            
        Returns:
            Dictionary with company information or None if not found
        """
        if self.df is None:
            self.load_data()
        
        mask = self.df['LEI'] == lei
        if not mask.any():
            return None
        
        row = self.df[mask].iloc[0]
        
        return {
            'lei': row['LEI'],
            'legal_name': row['Entity.LegalName'],
            'canonical_name': row.get('canonical_name', ''),
            'brief_name': row.get('brief_name', ''),
            'country': row.get('Entity.LegalAddress.Country', 'N/A'),
            'category': row.get('Entity.EntityCategory', 'N/A'),
            'subcategory': row.get('Entity.EntitySubCategory', 'N/A'),
            'real_flag': row.get('REAL_FLAG', 0),
            'is_financial': row.get('probably_financial', False),
            'is_technology': row.get('probably_technology', False),
            'is_healthcare': row.get('probably_healthcare', False),
            'is_automotive': row.get('probably_automotive', False),
            'is_manufacturing': row.get('probably_manufacturing', False),
            'is_transportation': row.get('probably_transportation', False),
            'is_real_estate': row.get('probably_real_estate', False),
            'is_retail_consumer': row.get('probably_retail_consumer', False),
            'is_metals_mining': row.get('probably_metals_and_mining', False),
        }
    
    def get_leis_by_country(self, country: str) -> List[str]:
        """
        Get all LEIs for companies in a specific country.
        
        Args:
            country: Country code (e.g., 'US', 'GB', 'DE')
            
        Returns:
            List of LEI strings
        """
        if self.df is None:
            self.load_data()
        
        mask = self.df['Entity.LegalAddress.Country'] == country.upper()
        return self.df[mask]['LEI'].tolist()
    
    def get_leis_by_category(self, category: str) -> List[str]:
        """
        Get all LEIs for companies in a specific category.
        
        Args:
            category: Entity category (e.g., 'GENERAL', 'FUND')
            
        Returns:
            List of LEI strings
        """
        if self.df is None:
            self.load_data()
        
        mask = self.df['Entity.EntityCategory'] == category.upper()
        return self.df[mask]['LEI'].tolist()
    
    def get_leis_by_flag(self, flag_name: str) -> List[str]:
        """
        Get all LEIs for companies with a specific classification flag.
        
        Args:
            flag_name: Classification flag (e.g., 'probably_financial', 'probably_technology')
            
        Returns:
            List of LEI strings
        """
        if self.df is None:
            self.load_data()
        
        if flag_name not in self.df.columns:
            return []
        
        mask = self.df[flag_name] == True
        return self.df[mask]['LEI'].tolist()
    
    def bulk_lookup_leis(self, company_names: List[str], exact_match: bool = False) -> dict:
        """
        Get LEIs for multiple company names in bulk.
        
        Args:
            company_names: List of company names to look up
            exact_match: If True, requires exact match (case-insensitive)
            
        Returns:
            Dictionary mapping company names to LEIs (None if not found)
        """
        if self.df is None:
            self.load_data()
        
        results = {}
        
        for name in company_names:
            lei = self.get_lei_by_name(name, exact_match=exact_match)
            results[name] = lei
        
        return results
    
    def bulk_get_company_info(self, leis: List[str]) -> List[dict]:
        """
        Get company information for multiple LEIs in bulk.
        
        Args:
            leis: List of LEIs to look up
            
        Returns:
            List of company info dictionaries (None entries for not found)
        """
        if self.df is None:
            self.load_data()
        
        results = []
        
        for lei in leis:
            info = self.get_company_info(lei)
            results.append(info)
        
        return results
    
    def export_search_results(self, results: List[dict], output_path: str, format: str = 'csv') -> None:
        """
        Export search results to file.
        
        Args:
            results: List of search result dictionaries
            output_path: Path to output file
            format: Output format ('csv' or 'json')
        """
        import pandas as pd
        import json
        from pathlib import Path
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == 'csv':
            df = pd.DataFrame(results)
            df.to_csv(output_path, index=False)
        elif format.lower() == 'json':
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def validate_lei(self, lei: str) -> bool:
        """
        Validate LEI format.
        
        Args:
            lei: LEI to validate
            
        Returns:
            True if valid LEI format, False otherwise
        """
        if not lei or len(lei) != 20:
            return False
        
        # LEI format: 20 characters, first 4 are letters, next 2 are numbers, 
        # next 12 are alphanumeric, last 2 are numbers
        import re
        pattern = r'^[A-Z]{4}[0-9]{2}[A-Z0-9]{12}[0-9]{2}$'
        return bool(re.match(pattern, lei))
    
    def find_duplicates(self, company_name: str, threshold: int = 85) -> List[dict]:
        """
        Find potential duplicate companies based on name similarity.
        
        Args:
            company_name: Company name to find duplicates for
            threshold: Similarity threshold (0-100)
            
        Returns:
            List of potential duplicate companies
        """
        if self.df is None:
            self.load_data()
        
        results = self.search(company_name, limit=50, min_score=threshold)
        duplicates = []
        
        for _, row in results.iterrows():
            if row['original_name'].lower() != company_name.lower():
                duplicates.append({
                    'name': row['original_name'],
                    'lei': row['lei'],
                    'score': row['score'],
                    'country': row['country'],
                    'category': row['category']
                })
        
        return duplicates
    
    def get_stats(self) -> dict:
        """Get statistics about the loaded dataset."""
        if self.df is None:
            return {}
        
        # Calculate real businesses from classification flags
        real_businesses = 0
        if 'REAL_FLAG' in self.df.columns:
            real_businesses = int(self.df['REAL_FLAG'].sum())
        else:
            # Calculate from individual classification flags
            # Real businesses are those that are NOT purely financial
            if 'probably_financial' in self.df.columns:
                real_businesses = int((~self.df['probably_financial']).sum())
            else:
                # If no financial flag, assume all are real businesses
                real_businesses = len(self.df)
        
        stats = {
            'total_companies': len(self.df),
            'real_businesses': real_businesses,
            'non_financial_entities': real_businesses,
            'countries': self.df['Entity.LegalAddress.Country'].nunique() if 'Entity.LegalAddress.Country' in self.df.columns else 0,
            'categories': self.df['Entity.EntityCategory'].nunique() if 'Entity.EntityCategory' in self.df.columns else 0,
        }
        
        return stats
    
    @staticmethod
    def list_available_categories() -> List[str]:
        """List all available category datasets.
        
        Returns:
            List of available category names
        """
        from goodgleif.loader import list_available_categories
        return list_available_categories()
    
    def check_duplicate_canonical_names(self) -> dict:
        """Check for canonical name clashes where different companies have the same canonical name.
        
        This identifies potential false positives where different companies
        end up with identical canonical names, which could cause incorrect matches.
        
        Returns:
            Dictionary with clash analysis results
        """
        if self.df is None:
            self.load_data()
        
        if 'canonical_name' not in self.df.columns:
            raise ValueError("canonical_name column not found. Please regenerate dataset with canonical names.")
        
        # Find canonical names that appear multiple times
        canonical_counts = self.df['canonical_name'].value_counts()
        duplicates = canonical_counts[canonical_counts > 1]
        
        # Analyze each duplicate to see if it's different companies
        clash_details = []
        for canonical_name in duplicates.index:
            matching_companies = self.df[self.df['canonical_name'] == canonical_name]
            original_names = matching_companies['Entity.LegalName'].tolist()
            
            # Check if these are actually different companies (not just same company with different LEIs)
            unique_original_names = set(original_names)
            
            if len(unique_original_names) > 1:
                # This is a clash - different companies with same canonical name
                clash_details.append({
                    'canonical_name': canonical_name,
                    'count': len(matching_companies),
                    'unique_companies': len(unique_original_names),
                    'original_names': list(unique_original_names),
                    'leis': matching_companies['LEI'].tolist(),
                    'countries': matching_companies['Entity.LegalAddress.Country'].tolist()
                })
        
        # Sort by count (most problematic clashes first)
        clash_details.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            'total_companies': len(self.df),
            'unique_canonical_names': len(canonical_counts),
            'canonical_name_clashes': len(clash_details),
            'clash_rate': len(clash_details) / len(canonical_counts) * 100,
            'companies_affected_by_clashes': sum(clash['count'] for clash in clash_details),
            'clash_details': clash_details[:20]  # Top 20 most problematic clashes
        }
    
    def show_duplicate_analysis(self) -> None:
        """Display canonical name clash analysis - different companies with same canonical names."""
        try:
            analysis = self.check_duplicate_canonical_names()
            
            print("\nCanonical Names Clash Analysis:")
            print("=" * 50)
            print(f"Total companies: {analysis['total_companies']:,}")
            print(f"Unique canonical names: {analysis['unique_canonical_names']:,}")
            print(f"Canonical name clashes: {analysis['canonical_name_clashes']:,}")
            print(f"Clash rate: {analysis['clash_rate']:.2f}%")
            print(f"Companies affected by clashes: {analysis['companies_affected_by_clashes']:,}")
            
            if analysis['clash_details']:
                print(f"\nTop {len(analysis['clash_details'])} Most Problematic Clashes:")
                print("-" * 60)
                print("(Different companies that have the same canonical name)")
                
                for i, clash in enumerate(analysis['clash_details'], 1):
                    print(f"\n{i}. Canonical: '{clash['canonical_name']}' ({clash['count']} companies, {clash['unique_companies']} unique)")
                    for j, (orig_name, lei, country) in enumerate(zip(clash['original_names'], clash['leis'], clash['countries']), 1):
                        print(f"   {j}. {orig_name} (LEI: {lei}, Country: {country})")
            else:
                print("\n✓ No canonical name clashes found!")
                print("   (All companies with same canonical names are actually the same company)")
                
        except Exception as e:
            print(f"Error analyzing clashes: {e}")
    
    def show_available_categories(self) -> None:
        """Display all available categories with descriptions.
        
        This method shows what categories are available for loading
        and provides brief descriptions of each category.
        """
        categories = self.list_available_categories()
        
        if not categories:
            print("No category datasets found.")
            return
            
        print("\nAvailable GLEIF Category Datasets:")
        print("=" * 50)
        
        # Category descriptions
        descriptions = {
            'financial': 'Financial services, banking, insurance, investment',
            'metals_and_mining': 'Metals, mining, energy, utilities, materials',
            'obviously_mining': 'Clear mining operations and exploration',
            'transportation': 'Transport, shipping, logistics, aviation',
            'automotive': 'Automotive, vehicles, manufacturing, parts',
            'technology': 'Technology, software, hardware, electronics',
            'healthcare': 'Healthcare, medical, pharmaceutical, biotech',
            'real_estate': 'Real estate, property, construction, REITs',
            'retail_consumer': 'Retail, consumer goods, hospitality, entertainment',
            'manufacturing': 'Manufacturing, industrial, production, machinery',
            'construction_infrastructure': 'Construction, infrastructure, civil engineering',
            'automotive_transportation': 'Automotive & transportation combined',
            'energy_power': 'Energy, power generation, renewable energy',
            'electronics_semiconductors': 'Electronics, semiconductors, technology hardware',
            'industrial_machinery': 'Industrial machinery, equipment, automation',
            'aerospace_defense': 'Aerospace, defense, military, aviation',
            'oil_gas_petrochemicals': 'Oil, gas, petrochemicals, drilling',
            'chemical_catalytic': 'Chemical, catalytic, industrial chemistry',
            'clean_tech_renewables': 'Clean tech, renewables, green energy',
            'consumer_goods_appliances': 'Consumer goods, appliances, home products',
            'maritime_rail': 'Maritime, shipping, rail, transportation',
            'jewelry_investment_coinage': 'Jewelry, precious metals, investment',
            'healthcare_medical_devices': 'Healthcare & medical devices combined',
            'recycling_circular_economy': 'Recycling, circular economy, waste management',
            'real_companies': 'Non-financial real businesses (all categories combined)'
        }
        
        for category in sorted(categories):
            description = descriptions.get(category, 'Industry-specific dataset')
            print(f"  {category:<30} - {description}")
        
        print(f"\nTotal categories available: {len(categories)}")
        print("\nUsage examples:")
        print("  matcher = CompanyMatcher(category='financial')")
        print("  matcher = CompanyMatcher(category='obviously_mining')")
        print("  matcher = CompanyMatcher(category='real_companies')")
    
    def _download_dataset_from_github(self) -> None:
        """Download the GLEIF dataset with canonical names from GitHub releases."""
        print("Downloading GLEIF dataset with canonical names from GitHub...")
        
        # Get the current version from the package
        try:
            import goodgleif
            version = getattr(goodgleif, '__version__', 'latest')
        except ImportError:
            version = 'latest'
        
        # GitHub release URL for the dataset
        release_url = f"https://github.com/microprediction/goodgleif/releases/download/{version}/gleif_dataset.zip"
        
        # Create data directory if it doesn't exist
        data_dir = self.parquet_path.parent
        data_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Download the zip file
            print("Downloading dataset...")
            response = requests.get(release_url, stream=True)
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
                tmp_zip_path = tmp_file.name
            
            # Extract the zip file
            print("Extracting dataset...")
            with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(data_dir)
            
            # Clean up temporary file
            os.unlink(tmp_zip_path)
            
            print("✓ Dataset downloaded and extracted successfully")
            
        except Exception as e:
            print(f"✗ Error downloading dataset: {e}")
            print("Please run 'python scripts/filter_gleif.py' to generate the dataset locally")
            raise
