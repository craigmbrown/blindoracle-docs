# RWA Stock Prediction Markets

**ACE-compliant prediction markets for tokenized real-world assets on Robinhood Chain**

---

## Introduction

BlindOracle RWA Stock Prediction Markets enable users to speculate on the price movements of tokenized real-world assets (stocks) deployed on Robinhood Chain. Markets are created through a factory pattern, resolved using Chainlink Data Streams V3 for sub-second stock price feeds, and fully compliant with the Chainlink ACE (Asset Compliance Engine) framework via the `PolicyProtected` modifier.

**Source Repository:** [github.com/craigmbrown/blindoracle-rwa-markets](https://github.com/craigmbrown/blindoracle-rwa-markets)

---

## Architecture

```
                         +---------------------+
                         |  RWAMarketFactory   |
                         |    (Ownable)        |
                         +----------+----------+
                                    |
                    createMarket()  |  deploys instances
                                    |
          +-------------------------+-------------------------+
          |                         |                         |
+---------v---------+   +-----------v---------+   +-----------v---------+
| RWAPredictionMarket|  | RWAPredictionMarket |  | RWAPredictionMarket |
|   TSLA > $250     |  |   AMZN > $200       |  |   HOOD > $50        |
|  (PolicyProtected)|  |  (PolicyProtected)   |  |  (PolicyProtected)  |
+---------+---------+   +-----------+---------+   +-----------+---------+
          |                         |                         |
          +------------+------------+------------+------------+
                       |                         |
            +----------v----------+   +----------v----------+
            | Chainlink ACE       |   | DataStreamConsumer  |
            | PolicyEngine        |   | (Data Streams V3)   |
            |                     |   |                     |
            | CompliancePolicyRules|  | Sub-second stock    |
            | - Sanctions list    |   | price verification  |
            | - Daily limits      |   | & storage           |
            | - Hold periods      |   |                     |
            +---------------------+   +---------------------+
                       |                         |
            +----------v----------+   +----------v----------+
            | BatchTransferHelper |   | Chainlink Verifier  |
            | (batch validation)  |   | Proxy               |
            +---------------------+   +---------------------+
```

---

## Market Lifecycle

The lifecycle of every RWA prediction market follows five distinct phases:

### 1. Creation

The factory owner calls `createMarket()` on `RWAMarketFactory`, specifying the collateral token, Chainlink feed ID, stock symbol, strike price, expiration time, and direction (above/below). A new `RWAPredictionMarket` contract is deployed and registered with a unique market ID derived from `keccak256(abi.encodePacked(feedId, strikePrice, expirationTime, isAbove))`.

### 2. Trading

While the market status is `Open` (before expiration), users can:

- **Buy shares** via `buyShares(bool isYes, uint256 amount)` -- deposit collateral to receive YES or NO shares
- **Sell shares** via `sellShares(bool isYes, uint256 amount)` -- return shares to receive collateral back (minus fees)

All trading functions enforce ACE compliance through the `runPolicy` modifier.

### 3. Expiration

When `block.timestamp >= expirationTime`, the market transitions to `Closed` status. No further trading is permitted. The market awaits resolution.

### 4. Resolution

Resolution can occur through two paths:

- **Standard resolution** via `resolve()` -- reads the latest verified price from `DataStreamConsumer`, compares against the strike price, and determines whether YES or NO wins
- **Emergency resolution** via `emergencyResolve(bool _yesWins, string reason)` -- owner-only fallback for oracle failures or exceptional circumstances

### 5. Claiming

After resolution, winning shareholders call `claimWinnings()` to receive their proportional share of the total collateral pool. The `runPolicy` modifier ensures compliance checks on all claim operations.

---

## Supported Assets

All assets are tokenized stocks deployed on Robinhood Chain:

| Symbol | Asset              | Feed Source            | Chain              |
|--------|--------------------|------------------------|--------------------|
| TSLA   | Tesla Inc.         | Chainlink Data Streams | Robinhood Chain    |
| AMZN   | Amazon.com Inc.    | Chainlink Data Streams | Robinhood Chain    |
| HOOD   | Robinhood Markets  | Chainlink Data Streams | Robinhood Chain    |
| PLTR   | Palantir Technologies | Chainlink Data Streams | Robinhood Chain |
| AMD    | Advanced Micro Devices | Chainlink Data Streams | Robinhood Chain |

**Chain Details:**

| Property       | Value                                        |
|----------------|----------------------------------------------|
| Chain Name     | Robinhood Chain                              |
| Chain ID       | 46630                                        |
| Type           | Arbitrum Orbit L2                            |
| RPC            | `https://rpc.testnet.chain.robinhood.com`    |

---

## Key Features

### ACE Compliance via PolicyProtected

Every user-facing function (`buyShares`, `sellShares`, `claimWinnings`) is protected by the `runPolicy` modifier inherited from Chainlink ACE's `PolicyProtected` contract. This enforces sanctions screening, daily volume limits, single transfer maximums, and hold period checks at the smart contract level.

### Data Streams V3 for Sub-Second Stock Prices

Market resolution uses Chainlink Data Streams V3, which provides cryptographically signed off-chain price reports verified on-chain through the `DataStreamConsumer` contract. This delivers sub-second price accuracy for settlement, with staleness protection and bid/ask spread data.

### Factory Pattern

The `RWAMarketFactory` contract manages the full lifecycle of market deployment. It maintains an approved collateral whitelist, generates deterministic market IDs, and provides paginated queries for market discovery. Only the factory owner can create new markets.

### 1% Platform Fee

A platform fee of 1% (`PLATFORM_FEE_BPS = 100`, with `BPS_DENOMINATOR = 10000`) is deducted on share sales. Accumulated fees can be withdrawn by the contract owner via `withdrawFees()`.

### Proportional Payouts

Winning shareholders receive payouts proportional to their share of the winning pool relative to the total collateral. If a user holds 30% of YES shares and YES wins, they receive 30% of the entire collateral pool (YES + NO deposits combined).

---

## Documentation Index

| Document                                              | Description                                      |
|-------------------------------------------------------|--------------------------------------------------|
| [contracts.md](contracts.md)                          | Complete contract reference with all signatures   |
| [deployment.md](deployment.md)                        | Deployment guide for Robinhood Chain              |
| [compliance.md](compliance.md)                        | ACE compliance and policy engine documentation    |
| [test-results.md](test-results.md)                    | Test suite results and gas benchmarks             |
| [../quickstart/rwa-quickstart.md](../quickstart/rwa-quickstart.md) | Quick start guide for RWA markets   |

---

## Contract Summary

| Contract                  | Lines | Role                                        |
|---------------------------|-------|---------------------------------------------|
| RWAPredictionMarket.sol   | 383   | Core prediction market logic with ACE       |
| RWAMarketFactory.sol      | 232   | Factory for deploying and managing markets  |
| DataStreamConsumer.sol    | 269   | Chainlink Data Streams V3 price oracle      |
| CompliancePolicyRules.sol | 309   | ACE policy rules engine                     |
| BatchTransferHelper.sol   | 133   | Batch transfer validation utilities         |
| SimpleToken.sol           | --    | ERC20 + ERC-2612 permit collateral token    |
