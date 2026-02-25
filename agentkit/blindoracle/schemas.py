"""Pydantic input schemas for BlindOracle AgentKit actions.

Copyright (c) 2025-2026 Craig M. Brown. All rights reserved.
"""

from pydantic import BaseModel, Field


class HelloWorldSchema(BaseModel):
    """Input schema for the Hello World all-in-one settlement demo."""

    question: str = Field(
        ...,
        description="The prediction question (e.g. 'Will BTC exceed $100k by March 2026?')",
    )
    position: str = Field(
        ...,
        description="Position to take: 'yes' or 'no'",
    )
    amount: str = Field(
        default="0.10",
        description="Amount in USDC to stake (default 0.10). First 1,000 settlements are free.",
    )
    settlement_rail: str = Field(
        default="auto",
        description="Settlement rail: 'auto' (default), 'private', 'instant', or 'onchain'",
    )


class ListMarketsSchema(BaseModel):
    """Input schema for listing active prediction markets."""

    category: str = Field(
        default="all",
        description="Market category filter: 'crypto', 'ai', 'sports', 'politics', or 'all'",
    )
    limit: int = Field(
        default=10,
        description="Maximum number of markets to return (1-50)",
    )
    status: str = Field(
        default="active",
        description="Market status filter: 'active', 'resolved', or 'all'",
    )


class GetMarketOddsSchema(BaseModel):
    """Input schema for fetching odds on a specific market."""

    market_id: str = Field(
        ...,
        description="The BlindOracle market ID (e.g. 'mkt_880f7442')",
    )


class CreateMarketSchema(BaseModel):
    """Input schema for creating a new prediction market."""

    question: str = Field(
        ...,
        description="The prediction question. Must be verifiable and time-bounded.",
    )
    resolution_source: str = Field(
        ...,
        description="How the market resolves (e.g. 'chainlink-price-feed', 'manual-oracle', 'api-endpoint')",
    )
    closing_date: str = Field(
        ...,
        description="ISO 8601 date when the market closes for new positions (e.g. '2026-03-31T00:00:00Z')",
    )
    resolution_date: str = Field(
        ...,
        description="ISO 8601 date when the market resolves (e.g. '2026-04-01T00:00:00Z')",
    )
    category: str = Field(
        default="crypto",
        description="Market category: 'crypto', 'ai', 'sports', 'politics'",
    )


class PlacePositionSchema(BaseModel):
    """Input schema for placing a prediction position."""

    market_id: str = Field(
        ...,
        description="The market to place a position on",
    )
    position: str = Field(
        ...,
        description="Position: 'yes' or 'no'",
    )
    amount_usdc: str = Field(
        ...,
        description="Amount in USDC to stake (minimum 0.01)",
    )
    privacy_mode: str = Field(
        default="commitment",
        description="Privacy mode: 'commitment' (default, SHA256 blinded), 'public' (visible on-chain)",
    )


class ResolveMarketSchema(BaseModel):
    """Input schema for resolving a market with oracle attestation."""

    market_id: str = Field(
        ...,
        description="The market to resolve",
    )
    outcome: str = Field(
        ...,
        description="Resolution outcome: 'yes', 'no', or 'void'",
    )
    attestation_source: str = Field(
        default="chainlink",
        description="Source of truth for resolution: 'chainlink', 'manual', 'api'",
    )


class VerifyCredentialSchema(BaseModel):
    """Input schema for verifying an agent identity credential."""

    agent_id: str = Field(
        ...,
        description="The agent ID to verify (e.g. 'agent-001')",
    )
    credential_type: str = Field(
        default="nip58",
        description="Credential type: 'nip58' (Nostr badge), 'vc' (W3C Verifiable Credential)",
    )
