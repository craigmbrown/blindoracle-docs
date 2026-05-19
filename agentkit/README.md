# blindoracle-agentkit

**Coinbase AgentKit action provider that adds verifiable agent identity, delegation proofs, and private settlement to any AI agent.**

[![Apache 2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/craigmbrown/blindoracle-docs/releases/tag/agentkit-v0.2.0)

## What is this?

A drop-in [ActionProvider](https://docs.cdp.coinbase.com/agentkit) for [Coinbase AgentKit](https://github.com/coinbase/agentkit) that gives your agent:

- **`verify_credential`** — Verify any agent has a valid ERC-8004 passport before delegating to it
- **`list_markets`**, **`create_market`**, **`get_market_odds`**, **`resolve_market`** — Operate on BlindOracle confidential prediction markets
- **`place_position`** — Place a position on a market (paid via x402)
- **`hello`** — Health-check round-trip

Pricing is x402-paywalled (per-call ecash micro-payments). The free tier covers reads; writes settle via the operator's Fedimint wallet.

## Why?

The Cryptorefills repo's AgentKit example README puts it plainly: *"Agent identity is the next unsolved layer."* BlindOracle solves it:

- **Identity** — Every action call carries an ERC-8004 passport hash
- **Delegation chain** — `ProofOfDelegation` (kind 30014) HMAC-signed, every spawn traces to operator
- **Reliability** — 60-second ACK rail, ship-or-no-credit deliverable validator, public live fleet-stats
- **Compliance** — pairs with [blindoracle-compliance](https://github.com/craigmbrown/ETAC-System/tree/main/sdk/python) (MiCA/SEC/OFAC presets)

## Install

```bash
pip install "blindoracle-agentkit @ git+https://github.com/craigmbrown/blindoracle-docs.git@agentkit-v0.2.0#subdirectory=agentkit"
```

(See [INSTALL.md](INSTALL.md) for verify + live endpoints.)

## Quickstart

```python
from coinbase_agentkit import AgentKit
from blindoracle import BlindOracleActionProvider

agent = AgentKit(
    action_providers=[
        BlindOracleActionProvider(api_base="https://craigmbrown.com/api"),
    ],
)

# Verify another agent's passport before delegating
result = agent.run("verify_credential", agent_id="agent_xyz")
print(result)  # {"valid": true, "passport_hash": "0x...", "tier": "operator"}
```

## Live API endpoints (verifiable)

| Resource | URL |
|---|---|
| Agent services manifest | https://craigmbrown.com/api/agent-services.json |
| Live fleet stats (RQ-212) | https://craigmbrown.com/api/fleet-stats.json |
| Reliability Manifesto (RQ-211) | https://craigmbrown.com/blindoracle/reliability.html |
| OpenAPI spec | https://craigmbrown.com/api/openapi.yaml |

Every claim this README makes can be verified by hitting one of those endpoints. No NDAs to read a proof.

## Status

- **Version:** 0.2.0
- **License:** Apache-2.0 (was Proprietary; switched in v0.2.0 to enable community pickup)
- **Actions:** 7 (1 free identity, 4 free reads, 2 paid writes)
- **Live API:** https://craigmbrown.com/api/ (200 from edge — Cloudflare-fronted)
- **Marketplace listings:** Glama (auto-indexed via `glama.json`), mcp.so (PR pending)

## What changed in 0.2.0

- License flipped Proprietary → Apache-2.0 (community-pickup unblocker, per operator directive 2026-05-13)
- Description updated to lead with identity (Coinbase AgentCore tailwind framing)
- Added `INSTALL.md` with VCS-install pattern (no PyPI, no token gating)
- Versioned for ecosystem-registry PR to `coinbase/agentkit`
- Beta status (was Alpha)

## Roadmap

- [ ] PR to `coinbase/agentkit` ecosystem docs adding BlindOracle as a partner (manual, this week)
- [x] Unit tests with `requests-mock` for each action (16 tests in `tests/test_actions.py`)
- [x] Live smoke test marked `@pytest.mark.slow` against craigmbrown.com/api (`tests/test_live_smoke.py`)
- [ ] X demo gist + thread referencing https://x.com/craigmbrown/status/2054379422753411523

## License

Apache-2.0 — see [LICENSE](LICENSE).

## Operator

Craig M. Brown — [craigmbrown.com](https://craigmbrown.com) · [GitHub](https://github.com/craigmbrown) · craigmbrown@gmail.com

Operates 130+ production agents. 7 of 9 payment rails live. MASSAT self-audit 4.3/10. BLP framework 60/60.
