"""
Example modules demonstrating GoodGLEIF functionality.

This package contains example scripts that show how to use the various
features of the GoodGLEIF package. All examples are designed to be
callable and testable.
"""

from goodgleif.examples.basic_matching_example import basic_matching_example, main as basic_main
from goodgleif.examples.matching_strategies_example import matching_strategies_example, main as strategies_main
from goodgleif.examples.score_thresholds_example import score_thresholds_example, main as thresholds_main
from goodgleif.examples.simple_usage_example import simple_usage_example, main as simple_main
from goodgleif.examples.exchange_matching_example import exchange_matching_example, main as exchange_main

__all__ = [
    'basic_matching_example',
    'matching_strategies_example', 
    'score_thresholds_example',
    'simple_usage_example',
    'exchange_matching_example',
    'basic_main',
    'strategies_main',
    'thresholds_main', 
    'simple_main',
    'exchange_main'
]
