#!/usr/bin/env python3
"""
Simple usage example showing how to use GoodGleif without worrying about file locations.

The system automatically:
1. Uses partitioned files if available (GitHub-friendly)
2. Falls back to single parquet file
3. Loads from package resources if distributed
4. Provides helpful error messages if data is missing
"""

from goodgleif.companymatcher import CompanyMatcher


def simple_usage_example(queries: list = None):
    """
    Simple usage example showing how to use GoodGleif without worrying about file locations.
    
    Args:
        queries: List of company names to search for
        
    Returns:
        Dictionary mapping queries to their match results
    """
    if queries is None:
        queries = ["Apple", "Microsoft", "Tesla", "Goldman Sachs"]
    
    print("=== Simple GoodGleif Usage ===\n")
    
    # Initialize without any path - uses smart defaults
    print("1. Initializing GoodGleif (no path needed)...")
    gg = CompanyMatcher()  # Uses default classified data
    
    print("2. Loading data (automatically finds best available source)...")
    gg.load_data()
    
    print("3. Searching for companies...")
    
    results = {}
    
    for query in queries:
        print(f"\nSearching for: '{query}'")
        matches = gg.match_best(query, limit=3, min_score=80)
        results[query] = matches
        
        if matches:
            for i, match in enumerate(matches, 1):
                print(f"  {i}. {match['original_name']} (Score: {match['score']:.1f})")
                print(f"     LEI: {match['lei']} | Country: {match['country']}")
        else:
            print(f"  No matches found for '{query}'")
    
    print(f"\n4. System automatically used the best available data source!")
    print("   - Partitioned files (if available)")
    print("   - Single parquet file (fallback)")
    print("   - Package resources (if distributed)")
    print("   - Helpful error messages (if missing)")
    
    return results


def main():
    """Run the simple usage example."""
    return simple_usage_example()


if __name__ == "__main__":
    main()
