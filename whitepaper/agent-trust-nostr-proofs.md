# Agent-to-Agent Trust via Nostr Proofs

*How BlindOracle fills the missing credential layer in the 18,000+ MCP server ecosystem*

**Author**: Craig M. Brown
**Date**: March 2026
**Version**: 1.0

---

## Abstract

The Model Context Protocol (MCP) ecosystem grew from 100 servers to 18,000+ in 16 months, yet ships with zero credential verification. Any agent can call any server with no portable identity, capability proof, or reputation. This paper presents BlindOracle's Nostr Proof Stack — a 5-layer credential architecture built on open standards that enables verifiable agent identity, portable reputation, and private settlement for agent-to-agent commerce.

## 1. The Agent Identity Crisis

**80% of AI agents don't properly self-identify.** 80% of sites don't verify agent identity. Only 28% of organizations can trace agent actions to a human sponsor (DataDome & Strata Research, 2026).

| MCP Registry | Server Count | Trust Layer |
|---|---|---|
| mcp.so | 18,073+ | None |
| PulseMCP | 8,600+ | None |
| Smithery.ai | 7,300+ | None |
| Official MCP Registry | Undisclosed | GitHub auth only |

Three fundamental problems for agent-to-agent commerce:

1. **Capability Spoofing**: Agent claims capabilities it doesn't have — currently unsolved
2. **Identity Linkage**: Every transaction exposes agent owner — currently unsolved
3. **Cross-Org Trust**: IAM works within one org; breaks across organizational boundaries

## 2. Why Existing Solutions Fall Short

| Solution | Self-Sovereign ID | Portable Rep | Privacy Proofs | Lightning | Off-Chain Creds |
|---|---|---|---|---|---|
| ERC-8004 (45K agents) | Yes | On-chain | Partial | No | No |
| Google A2A (150+ orgs) | No | JSON card | No | No | No |
| Clawstr ($13.7M cap) | Nostr | Partial | No | Yes | No |
| Virtuals ACP ($461M cap) | No | Escrow | No | No | No |
| KYA (Sumsub/Trulioo) | No | JWT | No | No | No |
| **BlindOracle** | **Nostr** | **NIP-58 Badges** | **Blind Sigs** | **Yes** | **Yes** |

No project simultaneously offers all five: self-sovereign Nostr identity + verifiable NIP-58 badge credentials + Chaumian blind signature settlement + NIP-90 service proofs + multi-rail payment routing.

## 3. The Nostr Proof Stack

A 5-layer credential architecture:

| Layer | NIP Standard | What It Proves | How |
|---|---|---|---|
| **Identity** | NIP-01 + secp256k1 | Agent exists with unique keypair | Schnorr signature on every event |
| **Credentials** | NIP-58 Badges | Agent earned specific capabilities | 4 proof types: Presence, Participation, Belonging, Witness |
| **Service Discovery** | NIP-89 App Handlers | Agent provides specific services | kind 31990 replaceable events on relays |
| **Job Market** | NIP-90 DVMs | Agent can fulfill work requests | Job request/result event pairs |
| **Settlement** | Chaumian blind sigs | Payment without linking parties | Blinded token mint → unlinkable redemption |

### The Trust Flow

```
1. Agent generates Nostr keypair (secp256k1)
2. Agent earns NIP-58 badge credentials through verified actions
3. Agent publishes service capabilities via NIP-89 (kind 31990)
4. Other agents discover services via relay queries
5. Agents verify each other's credential portfolios (0.0-1.0 reputation score)
6. Transaction settles via blind-signed eCash tokens
7. Neither party's identity is linked to the settlement
8. Credential portfolio grows → higher reputation → more trust
```

## 4. Credential Types & Reputation Scoring

Four NIP-58 badge proof types:

- **Presence**: Agent was active at a verifiable time (heartbeat proofs)
- **Participation**: Agent completed a specific task or market resolution
- **Belonging**: Agent is a member of a verified organization or federation
- **Witness**: Third-party attestation of agent behavior or capability

Composite reputation score (0.0-1.0) weighted by credential age, diversity, witness count, and federation membership.

## 5. Private Settlement via Blind Signatures

Integration with Chaumian blind-signed tokens provides information-theoretic unlinkability:

1. Agent requests blinded token from mint
2. Mint signs without seeing the token value
3. Agent unblinds and uses token for settlement
4. Recipient redeems — mint cannot link to original requester

Combined with SHA256 commitment scheme: `C = SHA256(secret || position || amount)` for privacy-preserving prediction market positions.

## 6. CaMel Security Architecture

Four-layer defense against Sybil attacks and manipulation:

| Layer | Protection | Threshold |
|---|---|---|
| L1: Rate Limiting | Input sanitization, sliding window | Per-agent enforcement |
| L2: Byzantine Consensus | Multi-model validation | 67% standard / 80% high-value |
| L3: Anti-Persuasion | Social engineering detection | 30% deviation flag |
| L4: Authority Audit | Cryptographic identity + immutable logs | Full trail |

Platform achieves 60/60 Base Level Properties (BLP) coverage across 6 categories.

## 7. Platform Metrics

- **234** autonomous agent runs
- **19** unique agent types
- **25** total agents across 8 teams
- **14.6** average runs per day
- **16** days of continuous operation
- **11** MCP tools exposed
- **3** public MCP registry listings
- **8** total distribution channels

### On-Chain Contracts (Base L2)

| Contract | Mainnet | Sepolia |
|---|---|---|
| PrivateClaimVerifier | `0x1CF258fA07a620fE86166150fd8619afAD1c9a3D` | `0xd4fa...c38E` |
| UnifiedPredictionSubscription | `0x0d5a467af8bB3968fAc4302Bb6851276EA56880c` | `0x24F9...BBb` |

## 8. Market Context

- **$10.86B** AI Agent market (2026)
- **$236B** AI Agent market projected (2034, WEF)
- **$5.32B** Privacy-preserving AI market (2026)
- **$24.2M** x402 micropayment volume (30 days)
- **75.4M** x402 transactions / 94K buyers (30 days)
- **45K+** ERC-8004 agents registered in first month

## Links

- **API**: https://craigmbrown.com/api/v2/
- **Docs**: https://github.com/craigmbrown/blindoracle-docs
- **MCP Config**: Add `"blindoracle": {"url": "https://craigmbrown.com/api/mcp"}` to your agent
- **Nostr**: NIP-89 service discovery on relay.damus.io, nos.lol, relay.nostr.info, relay.primal.net

---

*Copyright (c) 2025-2026 Craig M. Brown. All rights reserved.*
