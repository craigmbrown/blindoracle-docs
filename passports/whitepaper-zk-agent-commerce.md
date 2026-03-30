# Privacy-Preserving Agent Commerce: Zero-Knowledge Proofs for Autonomous AI Agents on Midnight Network

**RQ-119 | BlindOracle Technical Whitepaper**

**Author:** Craig M. Brown
**Date:** March 2026
**Version:** 1.0
**Copyright (c) 2026 Craig M. Brown. All rights reserved.**

---

## Abstract

Autonomous AI agents participating in open marketplaces face a fundamental tension: they must prove trustworthiness to transact, yet revealing the data that establishes trust -- reputation scores, trading positions, compliance records -- exposes them to front-running, competitive intelligence leakage, and regulatory risk. This paper presents BlindOracle's integration with the Midnight Network SDK (v4.0.2, mainnet Kukolu) to deliver three zero-knowledge proof capabilities for agent commerce: selective disclosure of reputation claims, private prediction market commitments, and confidential compliance audits. We describe a practical architecture bridging Python agent runtimes to Midnight's Compact/Minokawa ZK circuits via Node.js subprocess orchestration, and demonstrate cross-chain interoperability with Base (ERC-8004 identity), Robinhood Chain (RWA markets), and Chainlink CRE. BlindOracle is the first AI agent platform to deploy ZK-backed credentials on Midnight mainnet.

---

## 1. Introduction

The agent economy is growing rapidly. Marketplaces now host hundreds of AI agents offering prediction, analysis, and execution services. These agents must establish trust with counterparties -- proving they have sufficient reputation, regulatory clearance, or financial standing to participate in a given transaction.

Today, this trust establishment requires full disclosure. An agent proving its reputation score of 92 reveals that exact number. An agent entering a prediction market reveals its position and stake. An agent demonstrating regulatory compliance hands over its complete financial records.

Each disclosure creates attack surface:

- **Front-running:** Competitors observe an agent's prediction market position and trade against it before resolution.
- **Data leakage:** Reputation scores and performance metrics become competitive intelligence freely available to rivals.
- **Regulatory exposure:** Full financial records shared for compliance checks may be subpoenaed, leaked, or misused beyond the original audit scope.

Zero-knowledge proofs eliminate this tension. An agent can prove a statement about its data ("my reputation exceeds 85") without revealing the underlying data (the actual score of 92). This paper describes how BlindOracle implements this capability using the Midnight Network.

---

## 2. Problem Analysis

### 2.1 The Trust-Privacy Dilemma

Agent marketplaces require credential verification at multiple points:

| Verification Point       | Data Required Today         | Risk Created                    |
|--------------------------|-----------------------------|---------------------------------|
| Marketplace registration | Full reputation history     | Competitor profiling            |
| Prediction market entry  | Position direction + amount | Front-running, copy-trading     |
| Compliance audit         | Complete financial records  | Regulatory overreach, data leak |
| Cross-agent negotiation  | Performance metrics         | Strategic disadvantage          |
| Service tier qualification | Exact scores across axes  | Price discrimination            |

### 2.2 Why Existing Approaches Fail

**Raw credential sharing** is the status quo. Agent A sends its full passport to Agent B for verification. Agent B now possesses A's competitive data permanently, with no revocation mechanism.

**Trusted third parties** (centralized verification services) introduce a single point of failure. If the verifier is compromised, all agents' data is exposed. The verifier also accumulates a god-view of the entire marketplace, creating monopoly risk.

**Generic ZK frameworks** (Circom, Noir, Halo2) require agents to compile custom circuits per claim type, manage proving key ceremonies, and operate ZK-specific infrastructure. The integration cost is prohibitive for agent developers focused on AI/ML, not cryptography.

**Midnight Network** solves this with a purpose-built privacy blockchain where ZK proofs are a first-class primitive, smart contracts (Compact language) have native `disclose()` semantics, and the Minokawa runtime handles circuit generation transparently.

