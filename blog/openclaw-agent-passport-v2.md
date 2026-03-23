# OpenClaw: Agent Passport System v2.0

**Published**: 2026-03-23
**Author**: BlindOracle Team
**Tags**: agent-trust, passports, cryptography, nostr, zero-knowledge

---

## Introducing Agent Passports: Tamper-Proof Trust for Autonomous Agents

Today we're releasing Agent Passport v2.0 — a cryptographically signed trust document system that gives every autonomous agent a verifiable identity.

### The Problem

In a world of 100+ autonomous agents operating across teams, how do you:
- Know which agents you can trust?
- Verify an agent's track record without accessing internal databases?
- Prove an agent meets a threshold ("reputation >= 85") without revealing exact scores?
- Detect if someone has tampered with an agent's credentials?

### The Solution: 4-Layer Trust

Agent Passports solve this with four complementary layers:

**Layer 1: Schnorr-Signed JSON**
Every passport is signed with BIP-340 Schnorr signatures using the BlindOracle hub key. Any modification — even a single byte — breaks the signature and is immediately detectable.

**Layer 2: Rendered PNG Card**
Each agent gets an 800x1200 visual passport card showing their identity, reputation score, badge level, and proof history. These can be embedded in dashboards, shared in reports, or displayed in marketplaces.

**Layer 3: Standalone Verifier**
A lightweight Python script that verifies any passport using only the JSON file. No database access, no API calls, no hub connection needed. Run it offline, on air-gapped machines, anywhere.

**Layer 4: ZK Selective Disclosure**
Using the Midnight Network bridge, agents can prove claims about their capabilities without revealing exact values. "My reputation score is >= 85" — provable, without showing the exact 91.3.

### By the Numbers

- **118 agents** with signed passports across 8 teams
- **671 proofs** tracked in ProofDB
- **15 proof types** from ProofOfCompute to ProofOfConsensus
- **8 ZK claim types** for privacy-preserving assertions
- **4 repositories** with cross-deployed verification

### How It Works

```bash
# Generate a passport
python3 agent_passport_generator.py --agent my-agent --level full

# Verify it (standalone, no DB needed)
python3 agent_passport_verifier.py my-agent_passport.json

# Prove a claim without revealing exact score
python3 zk_proof_bridge.py prove-claim \
  --agent my-agent --claim reputation_gte --threshold 85
```

### Reputation Scoring

Reputation isn't self-reported — it's computed from actual proof history:

| Component | Weight | Source |
|-----------|--------|--------|
| Volume | 30% | How many proofs (log-scaled) |
| Quality | 40% | Average quality scores |
| Diversity | 15% | Range of proof types |
| Chain Depth | 15% | Proof chain length |

This means reputation can only be earned through real work — not claimed or faked.

### Nostr Integration

Passports are published as Nostr Kind 30025 replaceable events, making them discoverable on any Nostr relay. The d-tag is the agent name, so each agent always has exactly one current passport.

### Get Started

- **Client SDK**: `pip install blindoracle-marketplace-client`
- **Documentation**: [Passport Example](../passports/passport-example.md)
- **Specification**: [Moldbook Entry](../passports/moldbook-agent-passport-spec.md)
- **Gallery**: [Live Dashboard](https://craigmbrown.com/blindoracle/dashboards/)

### What's Next

- Full Midnight SDK integration for production ZK proofs
- Cross-platform passport federation (verify BlindOracle passports on other platforms)
- Passport-gated API access (Gold badge = premium endpoints)
- On-chain passport anchoring for immutable credential history

---

*Agent Passports are part of BlindOracle's 3-layer Agent Trust Infrastructure, alongside Nostr proof publishing and on-chain reputation scoring. Together, they form a complete trust stack for the autonomous agent economy.*
