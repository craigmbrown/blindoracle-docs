# RWA Market Resolution via Chainlink Data Streams

> How BlindOracle uses Chainlink Data Streams V3 to trustlessly resolve stock prediction markets on Robinhood Chain.

---

## Table of Contents

- [Overview](#overview)
- [PremiumReport Struct](#premiumreport-struct)
- [Resolution Flow](#resolution-flow)
- [Staleness Protection](#staleness-protection)
- [Multi-Asset Support](#multi-asset-support)
- [On-Chain Storage Model](#on-chain-storage-model)
- [Future: CRE Automated Resolution](#future-cre-automated-resolution)
- [Future: Chainlink Automation](#future-chainlink-automation)
- [Troubleshooting](#troubleshooting)

---

## Overview

Prediction markets are only as trustworthy as their resolution mechanism. A market that asks "Will TSLA close above $300 by March 31?" needs a verifiable, tamper-resistant answer. That answer cannot come from the market operator -- it must come from a decentralized oracle network.

BlindOracle uses **Chainlink Data Streams V3** to resolve RWA prediction markets. Data Streams delivers sub-second, institutional-grade price data for tokenized stocks via a pull-based model. Unlike traditional push oracles that update on a heartbeat, Data Streams reports are fetched on demand and submitted on-chain by the caller. The oracle network signs the data off-chain; the contract verifies the signature on-chain.

This architecture means:

1. **No trust in the market operator** -- the outcome is determined by oracle-signed price data that anyone can submit.
2. **No stale heartbeats** -- price data is fetched at resolution time, not relying on the most recent push update.
3. **Verifiable on-chain** -- the signed report is decoded and validated in the `DataStreamConsumer` contract.

---

## PremiumReport Struct

Every Data Streams V3 report contains a `PremiumReport` struct. This is the core data structure that carries the price from the Chainlink DON (Decentralized Oracle Network) to your contract.

```solidity
struct PremiumReport {
    bytes32 feedId;                // Unique identifier for the data feed (e.g., TSLA/USD)
    uint32  validFromTimestamp;    // Earliest timestamp this report is valid
    uint32  observationsTimestamp; // Timestamp when DON nodes observed the price
    uint192 nativeFee;            // Fee in native token to verify this report
    uint192 linkFee;              // Fee in LINK to verify this report
    uint32  expiresAt;            // Latest timestamp this report can be verified
    int192  price;                // Median price from DON consensus (18 decimals)
    int192  bid;                  // Best bid price
    int192  ask;                  // Best ask price
}
```

**Field details:**

| Field | Type | Description |
|-------|------|-------------|
| `feedId` | `bytes32` | Identifies the asset. Each stock (TSLA, AMZN, etc.) has a unique feed ID registered in the Chainlink Data Streams registry. |
| `validFromTimestamp` | `uint32` | The report is not valid before this timestamp. Prevents replaying old reports as current. |
| `observationsTimestamp` | `uint32` | When the DON nodes actually observed the price. This is what we compare against the staleness threshold. |
| `nativeFee` | `uint192` | Verification cost in the chain's native token. On Robinhood Chain, this is the native gas token. |
| `linkFee` | `uint192` | Alternative verification cost payable in LINK. |
| `expiresAt` | `uint32` | Hard expiry -- the verifier contract will reject the report after this timestamp. |
| `price` | `int192` | The median price agreed upon by the DON. 18 decimal places. A TSLA price of $300.00 is stored as `300000000000000000000`. |
| `bid` | `int192` | Best bid price -- useful for spread analysis but not used in resolution logic. |
| `ask` | `int192` | Best ask price -- useful for spread analysis but not used in resolution logic. |

**Why `int192`?** Chainlink uses signed 192-bit integers to support both positive and negative price values (relevant for derivatives and funding rates) while providing sufficient precision for 18 decimal places.

---

## Resolution Flow

The complete lifecycle from market expiration to payout:

```
                    Market Lifecycle
                    ================

 [1] Market Created          [2] Trading Active
      |                           |
      v                           v
 +-----------+              +-----------+
 | Factory   |-- deploys -->| Market    |
 | creates   |              | accepts   |
 | market    |              | buy/sell  |
 +-----------+              +-----------+
                                  |
                    block.timestamp >= expirationTime
                                  |
                                  v
                         [3] Market Expired
                              |
                              v
                    +-------------------+
                    | Caller fetches    |
                    | Data Streams      |
                    | signed report     |
                    | (off-chain API)   |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | verifyAndStore()  |  [4] Submit Report
                    | on DataStream-   |
                    | Consumer          |
                    +-------------------+
                              |
                    Decode -> Validate -> Store
                              |
                              v
                    +-------------------+
                    | resolve() on      |  [5] Resolve Market
                    | RWAPrediction-    |
                    | Market            |
                    +-------------------+
                              |
                    Read price -> Compare to strike
                              |
                         +----+----+
                         |         |
                    YES wins    NO wins
                         |         |
                         v         v
                    +-------------------+
                    | claimWinnings()   |  [6] Claim Payouts
                    | Winners claim     |
                    | proportional      |
                    | collateral        |
                    +-------------------+
```

### Step-by-Step Breakdown

#### Step 1: Market Expires

The market enters the `Expired` state when `block.timestamp >= expirationTime`. No more trading is allowed. The market is now waiting for resolution.

```solidity
// Inside RWAPredictionMarket
modifier onlyActive() {
    if (block.timestamp >= expirationTime || status != MarketStatus.Active) {
        revert MarketNotActive();
    }
    _;
}
```

#### Step 2: Caller Submits Signed Data Streams Report

Anyone can fetch a signed report from the Chainlink Data Streams API and submit it on-chain. This is the "pull" model -- the contract does not subscribe to price updates. Instead, the resolver pulls the latest signed data and pushes it to the contract.

```bash
# Off-chain: fetch the signed report from Data Streams API
# (In production, this is done by a backend service or Chainlink Automation)
SIGNED_REPORT=$(curl -s "$DATA_STREAMS_API/v1/reports?feedId=$TSLA_FEED_ID" \
  -H "Authorization: Bearer $DS_API_KEY" | jq -r '.report')

# On-chain: submit the report
cast send $CONSUMER "verifyAndStore(bytes)" $SIGNED_REPORT \
  --rpc-url $RPC_URL --private-key $PK
```

#### Step 3: DataStreamConsumer Decodes, Validates, and Stores

Inside `verifyAndStore()`:

```solidity
function verifyAndStore(bytes calldata signedReport) external {
    // 1. Decode the outer envelope
    (, bytes memory reportData) = abi.decode(signedReport, (bytes32[3], bytes));

    // 2. Decode the PremiumReport
    PremiumReport memory report = abi.decode(reportData, (PremiumReport));

    // 3. Validate feed is registered
    if (!registeredFeeds[report.feedId]) revert FeedNotRegistered();

    // 4. Validate freshness
    if (block.timestamp - report.observationsTimestamp > stalenessThreshold) {
        revert StalePrice();
    }

    // 5. Store the price
    latestPrices[report.feedId] = PriceData({
        price: report.price,
        bid: report.bid,
        ask: report.ask,
        observationsTimestamp: report.observationsTimestamp,
        storedAt: uint32(block.timestamp)
    });

    emit PriceUpdated(report.feedId, report.price, report.observationsTimestamp);
}
```

#### Step 4: Anyone Calls resolve()

The `resolve()` function is permissionless. It reads the stored price from the `DataStreamConsumer` and compares it to the market's strike price.

```solidity
function resolve() external {
    if (block.timestamp < expirationTime) revert MarketNotExpired();
    if (status != MarketStatus.Active) revert MarketAlreadyResolved();

    // Read the latest oracle price
    (int192 latestPrice, uint32 timestamp) = dataStreamConsumer.getLatestPrice(feedId);

    // Determine outcome
    if (isAbove) {
        yesWins = (latestPrice >= strikePrice);
    } else {
        yesWins = (latestPrice < strikePrice);
    }

    // Update state
    status = MarketStatus.Resolved;
    finalPrice = latestPrice;

    emit MarketResolved(yesWins, latestPrice, strikePrice);
}
```

**Resolution logic:**

| Market Type (`isAbove`) | Condition | Outcome |
|--------------------------|-----------|---------|
| `true` (above) | `latestPrice >= strikePrice` | YES wins |
| `true` (above) | `latestPrice < strikePrice` | NO wins |
| `false` (below) | `latestPrice < strikePrice` | YES wins |
| `false` (below) | `latestPrice >= strikePrice` | NO wins |

#### Step 5: Winners Claim

```solidity
function claimWinnings() external runPolicy nonReentrant {
    if (status != MarketStatus.Resolved && status != MarketStatus.EmergencyResolved) {
        revert MarketNotResolved();
    }
    if (claimed[msg.sender]) revert AlreadyClaimed();

    uint256 winningShares = yesWins ? yesShares[msg.sender] : noShares[msg.sender];
    if (winningShares == 0) revert NoWinningShares();

    uint256 totalWinning = yesWins ? totalYesShares : totalNoShares;
    uint256 pool = totalYesShares + totalNoShares;
    uint256 fee = (pool * feeRate) / FEE_DENOMINATOR;
    uint256 payout = ((pool - fee) * winningShares) / totalWinning;

    claimed[msg.sender] = true;
    accumulatedFees += fee;
    collateralToken.safeTransfer(msg.sender, payout);

    emit WinningsClaimed(msg.sender, payout);
}
```

---

## Staleness Protection

Stale price data is the primary attack vector against oracle-resolved markets. If the oracle price is hours old, it may not reflect the actual price at market expiration.

### Configuration

```solidity
uint256 public stalenessThreshold = 3600; // Default: 1 hour (3600 seconds)

function setStalenessThreshold(uint256 newThreshold) external onlyOwner {
    emit StalenessThresholdUpdated(stalenessThreshold, newThreshold);
    stalenessThreshold = newThreshold;
}
```

### How Staleness Is Checked

The `observationsTimestamp` from the `PremiumReport` is compared against `block.timestamp`:

```solidity
if (block.timestamp - report.observationsTimestamp > stalenessThreshold) {
    revert StalePrice();
}
```

### Checking Freshness Externally

Before attempting resolution, check if the stored price is fresh:

```bash
# Returns true if price is within staleness threshold
cast call $CONSUMER "isPriceFresh(bytes32)(bool)" $TSLA_FEED_ID --rpc-url $RPC_URL
```

### Recommended Thresholds by Use Case

| Use Case | Threshold | Rationale |
|----------|-----------|-----------|
| Stock markets (trading hours) | 300s (5 min) | Stocks move fast during trading |
| Stock markets (after hours) | 3600s (1 hour) | Limited after-hours movement |
| Weekly prediction markets | 1800s (30 min) | Balance between freshness and availability |
| Long-dated markets (monthly) | 3600s (1 hour) | Exact-second precision matters less |

---

## Multi-Asset Support

The system supports multiple tokenized stock feeds simultaneously. Each feed is registered in the `DataStreamConsumer` and can be used by any number of markets.

### Supported Assets

| Asset | Symbol | Feed ID | Status |
|-------|--------|---------|--------|
| Tesla | TSLA | `0x00037da06d56d083fe599397a4769a042d63aa73dc4ef57709d31e9971a5b439` | Active |
| Amazon | AMZN | `0x000235d7a36a1b3b6a893268509be14dce508025191a33cb2cc0764789599693` | Active |
| Robinhood | HOOD | `0x0003a2adce5c9c2fedae01e1a0e4c6e040fb70d03a981dce40e31d5a8015d1ff` | Active |
| Palantir | PLTR | `0x00034bfdb22d1e9aa02e97c4821a01229d981fb0f9e16533e04c6e97c2383c2e` | Active |
| AMD | AMD | `0x0003e21f4bf0f63c00e98bef2e051850fa9f99edaacdd3deec3f0b4a4e272f57` | Active |

### Registering New Feeds

When Robinhood Chain lists new tokenized stocks, register the corresponding Data Streams feed:

```bash
# Register a new feed (e.g., NVDA)
cast send $CONSUMER "registerFeed(bytes32,string)" \
  $NVDA_FEED_ID "NVDA" \
  --rpc-url $RPC_URL --private-key $PK

# Verify registration
cast call $CONSUMER "getLatestPrice(bytes32)(int192,uint32)" $NVDA_FEED_ID --rpc-url $RPC_URL
```

### Creating Markets for Any Registered Feed

Once a feed is registered, the factory can create markets against it:

```bash
# "Will AMZN be above $250 by April 30?"
cast send $FACTORY "createMarket(address,bytes32,string,int192,uint256,bool)" \
  $USDC \
  0x000235d7a36a1b3b6a893268509be14dce508025191a33cb2cc0764789599693 \
  "AMZN" \
  250000000000000000000 \
  1746057600 \
  true \
  --rpc-url $RPC_URL --private-key $PK
```

---

## On-Chain Storage Model

The `DataStreamConsumer` maintains a mapping of feed IDs to their latest price data:

```solidity
mapping(bytes32 => PriceData) public latestPrices;
mapping(bytes32 => bool) public registeredFeeds;
mapping(bytes32 => string) public feedSymbols;

struct PriceData {
    int192 price;                  // Median price (18 decimals)
    int192 bid;                    // Best bid
    int192 ask;                    // Best ask
    uint32 observationsTimestamp;  // When DON observed the price
    uint32 storedAt;               // When the contract stored it
}
```

**Storage layout notes:**
- `PriceData` packs into 2 storage slots (int192 + int192 = 384 bits in slot 1; int192 + uint32 + uint32 = 256 bits in slot 2)
- Each `verifyAndStore()` call writes 2 slots = ~40,000 gas
- On Robinhood Chain with sub-cent gas costs, this is negligible

---

## Future: CRE Automated Resolution

The Chainlink Runtime Environment (CRE) enables workflow-based automation using the **Trigger -> Read -> Compute -> Write** pattern. This will replace the current manual resolution flow.

### Planned CRE Workflow

```
Trigger: block.timestamp >= market.expirationTime
    |
    v
Read: Fetch latest Data Streams report for market.feedId
    |
    v
Compute: Decode report, validate freshness, determine outcome
    |
    v
Write: Call verifyAndStore() then resolve() on-chain
```

### CRE Workflow Definition (Draft)

```yaml
name: "rwa-market-auto-resolver"
trigger:
  type: "cron"
  schedule: "*/5 * * * *"  # Check every 5 minutes
steps:
  - id: "check-expired"
    action: "eth_call"
    target: "$FACTORY"
    method: "getMarketPage(uint256,uint256)"
    params: [0, 100]
  - id: "filter-expired"
    action: "compute"
    logic: "filter markets where block.timestamp >= expirationTime AND status == Active"
  - id: "fetch-prices"
    action: "data-streams-read"
    feeds: "$expired_market_feed_ids"
  - id: "resolve-markets"
    action: "eth_send"
    for_each: "$expired_markets"
    calls:
      - target: "$CONSUMER"
        method: "verifyAndStore(bytes)"
        params: ["$signed_report"]
      - target: "$market_address"
        method: "resolve()"
```

### Benefits Over Manual Resolution

| Aspect | Manual | CRE Automated |
|--------|--------|---------------|
| Latency | Minutes to hours after expiry | Under 5 minutes |
| Reliability | Depends on human operator | Decentralized, incentivized |
| Cost | Operator pays gas | CRE handles gas management |
| Trust | Requires trusting operator timing | Trustless, deterministic |

---

## Future: Chainlink Automation

As an alternative or complement to CRE, **Chainlink Automation** (formerly Keepers) can trigger resolution:

### Automation-Compatible Interface

```solidity
// Add to RWAPredictionMarket
function checkUpkeep(bytes calldata) external view returns (bool upkeepNeeded, bytes memory performData) {
    upkeepNeeded = (
        block.timestamp >= expirationTime &&
        status == MarketStatus.Active &&
        dataStreamConsumer.isPriceFresh(feedId)
    );
    performData = abi.encode(address(this));
}

function performUpkeep(bytes calldata performData) external {
    address market = abi.decode(performData, (address));
    RWAPredictionMarket(market).resolve();
}
```

### Registration

Register the market (or a batch resolver contract) as an Automation upkeep via the Chainlink Automation registry on Robinhood Chain once available.

---

## Troubleshooting

### "StalePrice" Revert on verifyAndStore

The signed report's `observationsTimestamp` is older than the staleness threshold.

**Fix:** Fetch a fresh report from the Data Streams API and resubmit.

```bash
# Check current staleness threshold
cast call $CONSUMER "stalenessThreshold()(uint256)" --rpc-url $RPC_URL

# Check stored price age
cast call $CONSUMER "getFullPriceData(bytes32)((int192,int192,int192,uint32,uint32))" \
  $FEED_ID --rpc-url $RPC_URL
```

### "MarketNotExpired" Revert on resolve

`block.timestamp` has not yet reached the market's `expirationTime`.

```bash
# Check expiration time
cast call $MARKET "getMarketSummary()(string,int192,uint256,bool,uint256,uint256,address,uint8)" \
  --rpc-url $RPC_URL

# Check current block timestamp
cast block latest --rpc-url $RPC_URL | grep timestamp
```

### "FeedNotRegistered" Revert

The feedId in the report does not match any registered feed.

```bash
# Check if feed is registered (will return empty symbol if not)
cast call $CONSUMER "feedSymbols(bytes32)(string)" $FEED_ID --rpc-url $RPC_URL
```

### Oracle Price Seems Wrong

If the stored price appears incorrect:

1. Check bid/ask spread via `getFullPriceData()` -- a wide spread suggests low liquidity
2. Verify the `observationsTimestamp` -- it should be close to market expiration
3. Cross-reference with the Chainlink Data Streams dashboard for the same feed and timestamp
4. If genuinely wrong, the owner can call `emergencyResolve()` with documentation

---

*Oracle infrastructure: Chainlink Data Streams V3 | Chain: Robinhood Chain (46630) | Staleness default: 3600s*
