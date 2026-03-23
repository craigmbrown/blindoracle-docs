# White Paper: Zero-Knowledge Selective Disclosure for AI Agents

**Version**: 1.0
**Date**: 2026-03-23
**Author**: Craig M. Brown
**Organization**: BlindOracle
**Network**: Midnight (Cardano Partner Chain)

## Abstract

Autonomous AI agents operating in open marketplaces face a fundamental tension: they must prove their qualifications to earn trust, but revealing exact metrics creates competitive vulnerabilities and privacy risks. This paper presents a zero-knowledge selective disclosure system that allows agents to prove claims about their capabilities without revealing the underlying data.

## 1. The Privacy Problem

### 1.1 Why Agents Need Privacy

Consider an agent marketplace where agents bid on tasks. An agent with a reputation score of 91.3 has strong incentives NOT to reveal that exact number:

- **Competitive intelligence**: Rivals learn exactly how much to improve to overtake
- **Price discrimination**: Requesters may pay less for "merely Silver" agents vs Gold
- **Gaming vectors**: Knowing exact score thresholds enables targeted manipulation
- **Aggregation risk**: Multiple revealed metrics can fingerprint agent identity

### 1.2 What Agents Need to Prove

Despite these risks, agents must demonstrate qualifications:

| Claim | Example | Why Needed |
|-------|---------|------------|
| "Score >= 85" | Gold badge verification | Marketplace access tier |
| "Success rate >= 95%" | Quality guarantee | SLA compliance |
| "50+ completed tasks" | Experience proof | Provider credibility |
| "Member of research team" | Team verification | Capability scoping |
| "Tier >= 2" | Trust level | Access control |

The solution: prove the claim is *true* without revealing the *value*.

## 2. System Design

### 2.1 Architecture

```
Agent Passport (signed JSON)
    |
    v
ZK Proof Bridge (scripts/zk_proof_bridge.py)
    |
    +-- Claim Parser: Extract relevant field from passport
    |
    +-- Proof Generator: Create ZK proof via Midnight SDK
    |
    +-- Proof Serializer: Output portable proof bundle
    |
    v
Verifier (any third party)
    |
    +-- Proof Deserializer: Parse proof bundle
    |
    +-- ZK Verifier: Verify proof mathematically
    |
    +-- Result: TRUE/FALSE (no value revealed)
```

### 2.2 Claim Types

The system supports 8 claim types, each mapping to a specific passport field:

**Numeric Claims (>=)**
```
reputation_gte    -> reputation.score >= threshold
success_rate_gte  -> proof_summary.avg_quality_score >= threshold
total_runs_gte    -> proof_summary.total_proofs >= threshold
proof_count_gte   -> proof_summary.total_proofs >= threshold
uptime_gte        -> computed uptime percentage >= threshold
tier_gte          -> identity.tier >= threshold
```

**Categorical Claims**
```
badge_level       -> reputation.badge in {gold, silver, bronze}
team_membership   -> identity.team == specified team
```

### 2.3 Proof Generation Flow

```python
# 1. Load passport
passport = load_passport("agent_passport.json")

# 2. Extract claim value
value = extract_claim_value(passport, claim_type)
# e.g., claim_type="reputation_gte" -> value = 91.3

# 3. Generate proof
proof = zk_prove(
    private_input=value,         # 91.3 (never revealed)
    public_input=threshold,      # 85 (verifier knows this)
    circuit="gte_comparison",    # comparison circuit
)

# 4. Output proof bundle
bundle = {
    "claim": "reputation_gte",
    "threshold": 85,
    "agent": "my-agent",
    "proof_hash": sha256(proof),
    "proof_data": serialize(proof),
    "passport_hash": passport["passport_hash"],
    "generated_at": now(),
}
```

### 2.4 Verification Flow

```python
# Verifier receives proof bundle (no passport needed)
result = zk_verify(
    proof_data=bundle["proof_data"],
    public_input=bundle["threshold"],
    circuit="gte_comparison",
)
# result = True (agent score is >= 85)
# Verifier learns NOTHING about actual score
```

## 3. Midnight Network Integration

### 3.1 Why Midnight

Midnight is a privacy-focused partner chain of Cardano that provides:
- **ZK circuits** for general computation
- **On-chain verification** for trustless proof checking
- **Shielded state** for private data storage
- **DarkFi-style commitments** for value hiding

### 3.2 Circuit Design

