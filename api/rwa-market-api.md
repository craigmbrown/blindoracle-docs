# RWA Market On-Chain API Reference

> Solidity interface reference for BlindOracle's RWA prediction market contracts on Robinhood Chain (chain ID 46630). All functions are on-chain -- interact via `cast`, ethers.js, or any EVM-compatible client.

---

## Table of Contents

- [Factory API (RWAMarketFactory)](#factory-api-rwamarketfactory)
- [Market API (RWAPredictionMarket)](#market-api-rwapredictionmarket)
- [Oracle API (DataStreamConsumer)](#oracle-api-datastreamconsumer)
- [Events Reference](#events-reference)
- [Error Codes](#error-codes)

---

## Factory API (RWAMarketFactory)

The factory deploys and indexes all RWA prediction markets. It enforces collateral whitelisting and wires up the policy engine and oracle consumer on each new market.

### createMarket

Creates a new binary prediction market for a tokenized stock.

```solidity
function createMarket(
    address collateral,
    bytes32 feedId,
    string calldata symbol,
    int192 strikePrice,
    uint256 expirationTime,
    bool isAbove
) external onlyOwner returns (address)
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `collateral` | `address` | ERC-20 token used for share purchases (must be approved) |
| `feedId` | `bytes32` | Chainlink Data Streams feed identifier (e.g., TSLA/USD) |
| `symbol` | `string` | Human-readable asset symbol (e.g., `"TSLA"`) |
| `strikePrice` | `int192` | Strike price in 18-decimal fixed point |
| `expirationTime` | `uint256` | Unix timestamp when the market expires |
| `isAbove` | `bool` | If `true`, YES wins when price >= strike. If `false`, YES wins when price < strike |

**Returns:** Address of the newly deployed `RWAPredictionMarket` contract.

**Reverts:**
- `CollateralNotApproved()` -- collateral token not whitelisted
- `ExpirationInPast()` -- expirationTime <= block.timestamp
- `InvalidFeedId()` -- feedId is bytes32(0)

```bash
# Create a TSLA market: "Will TSLA be above $300 by March 31, 2026?"
cast send $FACTORY "createMarket(address,bytes32,string,int192,uint256,bool)" \
  $USDC \
  0x00037da06d56d083fe599397a4769a042d63aa73dc4ef57709d31e9971a5b439 \
  "TSLA" \
  300000000000000000000 \
  1743379200 \
  true \
  --rpc-url $RPC_URL --private-key $PK
```

---

### getMarket

Returns the deployed market contract address for a given market ID.

```solidity
function getMarket(bytes32 marketId) external view returns (address)
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `marketId` | `bytes32` | Keccak256 hash of (feedId, strikePrice, expirationTime, isAbove) |

**Returns:** Market contract address, or `address(0)` if not found.

```bash
cast call $FACTORY "getMarket(bytes32)(address)" $MARKET_ID --rpc-url $RPC_URL
```

---

### getMarketPage

Paginated retrieval of market IDs. Use this instead of iterating the full array on-chain.

```solidity
function getMarketPage(uint256 offset, uint256 limit) external view returns (bytes32[] memory)
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `offset` | `uint256` | Starting index |
| `limit` | `uint256` | Maximum number of IDs to return |

**Returns:** Array of market IDs, length <= limit.

```bash
# Get the first 10 markets
cast call $FACTORY "getMarketPage(uint256,uint256)(bytes32[])" 0 10 --rpc-url $RPC_URL
```

---

### getMarketsByFeed

Returns all market IDs associated with a specific Data Streams feed.

```solidity
function getMarketsByFeed(bytes32 feedId) external view returns (bytes32[] memory)
```

```bash
# Get all TSLA markets
cast call $FACTORY "getMarketsByFeed(bytes32)(bytes32[])" $TSLA_FEED_ID --rpc-url $RPC_URL
```

---

### getMarketCount

Returns the total number of markets created by this factory.

```solidity
function getMarketCount() external view returns (uint256)
```

```bash
cast call $FACTORY "getMarketCount()(uint256)" --rpc-url $RPC_URL
```

---

### approveCollateral / revokeCollateral

Manages the whitelist of ERC-20 tokens that can be used as collateral.

```solidity
function approveCollateral(address token) external onlyOwner
function revokeCollateral(address token) external onlyOwner
```

```bash
# Approve USDC as collateral
cast send $FACTORY "approveCollateral(address)" $USDC --rpc-url $RPC_URL --private-key $PK

# Revoke a token
cast send $FACTORY "revokeCollateral(address)" $OLD_TOKEN --rpc-url $RPC_URL --private-key $PK
```

---

### setPolicyEngine / setDataStreamConsumer

Updates the ACE policy engine or oracle consumer used by newly created markets.

```solidity
function setPolicyEngine(address engine) external onlyOwner
function setDataStreamConsumer(address consumer) external onlyOwner
```

**Note:** These only affect markets created *after* the call. Existing markets retain their original references.

```bash
cast send $FACTORY "setPolicyEngine(address)" $NEW_ENGINE --rpc-url $RPC_URL --private-key $PK
cast send $FACTORY "setDataStreamConsumer(address)" $NEW_CONSUMER --rpc-url $RPC_URL --private-key $PK
```

---

## Market API (RWAPredictionMarket)

Each market is a standalone contract deployed by the factory. It holds collateral, tracks share balances, and resolves against oracle prices.

### buyShares

Purchase YES or NO shares. 1 share = 1 unit of collateral (fixed pricing model). Caller must have approved the market contract to spend their collateral tokens.

```solidity
function buyShares(bool isYes, uint256 amount) external runPolicy nonReentrant
```

**Modifiers:**
- `runPolicy` -- Executes ACE CompliancePolicyRules before proceeding. Reverts if the caller fails compliance checks.
- `nonReentrant` -- OpenZeppelin reentrancy guard.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `isYes` | `bool` | `true` to buy YES shares, `false` to buy NO shares |
| `amount` | `uint256` | Number of shares to buy (in collateral token decimals) |

**Reverts:**
- `MarketNotActive()` -- market is resolved or expired
- `InsufficientAllowance()` -- caller has not approved enough collateral
- Policy engine revert -- caller failed compliance check

```bash
# Buy 100 YES shares (assumes USDC with 6 decimals: 100e6 = 100000000)
cast send $MARKET "buyShares(bool,uint256)" true 100000000 \
  --rpc-url $RPC_URL --private-key $PK

# Buy 50 NO shares
cast send $MARKET "buyShares(bool,uint256)" false 50000000 \
  --rpc-url $RPC_URL --private-key $PK
```

---

### sellShares

Sell previously purchased shares back to the market. Returns collateral to the seller.

```solidity
function sellShares(bool isYes, uint256 amount) external runPolicy nonReentrant
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `isYes` | `bool` | `true` to sell YES shares, `false` to sell NO shares |
| `amount` | `uint256` | Number of shares to sell |

**Reverts:**
- `MarketNotActive()` -- market is resolved or expired
- `InsufficientShares()` -- caller holds fewer shares than `amount`

```bash
# Sell 25 YES shares
cast send $MARKET "sellShares(bool,uint256)" true 25000000 \
  --rpc-url $RPC_URL --private-key $PK
```

---

### resolve

Resolves the market by reading the latest oracle price and comparing it to the strike. Anyone can call this after the market has expired. The function is permissionless because the outcome is determined entirely by on-chain oracle data.

```solidity
function resolve() external
```

**Requirements:**
- `block.timestamp >= expirationTime`
- Market status must be `Active`
- Oracle must have a price for the market's feedId

**Resolution logic:**
- If `isAbove == true`: YES wins when `latestPrice >= strikePrice`
- If `isAbove == false`: YES wins when `latestPrice < strikePrice`

```bash
cast send $MARKET "resolve()" --rpc-url $RPC_URL --private-key $PK
```

---

### claimWinnings

After resolution, winning shareholders claim their proportional share of the total collateral pool.

```solidity
function claimWinnings() external runPolicy nonReentrant
```

**Payout calculation:**
```
payout = (userWinningShares / totalWinningShares) * totalCollateralPool * (1 - feeRate)
```

**Reverts:**
- `MarketNotResolved()` -- market has not been resolved yet
- `NoWinningShares()` -- caller holds zero winning shares
- `AlreadyClaimed()` -- caller has already claimed

```bash
cast send $MARKET "claimWinnings()" --rpc-url $RPC_URL --private-key $PK
```

---

### emergencyResolve

Owner-only emergency resolution. Use when oracle data is unavailable or demonstrably incorrect. Emits a reason string for audit trails.

```solidity
function emergencyResolve(bool _yesWins, string calldata reason) external onlyOwner
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `_yesWins` | `bool` | `true` if YES side wins, `false` if NO side wins |
| `reason` | `string` | Human-readable explanation for the emergency resolution |

```bash
cast send $MARKET "emergencyResolve(bool,string)" true "Oracle feed stale for 24h, resolving based on off-chain TSLA close" \
  --rpc-url $RPC_URL --private-key $PK
```

---

### withdrawFees

Withdraws accumulated protocol fees to a specified address.

```solidity
function withdrawFees(address to) external onlyOwner
```

```bash
cast send $MARKET "withdrawFees(address)" $TREASURY --rpc-url $RPC_URL --private-key $PK
```

---

### getMarketStatus

Returns the current lifecycle state of the market.

```solidity
function getMarketStatus() external view returns (MarketStatus)
```

**MarketStatus enum:**

| Value | Name | Description |
|-------|------|-------------|
| 0 | `Active` | Trading is open |
| 1 | `Expired` | Past expiration, awaiting resolution |
| 2 | `Resolved` | Outcome determined, claims open |
| 3 | `EmergencyResolved` | Owner forced resolution |

```bash
cast call $MARKET "getMarketStatus()(uint8)" --rpc-url $RPC_URL
```

---

### getShareBalances

Returns the YES and NO share balances for a given address.

```solidity
function getShareBalances(address account) external view returns (uint256 yes, uint256 no)
```

```bash
cast call $MARKET "getShareBalances(address)(uint256,uint256)" $USER_ADDR --rpc-url $RPC_URL
```

---

### getMarketSummary

Returns a comprehensive snapshot of the market's current state in a single call.

```solidity
function getMarketSummary() external view returns (
    string memory symbol,
    int192 strikePrice,
    uint256 expirationTime,
    bool isAbove,
    uint256 yesTotal,
    uint256 noTotal,
    address collateral,
    MarketStatus status
)
```

```bash
cast call $MARKET \
  "getMarketSummary()(string,int192,uint256,bool,uint256,uint256,address,uint8)" \
  --rpc-url $RPC_URL
```

---

## Oracle API (DataStreamConsumer)

The oracle layer decodes and stores Chainlink Data Streams V3 premium reports. It serves as the single source of truth for price data used in market resolution.

### verifyAndStore

Decodes a signed Data Streams premium report, validates freshness, and stores the price on-chain.

```solidity
function verifyAndStore(bytes calldata signedReport) external
```

**What happens internally:**
1. Decodes the outer envelope to extract the report payload
2. Decodes the `PremiumReport` struct from the payload
3. Validates `feedId` is registered
4. Checks `observationsTimestamp` is within the staleness threshold
5. Stores the price in the `latestPrices` mapping
6. Emits `PriceUpdated(feedId, price, timestamp)`

```bash
# signedReport is the raw bytes from the Data Streams API
cast send $CONSUMER "verifyAndStore(bytes)" $SIGNED_REPORT \
  --rpc-url $RPC_URL --private-key $PK
```

---

### getLatestPrice

Returns the most recently stored price for a feed.

```solidity
function getLatestPrice(bytes32 feedId) external view returns (int192 price, uint32 timestamp)
```

```bash
cast call $CONSUMER "getLatestPrice(bytes32)(int192,uint32)" $TSLA_FEED_ID --rpc-url $RPC_URL
```

---

### getFullPriceData

Returns the complete stored price data including bid/ask spread.

```solidity
function getFullPriceData(bytes32 feedId) external view returns (PriceData memory)
```

**PriceData struct:**

```solidity
struct PriceData {
    int192 price;
    int192 bid;
    int192 ask;
    uint32 observationsTimestamp;
    uint32 storedAt;
}
```

```bash
cast call $CONSUMER "getFullPriceData(bytes32)((int192,int192,int192,uint32,uint32))" \
  $TSLA_FEED_ID --rpc-url $RPC_URL
```

---

### isPriceFresh

Checks whether the stored price for a feed is within the staleness threshold.

```solidity
function isPriceFresh(bytes32 feedId) external view returns (bool)
```

```bash
cast call $CONSUMER "isPriceFresh(bytes32)(bool)" $TSLA_FEED_ID --rpc-url $RPC_URL
```

---

### registerFeed / deregisterFeed

Manages the set of recognized Data Streams feed IDs.

```solidity
function registerFeed(bytes32 feedId, string calldata symbol) external onlyOwner
function deregisterFeed(bytes32 feedId) external onlyOwner
```

```bash
# Register TSLA feed
cast send $CONSUMER "registerFeed(bytes32,string)" \
  0x00037da06d56d083fe599397a4769a042d63aa73dc4ef57709d31e9971a5b439 \
  "TSLA" \
  --rpc-url $RPC_URL --private-key $PK

# Deregister a feed
cast send $CONSUMER "deregisterFeed(bytes32)" $FEED_ID --rpc-url $RPC_URL --private-key $PK
```

---

## Events Reference

All events are indexed for efficient off-chain querying. Use these topics with `cast logs` or any indexer.

### RWAMarketFactory Events

```solidity
event MarketCreated(
    bytes32 indexed marketId,
    address indexed marketAddress,
    bytes32 indexed feedId,
    string symbol,
    int192 strikePrice,
    uint256 expirationTime,
    bool isAbove
);
// Topic 0: keccak256("MarketCreated(bytes32,address,bytes32,string,int192,uint256,bool)")

event CollateralApproved(address indexed token);
// Topic 0: keccak256("CollateralApproved(address)")

event CollateralRevoked(address indexed token);
// Topic 0: keccak256("CollateralRevoked(address)")

event PolicyEngineUpdated(address indexed oldEngine, address indexed newEngine);
// Topic 0: keccak256("PolicyEngineUpdated(address,address)")

event DataStreamConsumerUpdated(address indexed oldConsumer, address indexed newConsumer);
// Topic 0: keccak256("DataStreamConsumerUpdated(address,address)")
```

### RWAPredictionMarket Events

```solidity
event SharesPurchased(
    address indexed buyer,
    bool indexed isYes,
    uint256 amount
);
// Topic 0: keccak256("SharesPurchased(address,bool,uint256)")

event SharesSold(
    address indexed seller,
    bool indexed isYes,
    uint256 amount
);
// Topic 0: keccak256("SharesSold(address,bool,uint256)")

event MarketResolved(
    bool yesWins,
    int192 finalPrice,
    int192 strikePrice
);
// Topic 0: keccak256("MarketResolved(bool,int192,int192)")

event EmergencyResolved(
    bool yesWins,
    string reason
);
// Topic 0: keccak256("EmergencyResolved(bool,string)")

event WinningsClaimed(
    address indexed claimer,
    uint256 payout
);
// Topic 0: keccak256("WinningsClaimed(address,uint256)")

event FeesWithdrawn(
    address indexed to,
    uint256 amount
);
// Topic 0: keccak256("FeesWithdrawn(address,uint256)")
```

### DataStreamConsumer Events

```solidity
event PriceUpdated(
    bytes32 indexed feedId,
    int192 price,
    uint32 timestamp
);
// Topic 0: keccak256("PriceUpdated(bytes32,int192,uint32)")

event FeedRegistered(
    bytes32 indexed feedId,
    string symbol
);
// Topic 0: keccak256("FeedRegistered(bytes32,string)")

event FeedDeregistered(
    bytes32 indexed feedId
);
// Topic 0: keccak256("FeedDeregistered(bytes32)")

event StalenessThresholdUpdated(
    uint256 oldThreshold,
    uint256 newThreshold
);
// Topic 0: keccak256("StalenessThresholdUpdated(uint256,uint256)")
```

### Querying Events with cast

```bash
# Get all MarketCreated events from the factory
cast logs --from-block 0 --address $FACTORY \
  "MarketCreated(bytes32,address,bytes32,string,int192,uint256,bool)" \
  --rpc-url $RPC_URL

# Get all share purchases for a specific market
cast logs --from-block 0 --address $MARKET \
  "SharesPurchased(address,bool,uint256)" \
  --rpc-url $RPC_URL

# Filter by specific buyer (indexed topic1)
cast logs --from-block 0 --address $MARKET \
  "SharesPurchased(address,bool,uint256)" \
  --topic1 $(cast abi-encode "f(address)" $BUYER_ADDR) \
  --rpc-url $RPC_URL
```

---

## Error Codes

Custom errors used across the contract system. These replace require strings for gas efficiency.

```solidity
// RWAMarketFactory
error CollateralNotApproved();
error ExpirationInPast();
error InvalidFeedId();
error MarketAlreadyExists();
error ZeroAddress();

// RWAPredictionMarket
error MarketNotActive();
error MarketNotExpired();
error MarketNotResolved();
error MarketAlreadyResolved();
error InsufficientShares();
error InsufficientAllowance();
error NoWinningShares();
error AlreadyClaimed();
error TransferFailed();

// DataStreamConsumer
error FeedNotRegistered();
error StalePrice();
error InvalidReport();
error FeedAlreadyRegistered();
```

---

## Environment Variables

For the `cast` examples throughout this document, set these environment variables:

```bash
export RPC_URL="https://robin-rpc.lavish.dev"           # Robinhood Chain RPC
export FACTORY="0x..."                                    # RWAMarketFactory address
export MARKET="0x..."                                     # Specific RWAPredictionMarket
export CONSUMER="0x..."                                   # DataStreamConsumer address
export USDC="0x..."                                       # USDC on Robinhood Chain
export PK="0x..."                                         # Deployer private key (NEVER commit)
export TSLA_FEED_ID="0x00037da06d56d083fe599397a4769a042d63aa73dc4ef57709d31e9971a5b439"
```

---

*Contract source: [blindoracle-rwa-markets](https://github.com/craigmbrown/blindoracle-rwa-markets) | Chain: Robinhood Chain (46630) | Compiler: Solidity 0.8.24*
