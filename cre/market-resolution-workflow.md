# BlindOracle CRE Workflow: Market Resolution

**Workflow:** `market_resolution`
**SDK:** CRE TypeScript SDK
**Pattern:** Runner/Handler with Log Trigger (ref: [cre-por-llm-demo](https://github.com/Nalon/cre-por-llm-demo))

---

## Overview

The market resolution workflow is BlindOracle's primary CRE integration. When an agent requests settlement of a prediction market position, this workflow:

1. **Triggers** on the `SettlementRequested` log event from `UnifiedPredictionSubscription`
2. **Reads** market state from the on-chain contract (EVM Read)
3. **Queries** 3+ independent AI models via HTTP for outcome verification
4. **Aggregates** results using `ConsensusAggregationByFields` (67% threshold)
5. **Writes** the resolution result back via `IReceiver.onReport()` (EVM Write)

This follows the same Trigger -> Read -> Compute -> Write pattern demonstrated in the [CRE PoR x LLM demo](https://github.com/Nalon/cre-por-llm-demo/blob/main/workshop/chapter-3.md).

---

## Project Structure

```
market_resolution/
  ├── main.ts                    # Entry point (Runner + Handler)
  ├── config.staging.json        # Staging configuration
  ├── config.production.json     # Production configuration (Base mainnet)
  ├── handlers/
  │   ├── onSettlementRequested.ts  # Main callback
  │   ├── getMarketState.ts         # EVM Read: market data
  │   ├── getMultiAIConsensus.ts    # HTTP: LLM queries
  │   └── submitResolution.ts       # EVM Write: IReceiver callback
  ├── types.ts                   # Shared types
  ├── package.json
  └── tsconfig.json
```

---

## Configuration

### config.production.json

```json
{
  "contractAddress": "0x0d5a467af8bb3968fac4302bb6851276ea56880c",
  "chainSelectorName": "base-mainnet",
  "eventSignature": "SettlementRequested(bytes32,uint256)",
  "consensusThreshold": 67,
  "highValueThreshold": 80,
  "highValueAmount": "1000000000000000000",
  "aiProviders": [
    { "name": "anthropic", "model": "claude-sonnet-4-20250514", "secretId": "ANTHROPIC_API_KEY" },
    { "name": "openai", "model": "gpt-4o", "secretId": "OPENAI_API_KEY" },
    { "name": "google", "model": "gemini-2.5-flash", "secretId": "GEMINI_API_KEY" }
  ],
  "gasLimit": "500000",
  "disputeWindowSeconds": 86400
}
```

### secrets.yaml

```yaml
secrets:
  ANTHROPIC_API_KEY:
    type: env
  OPENAI_API_KEY:
    type: env
  GEMINI_API_KEY:
    type: env
```

---

## Implementation

### main.ts -- Entry Point

```typescript
import { Runner, handler } from "@chainlink/cre-sdk";
import { LogTriggerCapability, LogTriggerPayload } from "@chainlink/cre-sdk/triggers";
import { MarketConfig } from "./types";
import { onSettlementRequested } from "./handlers/onSettlementRequested";

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
        eventSignature: config.eventSignature,
        chainSelectorName: config.chainSelectorName,
      }),
      onSettlementRequested,
    ),
  ];
};
```

### handlers/onSettlementRequested.ts -- Main Callback

```typescript
import { Runtime } from "@chainlink/cre-sdk";
import { LogTriggerPayload } from "@chainlink/cre-sdk/triggers";
import { MarketConfig } from "../types";
import { getMarketState } from "./getMarketState";
import { getMultiAIConsensus } from "./getMultiAIConsensus";
import { submitResolution } from "./submitResolution";

export const onSettlementRequested = (
  runtime: Runtime<MarketConfig>,
  payload: LogTriggerPayload
): string => {
  runtime.log(`Settlement requested: marketId=${payload.topics[1]}`);
  const marketId = payload.topics[1]; // bytes32 market ID from event

  // Step 1: EVM Read -- Get market state
  const marketData = getMarketState(runtime, marketId);
  runtime.log(`Market: "${marketData.question}" | Options: ${marketData.options.join(", ")}`);

  // Step 2: Determine consensus threshold
  const threshold = marketData.totalStaked > BigInt(runtime.config.highValueAmount)
    ? runtime.config.highValueThreshold  // 80% for high-value
    : runtime.config.consensusThreshold; // 67% standard

  // Step 3: HTTP -- Query 3+ AI models
  const aiConsensus = getMultiAIConsensus(runtime, marketData);
  runtime.log(`AI consensus: ${aiConsensus.winningOption} (${aiConsensus.agreement}%)`);

  // Step 4: Verify consensus meets threshold
  if (aiConsensus.agreement < threshold) {
    runtime.log(`WARN: Consensus ${aiConsensus.agreement}% below ${threshold}% threshold`);
    // Escalate to dispute resolution workflow
    throw new Error(`Insufficient consensus: ${aiConsensus.agreement}% < ${threshold}%`);
  }

  // Step 5: EVM Write -- Submit resolution via IReceiver.onReport()
  const txHash = submitResolution(runtime, marketId, aiConsensus);
  runtime.log(`Resolution submitted: tx=${txHash}`);

  return `resolved:${marketId}:${aiConsensus.winningOption}:${txHash}`;
};
```

### handlers/getMarketState.ts -- EVM Read

```typescript
import { Runtime } from "@chainlink/cre-sdk";
import { EVMClient, getNetwork, encodeFunctionData, decodeFunctionResult } from "@chainlink/cre-sdk/evm";
import { bytesToHex } from "viem";
import { MarketConfig, MarketData } from "../types";
import { UnifiedPredictionSubscriptionABI } from "../abi";

export const getMarketState = (
  runtime: Runtime<MarketConfig>,
  marketId: string
): MarketData => {
  const network = getNetwork({
    chainFamily: "evm",
    chainSelectorName: runtime.config.chainSelectorName,
    isTestnet: false,
  });

  const evmClient = new EVMClient(network.chainSelector.selector);

  // Read market data from contract
  const callData = encodeFunctionData({
    abi: UnifiedPredictionSubscriptionABI,
    functionName: "getMarket",
    args: [marketId],
  });

  const result = evmClient
    .callContract(runtime, {
      call: encodeCallMsg({
        from: "0x0000000000000000000000000000000000000000",
        to: runtime.config.contractAddress,
        data: callData,
      }),
    })
    .result();

  const decoded = decodeFunctionResult({
    abi: UnifiedPredictionSubscriptionABI,
    functionName: "getMarket",
    data: bytesToHex(result.data),
  });

  return {
    marketId,
    question: decoded.question,
    options: decoded.options,
    resolutionDate: new Date(Number(decoded.resolutionDate) * 1000),
    totalStaked: decoded.totalStaked,
    commitments: decoded.commitmentCount,
  };
};
```

### handlers/getMultiAIConsensus.ts -- HTTP (Multi-LLM Queries)

```typescript
import { Runtime } from "@chainlink/cre-sdk";
import { HTTPClient, ConsensusAggregationByFields } from "@chainlink/cre-sdk/http";
import { MarketConfig, MarketData, AIConsensus } from "../types";

export const getMultiAIConsensus = (
  runtime: Runtime<MarketConfig>,
  marketData: MarketData
): AIConsensus => {
  const httpCapability = new HTTPClient();

  // Query each AI provider independently
  const responses: { provider: string; answer: string; confidence: number }[] = [];

  for (const provider of runtime.config.aiProviders) {
    const apiKey = runtime.getSecret({ id: provider.secretId }).result();

    const prompt = buildVerificationPrompt(marketData);

    const response = httpCapability
      .sendRequest(
        runtime,
        fetchAIVerification(provider, apiKey.value, prompt),
        ConsensusAggregationByFields<AIResponse>({
          answer: majorityVote,
          confidence: median,
        }),
      )(runtime.config)
      .result();

    responses.push({
      provider: provider.name,
      answer: response.answer,
      confidence: response.confidence,
    });
  }

  // Calculate consensus
  const voteCounts: Record<string, number> = {};
  for (const r of responses) {
    voteCounts[r.answer] = (voteCounts[r.answer] || 0) + 1;
  }

  const totalVotes = responses.length;
  const [winningOption, winningCount] = Object.entries(voteCounts)
    .sort(([, a], [, b]) => b - a)[0];

  return {
    winningOption,
    agreement: Math.round((winningCount / totalVotes) * 100),
    totalModels: totalVotes,
    agreeingModels: winningCount,
    responses,
  };
};

const buildVerificationPrompt = (market: MarketData): string => {
  return `You are a prediction market outcome verifier. Based on publicly available information, determine the outcome of this market.

Market question: "${market.question}"
Options: ${market.options.join(", ")}
Resolution date: ${market.resolutionDate.toISOString()}

Respond with ONLY a JSON object: {"answer": "<option>", "confidence": <0-100>}
Do not explain. Do not hedge. Pick the most likely correct answer.`;
};
```

### handlers/submitResolution.ts -- EVM Write

```typescript
import { Runtime } from "@chainlink/cre-sdk";
import { EVMClient, getNetwork, encodeFunctionData } from "@chainlink/cre-sdk/evm";
import { MarketConfig, AIConsensus } from "../types";
import { UnifiedPredictionSubscriptionABI } from "../abi";

export const submitResolution = (
  runtime: Runtime<MarketConfig>,
  marketId: string,
  consensus: AIConsensus
): string => {
  const network = getNetwork({
    chainFamily: "evm",
    chainSelectorName: runtime.config.chainSelectorName,
    isTestnet: false,
  });

  const evmClient = new EVMClient(network.chainSelector.selector);

  // Encode the onReport() callback with resolution data
  const metadata = new TextEncoder().encode(
    JSON.stringify({
      marketId,
      outcome: consensus.winningOption,
      agreement: consensus.agreement,
      models: consensus.totalModels,
      timestamp: Math.floor(Date.now() / 1000),
    })
  );

  const callData = encodeFunctionData({
    abi: UnifiedPredictionSubscriptionABI,
    functionName: "onReport",
    args: [metadata],
  });

  const txResult = evmClient
    .sendTransaction(runtime, {
      to: runtime.config.contractAddress,
      data: callData,
      gasLimit: BigInt(runtime.config.gasLimit),
    })
    .result();

  return txResult.txHash;
};
```

---

## Types

```typescript
// types.ts
export interface MarketConfig {
  contractAddress: string;
  chainSelectorName: string;
  eventSignature: string;
  consensusThreshold: number;
  highValueThreshold: number;
  highValueAmount: string;
  aiProviders: AIProvider[];
  gasLimit: string;
  disputeWindowSeconds: number;
}

export interface AIProvider {
  name: string;
  model: string;
  secretId: string;
}

export interface MarketData {
  marketId: string;
  question: string;
  options: string[];
  resolutionDate: Date;
  totalStaked: bigint;
  commitments: number;
}

export interface AIConsensus {
  winningOption: string;
  agreement: number;
  totalModels: number;
  agreeingModels: number;
  responses: { provider: string; answer: string; confidence: number }[];
}

export interface AIResponse {
  answer: string;
  confidence: number;
}
```

---

## Privacy Integration

The key innovation is that CRE resolves the market **without knowing who holds which position**:

1. Agents commit positions as `SHA256(secret || position || amount)` -- the commitment hash reveals nothing
2. CRE's Log Trigger fires on `SettlementRequested(marketId, ...)` -- no agent identity in the event
3. CRE queries AI models about the **market question**, not about any agent's position
4. CRE writes the **outcome** (yes/no/option) back to the contract via `onReport()`
5. Agents then **self-reveal** their commitments to claim payouts -- only they know their secret

The oracle is honest. The participants are private. CRE's decentralized consensus ensures the resolution is correct without compromising settlement privacy.

---

## Relationship to Other Workflows

| Workflow | Trigger | Relationship to market_resolution |
|---|---|---|
| `dispute_resolution` | `DisputeFiled` event | Escalation path when consensus < threshold |
| `fee_collection` | After resolution TX confirms | Automated fee distribution to treasury |
| `badge_minting` | After dispute window closes | NIP-58 ProofOfDelegation for participants |
| `health_monitoring` | Cron (every 4h) | Monitors resolution latency and success rates |

---

## References

- [CRE PoR x LLM Demo (Chapter 3)](https://github.com/Nalon/cre-por-llm-demo/blob/main/workshop/chapter-3.md) -- Runner/Handler pattern, HTTP + EVM capabilities
- [CRE TypeScript SDK Documentation](https://docs.chain.link/chainlink-automation/cre-sdk)
- [UnifiedPredictionSubscription Contract](https://basescan.org/address/0x0d5a467af8bb3968fac4302bb6851276ea56880c)
- [BlindOracle Commitment Scheme Whitepaper](https://github.com/craigmbrown/blindoracle-docs/blob/main/whitepaper/commitment-scheme.md)
