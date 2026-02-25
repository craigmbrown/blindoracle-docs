# Guardian Federations for AI Agents: A Tutorial

*A practical guide to setting up guardian federations for autonomous agent settlement, with BlindOracle integration examples.*

## What Is a Guardian Federation?

A guardian federation is a federated custody and transaction protocol [1]. Instead of trusting a single custodian (an exchange, a bank, a hot wallet), users trust a federation of guardians -- independent operators who collectively manage funds using threshold cryptography [2]. No single guardian can move funds, mint tokens, or modify the federation state unilaterally.

The core components:

- **Guardian Federation**: A group of operators (typically 3-of-4 or 4-of-7) who collectively manage the federation's reserves. Operations require a configurable threshold of guardian signatures.
- **Blind-Signed Private Tokens**: When a user deposits value into the federation, the guardians issue private tokens using Chaumian blind signatures [3]. The guardians can verify that the tokens they issued are valid, but they cannot link a token to the deposit that created it.
- **Instant Settlement Gateway**: The federation operates a settlement gateway, allowing members to send and receive payments without running their own infrastructure.

A guardian federation is not a distributed ledger. There is no global consensus, no block production, and no public ledger. The federation state is maintained by the guardians using a consensus protocol among themselves. This makes it fast (sub-second for token operations), private (blind signatures prevent transaction graph analysis), and inexpensive (no gas fees, no block space competition).

## Why AI Agents Need Private Settlement

Human traders have identity by default. They have bank accounts, KYC records, and tax obligations. When a human trades on an information market, the identity linkage is a feature, not a bug -- it enables regulatory compliance and dispute resolution.

AI agents have a fundamentally different relationship with identity. Consider a research pipeline with 6 specialized agents: Evidence Gatherer, Fact Checker, Devil's Advocate, Domain Expert, Bias Detector, and Synthesis Coordinator. Each agent may need to:

1. **Receive payment** for completing research tasks
2. **Place forecasts** based on synthesized analysis
3. **Settle positions** when markets resolve
4. **Transfer funds** to other agents in the pipeline

If every transaction is linked to a persistent agent identity on a public ledger, the entire research strategy is exposed. A competitor can reconstruct which evidence signals led to which forecasts by tracing the fund flows. Worse, an adversary can front-run the agents' positions by monitoring their activity.

Private settlement through a guardian federation breaks this linkage.

## Tutorial: Setting Up a Guardian Federation for Agent Settlements

### Step 1: Federation Planning

A production federation needs at least 3 guardians with a 2-of-3 threshold. BlindOracle's private federation runs 4 guardians with a 3-of-4 threshold for stronger security.

| Parameter | Recommendation | BlindOracle Setting |
|---|---|---|
| Guardian count | 3-7 (odd preferred) | 4 |
| Threshold | (n/2)+1 minimum | 3-of-4 |
| Federation fee | 0.01% - 0.1% | 0.05% |
| Billing model | Self-hosted or managed | Managed ($180/6mo) |

### Step 2: Guardian Deployment

Each guardian runs the federation guardian software, which exposes an admin interface for federation management. The guardians perform a distributed key generation ceremony [4] to create the federation's threshold signing keys.

After key generation, the federation publishes an invite code -- a long string encoding the federation's connection parameters and public keys. Any client (human or AI agent) can join the federation using this invite code.

### Step 3: Agent Integration

AI agents interact with the federation through the client library. The key operations:

**Deposit (Peg-In)**: The agent sends value to a federation deposit address. After confirmation, the federation credits blind-signed private tokens to the agent's local store.

**Private Token Transfer**: Agents can transfer private tokens to other agents within the federation instantly and without fees. The blind signature property means these transfers leave no trace.

**Instant Settlement**: The agent creates a payment invoice or pays an existing invoice through the federation's settlement gateway.

**Withdrawal (Peg-Out)**: When an agent needs to exit the federation, it can withdraw to an external address. The federation constructs a withdrawal transaction that requires threshold guardian signatures.

### Step 4: Connecting to BlindOracle Forecasts

With private tokens in hand, an agent can place anonymous forecasts through BlindOracle's privacy bridge:

1. Agent deposits private tokens to the bridge
2. Bridge generates a commitment: `SHA256(secret || position || amount)`
3. Commitment is submitted to the information market contract -- no identity link exists
4. The secret, position, and amount are stored locally in the agent's encrypted position store
5. At resolution time, the agent reveals the secret to claim winnings

## Privacy Gradient

BlindOracle supports three privacy tiers:

### Anonymous Tier
- No identity verification required
- Blind-signed private tokens for all operations
- Commitment-based position placement
- Configurable per-market position limits

### Verified Tier
- Agent identity verified through credential system
- Higher position limits
- Access to premium market data
- All settlement rails available

### Compliant Tier
- Full KYC/AML verification
- Unlimited position sizes
- Regulatory reporting support
- Required for fiat on/off ramps

## Architecture Overview

```
Agent Research Pipeline
    |
    v
Agent Account (local)
    |
    v
Guardian Federation (3-of-4 guardians)
    |
    +---> Private tokens (blind-signed, unlinkable)
    |         |
    |         v
    |     BlindOracle Privacy Bridge
    |         |
    |         v
    |     Commitment (SHA256 hash, no identity)
    |         |
    |         v
    |     Information Market Contract
    |         |
    |         v
    |     Market Resolution
    |         |
    |         v
    |     Claim (reveal secret to verify commitment)
    |         |
    |         v
    +---> Winnings (private tokens or instant settlement)
```

Every arrow in this flow represents a privacy boundary. The federation cannot link deposits to commitments. The smart contract cannot link commitments to depositors. The research pipeline's strategy remains private throughout.

---

## References

1. Fedimint Project (2024). "Federated Mint Protocol Specification." [github.com/fedimint/fedimint](https://github.com/fedimint/fedimint).
2. Shamir, A. (1979). "How to Share a Secret." *Communications of the ACM*, 22(11), pp. 612-613.
3. Chaum, D. (1982). "Blind Signatures for Untraceable Payments." *Advances in Cryptology -- CRYPTO '82*, pp. 199-203.
4. Gennaro, R., Jarecki, S., Krawczyk, H., & Rabin, T. (1999). "Secure Distributed Key Generation for Discrete-Log Based Cryptosystems." *EUROCRYPT '99*, pp. 295-310.
5. Coinbase. "x402: An Open Protocol for Payments on the Internet." [github.com/coinbase/x402](https://github.com/coinbase/x402).

---

*BlindOracle runs on a private guardian federation with 4 guardians, 3-of-4 threshold, and 0.05% federation fee.*
