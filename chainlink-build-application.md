# Chainlink BUILD Program Application - BlindOracle

**Application Date:** 2026-02-25
**Category:** Privacy & Confidentiality
**Applicant:** Craig M. Brown
**Project:** BlindOracle - Private Settlement Layer for Autonomous AI Agents
**Website:** https://craigmbrown.com/blindoracle/
**API:** https://craigmbrown.com/api/v2/
**GitHub (docs):** https://github.com/craigmbrown/blindoracle-docs
**Contract (Base):** 0x0d5a467af8bb3968fac4302bb6851276ea56880c
**Application URL:** https://chainlinkcommunity.typeform.com/BUILD
**Vertical:** Infrastructure (with Privacy & Confidentiality crossover)

---

## 1. Project Description

BlindOracle is a privacy-preserving financial settlement layer for autonomous AI agents. It combines Chainlink's decentralized oracle infrastructure with Chaumian blind signatures (Chaum, 1982) to enable agents to settle positions in information markets without revealing their strategies.

**The problem:** When AI agents trade in prediction/information markets, their fund flows are visible on-chain. Competitors can front-run positions by monitoring deposit addresses. No existing infrastructure provides both verifiable settlement AND deposit-position privacy for autonomous agents.

**The solution:** BlindOracle wraps Chainlink CRE workflows with a blind signature privacy layer. Agents deposit via guardian-federation blind tokens (unlinkable to identity), commit positions using SHA256 hashes, and settle through CRE-verified oracle resolution. The oracle is honest; the participants are private.

## 2. Chainlink Integration

### Products Used

| Chainlink Product | Integration | Status |
|---|---|---|
| **CRE (Compute Runtime Environment)** | 10 agent-native workflows for market resolution, compliance, treasury, DCA, arbitrage, health monitoring | Production YAML |
| **CCIP** | Cross-chain token + message transfer for multi-rail settlement routing | Architecture ready |
| **Data Streams** | Sub-second price feeds for information market oracle resolution | Integration planned |
| **Functions** | Multi-AI model queries (3+ independent models) for market outcome verification with consensus aggregation | Architecture ready |
| **Confidential Compute** | Alignment with blind signature privacy model for end-to-end private settlement | Roadmap (awaiting GA) |

### Smart Contract

**UnifiedPredictionSubscription** -- deployed on Base mainnet (chain 8453):
- Address: `0x0d5a467af8bb3968fac4302bb6851276ea56880c`
- Deployer: `0x42A09A72eC47647FE9BE1f450Ab8F835D0FF556a`
- Implements `IReceiver` interface for CRE callbacks
- 24-hour dispute window with multi-AI consensus (67% threshold)
- Deploy TX: `0xf9e2233e7a719096e7d7b65abfa04a32bbeb916e57876a031363cfc929b57a9e`

### CRE Workflows (10 total)

1. **market_resolution** -- Log Trigger on SettlementRequested event, EVM Read for market data, HTTP for AI provider queries, IReceiver callback with consensus result
2. **compliance_screening** -- Agent KYC/AML checks via external APIs
3. **treasury_rebalancing** -- Automated portfolio rebalancing across rails
4. **dca_execution** -- Dollar-cost averaging for agent positions
5. **arbitrage_detection** -- Cross-market price discrepancy detection
6. **health_monitoring** -- System health checks and automatic recovery
7. **badge_minting** -- NIP-58 credential minting on market completion
8. **fee_collection** -- Automated fee routing and treasury management
9. **dispute_resolution** -- Re-verification workflow on disputed outcomes
10. **agent_onboarding** -- New agent registration and verification

### CRE TypeScript SDK Implementation (market_resolution)

