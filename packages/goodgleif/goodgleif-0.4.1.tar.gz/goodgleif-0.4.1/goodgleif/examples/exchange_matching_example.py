#!/usr/bin/env python3
"""
Example: Match companies from various stock exchanges against GLEIF database.

This example demonstrates:
1. Loading companies from multiple exchanges (ASX, LSE, TSX)
2. Different matching strategies and thresholds
3. Analysis of match quality and coverage
"""

import pandas as pd
from goodgleif.companymatcher import CompanyMatcher


def exchange_matching_example(exchanges_data: dict = None, min_score: float = 80):
    """
    Example: Match companies from various stock exchanges against GLEIF database.
    
    Args:
        exchanges_data: Dictionary mapping exchange names to DataFrames of companies
        min_score: Minimum score threshold for matches
        
    Returns:
        Dictionary containing matching results for each exchange
    """
    if exchanges_data is None:
        exchanges_data = _get_sample_exchange_data()
    
    print("=== Multi-Exchange Company Matching Example ===\n")
    
    # Initialize GLEIF matcher
    print("1. Loading GLEIF database...")
    gg = CompanyMatcher()
    gg.load_data()
    print(f"   Loaded {len(gg.df)} companies from GLEIF database\n")
    
    # Match companies from each exchange
    print("2. Matching companies against GLEIF database...")
    all_results = {}
    
    for exchange_name, companies_df in exchanges_data.items():
        print(f"\n  {exchange_name} Results:")
        results = _match_exchange_companies(exchange_name, companies_df, gg, min_score)
        all_results[exchange_name] = results
        
        print(f"    Total companies: {results['total']}")
        print(f"    Found matches: {len(results['matches'])}")
        print(f"    No matches: {len(results['no_matches'])}")
        print(f"    Match rate: {results['match_rate']:.1f}%")
        
        # Show average score for matches
        if results['matches']:
            avg_score = sum(m['score'] for m in results['matches']) / len(results['matches'])
            print(f"    Average match score: {avg_score:.1f}")
    
    # Overall summary
    print(f"\n3. Overall Summary:")
    print("-" * 50)
    total_companies = sum(r['total'] for r in all_results.values())
    total_matches = sum(len(r['matches']) for r in all_results.values())
    overall_match_rate = total_matches / total_companies * 100 if total_companies > 0 else 0
    
    print(f"Total companies processed: {total_companies}")
    print(f"Total matches found: {total_matches}")
    print(f"Overall match rate: {overall_match_rate:.1f}%")
    
    # Show best matches across all exchanges
    print(f"\n4. Best Matches (Score >= 95):")
    print("-" * 60)
    all_matches = []
    for results in all_results.values():
        all_matches.extend(results['matches'])
    
    high_score_matches = [m for m in all_matches if m['score'] >= 95]
    for match in high_score_matches[:15]:  # Show top 15
        print(f"{match['exchange']}: {match['ticker']} - {match['exchange_name']}")
        print(f"  → {match['gleif_name']} (Score: {match['score']:.1f})")
        print(f"  LEI: {match['lei']} | Country: {match['country']}")
        print()
    
    return all_results


def _match_exchange_companies(exchange_name: str, companies_df: pd.DataFrame, gg: CompanyMatcher, 
                            min_score: float = 80) -> dict:
    """Match companies from a specific exchange against GLEIF database."""
    
    print(f"  Matching {len(companies_df)} {exchange_name} companies...")
    
    matches = []
    no_matches = []
    
    for idx, row in companies_df.iterrows():
        company_name = row['name']
        ticker = row['ticker']
        
        # Try to find matches
        best_matches = gg.match_best(company_name, limit=1, min_score=min_score)
        
        if best_matches:
            match = best_matches[0]
            matches.append({
                'exchange': exchange_name,
                'ticker': ticker,
                'exchange_name': company_name,
                'gleif_name': match['original_name'],
                'score': match['score'],
                'lei': match['lei'],
                'country': match['country'],
                'industry': row.get('industry', 'N/A')
            })
        else:
            no_matches.append({
                'exchange': exchange_name,
                'ticker': ticker,
                'exchange_name': company_name,
                'industry': row.get('industry', 'N/A')
            })
    
    return {
        'matches': matches,
        'no_matches': no_matches,
        'total': len(companies_df),
        'match_rate': len(matches) / len(companies_df) * 100 if len(companies_df) > 0 else 0
    }


def _get_sample_exchange_data():
    """Get sample exchange data for testing."""
    return {
        'ASX': _sample_asx_data(),
        'LSE': _sample_lse_data(),
        'TSX': _sample_tsx_data()
    }


def _sample_asx_data():
    """Sample ASX companies for testing."""
    data = [
        {'ticker': 'BHP', 'name': 'BHP Group Limited', 'country': 'AU', 'exchange': 'ASX', 'industry': 'Materials'},
        {'ticker': 'RIO', 'name': 'Rio Tinto Limited', 'country': 'AU', 'exchange': 'ASX', 'industry': 'Materials'},
        {'ticker': 'FMG', 'name': 'Fortescue Metals Group Ltd', 'country': 'AU', 'exchange': 'ASX', 'industry': 'Materials'},
        {'ticker': 'WBC', 'name': 'Westpac Banking Corporation', 'country': 'AU', 'exchange': 'ASX', 'industry': 'Financials'},
        {'ticker': 'CBA', 'name': 'Commonwealth Bank of Australia', 'country': 'AU', 'exchange': 'ASX', 'industry': 'Financials'},
    ]
    return pd.DataFrame(data)


def _sample_lse_data():
    """Sample LSE companies for testing."""
    data = [
        {'ticker': 'AAL', 'name': 'Anglo American plc', 'country': 'GB', 'exchange': 'LSE', 'industry': 'Materials'},
        {'ticker': 'GLEN', 'name': 'Glencore plc', 'country': 'GB', 'exchange': 'LSE', 'industry': 'Materials'},
        {'ticker': 'ANTO', 'name': 'Antofagasta plc', 'country': 'GB', 'exchange': 'LSE', 'industry': 'Materials'},
        {'ticker': 'LLOY', 'name': 'Lloyds Banking Group plc', 'country': 'GB', 'exchange': 'LSE', 'industry': 'Financials'},
        {'ticker': 'BARC', 'name': 'Barclays plc', 'country': 'GB', 'exchange': 'LSE', 'industry': 'Financials'},
    ]
    return pd.DataFrame(data)


def _sample_tsx_data():
    """Sample TSX companies for testing."""
    data = [
        {'ticker': 'ABX', 'name': 'Barrick Gold Corporation', 'country': 'CA', 'exchange': 'TSX', 'industry': 'Materials'},
        {'ticker': 'FNV', 'name': 'Franco-Nevada Corporation', 'country': 'CA', 'exchange': 'TSX', 'industry': 'Materials'},
        {'ticker': 'WPM', 'name': 'Wheaton Precious Metals Corp.', 'country': 'CA', 'exchange': 'TSX', 'industry': 'Materials'},
        {'ticker': 'RY', 'name': 'Royal Bank of Canada', 'country': 'CA', 'exchange': 'TSX', 'industry': 'Financials'},
        {'ticker': 'TD', 'name': 'The Toronto-Dominion Bank', 'country': 'CA', 'exchange': 'TSX', 'industry': 'Financials'},
    ]
    return pd.DataFrame(data)


def main():
    """Run the exchange matching example."""
    return exchange_matching_example()


if __name__ == "__main__":
    main()