---

## 3. Solution Architecture

### 3.1 System Overview

```
+------------------------------------------------------------------+
|                     BLINDORACLE AGENT (Python)                    |
|                                                                   |
|  +------------------+  +------------------+  +-----------------+  |
|  | Selective        |  | Private          |  | Compliance      |  |
|  | Disclosure       |  | Predictions      |  | Audits          |  |
|  | (RQ-050)         |  | (RQ-048)         |  | (RQ-049)        |  |
|  +--------+---------+  +--------+---------+  +--------+--------+  |
|           |                     |                     |           |
|           +----------+----------+----------+----------+           |
|                      |                     |                      |
|              +-------v-------+     +-------v-------+              |
|              | Passport SDK  |     | Commitment    |              |
|              | (8 claim      |     | Manager       |              |
|              |  types)       |     | (SHA-256)     |              |
|              +-------+-------+     +-------+-------+              |
|                      |                     |                      |
+----------------------+---------------------+----------------------+
                       |                     |
              +--------v---------------------v--------+
              |        NODE.JS SUBPROCESS BRIDGE       |
              |  +----------+  +----------+  +------+  |
              |  | local-   |  | local-   |  |remote|  |
              |  | hash     |  | prover   |  |      |  |
              |  | (SHA256) |  | (ZK)     |  |(chain|  |
              |  +----------+  +----------+  +------+  |
              +-------------------+--------------------+
                                  |
              +-------------------v--------------------+
              |        MIDNIGHT SDK (v4.0.2)           |
              |  Compact/Minokawa Smart Contracts      |
              |  disclose() semantics                  |
              |  Kukolu Mainnet                        |
              +-------------------+--------------------+
                                  |
    +-----------------------------+-----------------------------+
    |                             |                             |
+---v---+                   +----v----+                  +-----v------+
| BASE  |                   |MIDNIGHT |                  | ROBINHOOD  |
|ERC-8004|                  | Privacy |                  | CHAIN      |
|Identity|                  | / ZK    |                  | RWA / ACE  |
+---+---+                   +----+----+                  +-----+------+
    |                             |                             |
    +-----------------------------+-----------------------------+
                                  |
                       +----------v----------+
                       |   CHAINLINK CRE     |
                       | Cross-Chain Runtime  |
                       +---------------------+
```

### 3.2 Three Proof Modes

BlindOracle supports three proving modes with increasing trust assumptions:

| Mode           | Mechanism                        | Trust Assumption         | Latency  | Cost     |
|----------------|----------------------------------|--------------------------|----------|----------|
| `local-hash`   | SHA-256 attestation over claims | Verifier trusts issuer   | <100ms   | Free     |
| `local-prover` | Real ZK via compact-runtime     | Cryptographic soundness  | 1-5s     | Free     |
| `remote`       | On-chain Midnight transaction   | Full decentralization    | 10-30s   | Gas fee  |

**`local-hash`** generates a SHA-256 commitment over the claim data, suitable for trusted environments where the verifier accepts the issuer's attestation. This mode is used for development, testing, and intra-fleet agent communication.

**`local-prover`** invokes the Midnight compact-runtime locally to generate a real zero-knowledge proof without submitting a transaction. The proof is cryptographically sound and can be verified by any party holding the verification key. This mode suits high-frequency marketplace interactions.

**`remote`** submits a full transaction to Midnight mainnet (Kukolu), producing an on-chain proof record. This mode provides the strongest guarantees and is used for high-value transactions, regulatory submissions, and cross-organization verification.

### 3.3 Compact Contract Semantics

Midnight's Compact language provides native privacy primitives. A simplified selective disclosure contract:

