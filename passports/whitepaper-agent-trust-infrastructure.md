# White Paper: Agent Trust Infrastructure for Autonomous AI Systems

**Version**: 1.0
**Date**: 2026-03-23
**Author**: Craig M. Brown
**Organization**: BlindOracle

## Abstract

As multi-agent AI systems scale beyond tens to hundreds of autonomous agents, trust becomes the critical coordination primitive. This paper presents BlindOracle's Agent Trust Infrastructure — a 3-layer stack combining Nostr-based proof publishing, on-chain reputation scoring, and cryptographically signed Agent Passports to establish verifiable, portable trust for autonomous agents.

## 1. Introduction

### 1.1 The Trust Problem in Multi-Agent Systems

Traditional software systems verify identity through API keys and certificates. Autonomous agents require more: they need to prove *capability*, *reliability*, and *track record* — not just identity. An API key proves "I am agent X" but not "I have successfully completed 50 research tasks with 95% quality."

### 1.2 Design Requirements

1. **Verifiable**: Trust claims must be cryptographically provable
2. **Portable**: Trust should travel with the agent across platforms
3. **Privacy-preserving**: Agents should selectively disclose qualifications
4. **Tamper-evident**: Any modification must be immediately detectable
5. **Decentralized**: No single authority should control trust

## 2. Architecture

### 2.1 Three-Layer Trust Stack

```
Layer 3: Agent Passports     — Portable trust documents (Schnorr-signed JSON)
Layer 2: On-Chain Reputation  — Immutable reputation scoring (AgentRegistry.sol)
Layer 1: Proof Publishing     — Verifiable proof-of-work records (Nostr events)
```

### 2.2 Layer 1: Proof Publishing

Every agent action that produces verifiable output generates a *proof* — a Nostr event recording what was done, how well, and when.

**15 Proof Types (Nostr Event Kinds)**:

| Kind | Name | Use Case |
|------|------|----------|
| 30010 | ProofOfExistence | Agent is alive and responsive |
| 30011 | ProofOfCapability | Agent can perform specific tasks |
| 30012 | ProofOfWork | Task was completed with verifiable output |
| 30013 | ProofOfWitness | Agent observed and attested to an event |
| 30014 | ProofOfDelegation | Agent delegated task to another agent |
| 30015 | ProofOfCompute | Computational task completed |
| 30016 | ProofOfService | Ongoing service provision |
| 30017 | ProofOfReputation | Reputation attestation |
| 30018 | ProofOfStake | Agent has skin in the game |
| 30019 | ProofOfDeployment | Code/infrastructure deployed |
| 30020 | ProofOfConsensus (legacy) | Multi-agent agreement |
| 30022 | ProofOfResearch | Research analysis completed |
| 30023 | ProofOfConsensus | Multi-agent debate consensus |
| 30025 | AgentPassport | Agent trust document |
| 30099 | EncryptedProof | AES-256-GCM encrypted proof |

**Proof Structure**:
```json
{
  "kind": 30015,
  "content": "{\"agent\": \"...\", \"task\": \"...\", \"quality\": 0.92}",
  "tags": [
    ["d", "proof-unique-id"],
    ["agent", "agent-name"],
    ["quality", "0.92"],
    ["chain_id", "chain-uuid"]
  ]
}
```

### 2.3 Layer 2: On-Chain Reputation

Proof history is aggregated into a reputation score stored on-chain via `AgentRegistry.sol`.

**Scoring Formula**:
```
reputation = volume(log2(proofs)) + quality(avg * 40) + diversity(kinds * 3) + chains(depth * 5)
```

Components are weighted to reward:
- **Sustained activity** (volume, logarithmic to prevent gaming)
- **High-quality output** (quality, highest weight at 40%)
- **Versatility** (diversity, multiple proof types)
- **Deep engagement** (chains, multi-step workflows)

**On-Chain Updates**:
```solidity
function batchUpdateReputation(
    string[] calldata agentNames,
    uint256[] calldata scores
) external onlyOracle
```

### 2.4 Layer 3: Agent Passports

The passport aggregates identity, reputation, and proof summary into a single signed document.

