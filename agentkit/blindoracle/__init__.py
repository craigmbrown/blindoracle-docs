"""BlindOracle action provider for Coinbase AgentKit.

The private settlement layer for autonomous AI agents.
Provides prediction market, identity, and settlement actions via x402 micropayments.

Usage:
    from blindoracle import blind_oracle_action_provider

    agentkit = AgentKit(AgentKitConfig(
        action_providers=[blind_oracle_action_provider()]
    ))
"""

from .blind_oracle_action_provider import (
    BlindOracleActionProvider,
    blind_oracle_action_provider,
)
from .schemas import (
    CreateMarketSchema,
    GetMarketOddsSchema,
    HelloWorldSchema,
    ListMarketsSchema,
    PlacePositionSchema,
    ResolveMarketSchema,
    VerifyCredentialSchema,
)

__all__ = [
    "BlindOracleActionProvider",
    "blind_oracle_action_provider",
    "HelloWorldSchema",
    "ListMarketsSchema",
    "GetMarketOddsSchema",
    "CreateMarketSchema",
    "PlacePositionSchema",
    "ResolveMarketSchema",
    "VerifyCredentialSchema",
]

__version__ = "0.1.0"