```
contract AgentReputation {
    state: {
        agent_id: Field,
        reputation_score: Field,
        badge_tier: Field
    };

    fn prove_badge_tier(threshold: Field) -> disclose(result: Bool) {
        result = self.badge_tier >= threshold;
    }

    fn prove_reputation_range(min: Field, max: Field) -> disclose(in_range: Bool) {
        in_range = self.reputation_score >= min && self.reputation_score <= max;
    }
}
```

The `disclose()` keyword marks which values exit the ZK circuit as public outputs. All other state remains private. The Minokawa runtime compiles this to a ZK circuit automatically -- no manual circuit design required.

---

## 4. ZK Capabilities

### 4.1 Selective Disclosure (RQ-050)

Agents prove properties of their passport without revealing raw credentials. BlindOracle supports 8 claim types:

| Claim Type          | Proves                                    | Example Predicate             |
|---------------------|-------------------------------------------|-------------------------------|
| `reputation_tier`   | Badge level meets threshold               | `tier >= GOLD`                |
| `reputation_range`  | Score within range                        | `85 <= score <= 100`          |
| `compliance_status` | Regulatory clearance                      | `sanctions_clear == true`     |
| `fee_threshold`     | Revenue/fees above minimum                | `total_fees >= $500`          |
| `kyc_level`         | KYC tier sufficient                       | `kyc_tier >= 2`               |
| `age_threshold`     | Agent operational history                 | `active_days >= 90`           |
| `task_count`        | Completed task volume                     | `tasks_completed >= 1000`     |
| `accuracy_range`    | Prediction accuracy within band           | `accuracy >= 0.75`            |

**Example I/O -- Prove Gold Badge:**

```python
# Agent request
proof = passport_sdk.prove_claim(
    claim_type="reputation_tier",
    predicate={"operator": ">=", "threshold": "GOLD"},
    mode="local-prover"
)

# Output
{
    "claim_type": "reputation_tier",
    "predicate": "tier >= GOLD",
    "result": true,
    "proof": "0x7a6b3c...f91e",
    "mode": "local-prover",
    "verified": true,
    "agent_id": "agent-oracle-7x",
    "disclosed": ["result"],         # Only the boolean exits the circuit
    "hidden": ["exact_score", "tier_value", "history"]
}
```

The verifier learns only that the agent holds Gold tier or above. The exact score (92), tier assignment history, and performance breakdown remain private.

### 4.2 Private Predictions (RQ-048)

Prediction market entries use a SHA-256 commitment-reveal scheme:

```
COMMIT PHASE                          REVEAL PHASE
+---------------------------+         +---------------------------+
| Agent constructs:         |         | After market resolves:    |
|   position = "TSLA_UP"   |         |   Agent reveals:          |
|   amount   = 500 USDC    |         |     position, amount,     |
|   salt     = random_256  |         |     salt                  |
|                           |         |                           |
| commitment = SHA256(      |         | Verifier checks:          |
|   position || amount ||   |         |   SHA256(revealed) ==     |
|   salt)                   |         |   stored commitment       |
|                           |         |                           |
| Submit: commitment only   |         | Settlement executes       |
+---------------------------+         +---------------------------+
```

**Example I/O -- Hidden Position Commit:**

```python
# Commit
commitment = prediction_sdk.commit(
    market_id="TSLA-2026Q2-DIRECTION",
    position="UP",
    amount=500,
    currency="USDC"
)
# Returns: {"commitment": "a3f8c1...b2e4", "market_id": "TSLA-2026Q2-DIRECTION"}

# Reveal (after market resolves)
result = prediction_sdk.reveal(
    commitment_id="a3f8c1...b2e4",
    position="UP",
    amount=500,
    salt=commitment.salt
)
# Returns: {"verified": true, "payout": 950, "currency": "USDC"}
```

No other participant sees the agent's position or stake until after resolution. This eliminates front-running and copy-trading.

### 4.3 Compliance Audits (RQ-049)

Regulatory bodies can verify agent compliance without accessing full financial records:

**Example I/O -- Fee Threshold Proof:**

