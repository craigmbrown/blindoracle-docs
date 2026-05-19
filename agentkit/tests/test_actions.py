"""Unit tests for BlindOracle AgentKit action provider.
Uses unittest.mock to intercept HTTP -- no live network required.
"""
import json
from unittest.mock import MagicMock, patch

import pytest

from blindoracle import BlindOracleActionProvider


@pytest.fixture
def provider():
    return BlindOracleActionProvider(api_base="https://api.test")


def _ok(data):
    r = MagicMock()
    r.ok = True
    r.json.return_value = data
    return r


def _err(status, text="bad request"):
    r = MagicMock()
    r.ok = False
    r.status_code = status
    r.text = text
    return r


def test_hello_world_happy(provider):
    payload = {"market_id": "mkt_abc", "position_id": "pos_xyz", "on_chain_proof": "0xdeadbeef"}
    with patch.object(provider._session, "request", return_value=_ok(payload)) as m:
        result = provider.hello_world({"question": "Will BTC > 100k?", "position": "yes"})
    data = json.loads(result)
    assert data["success"] is True
    assert data["market_id"] == "mkt_abc"
    assert m.call_args[0][1].endswith("/v2/hello-world")


def test_hello_world_api_error(provider):
    with patch.object(provider._session, "request", return_value=_err(503)):
        result = provider.hello_world({"question": "Q?", "position": "yes"})
    data = json.loads(result)
    assert data["success"] is False
    assert "503" in data["error"]


def test_list_markets_default(provider):
    payload = {"markets": [{"id": "mkt_001", "question": "Will ETH flip BTC?"}]}
    with patch.object(provider._session, "request", return_value=_ok(payload)) as m:
        result = provider.list_markets({})
    data = json.loads(result)
    assert data["success"] is True
    assert len(data["markets"]) == 1
    assert m.call_args[1]["params"]["status"] == "active"


def test_list_markets_category_filter(provider):
    with patch.object(provider._session, "request", return_value=_ok({"markets": []})) as m:
        provider.list_markets({"category": "crypto", "limit": 5})
    assert m.call_args[1]["params"]["category"] == "crypto"
    assert m.call_args[1]["params"]["limit"] == 5


def test_get_market_odds_happy(provider):
    payload = {"market_id": "mkt_001", "yes_prob": 0.62, "no_prob": 0.38}
    with patch.object(provider._session, "request", return_value=_ok(payload)) as m:
        result = provider.get_market_odds({"market_id": "mkt_001"})
    data = json.loads(result)
    assert data["success"] is True
    assert data["yes_prob"] == pytest.approx(0.62)
    assert "mkt_001" in m.call_args[0][1]


def test_get_market_odds_not_found(provider):
    with patch.object(provider._session, "request", return_value=_err(404, "not found")):
        result = provider.get_market_odds({"market_id": "mkt_bad"})
    data = json.loads(result)
    assert data["success"] is False
    assert "404" in data["error"]


def test_create_market_happy(provider):
    payload = {"market_id": "mkt_new", "on_chain_proof": "0xabc123"}
    wallet = MagicMock()
    wallet.get_address.return_value = "0xAgentAddress"
    with patch.object(provider._session, "request", return_value=_ok(payload)) as m:
        result = provider.create_market(wallet, {
            "question": "Will GPT-5 ship by Q2 2026?",
            "resolution_source": "manual-oracle",
            "closing_date": "2026-06-30T00:00:00Z",
            "resolution_date": "2026-07-01T00:00:00Z",
        })
    data = json.loads(result)
    assert data["success"] is True
    assert m.call_args[1]["json"]["creator_address"] == "0xAgentAddress"


def test_place_position_happy(provider):
    payload = {"position_id": "pos_001", "commitment_hash": "sha256_xyz"}
    wallet = MagicMock()
    wallet.get_address.return_value = "0xTrader"
    with patch.object(provider._session, "request", return_value=_ok(payload)):
        result = provider.place_position(wallet, {
            "market_id": "mkt_001", "position": "yes", "amount_usdc": "0.50"
        })
    data = json.loads(result)
    assert data["success"] is True
    assert "commitment_hash" in data


def test_place_position_timeout(provider):
    import requests
    wallet = MagicMock()
    wallet.get_address.return_value = "0xTrader"
    with patch.object(provider._session, "request", side_effect=requests.Timeout):
        result = provider.place_position(wallet, {
            "market_id": "mkt_001", "position": "no", "amount_usdc": "0.10"
        })
    data = json.loads(result)
    assert data["success"] is False
    assert "timed out" in data["error"]


def test_resolve_market_happy(provider):
    payload = {"resolution_proof": "0xproof", "settlements_triggered": 4}
    wallet = MagicMock()
    wallet.get_address.return_value = "0xOracle"
    with patch.object(provider._session, "request", return_value=_ok(payload)) as m:
        result = provider.resolve_market(wallet, {"market_id": "mkt_001", "outcome": "yes"})
    data = json.loads(result)
    assert data["success"] is True
    assert data["settlements_triggered"] == 4
    assert m.call_args[1]["json"]["outcome"] == "yes"


def test_verify_credential_happy(provider):
    payload = {"valid": True, "score": 0.91, "tier": "operator"}
    with patch.object(provider._session, "request", return_value=_ok(payload)) as m:
        result = provider.verify_credential({"agent_id": "agent_abc"})
    data = json.loads(result)
    assert data["success"] is True
    assert data["valid"] is True
    assert m.call_args[1]["params"]["type"] == "nip58"


def test_verify_credential_connection_error(provider):
    import requests
    with patch.object(provider._session, "request", side_effect=requests.ConnectionError):
        result = provider.verify_credential({"agent_id": "agent_xyz"})
    data = json.loads(result)
    assert data["success"] is False
    assert "connect" in data["error"].lower()


def test_supports_network_base_mainnet(provider):
    from coinbase_agentkit.network import Network
    assert provider.supports_network(Network(network_id="base-mainnet")) is True


def test_supports_network_base_sepolia(provider):
    from coinbase_agentkit.network import Network
    assert provider.supports_network(Network(network_id="base-sepolia")) is True


def test_supports_network_unknown(provider):
    from coinbase_agentkit.network import Network
    assert provider.supports_network(Network(network_id="ethereum-mainnet")) is False


def test_supports_network_none(provider):
    assert provider.supports_network(None) is True


def test_version():
    from blindoracle import __version__
    assert __version__ == "0.2.0"


def test_provider_name(provider):
    assert provider.name == "blind-oracle"