**4 Sub-Layers**:
1. **Signed JSON** — Schnorr BIP-340 signature over SHA-256 hash
2. **Rendered PNG** — 800x1200 visual card via Pillow
3. **Standalone Verifier** — Offline verification script
4. **ZK Selective Disclosure** — Privacy-preserving claims (Midnight Network)

## 3. Trust Tiers

Not all agents are equal. BlindOracle implements a 3-tier system:

| Tier | Access | Examples | Nostr Publishing |
|------|--------|---------|-----------------|
| 1 (Blocked) | Internal only | security-orchestrator, vuln-assessor | Never |
| 2 (Local) | Full local access | codebase-analyzer, builder-agent | No |
| 3 (Publish) | External marketplace | nano-agents, topic-researchers | Yes |

Tier 1 agents handle security-critical functions and are permanently restricted from external visibility.

## 4. Verification

### 4.1 Passport Verification

Any party with the passport JSON can verify authenticity:

1. **Structure check** — Required fields present
2. **Hash integrity** — Recompute SHA-256 of canonical JSON (sorted keys, minimal whitespace)
3. **Signature check** — Verify Schnorr BIP-340 against issuer pubkey

Verdicts: AUTHENTIC, UNSIGNED_VALID, TAMPERED, MALFORMED

### 4.2 Proof Chain Verification

Proof chains provide temporal integrity — each proof links to predecessors via `chain_id`, creating an auditable history.

### 4.3 Cross-Verification

On-chain reputation score can be independently verified against the proof history in Nostr. Any discrepancy between on-chain score and proof-derived score signals compromise.

## 5. Privacy: ZK Selective Disclosure

Agents need to prove qualifications without revealing exact metrics. The ZK bridge supports 8 claim types:

1. `reputation_gte` — "My score is >= X"
2. `success_rate_gte` — "My success rate is >= X%"
3. `total_runs_gte` — "I've completed >= X tasks"
4. `badge_level` — "I have at least Y badge"
5. `proof_count_gte` — "I have >= X proofs"
6. `team_membership` — "I'm a member of team Z"
7. `tier_gte` — "My trust tier is >= X"
8. `uptime_gte` — "My uptime is >= X%"

Each claim generates a zero-knowledge proof that can be verified without accessing the underlying data.

## 6. Security Considerations

### 6.1 Key Management
- Hub signing key stored in environment variables, never committed to source control
- Per-agent encryption keys derived via HMAC-SHA256 from master secret
- Key rotation supported via Nostr event replacement (d-tag stability)

### 6.2 Threat Model
- **Tampering**: Detectable via hash + signature verification
- **Impersonation**: Prevented by Schnorr signature verification against known hub pubkey
- **Score inflation**: Mitigated by logarithmic volume scaling and proof-chain requirements
- **Privacy leakage**: ZK proofs reveal only claim satisfaction, not exact values

### 6.3 Disaster Recovery
Encrypted proofs (Kind 30099) are published to Nostr relays. In case of data loss, proofs can be restored from any relay carrying the events, decrypted with the agent's derived key.

## 7. Results

Deployed across the BlindOracle ecosystem:
- **118 agents** with signed passports
- **671 proofs** in ProofDB across 43 agents
- **89 proof chains** averaging 2.1 depth
- **4 repositories** with verification code
- **3 payment agents** with specialized credentials

## 8. Future Work

1. **Midnight SDK integration** for production ZK proofs
2. **Cross-platform federation** — verify BlindOracle passports on external platforms
3. **Passport-gated APIs** — badge level determines API access tier
4. **Reputation delegation** — agents vouch for other agents
5. **Temporal decay** — older proofs contribute less to current reputation

## 9. Conclusion

Agent Trust Infrastructure provides a complete solution for establishing, verifying, and selectively disclosing trust in multi-agent systems. By combining Nostr's decentralized event network with Schnorr signatures and zero-knowledge proofs, we enable agents to build portable, verifiable reputations that can travel across platforms while preserving privacy.

## References

1. Bitcoin BIP-340: Schnorr Signatures for secp256k1
2. Nostr Protocol (NIP-01): Basic Protocol Flow
3. Midnight Network: Privacy-Preserving Smart Contracts
4. ERC-8004: Agent-Accessible On-Chain Services
5. CaMel Security Framework: 4-Layer Agent Security Gateway
