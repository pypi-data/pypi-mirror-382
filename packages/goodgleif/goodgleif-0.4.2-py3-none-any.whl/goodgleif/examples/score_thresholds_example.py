#!/usr/bin/env python3
"""
Example showing how score thresholds affect results.

This example demonstrates how different minimum score thresholds
affect the number and quality of matches returned by the GoodGLEIF package.
"""

from goodgleif.companymatcher import CompanyMatcher


def score_thresholds_example(query: str = "Apple", thresholds: list = None):
    """
    Example showing how score thresholds affect results.
    
    Args:
        query: Company name to search for
        thresholds: List of score thresholds to test
        
    Returns:
        Dictionary mapping thresholds to match results
    """
    if thresholds is None:
        thresholds = [90, 80, 70, 60]
    
    gg = CompanyMatcher()
    gg.load_data()
    
    print(f"Score threshold comparison for: '{query}'")
    print("=" * 50)
    
    results = {}
    
    for min_score in thresholds:
        matches = gg.match_best(query, limit=3, min_score=min_score)
        results[min_score] = matches
        print(f"\nMin Score {min_score}: {len(matches)} matches")
        for match in matches:
            print(f"  {match['original_name']} (Score: {match['score']})")
    
    return results


def main():
    """Run the score thresholds example."""
    return score_thresholds_example()


if __name__ == "__main__":
    main()