```python
# Regulator requests proof of minimum fee payment
proof = compliance_sdk.prove_audit_claim(
    claim_type="fee_threshold",
    predicate={"total_fees_usd": ">=", "threshold": 500},
    audit_period="2026-Q1",
    mode="remote"  # On-chain for regulatory grade
)

# Output (submitted to Midnight mainnet)
{
    "claim_type": "fee_threshold",
    "predicate": "total_fees >= $500",
    "result": true,
    "tx_hash": "0xmidnight_abc123...",
    "block": 1847293,
    "chain": "midnight-kukolu",
    "disclosed": ["result", "audit_period"],
    "hidden": ["exact_fee_amount", "fee_breakdown", "counterparties"]
}
```

The regulator confirms the agent paid at least $500 in fees during Q1 2026. The exact amount ($2,847), the breakdown by counterparty, and the specific transactions remain confidential.

---

## 5. Cross-Chain Architecture

BlindOracle operates across four chains, each serving a distinct purpose:

```
+------------------+     +------------------+     +------------------+
|    MIDNIGHT      |     |      BASE        |     | ROBINHOOD CHAIN  |
|  Privacy Layer   |     |  Identity Layer  |     |   Markets Layer  |
|                  |     |                  |     |                  |
| - ZK proofs      |     | - ERC-8004       |     | - RWA markets    |
| - Private state  |     |   agent tokens   |     | - ACE compliance |
| - disclose()     |     | - On-chain       |     | - Settlement     |
| - Compact lang   |     |   reputation     |     | - Price feeds    |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         +------------------------+------------------------+
                                  |
                       +----------v----------+
                       |    CHAINLINK CRE    |
                       |                     |
                       | - Cross-chain msgs  |
                       | - Oracle data feeds |
                       | - CCIP bridging     |
                       | - ACE integration   |
                       +---------------------+
```

| Chain            | Role                  | Agent Interaction                          |
|------------------|-----------------------|--------------------------------------------|
| Midnight Kukolu  | Privacy / ZK proofs   | Generate and verify ZK claims              |
| Base             | Identity / ERC-8004   | Mint agent identity tokens, store public reputation |
| Robinhood Chain  | RWA markets / ACE     | Prediction markets, regulatory compliance via ACE  |
| Chainlink CRE    | Cross-chain runtime   | Message passing, oracle feeds, CCIP bridging |

**Flow example:** An agent mints its ERC-8004 identity on Base, generates a ZK reputation proof on Midnight, and uses Chainlink CCIP to bridge the proof attestation to Robinhood Chain where it enters a prediction market with ACE-compliant credentials -- all without revealing its actual reputation score.

---

## 6. Comparison to Alternatives

| Approach                    | Privacy | Trust Model         | Integration Cost | Latency | Agent-Native |
|-----------------------------|---------|---------------------|------------------|---------|--------------|
| Raw credential sharing      | None    | Full trust required | Low              | <10ms   | Yes          |
| Trusted third party (TTP)   | Partial | Trust the TTP       | Medium           | 100ms   | Yes          |
| Generic ZK (Circom/Noir)    | Full    | Cryptographic       | Very high        | 5-60s   | No           |
| **BlindOracle + Midnight**  | **Full**| **Cryptographic**   | **Low**          | **<5s** | **Yes**      |

Key differentiators:

- **Agent-native:** Python SDK with subprocess bridge handles all ZK complexity. Agent developers write `prove_claim()`, not circuit definitions.
- **Three proof modes** allow cost/trust tradeoff per use case rather than forcing all interactions through expensive on-chain proofs.
- **Compact language** with `disclose()` semantics is purpose-built for selective disclosure, unlike general-purpose ZK frameworks that require manual public/private input management.
- **Mainnet deployment** on Midnight Kukolu -- not testnet, not simulation.

---

## 7. Security Considerations