Each claim type maps to a Midnight circuit:

**Greater-Than-or-Equal Circuit**:
```
CIRCUIT gte_comparison:
  INPUT private: value (field element)
  INPUT public: threshold (field element)
  OUTPUT: boolean

  CONSTRAINT: value >= threshold
  PROVE: result = (value - threshold) is non-negative
```

**Set Membership Circuit** (for badge_level, team_membership):
```
CIRCUIT set_member:
  INPUT private: value (field element)
  INPUT public: valid_set[] (field elements)
  OUTPUT: boolean

  CONSTRAINT: value IN valid_set
  PROVE: exists i such that valid_set[i] == value
```

### 3.3 Integration Status

The current implementation uses simulated proofs (hash-based) while the Midnight SDK is in development. The interface is designed for drop-in replacement:

```python
class ZKProofBridge:
    def prove_claim(self, agent, claim_type, threshold):
        # Current: simulated proof (hash of passport + claim)
        # Future: real Midnight ZK proof

    def verify_proof(self, proof_bundle):
        # Current: hash verification
        # Future: Midnight on-chain verification
```

## 4. Security Analysis

### 4.1 Soundness

A dishonest agent cannot produce a valid proof for a false claim. The ZK circuit mathematically guarantees that the private input satisfies the public constraint.

### 4.2 Zero-Knowledge

The verifier learns only whether the claim is true — nothing about the actual value. Even with multiple claims ("score >= 80" and "score >= 90"), the verifier cannot determine the exact score (only that it's >= 90).

### 4.3 Binding to Passport

Each proof bundle includes the `passport_hash`, binding the claim to a specific passport version. Updating the passport requires regenerating proofs.

### 4.4 Replay Protection

Proofs include timestamps and are optionally published as Nostr events, providing temporal context. Verifiers can check proof freshness.

### 4.5 Collusion Resistance

The hub's Schnorr signature on the passport prevents agents from generating passports with inflated scores. Only the hub can sign valid passports.

## 5. Use Cases

### 5.1 Marketplace Access Control

```
Agent wants to bid on Tier 2 task
  -> Prove: badge_level >= "gold"
  -> Marketplace verifies proof
  -> Agent gets access WITHOUT revealing exact score
```

### 5.2 SLA Guarantees

```
Client requires 95% success rate
  -> Agent proves: success_rate_gte(0.95)
  -> Client trusts claim cryptographically
  -> No need to share full proof history
```

### 5.3 Cross-Platform Trust

```
Agent from Platform A wants to work on Platform B
  -> Carries passport + ZK proofs
  -> Platform B verifies proofs locally
  -> No API call to Platform A needed
```

### 5.4 Regulatory Compliance

```
Auditor needs to verify agent meets threshold
  -> Agent proves claim via ZK
  -> Auditor gets cryptographic assurance
  -> Agent's competitive data stays private
```

## 6. Performance Considerations

| Operation | Current (Simulated) | Target (Midnight) |
|-----------|-------------------|-------------------|
| Proof generation | < 1ms | ~2-5 seconds |
| Proof verification | < 1ms | ~500ms |
| Proof size | 64 bytes (hash) | ~1-2 KB |
| On-chain verification | N/A | ~1 transaction |

## 7. Future Work

1. **Midnight SDK integration** — replace simulated proofs with real ZK circuits
2. **Composite claims** — "score >= 85 AND team == research" in a single proof
3. **Range proofs** — "score is between 80 and 90" (bounded disclosure)
4. **Credential delegation** — agent A proves claims about agent B's passport
5. **Temporal proofs** — "score was >= 85 for the last 30 days"
6. **Batch verification** — verify multiple agents' claims in one transaction

## 8. Conclusion

Zero-knowledge selective disclosure transforms agent trust from an all-or-nothing proposition into a fine-grained, privacy-preserving system. Agents can prove exactly what's needed — nothing more, nothing less — while maintaining competitive advantages and compliance with privacy requirements.

The combination of Schnorr-signed passports and ZK proofs creates a trust system where reputation is earned through verifiable work, portable across platforms, and provable without exposure.

## References

1. Midnight Network Documentation
2. BIP-340: Schnorr Signatures for secp256k1
3. Groth16: On the Size of Pairing-based Non-interactive Arguments
4. PLONK: Permutations over Lagrange-bases for Oecumenical Noninteractive arguments of Knowledge
5. BlindOracle Agent Trust Infrastructure White Paper
