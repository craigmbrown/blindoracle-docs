"""BlindOracle action provider for Coinbase AgentKit.

Provides prediction market creation, position placement, settlement,
and identity verification through the BlindOracle x402 API.

Copyright (c) 2025-2026 Craig M. Brown. All rights reserved.

REQ-ALIGN-001: Domain Understanding [BLP-001] - AgentKit distribution channel
REQ-AUTO-003: Tool Selection [BLP-013] - Autonomous action routing
REQ-DUR-003: Error Recovery [BLP-023] - Graceful API error handling
"""

import json
import os
from typing import Any

import requests

from coinbase_agentkit.action_providers.action_decorator import create_action
from coinbase_agentkit.action_providers.action_provider import ActionProvider
from coinbase_agentkit.network import Network
from coinbase_agentkit.wallet_providers import WalletProvider

from .schemas import (
    CreateMarketSchema,
    GetMarketOddsSchema,
    HelloWorldSchema,
    ListMarketsSchema,
    PlacePositionSchema,
    ResolveMarketSchema,
    VerifyCredentialSchema,
)

# Default to public API; override with BLINDORACLE_API_BASE env var
BLINDORACLE_API_BASE = os.getenv(
    "BLINDORACLE_API_BASE", "https://craigmbrown.com/api"
)

# Request timeout (seconds)
BLINDORACLE_TIMEOUT = int(os.getenv("BLINDORACLE_TIMEOUT", "30"))