Following the CRE Runner/Handler pattern (ref: [cre-por-llm-demo](https://github.com/Nalon/cre-por-llm-demo)):

```typescript
// market_resolution/main.ts
export async function main() {
  const runner = await Runner.newRunner<MarketConfig>();
  await runner.run(initWorkflow);
}

const initWorkflow = (config: MarketConfig) => {
  const logTrigger = new LogTriggerCapability();
  return [
    handler(
      logTrigger.trigger({
        contractAddress: config.contractAddress,
        eventSignature: "SettlementRequested(bytes32,uint256)",
      }),
      onSettlementRequested,
    ),
  ];
};

const onSettlementRequested = (
  runtime: Runtime<MarketConfig>,
  payload: LogTriggerPayload
): string => {
  // 1. EVM Read: Get market state from UnifiedPredictionSubscription
  const marketData = getMarketState(runtime, payload.marketId);

  // 2. HTTP: Query 3+ AI models for outcome verification
  const aiConsensus = getMultiAIConsensus(
    runtime,
    marketData.question,
    marketData.options,
  );

  // 3. Consensus check: 67% threshold (80% for high-value)
  if (aiConsensus.agreement < runtime.config.consensusThreshold) {
    throw new Error(`Consensus ${aiConsensus.agreement}% below threshold`);
  }

  // 4. EVM Write: Callback via IReceiver.onReport()
  const txHash = submitResolution(runtime, payload.marketId, aiConsensus);

  return `resolved:${payload.marketId}:${txHash}`;
};
```

**Capabilities used per workflow:**

| Capability | market_resolution | compliance | treasury | dispute |
|---|---|---|---|---|
| Log Trigger | SettlementRequested | AgentRegistered | RebalanceNeeded | DisputeFiled |
| Cron Trigger | -- | Daily scan | Every 4h | -- |
| HTTP Client | AI model queries | KYC API calls | Price feeds | Re-verification |
| EVM Read | Market state | Agent record | Portfolio balance | Original result |
| EVM Write | onReport() callback | Compliance flag | Rebalance TX | Updated result |
| Secrets | AI API keys | KYC provider keys | -- | AI API keys |
| Consensus | ConsensusAggregation (median) | -- | -- | ConsensusAggregation |

## 3. What Makes This Novel

Three things combined here for the first time:

1. **Chaumian blind signatures (1982) applied to autonomous agent settlement.** The agent's deposit is information-theoretically unlinkable to its market position. This is not computational privacy -- it is mathematical privacy.

2. **CRE as the neutral verifier in a privacy-preserving market.** CRE's decentralized consensus resolves markets without knowing who holds which position. Positions are committed via SHA256 hashes. The oracle is honest; the participants are private.

3. **Multi-AI consensus for outcome verification.** CRE workflows query 3+ independent AI models (via Chainlink Functions) and require 67% consensus before accepting a market outcome. This is Byzantine fault-tolerant AI verification.

## 4. Architecture

```
Agent Research Pipeline (6 agents, private consensus)
    |
    v
Blind-Signed Token Deposit (Chaumian blind signatures, guardian federation)
    |
    v
Commitment: SHA256(secret || position || amount) -- no identity attached
    |
    v
CRE Workflow: Market Resolution
    |-- Log Trigger: SettlementRequested event on-chain
    |-- CRE reads market data (EVM Read)
    |-- CRE queries AI providers via Functions (HTTP)
    |-- Multi-AI consensus: 3 independent models verify outcome
    |-- CRE returns result via IReceiver.onReport()
    |
    v
24-Hour Dispute Window (on-chain, transparent)
    |
    v
Settlement: Agent reveals (secret, position, amount)
    |-- SHA256 verified on-chain
    |-- Payout via blind-signed tokens (privacy preserved)
    |-- OR instant settlement via payment channel
    |-- OR CCIP cross-chain transfer
```

## 5. Security

**CaMel 4-Layer Architecture:**

| Layer | Function | Mechanism |
|---|---|---|
| 1 | Rate Limiting & Input Sanitization | 60 req/min, SQL/prompt injection defense, payload validation |
| 2 | Byzantine Consensus | 67% threshold (standard), 80% threshold (high-value), independent validators |
| 3 | Anti-Persuasion Detection | 30% deviation detection, suspicious phrase filtering, gradual drift detection |
| 4 | Authority & Audit | Least privilege, cross-agent isolation, append-only audit trail, hash-linked chain |

**MASSAT Security Assessment:** 87 tests across 4 categories, 93% pass rate (81/87 passing).

| Category | Tests | Pass Rate |
|---|---|---|
| Core Functionality | 22 | 91% |
| Security Controls | 35 | 94% |
| Distribution Safety | 15 | 93% |
| Infrastructure | 15 | 93% |

## 6. Live Infrastructure

| Component | Status | URL/Address |
|---|---|---|
| x402 API Gateway | Running (port 8402) | https://craigmbrown.com/api/v2/ |
| Hello World Demo | Live | POST https://craigmbrown.com/api/v2/hello-world |
| Health Check | Live | GET https://craigmbrown.com/api/v2/health |
| CaMel Security Gateway | Running (port 8403) | Internal |
| Smart Contract | Deployed (Base 8453) | 0x0d5a467af8bb3968fac4302bb6851276ea56880c |
| NIP-58 Badges | Live on Nostr | Relays: damus.io, nos.lol |
| Documentation | Published | github.com/craigmbrown/blindoracle-docs |
| AgentKit Plugin | Published | blindoracle-agentkit v0.1.0 |

## 7. Team

**Craig M. Brown** -- Solo builder
- Multi-agent system architect operating 42+ specialized AI agents with 79-83% cost reduction
- Built: Limitless Lifelog Manager, TheBaby_Agents (19 SFAs), Orchestrator-Agent (13 coordination agents), WhatsApp-Manager-Agent, BlindOracle (25 agents)
- Infrastructure: GCP VM (c3-standard-4), 10+ MCP servers, Claude Code hooks observability
- Familiar with Chainlink ecosystem since CRE launch (Nov 2025)

## 8. Token & Economics

BlindOracle does not have a token. Revenue model is API-fee based:

| Operation | Fee | Rail |
|---|---|---|
| Market creation | $0.001 | x402 (USDC on Base) |
| Position placement | $0.0005 | x402 |
| Market resolution | $0.002 | x402 |
| Identity verification | $0.0002 | x402 |
| Badge minting | $0.001 | x402 |

Free trial: First 1,000 settlements free for new agents. Volume discounts at 10K+ settlements/month.

**Commitment to Chainlink:** BlindOracle will use LINK for CRE workflow execution fees and will promote Chainlink integration in all marketing materials, documentation, and community engagement.

**Token Plans:** BlindOracle plans to launch a utility token for prediction market staking, agent settlement fees, and x402 micropayment routing. Proposed commitment: **3-4% of total token supply** to jointly-administered Chainlink vault (aligned with Mind Network 3%, Rivalz 3%, Brickken 3.5% precedents). Tokens would participate in Chainlink Rewards seasons for LINK staker distribution.

**Funding:** Bootstrapped. No external funding raised. Lean operational costs ($408/mo verified: $200 Claude Max + $148 GCP VM + $50 disk + $10 network).

## 9. Comparable Projects

| Dimension | Mind Network (BUILD, 3%) | Rivalz (BUILD, 3%) | BlindOracle |
|---|---|---|---|
| Privacy Tech | FHE (lattice crypto) | FHE + DePIN | Chaumian blind signatures (1982) + CRE consensus |
| Chainlink Integration | CCIP, Functions | Functions | **CRE (10 workflows), CCIP, Data Streams, Functions** |
| AI Component | Confidential AI systems | AI agents + data provenance | **25 autonomous agents, multi-AI verification** |
| Security | Standard | Standard | **CaMel 4-layer, MASSAT 87 tests, 93% pass** |
| Smart Contract | Not specified on Base | Not specified | **Base mainnet deployed + IReceiver** |
| Micropayments | No | No | **x402 protocol (USDC on Base)** |
| Social Proof | None specific | None specific | **NIP-58 badges live on Nostr** |
| Funding | $12.5M raised | Funded | Bootstrapped ($408/mo) |

## 10. Roadmap

| Quarter | Milestone |
|---|---|
| Q1 2026 | Live API, smart contract on Base, NIP-58 badges, documentation |
| Q2 2026 | First 100 market resolutions, CCIP cross-chain transfers, Moltlaunch gig listings |
| Q3 2026 | 1,000+ transactions, OnboardingRegistry NFTs, prediction accuracy dashboard |
| Q4 2026 | Confidential Compute integration (when GA), open-source trust components |

## 11. Links

- **Live API Demo:** `curl -X POST https://craigmbrown.com/api/v2/hello-world -H "Content-Type: application/json" -d '{"agent_id": "your-agent"}'`
- **Documentation:** https://github.com/craigmbrown/blindoracle-docs
- **Landing Page:** https://craigmbrown.com/blindoracle/
- **Contract:** https://basescan.org/address/0x0d5a467af8bb3968fac4302bb6851276ea56880c
- **x402 Spec:** https://github.com/craigmbrown/blindoracle-docs/blob/main/api/x402-spec.md
- **Commitment Scheme Whitepaper:** https://github.com/craigmbrown/blindoracle-docs/blob/main/whitepaper/commitment-scheme.md
- **MASSAT Results:** https://github.com/craigmbrown/blindoracle-docs/blob/main/security/massat-results.md

---

*BlindOracle is built on Chainlink CRE, CCIP, Data Streams, Functions, and is architecturally prepared for Confidential Compute.*
