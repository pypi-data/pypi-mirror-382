#!/usr/bin/env python3
"""
Comprehensive example demonstrating all GoodGleif functionality.

This example shows:
1. Basic LEI lookup
2. Company information retrieval
3. Bulk operations
4. Search with different strategies
5. Data validation
6. Performance testing
"""

from goodgleif.companymatcher import CompanyMatcher


def comprehensive_example():
    """Demonstrate all GoodGleif functionality."""
    print("GoodGleif Comprehensive Example")
    print("=" * 50)
    
    # Initialize matcher
    print("1. Initializing CompanyMatcher...")
    matcher = CompanyMatcher()
    matcher.load_data()
    
    # Basic LEI lookup
    print("\n2. Basic LEI Lookup:")
    print("-" * 30)
    
    companies = ["Apple Inc.", "Microsoft Corporation", "Tesla, Inc."]
    for company in companies:
        lei = matcher.get_lei_by_name(company)
        if lei:
            print(f"  {company:25} -> {lei}")
        else:
            print(f"  {company:25} -> Not found")
    
    # Company information retrieval
    print("\n3. Company Information Retrieval:")
    print("-" * 40)
    
    lei = matcher.get_lei_by_name("Apple Inc.")
    if lei:
        info = matcher.get_company_info(lei)
        print(f"  Company: {info['legal_name']}")
        print(f"  LEI: {info['lei']}")
        print(f"  Country: {info['country']}")
        print(f"  Category: {info['category']}")
        print(f"  Industry Classifications:")
        for key, value in info.items():
            if key.startswith('is_') and value:
                print(f"    - {key.replace('is_', '').replace('_', ' ').title()}")
    
    # Search with different strategies
    print("\n4. Search Strategies:")
    print("-" * 25)
    
    query = "Apple"
    
    # Canonical search (preserves legal suffixes)
    canonical_matches = matcher.match_canonical(query, limit=3)
    print(f"  Canonical search for '{query}':")
    for match in canonical_matches:
        print(f"    - {match['original_name']} (Score: {match['score']})")
    
    # Brief search (removes legal suffixes)
    brief_matches = matcher.match_brief(query, limit=3)
    print(f"  Brief search for '{query}':")
    for match in brief_matches:
        print(f"    - {match['original_name']} (Score: {match['score']})")
    
    # Best search (combines both)
    best_matches = matcher.match_best(query, limit=3)
    print(f"  Best search for '{query}':")
    for match in best_matches:
        print(f"    - {match['original_name']} (Score: {match['score']})")
    
    # Bulk operations
    print("\n5. Bulk Operations:")
    print("-" * 20)
    
    company_list = ["Apple Inc.", "Microsoft Corporation", "Tesla, Inc.", "Amazon.com, Inc."]
    print(f"  Bulk LEI lookup for {len(company_list)} companies:")
    
    bulk_results = matcher.bulk_lookup_leis(company_list)
    for name, lei in bulk_results.items():
        status = "✓" if lei else "✗"
        print(f"    {status} {name:25} -> {lei or 'Not found'}")
    
    # Data validation
    print("\n6. Data Validation:")
    print("-" * 20)
    
    test_leis = [
        "HWUPKR0MPOU8FGXBT394",  # Valid Apple LEI
        "INVALID123",            # Invalid format
        "12345678901234567890"   # Invalid format
    ]
    
    for lei in test_leis:
        is_valid = matcher.validate_lei(lei)
        print(f"  {lei:20} -> {'Valid' if is_valid else 'Invalid'}")
    
    # Duplicate detection
    print("\n7. Duplicate Detection:")
    print("-" * 25)
    
    duplicates = matcher.find_duplicates("Apple", threshold=80)
    print(f"  Potential duplicates for 'Apple':")
    for i, dup in enumerate(duplicates[:5], 1):  # Show top 5
        print(f"    {i}. {dup['name']} (Score: {dup['score']}, Country: {dup['country']})")
    
    # Dataset statistics
    print("\n8. Dataset Statistics:")
    print("-" * 25)
    
    stats = matcher.get_stats()
    print(f"  Total companies: {stats['total_companies']:,}")
    print(f"  Countries: {stats['countries']}")
    print(f"  Categories: {stats['categories']}")
    print(f"  Real businesses: {stats['real_businesses']:,}")
    
    # Country and category filtering
    print("\n9. Filtering Examples:")
    print("-" * 25)
    
    # Get LEIs by country
    us_leis = matcher.get_leis_by_country("US")
    print(f"  US companies: {len(us_leis):,}")
    
    # Get LEIs by category
    general_leis = matcher.get_leis_by_category("GENERAL")
    print(f"  GENERAL category: {len(general_leis):,}")
    
    # Get LEIs by industry
    tech_leis = matcher.get_leis_by_flag("probably_technology")
    print(f"  Technology companies: {len(tech_leis):,}")
    
    print("\n" + "=" * 50)
    print("Comprehensive example completed!")
    
    return {
        'companies': companies,
        'bulk_results': bulk_results,
        'stats': stats
    }


def performance_example():
    """Demonstrate performance testing."""
    print("\nPerformance Testing Example")
    print("=" * 30)
    
    import time
    
    matcher = CompanyMatcher()
    
    # Test load time
    start_time = time.time()
    matcher.load_data()
    load_time = time.time() - start_time
    print(f"Load time: {load_time:.2f}s")
    
    # Test search time
    start_time = time.time()
    results = matcher.search("Apple", limit=10)
    search_time = time.time() - start_time
    print(f"Search time: {search_time:.3f}s")
    print(f"Search throughput: {1/search_time:.0f} queries/second")
    
    # Test bulk operations
    companies = ["Apple Inc.", "Microsoft Corporation", "Tesla, Inc."]
    start_time = time.time()
    bulk_results = matcher.bulk_lookup_leis(companies)
    bulk_time = time.time() - start_time
    print(f"Bulk lookup time: {bulk_time:.3f}s for {len(companies)} companies")
    print(f"Bulk throughput: {len(companies)/bulk_time:.0f} companies/second")


def main():
    """Run the comprehensive example."""
    try:
        results = comprehensive_example()
        performance_example()
        return results
    except Exception as e:
        print(f"Error running example: {e}")
        print("Make sure the GLEIF data is available and the package is properly installed.")
        return None


if __name__ == "__main__":
    main()
