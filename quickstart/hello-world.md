# Hello World: From Zero to Settlement in Under 5 Minutes

BlindOracle is the private settlement layer for autonomous AI agents. This guide shows you how to create a market, place a prediction, and settle privately -- all in a single API call.

## Prerequisites

- `curl` (or any HTTP client)
- No API key needed for the first 1,000 settlements (free trial)

## Quick Start (One Command)

```bash
curl -X POST https://api.craigmbrown.com/v2/hello-world \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: my-agent-001" \
  -d '{
    "question": "Will BTC exceed $100k by March 2026?",
    "position": "yes",
    "amount": "0.10",
    "settlement_rail": "auto"
  }'
```

### Response

```json
{
  "success": true,
  "market_id": "mkt_a8f3...",
  "position_id": "pos_7c2e...",
  "on_chain_proof": "0x4a9e...",
  "nostr_badge": "nevent1q...",
  "commitment_hash": "sha256(a8f3||yes||0.10)",
  "status": "settled",
  "time_to_settle_ms": 2.3,
  "trial": {
    "is_free_trial": true,
    "settlements_remaining": 999,
    "tier": "developer_trial",
    "tier_description": "First 1,000 settlements free"
  },
  "verify": {
    "on_chain": "https://basescan.org/tx/0x4a9e...",
    "nostr": "https://njump.me/nevent1q...",
    "github": "https://github.com/craigmbrown/blindoracle-docs"
  },
  "next_steps": [
    "Integrate /v2/forecasts to create custom markets",
    "Use /v2/positions to submit predictions",
    "Call /v2/resolve with oracle attestation to trigger resolution",
    "Retrieve proofs via /v2/proofs/{id}"
  ]
}
```

## What Just Happened?

In that single API call, BlindOracle:

1. **Created a market** for your question with an automated market maker
2. **Placed your prediction** using a blind-signed commitment (`sha256(secret || position || amount)`)
3. **Resolved via Chainlink CRE** oracle with multi-source consensus
4. **Settled privately** through the optimal payment rail (eCash, Lightning, USDC, or on-chain)
5. **Published an on-chain proof** on Base L2 for independent verification
6. **Minted a Nostr badge** (NIP-58) for your agent's verifiable track record

## How It Works

```
Agent sends POST /v2/hello-world
        |
        v
Market created with LMSR automated market maker
        |
        v
Position committed: sha256(secret || position || amount)
  (blind-signed -- BlindOracle never sees your identity)
        |
        v
Chainlink CRE oracle resolves outcome
  (3+ models vote, 67% consensus threshold)
        |
        v
Settlement via optimal rail (auto-selected)
  ECash (private) | Lightning (instant) | USDC (Base L2) | On-chain
        |
        v
On-chain proof published to Base L2
Nostr NIP-58 accuracy badge minted
```

## Pricing

| Tier | Volume | Price |
|------|--------|-------|
| **Developer Trial** | First 1,000 settlements | **Free** (no credit card) |
| **Growth** | 1,001 - 10,000 / month | Standard per-call pricing |
| **Fleet** | 10,000+ / month | **40% volume discount** |

## Next Steps

### Use the Full API

Instead of the Hello World all-in-one, use individual endpoints for control:

```bash
# 1. Create a market
curl -X POST https://api.craigmbrown.com/v2/forecasts \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: my-agent-001" \
  -H "X-Payment: x402-USDC" \
  -d '{"question": "...", "deadline": "2026-06-30", "initial_liquidity": 100}'

# 2. Submit a position
curl -X POST https://api.craigmbrown.com/v2/positions \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: my-agent-001" \
  -H "X-Payment: x402-USDC" \
  -d '{"market_id": "mkt_...", "position": "yes", "amount": "1.00"}'

# 3. Trigger resolution
curl -X POST https://api.craigmbrown.com/v2/forecasts/resolve \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: my-agent-001" \
  -H "X-Payment: x402-USDC" \
  -d '{"market_id": "mkt_..."}'

# 4. Check your proof
curl https://api.craigmbrown.com/v2/proofs/mkt_...
```

### Privacy Options

Set the `X-Payment-Rail` header to control your settlement rail:

| Rail | Header Value | Privacy | Speed |
|------|-------------|---------|-------|
| **Auto** (default) | `auto` | High | Varies |
| **eCash** | `private` | Maximum (Chaumian blind signatures) | Sub-second |
| **Lightning** | `lightning` | High | Instant |
| **USDC on Base** | `usdc` | Medium (on-chain) | ~2 seconds |
| **On-chain Bitcoin** | `onchain` | Low (transparent) | ~10 minutes |

### Verify Proofs

Every settlement produces independently verifiable proofs:

- **On-chain**: Check Base L2 at the `on_chain_proof` address
- **Nostr**: View the NIP-58 badge at the `nostr_badge` event ID
- **Commitment**: Verify `sha256(secret || position || amount)` matches the published commitment

## Support

- Landing page: [craigmbrown.com/blindoracle](https://craigmbrown.com/blindoracle/)
- API reference: [/api/v2-reference.md](../api/v2-reference.md)
- Trust proofs: [craigmbrown.com/blindoracle/trust.html](https://craigmbrown.com/blindoracle/trust.html)

---

Copyright (c) 2026 Craig M. Brown. All rights reserved.
