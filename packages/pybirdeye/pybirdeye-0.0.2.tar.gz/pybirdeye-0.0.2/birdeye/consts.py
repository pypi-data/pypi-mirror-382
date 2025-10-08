"""
Type definitions for Birdeye API.

This module provides type hints using Literal for all Birdeye API parameters.
These types provide IDE autocomplete support and type checking.
"""

from typing import Literal

# ============================================================================
# Chains
# ============================================================================

Chain = Literal[
    "solana",
    "ethereum",
    "arbitrum",
    "avalanche",
    "bsc",
    "optimism",
    "polygon",
    "base",
    "zksync",
    "sui",
]