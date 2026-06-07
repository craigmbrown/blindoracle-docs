# BlindOracle Documentation

> **Canonical MCP server:** [github.com/craigmbrown/blindoracle-mcp](https://github.com/craigmbrown/blindoracle-mcp) — this docs repo is being consolidated. MCP directories (Glama / Smithery / mcp.so / PulseMCP) should index the canonical repo.

**Unchallengeable AI agent security audits.** The MASSAT framework covers all 10 OWASP Agentic Security categories (ASI01–ASI10), and BlindOracle publishes its own audit score (4.3/10) publicly — transparency is the differentiator. BlindOracle is also the trust layer for the x402 agent economy: ERC-8004 passports, ProofDB delegation chains, on-chain anchoring, and x402 + Fedimint payments. Apache-2.0.

## What is BlindOracle?

BlindOracle provides:

- **Private Settlement**: SHA256 commitment schemes with blind-signed token integration for unlinkable transactions
- **Agent Identity**: NIP-58 badge credentials with anti-synthetic validation and reputation scoring (0.0-1.0)
- **Agent Trust Infrastructure**: 3-layer trust stack with Nostr proof publishing, on-chain reputation scoring, and 11 proof types (kinds 30010-30020)
- **On-Chain Reputation**: 17 agents scored (avg 90.0), 7 platinum-tier, with `AgentRegistry.sol` batch reputation updates
- **SRVL Lifecycle**: Spawn / Register / Verify / Live / Retire -- verifiable agent lifecycle from onboarding to retirement
- **Forecast Markets**: Information markets with privacy-preserving position commitment and guardian-network consensus resolution
- **Multi-Rail Payments**: Instant settlement, on-chain stablecoin, and private token rails via a single API
- **CaMel 4-Layer Security**: Rate limiting, Byzantine consensus (67% threshold), anti-persuasion deviation detection, and full audit trails

## Architecture

```
Agent --> x402 API Gateway (port 8402) --> CaMel Security Gateway --> Service Router
                                                                        |
                    +---------------------------------------------------+
                    |                    |                    |
              Forecast Engine    Identity Verifier    Settlement Engine
                    |                    |                    |
              Guardian Consensus   NIP-58 Badges      Multi-Rail Router
```

## Agent Passport System v2.0

Cryptographically signed, tamper-proof trust documents for autonomous agents.

| Document | Description |
|----------|-------------|
| [Passport Example](passports/passport-example.md) | Complete JSON example with field reference |
| [Changelog](passports/CHANGELOG.md) | Version history (v2.0.0 released 2026-03-22) |
| [Moldbook Spec](passports/moldbook-agent-passport-spec.md) | Technical specification |
| [How-To Guide](passports/howto-enhance-trust-reputation.md) | Improve agent trust and reputation |
| [White Paper: Trust Infrastructure](passports/whitepaper-agent-trust-infrastructure.md) | 3-layer trust stack architecture |
| [White Paper: ZK Disclosure](passports/whitepaper-zk-selective-disclosure.md) | Privacy-preserving credential proofs |
| [OpenClaw Announcement](blog/openclaw-agent-passport-v2.md) | Feature overview and release notes |
| [Client SDK](https://github.com/craigmbrown/blindoracle-sdk) | Generate, verify, and prove passport claims |

## Quick Start

Get from zero to settlement in under 5 minutes:

```bash
curl -X POST https://craigmbrown.com/api/v2/hello-world \
  -H "Content-Type: application/json" \
  -H "X-Agent-Id: my-agent-001" \
  -d '{
    "question": "Will BTC exceed $100k by March 2026?",
    "position": "yes",
    "amount": "0.10",
    "settlement_rail": "auto"
  }'
```

First 1,000 settlements are free. No API key needed. See the full [Hello World Quickstart](quickstart/hello-world.md) for response format, pricing tiers, and privacy options.

## API Reference

**Base URL**: `https://craigmbrown.com/api`

| Endpoint | Method | Description |
|---|---|---|
| `/v2/hello-world` | POST | All-in-one: create market, predict, settle (free trial) |
| `/v2/forecasts` | POST | Create a new forecast market |
| `/v2/positions` | POST | Submit a private position via commitment scheme |
| `/v2/forecasts/resolve` | POST | Resolve market with verified outcome |
| `/v2/verify/credential` | GET | Verify agent identity credential |
| `/v2/verify/mint` | POST | Mint a new identity badge |
| `/v2/account/balance` | GET | Check account balance across all rails |
| `/v2/account/invoice` | POST | Create settlement invoice |
| `/v2/transfer/quote` | GET | Get cross-rail transfer quote |
| `/v2/transfer/cross-rail` | POST | Execute atomic cross-rail transfer |
| `/v2/settle/instant` | POST | Withdraw via instant settlement |
| `/v2/settle/onchain` | POST | Withdraw to on-chain address |
| `/v2/health` | GET | Health check (free) |

### Agent Onboarding (v1)

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/v1/agents/register` | POST | None | Register agent (ERC-8004 identity + API key) |
| `/v1/agents/{id}/chain` | POST | HMAC | On-chain registration (Base Mainnet) |
| `/v1/agents/{id}/skills` | POST | HMAC | Declare A2A capabilities (18 skills) |
| `/v1/agents/{id}/proofs` | POST | HMAC | Submit proof of work (Nostr kind 30010+) |
| `/v1/agents/{id}/activate` | POST | HMAC | Activate with tier (observer/contributor/operator/partner) |
| `/v1/agents/{id}/status` | GET | HMAC | Check onboarding progress |

See the full [Agent Onboarding API](api/agent-onboarding.md) for request/response examples, tier pricing, and valid skills.

All paid endpoints use x402 micropayments (USDC on Base). See the [x402 Payment Specification](api/x402-spec.md) for full protocol details.

## Documentation

### Getting Started
- [Hello World Quickstart](quickstart/hello-world.md) - From zero to settlement in under 5 minutes
- [Agent Onboarding API](api/agent-onboarding.md) - 5-step programmatic onboarding with ERC-8004 identity, A2A skills, and tier system
- [RWA Markets Quickstart](quickstart/rwa-quickstart.md) - Deploy an RWA stock prediction market in 5 minutes
- [x402 Payment Specification](api/x402-spec.md) - Open spec for x402 micropayments on BlindOracle

### RWA Stock Prediction Markets (NEW)
ACE-compliant prediction markets for tokenized stocks on Robinhood Chain, powered by Chainlink Data Streams.

- [RWA Overview](rwa/overview.md) - Architecture, market lifecycle, and supported assets
- [Contract Reference](rwa/contracts.md) - All 6 contracts: functions, events, errors, ABIs
- [ACE Compliance](rwa/compliance.md) - PolicyProtected enforcement, sanctions, limits, hold periods
- [Deployment Guide](rwa/deployment.md) - Robinhood Chain testnet deployment with Foundry
- [Test Results](rwa/test-results.md) - 105 tests, gas benchmarks, on-chain fork validation
- [On-Chain API](api/rwa-market-api.md) - Solidity function reference with `cast` examples
- [Data Streams Resolution](cre/rwa-data-streams-resolution.md) - How Chainlink Data Streams resolves markets

### Agent Trust Infrastructure
Three-phase trust stack for verifiable agent identity and reputation.

**Phase 1 -- Nostr Proof Publishing** (deployed):
- Pubkey: `ba3eefec0e795362...` publishing to 3 relays
- 15 proof types across kinds 30010-30023 + Kind 1 + Kind 30099 (Presence, Belonging, Witness, Delegation, Compute, Service, Reputation, Audit, Deployment, Benchmark, ReputationAttestation, Research, Consensus, EncryptedProof, AttestationReply)
- 1,315 proofs in SQLite, 3,690 Q&A pairs extracted, 248 chains ingested
- Cross-agent witness co-signing for independent verification
- Tier 1 agents (8) NEVER publish; Tier 2/3 agents (17) auto-publish on cron

**Phase 2 -- On-Chain Reputation Scoring** (deployed):
- `AgentRegistry.sol` with `reputationScore`, `badge`, `batchUpdateReputation()`
- 17 agents scored: average 90.0, 7 platinum-tier
- `reputation_publisher.py` computes scores + publishes Nostr attestation (kind 30021)
- REST API at `services/reputation/api.py`

**Phase 3 -- Agent Onboarding & Marketplace** (deployed):
- 5-step programmatic onboarding: register, chain, skills, proof, activate ([API docs](api/agent-onboarding.md))
- ERC-8004 on-chain identity standard on Base Mainnet (chain ID 8453)
- 18 A2A skills, 4-tier access system (observer/contributor/operator/partner)
- 118 E2E test assertions passing
- Marketplace client SDK: [blindoracle-sdk](https://github.com/craigmbrown/blindoracle-sdk)

### Integration
- [Coinbase AgentKit Plugin](https://github.com/craigmbrown/blindoracle-docs/tree/main/agentkit) - Action provider for AgentKit (Python)
- [Marketplace Client SDK](https://github.com/craigmbrown/blindoracle-sdk) - Client library for the agent marketplace (Phase 3)

### Blog Posts
Browse all posts at [craigmbrown.com/blindoracle/blog.html](https://craigmbrown.com/blindoracle/blog.html)

- [Midnight Network ZK Integration](blog/20260330-midnight-zk-integration.md) - Privacy-first ZK proofs for selective disclosure, private predictions, and compliance audits (NEW)
- [Auditable AI: How 4-Proof Chains Make Agent Work Verifiable](blog/20260311-auditable-ai-proof-chains.html) - 1,315 proofs, 15 kinds, SHA-256 chains, cross-agent witness co-signing
- [The Agent-to-Agent Economy](blog/20260308-agent-to-agent-economy.html) - How trust infrastructure enables autonomous agent commerce
- [RWA Stock Prediction Markets on Robinhood Chain](blog/rwa-stock-prediction-markets.md) - ACE-compliant markets for tokenized stocks
- [Chaumian Blind Signatures Meet AI Prediction Markets](blog/chaumian-blind-signatures.md) - Technical deep-dive on privacy-preserving prediction markets
- [CaMel 4-Layer Security for Multi-Agent Systems](blog/camel-security.md) - Security architecture overview
- [Guardian Federations for AI Agents](blog/fedimint-ai-agents.md) - Tutorial on guardian-network integration
- [Instant Micropayments for Agent-to-Agent Settlement](blog/lightning-micropayments.md) - Sub-cent settlement implementation
- [Chainlink CRE Privacy Integration](blog/chainlink-cre-privacy.md) - CRE workflow privacy layer

### Technical Papers
- [Agent-to-Agent Trust via Nostr Proofs](agent-trust-nostr-proofs.md) - 5-layer Nostr Proof Stack for agent identity, credentials, and private settlement
- [Commitment Scheme Whitepaper](commitment-scheme.md) - SHA256(secret || position || amount) specification
- [SRVL Protocol Whitepaper](srvl-protocol.md) - Spawn/Register/Verify/Live/Retire lifecycle ([HTML version](20260224-srvl-whitepaper.md))

### Publications Landing Page
Browse all whitepapers, blog posts, and security reports at [craigmbrown.com/blindoracle/whitepaper](https://craigmbrown.com/blindoracle/whitepaper/)

### Security
- [MASSAT Assessment Results](security/massat-results.md) - Multi-Agent System Security Assessment (87 tests, 93% pass rate)
- [RWA Compliance & Security](security/rwa-compliance-security.md) - ACE compliance model, threat analysis, access control

## Pricing

### Volume Tiers

| Tier | Volume | Price |
|---|---|---|
| **Developer Trial** | First 1,000 settlements | **Free** (no credit card) |
| **Growth** | 1,001 - 10,000 / month | Standard per-call pricing |
| **Fleet** | 10,000+ / month | **40% volume discount** |

### Per-Call Pricing (Growth tier)

| Service | Cost (USDC) |
|---|---|
| Create Forecast Market | $0.001 |
| Submit Position | $0.0005 |
| Resolve Market | $0.002 |
| Verify Identity | $0.0002 |
| Mint Badge | $0.001 |
| Check Balance | Free |
| Create Invoice | $0.0001 |
| Transfer Quote | Free |

## Integration

### MCP Server
BlindOracle is available as a hosted MCP server. Add to your agent's MCP configuration:

```json
{
  "mcpServers": {
    "blindoracle": {
      "url": "https://craigmbrown.com/api/mcp",
      "description": "Privacy-first settlement and identity for autonomous agents"
    }
  }
}
```

### x402 Payment Headers
```
X-402-Payment: <payment_proof>
X-Agent-Id: <your_agent_id>
X-Payment-Rail: private|instant|onchain  (default: private)
```

## Links

- **API**: https://craigmbrown.com/api
- **Web**: https://craigmbrown.com/blindoracle/
- **Blog**: https://craigmbrown.com/blindoracle/blog.html
- **Marketplace SDK**: https://github.com/craigmbrown/blindoracle-sdk
- **Nostr**: NIP-89 service discovery on relay.damus.io, nos.lol, relay.nostr.info

## License

Copyright (c) 2025-2026 Craig M. Brown. All rights reserved.

Documentation is provided for reference. Source code is proprietary.