class BlindOracleActionProvider(ActionProvider[WalletProvider]):
    """Action provider for BlindOracle prediction markets.

    BlindOracle is the private settlement layer for autonomous AI agents.
    First 1,000 settlements are free per agent.

    Capabilities:
    - Hello World: All-in-one demo (create market + predict + settle)
    - Markets: Create, list, and get odds for prediction markets
    - Positions: Place private positions using commitment schemes
    - Resolution: Resolve markets with oracle attestation
    - Identity: Verify agent credentials via NIP-58 badges

    All paid endpoints use x402 micropayments (USDC on Base).
    """

    def __init__(self, api_base: str = BLINDORACLE_API_BASE):
        super().__init__("blind-oracle", [])
        self.api_base = api_base.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})

    def _request(
        self,
        method: str,
        path: str,
        agent_id: str = "agentkit-default",
        json_data: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        """Make an API request to BlindOracle."""
        url = f"{self.api_base}{path}"
        headers = {"X-Agent-Id": agent_id}
        try:
            resp = self._session.request(
                method,
                url,
                json=json_data,
                params=params,
                headers=headers,
                timeout=BLINDORACLE_TIMEOUT,
            )
            if resp.ok:
                return {"success": True, **resp.json()}
            else:
                return {
                    "success": False,
                    "error": f"HTTP {resp.status_code}",
                    "detail": resp.text[:500],
                }
        except requests.Timeout:
            return {"success": False, "error": "Request timed out"}
        except requests.ConnectionError:
            return {"success": False, "error": "Could not connect to BlindOracle API"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ─────────────────────────────────────────────────────────
    # Hello World (Free Trial)
    # ─────────────────────────────────────────────────────────

    @create_action(
        name="hello_world",
        description=(
            "Run the BlindOracle Hello World demo. Creates a prediction market, "
            "places a position, and settles it privately — all in one call. "
            "First 1,000 settlements are FREE per agent (no payment required). "
            "Use this to test the BlindOracle integration before using paid endpoints. "
            "Returns: market_id, position_id, on_chain_proof, nostr_badge, trial info."
        ),
        schema=HelloWorldSchema,
    )
    def hello_world(self, args: dict[str, Any]) -> str:
        """All-in-one: create market + predict + settle."""
        validated = HelloWorldSchema(**args)
        result = self._request(
            "POST",
            "/v2/hello-world",
            json_data={
                "question": validated.question,
                "position": validated.position,
                "amount": validated.amount,
                "settlement_rail": validated.settlement_rail,
            },
        )
        return json.dumps(result)

    # ─────────────────────────────────────────────────────────
    # Market Discovery (Read-only)
    # ─────────────────────────────────────────────────────────

    @create_action(
        name="list_markets",
        description=(
            "List active prediction markets on BlindOracle. "
            "Filter by category (crypto, ai, sports, politics) and status. "
            "Returns market IDs, questions, current odds, volume, and closing dates. "
            "Use this to discover markets before placing positions."
        ),
        schema=ListMarketsSchema,
    )
    def list_markets(self, args: dict[str, Any]) -> str:
        """List prediction markets."""
        validated = ListMarketsSchema(**args)
        result = self._request(
            "GET",
            "/v2/forecasts",
            params={
                "category": validated.category,
                "limit": validated.limit,
                "status": validated.status,
            },
        )
        return json.dumps(result)

    @create_action(
        name="get_market_odds",
        description=(
            "Get current odds, volume, and metadata for a specific prediction market. "
            "Returns YES/NO probabilities, total volume, number of positions, "
            "closing date, resolution criteria, and privacy options."
        ),
        schema=GetMarketOddsSchema,
    )
    def get_market_odds(self, args: dict[str, Any]) -> str:
        """Get odds for a specific market."""
        validated = GetMarketOddsSchema(**args)
        result = self._request("GET", f"/v2/forecasts/{validated.market_id}")
        return json.dumps(result)

    # ─────────────────────────────────────────────────────────
    # Market Creation (Requires x402 payment)
    # ─────────────────────────────────────────────────────────

    @create_action(
        name="create_market",
        description=(
            "Create a new prediction market on BlindOracle. "
            "Requires x402 payment ($0.001 USDC). "
            "The question must be verifiable and time-bounded. "
            "Returns: market_id, on_chain_proof, closing_date, resolution_date."
        ),
        schema=CreateMarketSchema,
    )
    def create_market(self, wallet_provider: WalletProvider, args: dict[str, Any]) -> str:
        """Create a prediction market. Wallet used for x402 payment."""
        validated = CreateMarketSchema(**args)
        address = wallet_provider.get_address()
        result = self._request(
            "POST",
            "/v2/forecasts",
            agent_id=address,
            json_data={
                "question": validated.question,
                "resolution_source": validated.resolution_source,
                "closing_date": validated.closing_date,
                "resolution_date": validated.resolution_date,
                "category": validated.category,
                "creator_address": address,
            },
        )
        return json.dumps(result)

    # ─────────────────────────────────────────────────────────
    # Position Placement (Requires x402 payment)
    # ─────────────────────────────────────────────────────────

    @create_action(
        name="place_position",
        description=(
            "Place a prediction position on a BlindOracle market. "
            "Requires x402 payment ($0.0005 USDC per position). "
            "Positions are private by default using SHA256 commitment schemes. "
            "Returns: position_id, commitment_hash, on_chain_proof."
        ),
        schema=PlacePositionSchema,
    )
    def place_position(self, wallet_provider: WalletProvider, args: dict[str, Any]) -> str:
        """Place a prediction position. Wallet used for x402 payment + identity."""
        validated = PlacePositionSchema(**args)
        address = wallet_provider.get_address()
        result = self._request(
            "POST",
            "/v2/positions",
            agent_id=address,
            json_data={
                "market_id": validated.market_id,
                "position": validated.position,
                "amount_usdc": validated.amount_usdc,
                "privacy_mode": validated.privacy_mode,
                "wallet_address": address,
            },
        )
        return json.dumps(result)

    # ─────────────────────────────────────────────────────────
    # Market Resolution (Requires x402 payment + oracle attestation)
    # ─────────────────────────────────────────────────────────

    @create_action(
        name="resolve_market",
        description=(
            "Resolve a prediction market with oracle attestation. "
            "Requires x402 payment ($0.002 USDC). "
            "Only the market creator or authorized oracle can resolve. "
            "Triggers automatic settlement to all position holders. "
            "Returns: resolution_proof, settlements_triggered, total_payout."
        ),
        schema=ResolveMarketSchema,
    )
    def resolve_market(self, wallet_provider: WalletProvider, args: dict[str, Any]) -> str:
        """Resolve a market. Wallet used for authorization."""
        validated = ResolveMarketSchema(**args)
        address = wallet_provider.get_address()
        result = self._request(
            "POST",
            "/v2/forecasts/resolve",
            agent_id=address,
            json_data={
                "market_id": validated.market_id,
                "outcome": validated.outcome,
                "attestation_source": validated.attestation_source,
                "resolver_address": address,
            },
        )
        return json.dumps(result)

    # ─────────────────────────────────────────────────────────
    # Identity Verification (Free)
    # ─────────────────────────────────────────────────────────

    @create_action(
        name="verify_credential",
        description=(
            "Verify an agent's identity credential on BlindOracle. "
            "Free — no payment required. "
            "Returns: agent reputation score (0.0-1.0), badge status, "
            "settlement history count, and anti-synthetic validation result."
        ),
        schema=VerifyCredentialSchema,
    )
    def verify_credential(self, args: dict[str, Any]) -> str:
        """Verify an agent credential. No wallet needed."""
        validated = VerifyCredentialSchema(**args)
        result = self._request(
            "GET",
            "/v2/verify/credential",
            agent_id=validated.agent_id,
            params={"type": validated.credential_type},
        )
        return json.dumps(result)

    # ─────────────────────────────────────────────────────────
    # Network Support
    # ─────────────────────────────────────────────────────────

    def supports_network(self, network: Network) -> bool:
        """BlindOracle supports Base mainnet, Base Sepolia, and chain-agnostic mode."""
        if network is None or network.network_id is None:
            return True  # Chain-agnostic (Hello World, read-only actions)
        return network.network_id in (
            "base-mainnet",
            "base-sepolia",
            "eip155:8453",
            "eip155:84532",
        )


def blind_oracle_action_provider(
    api_base: str = BLINDORACLE_API_BASE,
) -> BlindOracleActionProvider:
    """Factory function for the BlindOracle action provider.

    Usage:
        from blindoracle import blind_oracle_action_provider

        agentkit = AgentKit(AgentKitConfig(
            action_providers=[blind_oracle_action_provider()]
        ))

    Args:
        api_base: BlindOracle API base URL. Defaults to https://craigmbrown.com/api.
                  Override with BLINDORACLE_API_BASE env var.
    """
    return BlindOracleActionProvider(api_base=api_base)
