#!/usr/bin/env python3
"""
Simple example of basic company matching.

This example demonstrates how to use the basic matching functionality
of the GoodGLEIF package to find companies in the GLEIF database.
"""

from goodgleif.companymatcher import CompanyMatcher


def basic_matching_example(query: str = "Apple", limit: int = 3, min_score: float = 70):
    """
    Simple example of basic company matching.
    
    Args:
        query: Company name to search for
        limit: Maximum number of results to return
        min_score: Minimum score threshold for matches
        
    Returns:
        List of match dictionaries
    """
    gg = CompanyMatcher()
    gg.load_data()
    
    matches = gg.match_best(query, limit=limit, min_score=min_score)
    
    print(f"Searching for: '{query}'")
    print("-" * 40)
    
    for i, match in enumerate(matches, 1):
        print(f"{i}. {match['original_name']}")
        print(f"   Score: {match['score']}")
        print(f"   LEI: {match['lei']}")
        print(f"   Country: {match['country']}")
        print()
    
    return matches


def main():
    """Run the basic matching example."""
    return basic_matching_example()


if __name__ == "__main__":
    main()
