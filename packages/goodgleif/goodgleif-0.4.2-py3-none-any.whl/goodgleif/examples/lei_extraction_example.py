#!/usr/bin/env python
"""
Example script demonstrating how to extract LEI and company information using goodgleif.
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from goodgleif.companymatcher import CompanyMatcher


def main():
    """Demonstrate LEI extraction and company information retrieval."""
    print("GoodGleif LEI Extraction Examples")
    print("=" * 50)
    
    # Initialize the matcher
    matcher = CompanyMatcher()
    
    # Example 1: Get LEI by company name (fuzzy match)
    print("\n1. Getting LEI by company name (fuzzy match):")
    print("-" * 40)
    
    company_names = ["Apple Inc.", "Microsoft Corporation", "Tesla", "Amazon"]
    
    for name in company_names:
        lei = matcher.get_lei_by_name(name)
        if lei:
            print(f"  {name:20} -> LEI: {lei}")
        else:
            print(f"  {name:20} -> Not found")
    
    # Example 2: Get LEI by exact company name match
    print("\n2. Getting LEI by exact company name match:")
    print("-" * 40)
    
    # First, let's find some exact company names from the dataset
    results = matcher.search("Apple", limit=5)
    if not results.empty:
        exact_name = results.iloc[0]['original_name']
        print(f"  Searching for exact match: '{exact_name}'")
        lei = matcher.get_lei_by_name(exact_name, exact_match=True)
        if lei:
            print(f"  Found LEI: {lei}")
    
    # Example 3: Get comprehensive company information by LEI
    print("\n3. Getting comprehensive company information by LEI:")
    print("-" * 40)
    
    # Get a LEI from search results
    results = matcher.search("Microsoft", limit=1)
    if not results.empty:
        lei = results.iloc[0]['lei']
        print(f"  LEI: {lei}")
        
        company_info = matcher.get_company_info(lei)
        if company_info:
            print(f"  Legal Name: {company_info['legal_name']}")
            print(f"  Country: {company_info['country']}")
            print(f"  Category: {company_info['category']}")
            print(f"  Subcategory: {company_info['subcategory']}")
            print(f"  Real Business: {company_info['real_flag']}")
            print(f"  Industry Classifications:")
            for key, value in company_info.items():
                if key.startswith('is_') and value:
                    print(f"    - {key}: {value}")
    
    # Example 4: Get LEIs by country
    print("\n4. Getting LEIs by country:")
    print("-" * 40)
    
    countries = ["US", "GB", "DE", "FR"]
    for country in countries:
        leis = matcher.get_leis_by_country(country)
        print(f"  {country}: {len(leis):,} companies")
        if leis:
            print(f"    Sample LEIs: {leis[:3]}...")
    
    # Example 5: Get LEIs by category
    print("\n5. Getting LEIs by category:")
    print("-" * 40)
    
    categories = ["GENERAL", "FUND"]
    for category in categories:
        leis = matcher.get_leis_by_category(category)
        print(f"  {category}: {len(leis):,} companies")
        if leis:
            print(f"    Sample LEIs: {leis[:3]}...")
    
    # Example 6: Get LEIs by industry classification
    print("\n6. Getting LEIs by industry classification:")
    print("-" * 40)
    
    flags = ["probably_technology", "probably_financial", "probably_healthcare"]
    for flag in flags:
        leis = matcher.get_leis_by_flag(flag)
        print(f"  {flag}: {len(leis):,} companies")
        if leis:
            print(f"    Sample LEIs: {leis[:3]}...")
    
    # Example 7: Search with detailed results
    print("\n7. Search with detailed results (including LEI):")
    print("-" * 40)
    
    query = "Apple"
    results = matcher.search(query, limit=3)
    
    if not results.empty:
        print(f"  Search results for '{query}':")
        for i, (_, row) in enumerate(results.iterrows(), 1):
            print(f"    {i}. {row['original_name']}")
            print(f"       LEI: {row['lei']}")
            print(f"       Score: {row['score']}")
            print(f"       Country: {row['country']}")
            print(f"       Category: {row['category']}")
            print()
    
    # Example 8: Dataset statistics
    print("\n8. Dataset statistics:")
    print("-" * 40)
    
    stats = matcher.get_stats()
    print(f"  Total companies: {stats['total_companies']:,}")
    print(f"  Real businesses: {stats['real_businesses']:,}")
    print(f"  Non-financial entities: {stats['non_financial_entities']:,}")
    print(f"  Countries: {stats['countries']}")
    print(f"  Categories: {stats['categories']}")
    
    print("\n" + "=" * 50)
    print("LEI extraction examples completed!")


if __name__ == "__main__":
    main()
