"""Live smoke tests -- hit craigmbrown.com/api directly.
Run with: pytest -v -m slow
"""
import json
import pytest
from blindoracle import BlindOracleActionProvider


@pytest.fixture(scope="module")
def live_provider():
    return BlindOracleActionProvider(api_base="https://craigmbrown.com/api")


@pytest.mark.slow
def test_live_hello_world(live_provider):
    result = live_provider.hello_world({
        "question": "Will AI agents dominate software development by 2027?",
        "position": "yes",
        "amount": "0.10",
    })
    data = json.loads(result)
    assert "success" in data, f"unexpected response: {data}"


@pytest.mark.slow
def test_live_list_markets(live_provider):
    result = live_provider.list_markets({"limit": 5})
    data = json.loads(result)
    assert "success" in data
    if data["success"]:
        assert isinstance(data.get("markets", []), list)


@pytest.mark.slow
def test_live_verify_credential(live_provider):
    result = live_provider.verify_credential({"agent_id": "agentkit-smoke-test"})
    data = json.loads(result)
    assert "success" in data
