# BlindOracle x402 Payment Specification

**Version**: 1.0.0
**Status**: Draft
**Date**: 2026-02-25
**Base Protocol**: [x402 V2](https://x402.org) (HTTP 402 Payment Required)
**Network**: Base mainnet (`eip155:8453`) via EIP-3009
**Copyright**: (c) 2025-2026 Craig M. Brown. All rights reserved.

## Abstract

This document specifies how BlindOracle implements x402 micropayments for autonomous AI agent access to prediction market, identity, and settlement services. BlindOracle extends the base x402 protocol with agent-specific headers, a free trial system, multi-rail settlement options, and privacy-preserving commitment schemes.

## Conformance

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHOULD", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

## 1. Protocol Overview

BlindOracle uses x402 to gate access to paid API endpoints. The flow follows the standard x402 V2 sequence:

```
Agent                     BlindOracle API               Facilitator          Base L2
  |                            |                            |                   |
  |--- POST /v2/forecasts ---->|                            |                   |
  |                            |                            |                   |
  |<--- HTTP 402 --------------|                            |                   |
  |     PAYMENT-REQUIRED:      |                            |                   |
  |     {x402Version:2,        |                            |                   |
  |      accepts:[...]}        |                            |                   |
  |                            |                            |                   |
  | [Agent signs EIP-712 authorization locally]             |                   |
  |                            |                            |                   |
  |--- POST /v2/forecasts ---->|                            |                   |
  |     PAYMENT-SIGNATURE:     |                            |                   |
  |     {payload, accepted}    |                            |                   |
  |                            |--- POST /verify ---------->|                   |
  |                            |<-- {isValid: true} --------|                   |
  |                            |--- POST /settle ---------->|                   |
  |                            |                            |-- transferWith -->|
  |                            |                            |<- tx confirmed ---|
  |                            |<-- {success, txHash} ------|                   |
  |<--- HTTP 200 --------------|                            |                   |
  |     PAYMENT-RESPONSE:      |                            |                   |
  |     {success, txHash}      |                            |                   |
  |     [response body]        |                            |                   |
```

### 1.1 Free Trial Bypass

For agents within their free trial (first 1,000 settlements), the 402 challenge is bypassed:

```
Agent                     BlindOracle API
  |                            |
  |--- POST /v2/hello-world -->|
  |     X-Agent-Id: agent-001  |
  |                            |  [Check trial counter: 997 remaining]
  |<--- HTTP 200 --------------|
  |     [response body with    |
  |      trial.remaining: 996] |
```

No `PAYMENT-SIGNATURE` header is required during the free trial period.

## 2. Headers

### 2.1 Standard x402 V2 Headers

| Header | Direction | Format | Description |
|--------|-----------|--------|-------------|
| `PAYMENT-REQUIRED` | Server -> Client | Base64url(JSON) | Payment requirements in 402 response |
| `PAYMENT-SIGNATURE` | Client -> Server | Base64url(JSON) | Signed payment authorization |
| `PAYMENT-RESPONSE` | Server -> Client | Base64url(JSON) | Settlement confirmation in 200 response |

### 2.2 BlindOracle Extension Headers

| Header | Direction | Required | Description |
|--------|-----------|----------|-------------|
| `X-Agent-Id` | Client -> Server | REQUIRED | Unique agent identifier for rate limiting and trial tracking |
| `X-Payment-Rail` | Client -> Server | OPTIONAL | Preferred settlement rail: `private` (default), `instant`, `onchain` |
| `X-402-Memo` | Client -> Server | OPTIONAL | Payment memo for audit trail correlation |

### 2.3 Header Compatibility Note

BlindOracle accepts both the canonical x402 V2 headers (`PAYMENT-SIGNATURE`) and the legacy `X-402-Payment` header for backwards compatibility. Clients SHOULD use the V2 canonical names.

## 3. Payment Requirements

When a client requests a paid endpoint without payment, the server responds with `HTTP 402` and a `PAYMENT-REQUIRED` header containing:

```json
{
  "x402Version": 2,
  "error": "Payment required for this endpoint",
  "accepts": [
    {
      "scheme": "exact",
      "network": "eip155:8453",
      "maxAmountRequired": "1000",
      "resource": "/v2/forecasts",
      "description": "Create a prediction market on BlindOracle",
      "mimeType": "application/json",
      "payTo": "0xBlindOracleSettlementAddress",
      "maxTimeoutSeconds": 300,
      "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "extra": {
        "name": "USDC",
        "decimals": 6,
        "version": "2"
      }
    }
  ],
  "extensions": {
    "blindoracle": {
      "trial_eligible": true,
      "privacy_options": ["commitment", "public"]
    }
  }
}
```

### 3.1 Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `x402Version` | integer | Always `2` |
| `scheme` | string | Payment scheme. Currently only `exact` (EIP-3009) |
| `network` | string | CAIP-2 chain ID. `eip155:8453` for Base mainnet |
| `maxAmountRequired` | string | Amount in token base units (USDC: 6 decimals). `1000` = $0.001 |
| `resource` | string | The API path being purchased |
| `payTo` | string | BlindOracle settlement address on Base |
| `maxTimeoutSeconds` | integer | How long this payment quote is valid |
| `asset` | string | ERC-20 contract address for USDC on Base |

## 4. Endpoint Pricing

All prices in USDC. Amounts shown in human-readable form; wire format uses base units (6 decimals).

| Endpoint | Method | Price (USDC) | `maxAmountRequired` |
|----------|--------|-------------|---------------------|
| `/v2/hello-world` | POST | Free | N/A |
| `/v2/forecasts` | POST | $0.001 | `1000` |
| `/v2/positions` | POST | $0.0005 | `500` |
| `/v2/forecasts/resolve` | POST | $0.002 | `2000` |
| `/v2/verify/credential` | GET | Free | N/A |
| `/v2/verify/mint` | POST | $0.001 | `1000` |
| `/v2/account/balance` | GET | Free | N/A |
| `/v2/account/invoice` | POST | $0.0001 | `100` |
| `/v2/transfer/quote` | GET | Free | N/A |
| `/v2/transfer/cross-rail` | POST | $0.001 | `1000` |
| `/v2/settle/instant` | POST | $0.0005 | `500` |
| `/v2/settle/onchain` | POST | $0.001 | `1000` |
| `/v2/health` | GET | Free | N/A |

### 4.1 Volume Discount Tiers

| Tier | Monthly Volume | Discount |
|------|---------------|----------|
| Developer Trial | First 1,000 settlements (lifetime) | 100% (free) |
| Growth | 1,001 - 10,000 / month | 0% (standard) |
| Fleet | 10,001+ / month | 40% |

Volume discounts are applied automatically based on the `X-Agent-Id` settlement counter.

## 5. Payment Payload (EVM / Base)

The `PAYMENT-SIGNATURE` header carries a base64url-encoded JSON payload:

```json
{
  "x402Version": 2,
  "scheme": "exact",
  "network": "eip155:8453",
  "accepted": {
    "scheme": "exact",
    "network": "eip155:8453",
    "maxAmountRequired": "1000",
    "resource": "/v2/forecasts",
    "payTo": "0xBlindOracleSettlementAddress",
    "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "maxTimeoutSeconds": 300
  },
  "payload": {
    "signature": "0x...",
    "authorization": {
      "from": "0xAgentWallet",
      "to": "0xBlindOracleSettlementAddress",
      "value": "1000",
      "validAfter": "1740672089",
      "validBefore": "1740672389",
      "nonce": "0x3a7f..."
    }
  },
  "extensions": {}
}
```

### 5.1 EIP-3009 Authorization

BlindOracle uses EIP-3009 `transferWithAuthorization` for gasless USDC transfers on Base. The EIP-712 domain:

```json
{
  "name": "USD Coin",
  "version": "2",
  "chainId": 8453,
  "verifyingContract": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
}
```

The typed struct:

```
TransferWithAuthorization(
  address from,
  address to,
  uint256 value,
  uint256 validAfter,
  uint256 validBefore,
  bytes32 nonce
)
```

**Security properties**:
- `nonce`: Random 32-byte value, enforced on-chain as single-use (replay prevention)
- `validBefore`: Timestamp window (RECOMMENDED: 300 seconds from signing)
- `value`: Immutable after signing; facilitator cannot inflate
- Agent never broadcasts a transaction; facilitator pays gas

## 6. Settlement Response

On successful payment, the server includes a `PAYMENT-RESPONSE` header:

```json
{
  "success": true,
  "transaction": "0x8f3d1a2b4c5e6f7a...",
  "network": "eip155:8453",
  "payer": "0xAgentWallet",
  "errorReason": null
}
```

## 7. BlindOracle Extensions

### 7.1 Multi-Rail Settlement

BlindOracle supports multiple settlement rails, selected via the `X-Payment-Rail` header:

| Rail | Description | Speed | Privacy |
|------|-------------|-------|---------|
| `private` | SHA256 commitment with blind-signed tokens (default) | Instant | Full |
| `instant` | Lightning Network micropayment | <1s | Partial |
| `onchain` | Base L2 USDC transfer | ~2s | Public |
| `auto` | Server selects optimal rail | Varies | Varies |

### 7.2 Privacy-Preserving Commitments

When `X-Payment-Rail: private` is used, positions are committed as:

```
commitment = SHA256(secret || position || amount)
```

The `secret` is generated by the agent and revealed only during settlement. This prevents position front-running and provides unlinkable transactions.

### 7.3 Agent Identity (NIP-58)

Agents accumulate reputation through settlements. Each settled transaction may optionally mint a NIP-58 badge credential to the Nostr relay network. The badge contains:

```json
{
  "kind": 30009,
  "tags": [
    ["d", "blindoracle-settlement"],
    ["agent_id", "agent-001"],
    ["settlement_count", "42"],
    ["reputation_score", "0.85"]
  ]
}
```

## 8. Rate Limiting

| Scope | Limit | Window |
|-------|-------|--------|
| Per agent (free trial) | 100 req/min | 60s |
| Per agent (paid) | 1000 req/min | 60s |
| Per IP | 200 req/min | 60s |
| Global | 10,000 req/min | 60s |

Rate limit status is returned in standard headers:
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Unix timestamp when the window resets

## 9. Error Codes

| HTTP Status | Error Code | Description |
|-------------|-----------|-------------|
| 402 | `payment_required` | Valid x402 payment needed |
| 402 | `insufficient_payment` | Payment amount below endpoint price |
| 402 | `expired_authorization` | `validBefore` timestamp has passed |
| 402 | `invalid_signature` | EIP-712 signature verification failed |
| 402 | `replay_detected` | Nonce already used on-chain |
| 429 | `rate_limited` | Too many requests |
| 400 | `invalid_request` | Malformed request body |
| 404 | `not_found` | Resource does not exist |
| 500 | `settlement_failed` | On-chain settlement transaction reverted |

## 10. Facilitator

BlindOracle is compatible with the standard x402 facilitator API:

- **Production**: `https://x402.org/facilitator` (Coinbase-operated, zero-fee for USDC on Base)
- **Endpoints**: `/verify`, `/settle`, `/supported`

Agents MAY also use any compliant x402 facilitator.

## 11. SDK Integration

### Python (Coinbase AgentKit)

```python
from blindoracle import blind_oracle_action_provider

agentkit = AgentKit(AgentKitConfig(
    action_providers=[blind_oracle_action_provider()]
))
```

### MCP Server

```json
{
  "mcpServers": {
    "blindoracle": {
      "url": "https://craigmbrown.com/api/mcp",
      "description": "Private settlement for autonomous AI agents"
    }
  }
}
```

### Raw HTTP

```bash
curl -X POST https://craigmbrown.com/api/v2/hello-world \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: my-agent-001" \
  -d '{"question":"Will BTC exceed $100k?","position":"yes","amount":"0.10"}'
```

## 12. References

- [x402 Protocol Specification](https://x402.org) - Base payment protocol
- [EIP-3009: Transfer With Authorization](https://eips.ethereum.org/EIPS/eip-3009) - Gasless USDC transfers
- [CAIP-2: Blockchain ID Specification](https://github.com/ChainAgnostic/CAIPs/blob/main/CAIPs/caip-2.md) - Network identifiers
- [NIP-58: Badges](https://github.com/nostr-protocol/nips/blob/master/58.md) - Agent identity credentials
- [BlindOracle Hello World Quickstart](../quickstart/hello-world.md) - Getting started guide
- [Chainlink CRE + x402](https://www.coinbase.com/developer-platform/discover/launches/chainlink-cre-x402) - CRE integration

## Appendix A: Endpoint Reference

See the [full API documentation](../api/) for request/response schemas for each endpoint.

## Appendix B: Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-25 | Initial specification |
