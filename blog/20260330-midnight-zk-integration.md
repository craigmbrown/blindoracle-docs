# Midnight Network ZK Integration: Privacy-First AI Agent Proofs

BlindOracle now uses the [Midnight Network](https://midnight.network) SDK (`@midnight-ntwrk/*` v4.0.2) for zero-knowledge proof generation across three production capabilities. Midnight mainnet (Kukolu phase) launched March 2026.

## What This Unlocks

| Capability | What agents can prove | What stays private |
|---|---|---|
| **Selective Disclosure** (RQ-050) | "My reputation is >= 85" | Exact reputation score |
| **Private Predictions** (RQ-048) | Position commitment hash | Position, amount, secret |
| **Compliance Audits** (RQ-049) | "I paid >= 500 USDC in fees" | Exact fee amount |

This means **external agents can participate in BlindOracle markets, prove their credentials, and pass compliance checks without revealing competitive intelligence**.

## Production Examples

### RQ-050: Selective Disclosure

**Scenario**: Agent `acme-research-bot` wants priority routing. The marketplace requires gold+ badge. The agent proves this without revealing its exact score.

```bash
node midnight/dist/cli.js prove-claim \
  --claim badge_level --threshold 3 \
  --agent-data '{"agent_name":"acme-research-bot","badge_level":3,...}'
```

**Response:**
```json
{
  "status": "proven",
  "sdk_version": "4.0.2",
  "claim_type": "badge_level",
  "threshold": 3,
  "claim_met": true,
  "proof_hash": "e45eceb553b362ba...",
  "circuit_id": "blindoracle_disclosure_badge_level_v1",
  "network": "testnet"
}
```

The marketplace sees: "badge >= gold: TRUE". It never sees the actual score (88), proof count (31), or team assignment.

**8 claim types available**: `reputation_gte`, `badge_level`, `proof_count_gte`, `tier_gte`, `team_membership`, `uptime_gte`, `success_rate_gte`, `total_runs_gte`.

### RQ-048: Private Prediction Markets

**Scenario**: Agent commits a prediction on BTC hitting $120K by Q3 2026. The position and amount are hidden until the market resolves.

**Step 1 -- Commit** (position hidden):
```bash
node midnight/dist/cli.js commit \
  --market-id "btc-120k-q3-2026" \
  --position yes --amount 100 --agent "acme-research-bot"
```
```json
{
  "status": "committed",
  "commitment_hash": "a26ba937901...",
  "secret": "9727b4ad3098..."
}
```

Only the `commitment_hash` goes on-chain. Nobody can determine the position or amount from it.

**Step 2 -- Reveal** (after market resolution):
```bash
node midnight/dist/cli.js reveal \
  --market-id "btc-120k-q3-2026" \
  --commitment "a26ba937901..." --secret "9727b4ad3098..." \
  --position yes --amount 100
```
```json
{
  "status": "revealed",
  "position": "yes",
  "amount": 100
}
```

The reveal proves the preimage matches the commitment. No front-running possible.

### RQ-049: Compliance Audit Proofs

**Scenario**: Regulatory check -- prove an agent paid >= 500 USDC in fees this quarter without revealing the exact spend (1,247 USDC).

```bash
node midnight/dist/cli.js prove-compliance \
  --claim fee_paid_gte --threshold 500 --agent "acme-research-bot" \
  --data '{"fee_total":1247,"kyc_tier":3,"sanctions_status":"clear"}'
```
```json
{
  "status": "proven",
  "claim_type": "fee_paid_gte",
  "claim_met": true,
  "proof_hash": "840a6e6054aec..."
}
```

The regulator sees: "fees >= 500 USDC: TRUE". The exact 1,247 USDC figure stays private.

**4 compliance types**: `fee_paid_gte`, `kyc_tier_gte`, `audit_passed`, `sanctions_clear`.

## Architecture

```
Python Agent --> zk_proof_bridge.py v3.0 --> subprocess --> Node CLI
                                                              |
                                              Midnight SDK v4.0.2
                                              (@midnight-ntwrk/*)
                                                              |
                                          compact-runtime + ZK circuits
                                                              |
                                              Midnight testnet / mainnet
```

## What This Enables for Clients

1. **Agent marketplace with privacy**: Agents prove capabilities without revealing proprietary algorithms or internal metrics
2. **Front-running protection**: Prediction positions are hidden until reveal -- no information leakage to competing agents
3. **Compliance without exposure**: Pass regulatory checks without sharing exact financial data with counterparties
4. **Progressive trust**: Onboarded agents get "limited" disclosure passports with real ZK claims, upgrading to "full" at operator tier
5. **Interoperability**: Any external agent can generate proofs -- not locked to BlindOracle's internal agents

## Integration

```bash
# Python
from scripts.zk_proof_bridge import prove_claim, commit_position, prove_compliance

# Selective disclosure
result = prove_claim("my-agent", "reputation_gte", 85, agent_data={...})

# Private prediction
commit = commit_position("btc-120k", "yes", 100, "my-agent")

# Compliance proof
proof = prove_compliance("my-agent", "sanctions_clear", 0, {...})
```

## Status

- SDK: `@midnight-ntwrk/*` v4.0.2 (mainnet Kukolu)
- Network: Targeting testnet-02, mainnet-ready
- Test coverage: 200+ assertions (onboarding E2E suite)
- PR: [chainlink-prediction-markets-mcp-enhanced#61](https://github.com/craigmbrown/chainlink-prediction-markets-mcp-enhanced/pull/61)

---

*Built with Midnight Network SDK on the Kukolu mainnet launch. March 30, 2026.*
