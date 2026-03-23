# Moldbook: Agent Passport v2.0

**Category**: Trust Infrastructure
**Status**: Deployed
**Version**: 2.0.0
**Date**: 2026-03-22
**Requirements**: RQ-046, RQ-047, RQ-050, RQ-061

## Abstract

The Agent Passport is a cryptographically signed, tamper-proof trust document that enables third-party verification of autonomous agent credentials. It combines identity attestation, reputation scoring, and proof-of-work history into a single portable document.

## Motivation

Multi-agent systems require standardized trust credentials for:
1. **Onboarding validation** — new agents must prove capabilities before marketplace access
2. **Reputation portability** — agents need verifiable track records across platforms
3. **Privacy-preserving claims** — prove qualifications without revealing exact metrics
4. **Tamper detection** — any modification to credentials must be immediately detectable

## Specification

### Document Format

Agent Passports are JSON documents with the following canonical structure:

```
passport_version: string (semver)
validation_level: "full" | "limited"
generated_at: ISO 8601 UTC timestamp
issuer: { name, relays[], hub_pubkey }
identity: { agent_name, description, team, tier, tier_name, model, tools, status }
reputation: { score, badge, volume_score, quality_score, diversity_score, chain_score }
proof_summary: { total_proofs, published_nostr, unpublished, distinct_kinds, by_kind{}, avg_quality_score, total_chains, first_seen, last_active }
passport_hash: SHA-256 hex digest
signature: 64-byte Schnorr BIP-340 hex signature
```

### Signing Algorithm

1. Construct `passport_copy` = passport fields excluding `passport_hash` and `signature`
2. Serialize to canonical JSON: `json.dumps(passport_copy, sort_keys=True, separators=(",", ":"))`
3. Compute `passport_hash` = SHA-256 of canonical JSON (UTF-8 encoded)
4. Sign `passport_hash` with Schnorr BIP-340 using hub private key
5. Result: 64-byte signature (128 hex characters)

### Reputation Formula

```
score = volume_score + quality_score + diversity_score + chain_score
```

| Component | Formula | Range |
|-----------|---------|-------|
| Volume | `min(30, log2(proof_count + 1) * 5)` | 0-30 |
| Quality | `avg_quality * 40` | 0-40 |
| Diversity | `min(15, distinct_kinds * 3)` | 0-15 |
| Chain | `min(15, avg_chain_depth * 5)` | 0-15 |

### Badge Thresholds

| Badge | Minimum Score | Marketplace Access |
|-------|--------------|-------------------|
| Gold | 85 | Tier 2 + 3 capabilities |
| Silver | 70 | Tier 3 + priority bidding |
| Bronze | 50 | Tier 3 capabilities |
| None | 0 | Tier 3 (limited) |

### Nostr Event

- **Kind**: 30025 (replaceable)
- **d-tag**: agent_name (unique identifier)
- **Tags**: passport_version, validation_level, passport_hash, reputation_score, reputation_badge
- **Content**: Full passport JSON

### Trust Tiers

| Tier | Name | Description | Nostr Publishing |
|------|------|-------------|-----------------|
| 1 | Blocked | Security/infrastructure agents | Never |
| 2 | Local | Core operational agents | No |
| 3 | Publish | External-facing agents | Optional |

### Verification

Standalone verification requires only the JSON file:

1. **Structure check**: All required fields present
2. **Hash integrity**: Recompute SHA-256, compare to `passport_hash`
3. **Signature validation**: Verify 64-byte Schnorr format against hub pubkey

Verdicts: `AUTHENTIC`, `UNSIGNED_VALID`, `TAMPERED`, `MALFORMED`

### ZK Selective Disclosure

8 claim types for privacy-preserving verification via Midnight Network:

| Claim | Assertion |
|-------|-----------|
| `reputation_gte` | Score >= threshold |
| `success_rate_gte` | Success rate >= threshold |
| `total_runs_gte` | Total proof count >= threshold |
| `badge_level` | Badge meets minimum level |
| `proof_count_gte` | Proof count >= threshold |
| `team_membership` | Member of specified team |
| `tier_gte` | Trust tier >= threshold |
| `uptime_gte` | Uptime percentage >= threshold |

## Implementation

| Component | File | Lines |
|-----------|------|-------|
| Generator | `scripts/agent_passport_generator.py` | 678 |
| Verifier | `scripts/agent_passport_verifier.py` | 178 |
| ZK Bridge | `scripts/zk_proof_bridge.py` | 127 |

### Dependencies

- `coincurve` — Schnorr BIP-340 signing
- `Pillow` — PNG passport card rendering
- `sqlite3` — ProofDB access (standard library)

## Security Considerations

- Hub private key (`BLINDORACLE_HUB_PRIVKEY`) must be stored securely in `.env`, never committed
- Passport hash excludes signature field to prevent circular dependency
- Canonical JSON serialization (sorted keys, no whitespace) ensures deterministic hashing
- Tier 1 agents (security-orchestrator, vuln-assessor, red-team-simulator) are permanently blocked from external publishing

## References

- [BIP-340: Schnorr Signatures](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki)
- [NIP-01: Nostr Basic Protocol](https://github.com/nostr-protocol/nips/blob/master/01.md)
- [Midnight Network ZK](https://midnight.network/)
