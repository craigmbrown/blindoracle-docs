# Contract Reference

Complete API reference for all BlindOracle RWA Stock Prediction Market contracts.

---

## Table of Contents

- [RWAPredictionMarket.sol](#rwapredictionmarketsol)
- [RWAMarketFactory.sol](#rwamarketfactorysol)
- [DataStreamConsumer.sol](#datastreamconsumersol)
- [CompliancePolicyRules.sol](#compliancepolicyrulessol)
- [BatchTransferHelper.sol](#batchtransferhelpersol)
- [SimpleToken.sol](#simpletokensol)

---

## RWAPredictionMarket.sol

**383 lines** | Core prediction market contract for a single RWA stock market.

### Inheritance

```
PolicyProtected, ReentrancyGuard
```

### Constructor

```solidity
constructor(
    address initialOwner,
    address policyEngine,
    address _collateral,
    address _dataStream,
    bytes32 _feedId,
    string memory _symbol,
    int192 _strikePrice,
    uint256 _expirationTime,
    bool _isAbove
)
```

| Parameter        | Type      | Description                                                   |
|------------------|-----------|---------------------------------------------------------------|
| initialOwner     | address   | Owner of the market contract                                  |
| policyEngine     | address   | Chainlink ACE PolicyEngine address for compliance checks      |
| _collateral      | address   | ERC20 token used as collateral (e.g., USDC)                  |
| _dataStream      | address   | DataStreamConsumer contract address                           |
| _feedId          | bytes32   | Chainlink Data Streams feed identifier for the stock          |
| _symbol          | string    | Stock ticker symbol (e.g., "TSLA")                           |
| _strikePrice     | int192    | Target price for market resolution                            |
| _expirationTime  | uint256   | Unix timestamp when the market closes for trading             |
| _isAbove         | bool      | If true, YES wins when price > strike; if false, YES wins when price < strike |

### Enums

```solidity
enum MarketStatus {
    Open,
    Closed,
    Resolved
}
```

| Value    | Description                                        |
|----------|----------------------------------------------------|
| Open     | Market is accepting trades                         |
| Closed   | Expiration reached, awaiting resolution            |
| Resolved | Outcome determined, winnings can be claimed        |

### Struct

```solidity
struct MarketParams {
    bytes32 feedId;
    string symbol;
    int192 strikePrice;
    uint256 expirationTime;
    bool isAbove;
}
```

### Constants

| Constant          | Type    | Value  | Description                            |
|-------------------|---------|--------|----------------------------------------|
| PLATFORM_FEE_BPS  | uint256 | 100    | Platform fee in basis points (1%)      |
| BPS_DENOMINATOR   | uint256 | 10000  | Basis points denominator               |

### Functions

#### buyShares

```solidity
function buyShares(bool isYes, uint256 amount) external nonReentrant runPolicy
```

Purchase YES or NO shares by depositing collateral tokens.

| Parameter | Type    | Description                                    |
|-----------|---------|------------------------------------------------|
| isYes     | bool    | `true` to buy YES shares, `false` for NO       |
| amount    | uint256 | Amount of collateral tokens to deposit          |

**Modifiers:** `nonReentrant`, `runPolicy`

**Reverts:** `MarketNotOpen()`, `InvalidAmount()`

---

#### sellShares

```solidity
function sellShares(bool isYes, uint256 amount) external nonReentrant runPolicy
```

Sell shares back to the market and receive collateral minus platform fee.

| Parameter | Type    | Description                                    |
|-----------|---------|------------------------------------------------|
| isYes     | bool    | `true` to sell YES shares, `false` for NO      |
| amount    | uint256 | Number of shares to sell                        |

**Modifiers:** `nonReentrant`, `runPolicy`

**Reverts:** `MarketNotOpen()`, `InsufficientShares()`, `InvalidAmount()`

---

#### resolve

```solidity
function resolve() external nonReentrant
```

Resolve the market using the latest verified price from DataStreamConsumer. Compares the settlement price against the strike price to determine whether YES or NO wins.

**Modifiers:** `nonReentrant`

**Reverts:** `MarketNotResolvable()`, `MarketAlreadyResolved()`, `ResolutionTooEarly()`, `FeedMismatch()`

---

#### emergencyResolve

```solidity
function emergencyResolve(bool _yesWins, string calldata reason) external onlyOwner
```

Owner-only emergency resolution for oracle failures or exceptional circumstances.

| Parameter | Type   | Description                                     |
|-----------|--------|-------------------------------------------------|
| _yesWins  | bool   | Manually set the winning outcome                |
| reason    | string | Human-readable reason for emergency resolution  |

**Modifiers:** `onlyOwner`

**Reverts:** `MarketAlreadyResolved()`

---

#### claimWinnings

```solidity
function claimWinnings() external nonReentrant runPolicy
```

Claim proportional winnings from the collateral pool after market resolution.

**Modifiers:** `nonReentrant`, `runPolicy`

**Reverts:** `MarketNotResolved()`, `NothingToClaim()`, `TransferFailed()`

---

#### withdrawFees

```solidity
function withdrawFees(address to) external onlyOwner
```

Withdraw accumulated platform fees to the specified address.

| Parameter | Type    | Description                              |
|-----------|---------|------------------------------------------|
| to        | address | Recipient address for accumulated fees   |

**Modifiers:** `onlyOwner`

---

#### getMarketStatus

```solidity
function getMarketStatus() external view returns (MarketStatus)
```

Returns the current market status (`Open`, `Closed`, or `Resolved`).

---

#### getShareBalances

```solidity
function getShareBalances(address account) external view returns (uint256 yes, uint256 no)
```

Returns the YES and NO share balances for a given account.

| Parameter | Type    | Description                    |
|-----------|---------|--------------------------------|
| account   | address | Address to query balances for  |

| Return | Type    | Description              |
|--------|---------|--------------------------|
| yes    | uint256 | Number of YES shares     |
| no     | uint256 | Number of NO shares      |

---

#### getMarketSummary

```solidity
function getMarketSummary() external view returns (
    string memory symbol,
    int192 strikePrice,
    uint256 expirationTime,
    bool isAbove,
    uint256 yesTotal,
    uint256 noTotal,
    uint256 collateral,
    MarketStatus currentStatus
)
```

Returns a comprehensive summary of the market state.

| Return        | Type         | Description                           |
|---------------|--------------|---------------------------------------|
| symbol        | string       | Stock ticker symbol                   |
| strikePrice   | int192       | Target price for resolution           |
| expirationTime| uint256      | Unix timestamp of market expiration   |
| isAbove       | bool         | Direction of the market bet           |
| yesTotal      | uint256      | Total YES shares outstanding          |
| noTotal       | uint256      | Total NO shares outstanding           |
| collateral    | uint256      | Total collateral in the pool          |
| currentStatus | MarketStatus | Current market status                 |

### Events

#### MarketCreated

```solidity
event MarketCreated(
    bytes32 indexed feedId,
    string symbol,
    int192 strikePrice,
    uint256 expirationTime,
    bool isAbove
)
```

Emitted when the market contract is deployed.

---

#### SharesPurchased

```solidity
event SharesPurchased(
    address indexed buyer,
    bool isYes,
    uint256 amount,
    uint256 cost
)
```

Emitted when a user purchases shares.

---

#### SharesSold

```solidity
event SharesSold(
    address indexed seller,
    bool isYes,
    uint256 amount,
    uint256 payout
)
```

Emitted when a user sells shares.

---

#### MarketResolved

```solidity
event MarketResolved(
    bool yesWins,
    int192 settlementPrice,
    uint32 priceTimestamp
)
```

Emitted when the market is resolved via standard oracle resolution.

---

#### WinningsClaimed

```solidity
event WinningsClaimed(
    address indexed claimer,
    uint256 amount
)
```

Emitted when a user claims their winnings.

---

#### EmergencyResolved

```solidity
event EmergencyResolved(
    bool yesWins,
    string reason
)
```

Emitted when the owner triggers an emergency resolution.

### Errors

| Error                    | Description                                              |
|--------------------------|----------------------------------------------------------|
| `MarketNotOpen()`        | Attempted trade on a non-open market                     |
| `MarketNotResolvable()`  | Market cannot be resolved in its current state            |
| `MarketAlreadyResolved()`| Market has already been resolved                         |
| `MarketNotResolved()`    | Attempted claim before resolution                        |
| `InsufficientShares()`   | User does not hold enough shares to sell                 |
| `InvalidAmount()`        | Zero or invalid amount provided                          |
| `InvalidStrikePrice()`   | Strike price is zero or invalid                          |
| `InvalidExpirationTime()`| Expiration time is in the past                           |
| `ResolutionTooEarly()`   | Attempted resolution before expiration                   |
| `NothingToClaim()`       | User has no winning shares to claim                      |
| `FeedMismatch()`         | Oracle feed ID does not match the market's configured feed |
| `TransferFailed()`       | ERC20 token transfer failed                              |

---

## RWAMarketFactory.sol

**232 lines** | Factory contract for deploying and managing RWA prediction markets.

### Inheritance

```
Ownable
```

### Constructor

```solidity
constructor(
    address initialOwner,
    address _policyEngine,
    address _dataStream
)
```

| Parameter      | Type    | Description                                  |
|----------------|---------|----------------------------------------------|
| initialOwner   | address | Owner of the factory contract                |
| _policyEngine  | address | Chainlink ACE PolicyEngine address           |
| _dataStream    | address | DataStreamConsumer contract address           |

### Market ID Derivation

Market IDs are deterministically computed as:

```solidity
bytes32 marketId = keccak256(abi.encodePacked(feedId, strikePrice, expirationTime, isAbove));
```

This ensures each unique combination of feed, strike price, expiration, and direction produces a unique market ID.

### Functions

#### createMarket

```solidity
function createMarket(
    address collateral,
    bytes32 feedId,
    string calldata symbol,
    int192 strikePrice,
    uint256 expirationTime,
    bool isAbove
) external onlyOwner returns (address marketAddress)
```

Deploy a new RWAPredictionMarket instance.

| Parameter      | Type    | Description                                   |
|----------------|---------|-----------------------------------------------|
| collateral     | address | Approved ERC20 collateral token address       |
| feedId         | bytes32 | Chainlink Data Streams feed identifier        |
| symbol         | string  | Stock ticker symbol                           |
| strikePrice    | int192  | Target price for resolution                   |
| expirationTime | uint256 | Unix timestamp for market expiration          |
| isAbove        | bool    | Direction of the market bet                   |

| Return         | Type    | Description                                   |
|----------------|---------|-----------------------------------------------|
| marketAddress  | address | Address of the newly deployed market contract |

**Modifiers:** `onlyOwner`

**Reverts:** `CollateralNotApproved(address token)`, `MarketAlreadyExists(bytes32 marketId)`, `InvalidParameters()`

---

#### approveCollateral

```solidity
function approveCollateral(address token) external onlyOwner
```

Add a token to the approved collateral whitelist.

**Modifiers:** `onlyOwner`

**Reverts:** `ZeroAddress()`

---

#### revokeCollateral

```solidity
function revokeCollateral(address token) external onlyOwner
```

Remove a token from the approved collateral whitelist.

**Modifiers:** `onlyOwner`

---

#### setPolicyEngine

```solidity
function setPolicyEngine(address newEngine) external onlyOwner
```

Update the ACE PolicyEngine address used for future market deployments.

**Modifiers:** `onlyOwner`

**Reverts:** `ZeroAddress()`

---

#### setDataStreamConsumer

```solidity
function setDataStreamConsumer(address newStream) external onlyOwner
```

Update the DataStreamConsumer address used for future market deployments.

**Modifiers:** `onlyOwner`

**Reverts:** `ZeroAddress()`

---

#### getMarketCount

```solidity
function getMarketCount() external view returns (uint256)
```

Returns the total number of markets deployed by this factory.

---

#### getMarketsByFeed

```solidity
function getMarketsByFeed(bytes32 feedId) external view returns (bytes32[] memory)
```

Returns all market IDs associated with a specific Chainlink feed.

| Parameter | Type    | Description                          |
|-----------|---------|--------------------------------------|
| feedId    | bytes32 | Chainlink Data Streams feed ID       |

---

#### getMarket

```solidity
function getMarket(bytes32 marketId) external view returns (address)
```

Returns the contract address for a given market ID.

| Parameter | Type    | Description         |
|-----------|---------|---------------------|
| marketId  | bytes32 | Unique market ID    |

**Reverts:** `MarketNotFound(bytes32 marketId)`

---

#### getMarketPage

```solidity
function getMarketPage(uint256 offset, uint256 limit) external view returns (bytes32[] memory page)
```

Returns a paginated list of market IDs.

| Parameter | Type    | Description                        |
|-----------|---------|------------------------------------|
| offset    | uint256 | Starting index for pagination      |
| limit     | uint256 | Maximum number of results          |

### Events

#### MarketDeployed

```solidity
event MarketDeployed(
    bytes32 indexed marketId,
    address indexed market,
    bytes32 feedId,
    string symbol,
    int192 strikePrice,
    uint256 expirationTime,
    bool isAbove
)
```

Emitted when a new market is deployed.

---

#### CollateralApproved

```solidity
event CollateralApproved(address indexed token)
```

Emitted when a collateral token is added to the whitelist.

---

#### CollateralRevoked

```solidity
event CollateralRevoked(address indexed token)
```

Emitted when a collateral token is removed from the whitelist.

---

#### PolicyEngineUpdated

```solidity
event PolicyEngineUpdated(address indexed oldEngine, address indexed newEngine)
```

Emitted when the ACE PolicyEngine address is updated.

---

#### DataStreamUpdated

```solidity
event DataStreamUpdated(address indexed oldStream, address indexed newStream)
```

Emitted when the DataStreamConsumer address is updated.

### Errors

| Error                                  | Description                                         |
|----------------------------------------|-----------------------------------------------------|
| `ZeroAddress()`                        | A zero address was provided where not allowed        |
| `MarketAlreadyExists(bytes32 marketId)`| A market with this ID has already been deployed      |
| `MarketNotFound(bytes32 marketId)`     | No market exists with this ID                        |
| `CollateralNotApproved(address token)` | Collateral token is not on the approved whitelist    |
| `InvalidParameters()`                  | One or more parameters failed validation             |

---

## DataStreamConsumer.sol

**269 lines** | Chainlink Data Streams V3 consumer for verifying and storing stock price data.

### Inheritance

```
Ownable
```

### Constructor

```solidity
constructor(
    address initialOwner,
    address _verifier,
    uint256 _stalenessThreshold
)
```

| Parameter            | Type    | Description                                         |
|----------------------|---------|-----------------------------------------------------|
| initialOwner         | address | Owner of the consumer contract                      |
| _verifier            | address | Chainlink Data Streams verifier proxy address       |
| _stalenessThreshold  | uint256 | Maximum age (in seconds) for a price to be valid    |

### Structs

#### PremiumReport

```solidity
struct PremiumReport {
    bytes32 feedId;
    uint32 validFromTimestamp;
    uint32 observationsTimestamp;
    uint192 nativeFee;
    uint192 linkFee;
    uint32 expiresAt;
    int192 price;
    int192 bid;
    int192 ask;
}
```

| Field                  | Type    | Description                                     |
|------------------------|---------|-------------------------------------------------|
| feedId                 | bytes32 | Chainlink feed identifier                       |
| validFromTimestamp     | uint32  | Earliest timestamp the report is valid from     |
| observationsTimestamp  | uint32  | Timestamp of the price observation              |
| nativeFee              | uint192 | Fee in native token for verification            |
| linkFee                | uint192 | Fee in LINK for verification                    |
| expiresAt              | uint32  | Report expiration timestamp                     |
| price                  | int192  | Mid-market price                                |
| bid                    | int192  | Best bid price                                  |
| ask                    | int192  | Best ask price                                  |

---

#### PriceData

```solidity
struct PriceData {
    int192 price;
    int192 bid;
    int192 ask;
    uint32 observationsTimestamp;
    uint256 updatedAtBlock;
    bool initialized;
}
```

| Field                  | Type    | Description                                     |
|------------------------|---------|-------------------------------------------------|
| price                  | int192  | Stored mid-market price                         |
| bid                    | int192  | Stored bid price                                |
| ask                    | int192  | Stored ask price                                |
| observationsTimestamp  | uint32  | Timestamp of the price observation              |
| updatedAtBlock         | uint256 | Block number when the price was last updated    |
| initialized            | bool    | Whether this feed has received at least one update |

---

#### FeedInfo

```solidity
struct FeedInfo {
    string symbol;
    bool active;
    uint256 registeredAt;
}
```

| Field        | Type    | Description                              |
|--------------|---------|------------------------------------------|
| symbol       | string  | Human-readable stock ticker symbol       |
| active       | bool    | Whether the feed is currently active     |
| registeredAt | uint256 | Timestamp when the feed was registered   |

### Functions

#### registerFeed

```solidity
function registerFeed(bytes32 feedId, string calldata symbol) external onlyOwner
```

Register a new Chainlink Data Streams feed for a stock.

| Parameter | Type    | Description                          |
|-----------|---------|--------------------------------------|
| feedId    | bytes32 | Chainlink feed identifier            |
| symbol    | string  | Stock ticker symbol                  |

**Modifiers:** `onlyOwner`

---

#### deregisterFeed

```solidity
function deregisterFeed(bytes32 feedId) external onlyOwner
```

Deactivate a registered feed.

**Modifiers:** `onlyOwner`

---

#### setVerifier

```solidity
function setVerifier(address newVerifier) external onlyOwner
```

Update the Chainlink Data Streams verifier proxy address.

**Modifiers:** `onlyOwner`

**Reverts:** `ZeroAddress()`

---

#### setStalenessThreshold

```solidity
function setStalenessThreshold(uint256 newThreshold) external onlyOwner
```

Update the maximum allowed age for price data.

**Modifiers:** `onlyOwner`

---

#### verifyAndStore

```solidity
function verifyAndStore(bytes calldata signedReport) external
```

Verify a signed Chainlink Data Streams report and store the price data on-chain. The report is decoded into a `PremiumReport`, verified against the Chainlink verifier proxy, and stored if the feed is registered and the price is valid.

| Parameter    | Type  | Description                                    |
|--------------|-------|------------------------------------------------|
| signedReport | bytes | Signed report payload from Chainlink Data Streams |

**Reverts:** `FeedNotRegistered(bytes32 feedId)`, `StalePrice(bytes32 feedId, uint256 reportTimestamp, uint256 currentTime, uint256 threshold)`, `VerificationFailed(bytes32 feedId)`, `InvalidPrice(bytes32 feedId, int192 price)`

---

#### getLatestPrice

```solidity
function getLatestPrice(bytes32 feedId) external view returns (int192 price, uint32 timestamp)
```

Returns the latest verified price and observation timestamp for a feed.

| Parameter | Type    | Description                    |
|-----------|---------|--------------------------------|
| feedId    | bytes32 | Chainlink feed identifier      |

| Return    | Type   | Description                     |
|-----------|--------|---------------------------------|
| price     | int192 | Latest verified mid-market price|
| timestamp | uint32 | Observation timestamp           |

**Reverts:** `FeedNotRegistered(bytes32 feedId)`

---

#### getFullPriceData

```solidity
function getFullPriceData(bytes32 feedId) external view returns (PriceData memory data)
```

Returns the full stored price data including bid, ask, and update metadata.

| Parameter | Type    | Description                    |
|-----------|---------|--------------------------------|
| feedId    | bytes32 | Chainlink feed identifier      |

---

#### isPriceFresh

```solidity
function isPriceFresh(bytes32 feedId) external view returns (bool fresh)
```

Check whether the stored price for a feed is within the staleness threshold.

| Parameter | Type    | Description                    |
|-----------|---------|--------------------------------|
| feedId    | bytes32 | Chainlink feed identifier      |

| Return | Type | Description                                        |
|--------|------|----------------------------------------------------|
| fresh  | bool | `true` if the price age is within the threshold    |

---

#### feedCount

```solidity
function feedCount() external view returns (uint256)
```

Returns the total number of registered feeds.

### Events

#### PriceUpdated

```solidity
event PriceUpdated(
    bytes32 indexed feedId,
    int192 price,
    uint32 observationsTimestamp,
    uint256 blockTimestamp
)
```

Emitted when a new price is verified and stored.

---

#### FeedRegistered

```solidity
event FeedRegistered(bytes32 indexed feedId, string symbol)
```

Emitted when a new feed is registered.

---

#### FeedDeregistered

```solidity
event FeedDeregistered(bytes32 indexed feedId)
```

Emitted when a feed is deactivated.

---

#### VerifierUpdated

```solidity
event VerifierUpdated(address indexed oldVerifier, address indexed newVerifier)
```

Emitted when the verifier proxy address is changed.

---

#### StalenessThresholdUpdated

```solidity
event StalenessThresholdUpdated(uint256 oldThreshold, uint256 newThreshold)
```

Emitted when the staleness threshold is modified.

### Errors

| Error                                                                              | Description                                              |
|------------------------------------------------------------------------------------|----------------------------------------------------------|
| `ZeroAddress()`                                                                    | A zero address was provided where not allowed             |
| `FeedNotRegistered(bytes32 feedId)`                                                | The specified feed ID has not been registered             |
| `StalePrice(bytes32 feedId, uint256 reportTimestamp, uint256 currentTime, uint256 threshold)` | Price report exceeds the staleness threshold  |
| `VerificationFailed(bytes32 feedId)`                                               | Chainlink verifier rejected the signed report            |
| `InvalidPrice(bytes32 feedId, int192 price)`                                       | Price value is zero or otherwise invalid                 |

---

## CompliancePolicyRules.sol

**309 lines** | ACE-compatible compliance policy engine enforcing sanctions, limits, and hold periods.

### Inheritance

```
Ownable, Pausable
```

### Constructor

```solidity
constructor(
    address initialOwner,
    uint256 _dailyLimit,
    uint256 _singleMax,
    uint256 _holdPeriod
)
```

| Parameter      | Type    | Description                                      |
|----------------|---------|--------------------------------------------------|
| initialOwner   | address | Owner of the policy rules contract               |
| _dailyLimit    | uint256 | Maximum total volume allowed per address per day |
| _singleMax     | uint256 | Maximum single transaction amount                |
| _holdPeriod    | uint256 | Minimum hold period in seconds before withdrawal |

### Functions

#### checkDepositAllowed

```solidity
function checkDepositAllowed(...)
```

Validates whether a deposit operation is allowed under current compliance rules. Checks sanctions list, daily volume limits, and single transfer maximums.

---

#### checkWithdrawAllowed

```solidity
function checkWithdrawAllowed(...)
```

Validates whether a withdrawal is allowed. Additionally checks hold period requirements.

---

#### checkPrivateTransferAllowed

```solidity
function checkPrivateTransferAllowed(...)
```

Validates whether a private transfer between addresses is allowed under compliance rules.

---

#### remainingDailyVolume

```solidity
function remainingDailyVolume(...) external view
```

Returns the remaining daily volume allowance for an address. Daily limits reset at midnight UTC.

---

#### isHoldPeriodElapsed

```solidity
function isHoldPeriodElapsed(...) external view
```

Checks whether the required hold period has elapsed for a given position.

---

#### setDailyTransferLimit

```solidity
function setDailyTransferLimit(uint256 newLimit) external onlyOwner
```

Update the daily volume limit per address.

**Modifiers:** `onlyOwner`

---

#### setSingleTransferMax

```solidity
function setSingleTransferMax(uint256 newMax) external onlyOwner
```

Update the maximum single transaction amount.

**Modifiers:** `onlyOwner`

---

#### setHoldPeriod

```solidity
function setHoldPeriod(uint256 newPeriod) external onlyOwner
```

Update the minimum hold period before withdrawal.

**Modifiers:** `onlyOwner`

---

#### addSanctionedAddress

```solidity
function addSanctionedAddress(address account) external onlyOwner
```

Add an address to the sanctions list.

**Modifiers:** `onlyOwner`

---

#### removeSanctionedAddress

```solidity
function removeSanctionedAddress(address account) external onlyOwner
```

Remove an address from the sanctions list.

**Modifiers:** `onlyOwner`

---

#### pause

```solidity
function pause() external onlyOwner
```

Pause all compliance-gated operations.

**Modifiers:** `onlyOwner`

---

#### unpause

```solidity
function unpause() external onlyOwner
```

Unpause compliance-gated operations.

**Modifiers:** `onlyOwner`

### Events

| Event                           | Description                                        |
|---------------------------------|----------------------------------------------------|
| `DailyTransferLimitUpdated`     | Daily volume limit was changed                     |
| `SingleTransferMaxUpdated`      | Single transfer maximum was changed                |
| `HoldPeriodUpdated`             | Hold period was changed                            |
| `AddressSanctioned_Added`       | An address was added to the sanctions list          |
| `AddressSanctioned_Removed`     | An address was removed from the sanctions list      |
| `DepositRecorded`               | A deposit was recorded for volume tracking          |
| `DailyVolumeConsumed`           | Daily volume was consumed by a transaction          |

### Errors

| Error                          | Description                                        |
|--------------------------------|----------------------------------------------------|
| `ExceedsSingleTransferMax`     | Transaction exceeds the single transfer maximum    |
| `ExceedsDailyTransferLimit`    | Transaction would exceed the daily volume limit    |
| `AddressSanctioned`            | Address is on the sanctions list                   |
| `HoldPeriodNotElapsed`         | Required hold period has not passed                |
| `ZeroAddress`                  | Zero address provided where not allowed            |

---

## BatchTransferHelper.sol

**133 lines** | Utility contract for validating and hashing batch transfers.

### Struct

```solidity
struct TransferItem {
    address recipient;
    address token;
    uint256 amount;
    string[] flags;
}
```

| Field     | Type      | Description                                    |
|-----------|-----------|------------------------------------------------|
| recipient | address   | Destination address for the transfer           |
| token     | address   | ERC20 token address to transfer                |
| amount    | uint256   | Amount of tokens to transfer                   |
| flags     | string[]  | Compliance flags (e.g., "KYC", "ACCREDITED")  |

### Constants

| Constant              | Type    | Description                                      |
|-----------------------|---------|--------------------------------------------------|
| TRANSFER_ITEM_TYPEHASH| bytes32 | EIP-712 type hash for a single TransferItem      |
| BATCH_TYPEHASH        | bytes32 | EIP-712 type hash for a batch of TransferItems   |

### Functions

#### validateBatch

```solidity
function validateBatch(TransferItem[] calldata items)
```

Validate an array of transfer items against compliance rules. Checks each item's recipient, token approval status, amount, and flags.

| Parameter | Type              | Description                        |
|-----------|-------------------|------------------------------------|
| items     | TransferItem[]    | Array of transfer items to validate|

---

#### getBatchHash

```solidity
function getBatchHash(
    TransferItem[] calldata items,
    address sender,
    uint256 timestamp
)
```

Compute the EIP-712 compatible hash of a batch transfer for signature verification.

| Parameter | Type           | Description                            |
|-----------|----------------|----------------------------------------|
| items     | TransferItem[] | Array of transfer items                |
| sender    | address        | Address initiating the batch transfer  |
| timestamp | uint256        | Timestamp of the batch operation       |

---

## SimpleToken.sol

ERC20 token with ERC-2612 `permit` support, used as collateral in prediction markets.

### Inheritance

```
ERC20, ERC20Permit
```

### Features

- Standard ERC20 functionality (transfer, approve, transferFrom)
- ERC-2612 gasless approvals via `permit(owner, spender, value, deadline, v, r, s)`
- Used as the collateral token for market operations (e.g., mock USDC in testing)
