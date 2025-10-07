#!/usr/bin/env python3
"""
Example comparing different matching strategies.

This example demonstrates the different matching strategies available
in the GoodGLEIF package: canonical, brief, and best matching.
"""

from goodgleif.companymatcher import CompanyMatcher


def matching_strategies_example(query: str = "Apple Inc"):
    """
    Example comparing different matching strategies.
    
    Args:
        query: Company name to search for
        
    Returns:
        Dictionary containing results from different matching strategies
    """
    gg = CompanyMatcher()
    gg.load_data()
    
    print(f"Comparing matching strategies for: '{query}'")
    print("=" * 50)
    
    results = {}
    
    # Canonical matching (preserves legal suffixes)
    canonical_matches = gg.match_canonical(query, limit=2)
    results['canonical'] = canonical_matches
    print(f"\nCanonical matching:")
    for match in canonical_matches:
        print(f"  {match['original_name']} (Score: {match['score']})")
    
    # Brief matching (removes legal suffixes)
    brief_matches = gg.match_brief(query, limit=2)
    results['brief'] = brief_matches
    print(f"\nBrief matching:")
    for match in brief_matches:
        print(f"  {match['original_name']} (Score: {match['score']})")
    
    # Best matching (combines both)
    best_matches = gg.match_best(query, limit=2)
    results['best'] = best_matches
    print(f"\nBest matching:")
    for match in best_matches:
        canonical_score = match.get('canonical_score', 0)
        brief_score = match.get('brief_score', 0)
        print(f"  {match['original_name']} (Canonical: {canonical_score}, Brief: {brief_score})")
    
    return results


def main():
    """Run the matching strategies example."""
    return matching_strategies_example()


if __name__ == "__main__":
    main()