**Proof soundness:** In `local-prover` and `remote` modes, proofs are cryptographically sound under the Midnight proof system's security assumptions. A malicious agent cannot forge a proof that its reputation exceeds 85 when it does not.

**Commitment binding:** The SHA-256 commitment scheme for private predictions is computationally binding. An agent cannot change its committed position after observing market movement.

**Salt entropy:** Commitment salts must be generated from a cryptographically secure random source (256-bit minimum). Weak salts enable brute-force recovery of committed values.

**Replay protection:** Each proof includes a nonce and timestamp. Verifiers reject proofs older than a configurable window (default: 5 minutes for `local-prover`, permanent for `remote` on-chain proofs).

**Cross-chain attestation:** CCIP messages carrying proof attestations are signed by Chainlink's decentralized oracle network, preventing spoofed cross-chain claims.

---

## 8. Future Work

**Passport v3.0** will extend the current system with:

- **On-chain ZK claims registry:** Persistent, composable claims stored on Midnight that agents can reference across multiple verifications without regenerating proofs.
- **Compliance API:** RESTful endpoint for regulators to request and verify audit proofs programmatically, with rate limiting and access control per regulatory jurisdiction.
- **Demo application:** Interactive web dashboard demonstrating all three ZK capabilities with live Midnight mainnet transactions.
- **Batch proofs:** Aggregate multiple claims into a single proof to reduce verification overhead for agents requiring simultaneous reputation, compliance, and performance attestation.
- **Threshold disclosure:** Prove compound predicates ("reputation >= 85 AND fees >= $500 AND kyc_tier >= 2") in a single proof rather than three separate proofs.
- **Revocation:** On-chain revocation registry allowing issuers to invalidate claims without revealing which specific claim was revoked.

---

## 9. Conclusion

AI agent commerce requires trust establishment without data exposure. BlindOracle's integration with Midnight Network delivers this through three ZK capabilities -- selective disclosure, private predictions, and compliance audits -- accessible via a Python SDK that abstracts all cryptographic complexity. The three-tier proof mode system (local-hash, local-prover, remote) allows agents to choose their trust/cost tradeoff per interaction. Cross-chain architecture spanning Midnight, Base, Robinhood Chain, and Chainlink CRE enables agents to maintain a single private identity across multiple marketplaces and regulatory jurisdictions.

BlindOracle is the first AI agent platform to deploy ZK-backed credentials on Midnight mainnet, establishing a foundation for privacy-preserving agent commerce at scale.

---

## References

1. Midnight Network. "Compact Language Specification v4.0." Midnight Documentation, 2025.
2. Midnight Network. "Kukolu Mainnet Launch." https://midnight.network, 2025.
3. Chainlink Labs. "Chainlink Runtime Environment (CRE)." Chainlink Documentation, 2025.
4. Chainlink Labs. "Agent Compliance Engine (ACE)." Chainlink Labs Blog, 2026.
5. ERC-8004. "Agent Identity Token Standard." Ethereum Improvement Proposals, 2025.
6. Brown, C. "Agent Trust Infrastructure: ERC-8004 Identity and Reputation for AI Agents." BlindOracle Whitepaper Series, 2026.
7. Brown, C. "ZK Selective Disclosure for Agent Passports." BlindOracle Technical Report RQ-050, 2026.
8. Robinhood. "Robinhood Chain: Real-World Asset Markets." Robinhood Documentation, 2026.
9. Goldwasser, S., Micali, S., Rackoff, C. "The Knowledge Complexity of Interactive Proof Systems." SIAM Journal on Computing, 1989.
10. Ben-Sasson, E., et al. "SNARKs for C: Verifying Program Executions Succinctly and in Zero Knowledge." CRYPTO 2013.

---

*Copyright (c) 2026 Craig M. Brown. All rights reserved. BlindOracle is a product of the TheBaby Multi-Agent System. Midnight and Compact are trademarks of Input Output Global, Inc. Chainlink is a trademark of Chainlink Labs.*
