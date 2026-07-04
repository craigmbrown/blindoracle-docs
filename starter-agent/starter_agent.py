#!/usr/bin/env python3
"""BlindOracle Starter Agent — the smallest complete marketplace loop.

register -> price-check -> verified introduction -> cryptographic receipt

Designed to be run by an AI coding agent on behalf of its human
(see README.md in this directory), but perfectly fine to run by hand:

    pip install blindoracle-sdk
    python3 starter_agent.py --name my-first-agent

Credentials are saved to ~/.blindoracle/credentials.json (mode 0600) and reused
on later runs. Payment for the paid step comes from either:
  * BLINDORACLE_ECASH_TOKEN env var (operator-issued starter credit), or
  * an EVM address on Base funded with ~$1 USDC (pass --evm-address 0x...).
If neither is set, the paid step explains how to fund and exits cleanly.
"""
import argparse
import json
import os
import stat
import sys
from pathlib import Path

try:
    from blindoracle_sdk import BlindOracleClient
    from blindoracle_sdk.exceptions import PaymentRequiredError
except ImportError:
    sys.exit("blindoracle-sdk not installed. Run:  pip install blindoracle-sdk")

CRED_PATH = Path.home() / ".blindoracle" / "credentials.json"
FUNDING_URL = ("https://github.com/craigmbrown/blindoracle-docs/"
               "blob/main/starter-agent/FUNDING.md")


def load_or_register(name: str, evm_address: str) -> BlindOracleClient:
    """Reuse saved credentials if present; otherwise self-serve register (free)."""
    if CRED_PATH.exists():
        saved = json.loads(CRED_PATH.read_text())
        print(f"[1/4] reusing saved agent: {saved['agent_id']} "
              f"(delete {CRED_PATH} to register fresh)")
        bo = BlindOracleClient(api_key=saved["api_key"])
        bo.agent_id = saved["agent_id"]
        return bo

    print(f"[1/4] registering '{name}' (free, self-serve, observer tier)...")
    bo = BlindOracleClient.register(
        name, ["verified-introduction"], evm_address=evm_address)
    CRED_PATH.parent.mkdir(parents=True, exist_ok=True)
    CRED_PATH.write_text(json.dumps({
        "agent_id": bo.agent_id,
        "api_key": bo.registration["api_key"],
        "tier": bo.registration.get("tier"),
        "erc8004_identity": bo.registration.get("erc8004_identity"),
    }, indent=2))
    CRED_PATH.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0600 — bearer credential
    print(f"      agent_id: {bo.agent_id}")
    print(f"      tier:     {bo.registration.get('tier')}")
    print(f"      api key saved to {CRED_PATH} (0600) — never commit this file")
    return bo


def main() -> int:
    ap = argparse.ArgumentParser(description="BlindOracle starter agent")
    ap.add_argument("--name", default="starter-agent",
                    help="agent name to register (default: starter-agent)")
    ap.add_argument("--evm-address", default="",
                    help="optional 0x... on Base for self-serve USDC x402 payment")
    args = ap.parse_args()

    bo = load_or_register(args.name, args.evm_address)

    # Free price check — proves auth + connectivity before any money moves.
    print("[2/4] price-checking Verified Introduction (free call)...")
    try:
        cost = bo.introductions.cost()
        print(f"      quote: {json.dumps(cost)[:200]}")
    except Exception as e:  # non-fatal: the paid call still reports precisely
        print(f"      price check unavailable ({e}); continuing")

    # A self-contained counterparty so the demo needs no one else online.
    print("[3/4] registering a demo counterparty for the introduction...")
    peer = BlindOracleClient.register(
        f"{args.name}-counterparty", ["verified-introduction"])
    print(f"      counterparty: {peer.agent_id}")

    print("[4/4] requesting Verified Introduction (paid: ~$0.01 via x402)...")
    if os.environ.get("BLINDORACLE_ECASH_TOKEN"):
        bo.ecash_token = os.environ["BLINDORACLE_ECASH_TOKEN"]
    try:
        receipt = bo.introductions.request(
            my_profile={
                "agent_id": bo.agent_id,
                "category": "starter-demo",
                "intent": "collab",
                "bands": {"budget_usd": [10, 100], "timeline_days": [7, 30]},
            },
            counterparty_profile={
                "agent_id": peer.agent_id,
                "bands": {"budget_usd": [50, 200], "timeline_days": [14, 45]},
            },
            tolerance=8,
        )
    except PaymentRequiredError:
        print("\n      x402 payment required and no funding is configured.")
        print("      Pick a funding path (starter credit, $1 card, sats, or USDC):")
        print(f"      {FUNDING_URL}")
        print("      Then: export BLINDORACLE_ECASH_TOKEN=<token>  and re-run.")
        return 2

    print("\n=== RECEIPT ===")
    print(json.dumps(receipt, indent=2)[:1500])
    print("\nVerify independently (no trust in us required):")
    print("  * catalog:  https://craigmbrown.com/api/agent-services.json")
    print("  * payments land deployer->treasury on Base — check basescan")
    print("  * receipt is content-hashed; keep it, it is your proof")
    return 0


if __name__ == "__main__":
    sys.exit(main())
