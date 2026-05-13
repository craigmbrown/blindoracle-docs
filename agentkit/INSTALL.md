# Install — blindoracle-agentkit

## Canonical install (GitHub VCS, no PyPI)

```bash
pip install "blindoracle-agentkit @ git+https://github.com/craigmbrown/blindoracle-docs.git@agentkit-v0.2.0#subdirectory=agentkit"
```

This installs version `0.2.0` (Apache-2.0) directly from the `craigmbrown/blindoracle-docs` repository, using the `agentkit/` subdirectory as the package root. **No PyPI account or token required.**

## 30-second quickstart

```python
from coinbase_agentkit import AgentKit
from blindoracle import BlindOracleActionProvider

agent = AgentKit(
    action_providers=[
        BlindOracleActionProvider(api_base="https://craigmbrown.com/api"),
    ],
)

# Now the agent can call:
#   verify_credential   — ERC-8004 passport check
#   list_markets        — list active BlindOracle prediction markets
#   create_market       — create a new market (paid via x402)
#   place_position      — place a position on a market
#   get_market_odds     — query current odds
#   resolve_market      — settle a market on outcome (paid)
#   hello               — health-check round-trip
```

## Verify install

```bash
python -c "from blindoracle import BlindOracleActionProvider; print(BlindOracleActionProvider().name)"
# → "blindoracle"
```

## Live API endpoints (verifiable)

| Resource | URL | Auth |
|---|---|---|
| Agent services manifest | `https://craigmbrown.com/api/agent-services.json` | public |
| Live fleet stats | `https://craigmbrown.com/api/fleet-stats.json` | public |
| Reliability Manifesto | `https://craigmbrown.com/blindoracle/reliability.html` | public |
| OpenAPI spec | `https://craigmbrown.com/api/openapi.yaml` | public |

## Pricing (via x402)

| Action | Price |
|---|---|
| `verify_credential` | $0.001/call |
| `list_markets`, `get_market_odds`, `hello` | free |
| `create_market`, `place_position` | $0.05/call |
| `resolve_market` | $0.50/call (deferred to operator co-sign) |

All paid endpoints accept `X-402-Payment` header with ecash token. See https://craigmbrown.com/api/agent-services.json for payment-rail details.

## License

Apache-2.0 (changed from Proprietary in v0.2.0 — community-pickup unblocker).

## Support

- Issues: https://github.com/craigmbrown/blindoracle-docs/issues
- Email: craigmbrown@gmail.com (subject: "BlindOracle AgentKit")
- Reliability claims: https://craigmbrown.com/blindoracle/reliability.html

---

_Built for the 2026-05-13 Coinbase AgentCore + x402 launch. Operator: Craig M. Brown._
