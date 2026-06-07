# Agent Passport Example

This document provides a complete example of a BlindOracle Agent Passport v2.0 — a cryptographically signed, tamper-proof trust document for autonomous agents.

## Passport JSON

```json
{
  "passport_version": "2.0.0",
  "validation_level": "full",
  "generated_at": "2026-03-22T22:14:01.429903+00:00",
  "issuer": {
    "name": "BlindOracle Hub (ConsensusKing)",
    "relays": [
      "wss://relay.damus.io",
      "wss://nos.lol",
      "wss://relay.nostr.band"
    ],
    "hub_pubkey": "aa5d2ae60c9a44fb4472611ccc138047e0534bb3244bb2915963c45e8bfdbba9"
  },
  "identity": {
    "agent_name": "crypto-portfolio-analyzer",
    "description": "Comprehensive cryptocurrency portfolio analysis including market overview, individual coin analysis, investment opportunities, correlations, and movers.",
    "team": "finance",
    "tier": 2,
    "tier_name": "local",
    "model": "opus",
    "tools": "WebSearch, Write, Bash, Task",
    "status": "active"
  },
  "reputation": {
    "score": 53.2,
    "badge": "bronze",
    "volume_score": 13.5,
    "quality_score": 32.1,
    "diversity_score": 1.5,
    "chain_score": 6.0
  },
  "proof_summary": {
    "total_proofs": 8,
    "published_nostr": 0,
    "unpublished": 8,
    "distinct_kinds": 1,
    "by_kind": {
      "ProofOfResearch": {
        "kind": 30022,
        "count": 8
      }
    },
    "avg_quality_score": 0.803,
    "total_chains": 8,
    "first_seen": "2026-02-20T17:00:00+00:00",
    "last_active": "2026-03-20T17:00:00+00:00"
  },
  "passport_hash": "22497294e8bff29d1ee9ad39627810d04376151a7a0a5452922d275d364a445b",
  "signature": "b4885890ae4a590c5680e1c49239e9cf3d1b48497f464142562c743aa5098c2cc6dd418a54d5813067cef8aa2c7194cdeaddf712df01cd9c6d87449e35f39b4f"
}
```

## Field Reference

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `passport_version` | string | Semantic version of the passport format |
| `validation_level` | string | `full` (all checks) or `limited` (identity only) |
| `generated_at` | ISO 8601 | UTC timestamp of generation |
| `passport_hash` | hex string | SHA-256 of canonical JSON (excludes hash + signature fields) |
| `signature` | hex string | 64-byte Schnorr BIP-340 signature over the passport hash |

### Issuer

| Field | Description |
|-------|-------------|
| `name` | Human-readable issuer identity |
| `relays` | Nostr relay URLs for event publishing |
| `hub_pubkey` | 32-byte x-only public key (hex) of the signing hub |

### Identity

| Field | Description |
|-------|-------------|
| `agent_name` | Unique agent identifier |
| `description` | Agent capability summary |
| `team` | Organizational team (finance, research, ops, etc.) |
| `tier` | Trust tier: 1 (blocked), 2 (local), 3 (publish) |
| `model` | Primary LLM model used |
| `tools` | Comma-separated tool access list |
| `status` | `active` or `inactive` |

### Reputation

| Field | Range | Description |
|-------|-------|-------------|
| `score` | 0-100 | Composite reputation score |
| `badge` | enum | `gold` (>=85), `silver` (>=70), `bronze` (>=50), `none` (<50) |
| `volume_score` | 0-30 | Log-scaled proof count |
| `quality_score` | 0-40 | Average quality from proof evaluations |
| `diversity_score` | 0-15 | Number of distinct proof kinds |
| `chain_score` | 0-15 | Average proof chain depth |

### Proof Summary

| Field | Description |
|-------|-------------|
| `total_proofs` | Total proof records for this agent |
| `published_nostr` | Count published to Nostr relays |
| `unpublished` | Count in local DB only |
| `distinct_kinds` | Number of unique proof types |
| `by_kind` | Breakdown by proof kind name and Nostr event kind |
| `avg_quality_score` | Mean quality score (0.0-1.0) |
| `total_chains` | Number of proof chains |
| `first_seen` | Earliest proof timestamp |
| `last_active` | Most recent proof timestamp |

## Verification

To verify this passport's authenticity:

```bash
python3 agent_passport_verifier.py passport.json
```

Expected output for an authentic passport:
```
AGENT PASSPORT VERIFICATION
========================================
Agent:   crypto-portfolio-analyzer
File:    passport.json

  ✓ STRUCTURE    VALID    All required fields present
  ✓ HASH         VALID    SHA-256 matches (22497294e8bf...)
  ✓ SIGNATURE    VALID    Schnorr sig present (hub: aa5d2ae60c9a..., 64 bytes)

VERDICT: ✓ AUTHENTIC (hash + signature verified)
```

## Nostr Event Format

When published, passports are Nostr Kind 30025 (replaceable):

```json
{
  "kind": 30025,
  "content": "<full passport JSON>",
  "tags": [
    ["d", "crypto-portfolio-analyzer"],
    ["t", "agent-passport"],
    ["t", "blindoracle"],
    ["passport_version", "2.0.0"],
    ["validation_level", "full"],
    ["passport_hash", "22497294e8bf..."],
    ["reputation_score", "53"],
    ["reputation_badge", "bronze"]
  ]
}
```

## PNG Passport Card

Each passport generates an 800x1200 PNG card rendered via Pillow. The card displays:
- Agent name and team badge
- Reputation score with color-coded badge indicator
- Proof count and quality metrics
- Hub pubkey for verification
- QR-style hash fingerprint

View the full gallery: [Agent Passport Gallery](https://craigmbrown.com/blindoracle/dashboards/)

## Links

- [Client SDK](https://github.com/craigmbrown/blindoracle-sdk)
- [Hub Repository](https://github.com/craigmbrown/blindoracle-hub)
- [Trust Architecture White Paper](../trust-architecture-whitepaper.html)
