# ACE Compliance Documentation

This document describes how the BlindOracle RWA Stock Prediction Markets integrate with the Chainlink ACE (Asset Compliance Engine) framework to enforce on-chain compliance for all market operations.

---

## Table of Contents

- [Overview](#overview)
- [PolicyProtected Modifier](#policyprotected-modifier)
- [CompliancePolicyRules Engine](#compliancepolicyrules-engine)
- [Batch Validation](#batch-validation)
- [Emergency Controls](#emergency-controls)
- [Compliance Flow Diagrams](#compliance-flow-diagrams)

---

## Overview

Chainlink ACE provides a modular compliance layer that intercepts function calls at the smart contract level. By inheriting `PolicyProtected` and applying the `runPolicy` modifier, prediction market functions automatically route through a configurable `PolicyEngine` before execution. This ensures that every trade, sale, and claim operation passes sanctions screening, volume limits, and hold period checks without requiring off-chain compliance infrastructure.

The ACE integration is imported from:

```solidity
import {PolicyProtected} from "chainlink-ace/packages/policy-management/src/core/PolicyProtected.sol";
```

---

## PolicyProtected Modifier

### How It Works

The `PolicyProtected` base contract exposes the `runPolicy` modifier. When applied to a function, the modifier calls the configured `PolicyEngine` contract before the function body executes. The PolicyEngine evaluates the caller, parameters, and current state against all registered policy rules. If any rule is violated, the transaction reverts.

### Protected Functions

The `runPolicy` modifier is applied to the following functions in `RWAPredictionMarket`:

| Function         | Modifier                        | What Is Checked                                       |
|------------------|---------------------------------|-------------------------------------------------------|
| `buyShares`      | `nonReentrant runPolicy`        | Sanctions, daily volume, single transfer max           |
| `sellShares`     | `nonReentrant runPolicy`        | Sanctions, daily volume, single transfer max           |
| `claimWinnings`  | `nonReentrant runPolicy`        | Sanctions, hold period, daily volume                   |

### Modifier Execution Order

```
User calls buyShares(isYes, amount)
    |
    v
[nonReentrant] -- Reentrancy lock acquired
    |
    v
[runPolicy] -- PolicyEngine.checkPolicy() called
    |           |
    |           +-- CompliancePolicyRules.checkDepositAllowed()
    |           |     |-- Check sanctions list
    |           |     |-- Check single transfer max
    |           |     |-- Check daily volume limit
    |           |     +-- Record volume consumed
    |           |
    |           +-- All checks pass? Continue : Revert
    |
    v
[Function body] -- buyShares logic executes
    |
    v
[nonReentrant] -- Reentrancy lock released
```

### Policy Engine Configuration

The PolicyEngine address is set during market contract deployment via the constructor parameter `policyEngine`. For the factory pattern, the factory passes its stored PolicyEngine address to each new market it deploys. The factory owner can update the engine for future deployments via `setPolicyEngine(address newEngine)`.

---

## CompliancePolicyRules Engine

The `CompliancePolicyRules` contract (309 lines) implements the concrete compliance logic that the ACE PolicyEngine evaluates. It inherits from `Ownable` and `Pausable`.

### Constructor

```solidity
constructor(
    address initialOwner,
    uint256 _dailyLimit,
    uint256 _singleMax,
    uint256 _holdPeriod
)
```

### Rule Categories

#### 1. Sanctions List

A mapping of addresses that are prohibited from all market interactions.

- **Check:** Every `checkDepositAllowed`, `checkWithdrawAllowed`, and `checkPrivateTransferAllowed` call verifies the caller is not sanctioned
- **Management:**
  - `addSanctionedAddress(address account)` -- add to the blocklist
  - `removeSanctionedAddress(address account)` -- remove from the blocklist
- **Error:** `AddressSanctioned` -- reverts if the caller is on the list
- **Events:** `AddressSanctioned_Added`, `AddressSanctioned_Removed`

#### 2. Daily Volume Limits

Per-address daily volume caps that reset at midnight UTC (00:00 UTC).

- **Check:** Each deposit or trade operation records the volume consumed and verifies it does not exceed the daily limit
- **Management:**
  - `setDailyTransferLimit(uint256 newLimit)` -- update the daily cap
  - `remainingDailyVolume(...)` -- query remaining allowance
- **Error:** `ExceedsDailyTransferLimit` -- reverts if the transaction would push the address over its daily limit
- **Events:** `DailyTransferLimitUpdated`, `DailyVolumeConsumed`

**Reset Mechanism:**

```
Day boundary detection:
    currentDay = block.timestamp / 86400
    if (currentDay > lastRecordedDay[user]):
        dailyVolumeUsed[user] = 0
        lastRecordedDay[user] = currentDay
```

#### 3. Single Transfer Maximum

A per-transaction cap that prevents any individual operation from exceeding a configured maximum.

- **Check:** Every deposit, withdrawal, and transfer amount is compared against the single transfer max
- **Management:**
  - `setSingleTransferMax(uint256 newMax)` -- update the cap
- **Error:** `ExceedsSingleTransferMax` -- reverts if the amount exceeds the maximum
- **Events:** `SingleTransferMaxUpdated`

#### 4. Hold Periods

A minimum time interval that must elapse between a deposit and a withdrawal or claim.

- **Check:** Withdrawal and claim operations verify that sufficient time has passed since the user's last deposit
- **Management:**
  - `setHoldPeriod(uint256 newPeriod)` -- update the hold duration (in seconds)
  - `isHoldPeriodElapsed(...)` -- query whether the hold period has passed
- **Error:** `HoldPeriodNotElapsed` -- reverts if the user attempts to withdraw too early
- **Events:** `HoldPeriodUpdated`, `DepositRecorded`

### Compliance Check Functions

| Function                       | Used By               | Checks                                          |
|--------------------------------|-----------------------|--------------------------------------------------|
| `checkDepositAllowed`          | `buyShares`           | Sanctions, single max, daily limit               |
| `checkWithdrawAllowed`         | `sellShares`, `claimWinnings` | Sanctions, single max, daily limit, hold period |
| `checkPrivateTransferAllowed`  | Future transfer ops   | Sanctions (both parties), single max, daily limit|

---

## Batch Validation

The `BatchTransferHelper` contract (133 lines) provides utilities for validating and hashing multiple transfer operations as a batch.

### TransferItem Struct

```solidity
struct TransferItem {
    address recipient;
    address token;
    uint256 amount;
    string[] flags;
}
```

The `flags` array carries compliance metadata (e.g., `"KYC"`, `"ACCREDITED"`) that policy rules can inspect during validation.

### Validation Flow

```
BatchTransferHelper.validateBatch(items)
    |
    +-- For each TransferItem:
    |     |-- Verify recipient != address(0)
    |     |-- Verify token is approved collateral
    |     |-- Verify amount > 0
    |     |-- Verify compliance flags are valid
    |     +-- Run per-item policy check
    |
    +-- All items valid? Return success : Revert
```

### Batch Hashing

For EIP-712 signature verification of batch operations:

```solidity
function getBatchHash(
    TransferItem[] calldata items,
    address sender,
    uint256 timestamp
) returns (bytes32)
```

Uses `TRANSFER_ITEM_TYPEHASH` and `BATCH_TYPEHASH` constants for structured data hashing, enabling off-chain signature generation and on-chain verification of approved batch transfers.

---

## Emergency Controls

### Pause Mechanism

`CompliancePolicyRules` inherits OpenZeppelin's `Pausable`, providing a global circuit breaker.

```
Owner calls pause()
    |
    v
All compliance-gated operations revert
    |
    (No buyShares, sellShares, or claimWinnings can execute)
    |
    v
Owner calls unpause()
    |
    v
Normal operations resume
```

- **pause()** -- `onlyOwner`, immediately halts all policy-gated operations
- **unpause()** -- `onlyOwner`, resumes normal operations

### Emergency Resolution

`RWAPredictionMarket` provides an owner-only emergency resolution path:

```solidity
function emergencyResolve(bool _yesWins, string calldata reason) external onlyOwner
```

This bypasses the oracle-based resolution flow and allows the owner to manually set the market outcome when:

- The Chainlink Data Streams oracle is unavailable
- Price data is stale beyond acceptable thresholds
- Exceptional market conditions require manual intervention

The `reason` parameter is emitted in the `EmergencyResolved` event for transparency and audit purposes.

---

## Compliance Flow Diagrams

### Deposit (buyShares) Compliance Flow

```
User                    RWAPredictionMarket         PolicyEngine         CompliancePolicyRules
  |                            |                        |                        |
  |--- buyShares(isYes, amt)-->|                        |                        |
  |                            |                        |                        |
  |                            |--- runPolicy --------->|                        |
  |                            |                        |                        |
  |                            |                        |--- checkDepositAllowed->|
  |                            |                        |                        |
  |                            |                        |                  [Check sanctions]
  |                            |                        |                        |
  |                            |                        |                  [Check amt <= singleMax]
  |                            |                        |                        |
  |                            |                        |                  [Check dailyUsed + amt
  |                            |                        |                        <= dailyLimit]
  |                            |                        |                        |
  |                            |                        |                  [Record volume]
  |                            |                        |                        |
  |                            |                        |<--- OK / Revert -------|
  |                            |                        |                        |
  |                            |<--- Policy passed -----|                        |
  |                            |                        |                        |
  |                            |  [Execute buyShares logic]                      |
  |                            |  [Transfer collateral from user]                |
  |                            |  [Mint shares to user]                          |
  |                            |                        |                        |
  |<--- SharesPurchased -------|                        |                        |
```

### Withdrawal (sellShares) Compliance Flow

```
User                    RWAPredictionMarket         PolicyEngine         CompliancePolicyRules
  |                            |                        |                        |
  |--- sellShares(isYes,amt)-->|                        |                        |
  |                            |                        |                        |
  |                            |--- runPolicy --------->|                        |
  |                            |                        |                        |
  |                            |                        |--- checkWithdrawAllowed>|
  |                            |                        |                        |
  |                            |                        |                  [Check sanctions]
  |                            |                        |                        |
  |                            |                        |                  [Check amt <= singleMax]
  |                            |                        |                        |
  |                            |                        |                  [Check dailyUsed + amt
  |                            |                        |                        <= dailyLimit]
  |                            |                        |                        |
  |                            |                        |                  [Check holdPeriod
  |                            |                        |                        elapsed since
  |                            |                        |                        last deposit]
  |                            |                        |                        |
  |                            |                        |<--- OK / Revert -------|
  |                            |                        |                        |
  |                            |<--- Policy passed -----|                        |
  |                            |                        |                        |
  |                            |  [Execute sellShares logic]                     |
  |                            |  [Deduct platform fee (1%)]                     |
  |                            |  [Burn shares from user]                        |
  |                            |  [Transfer collateral to user]                  |
  |                            |                        |                        |
  |<--- SharesSold ------------|                        |                        |
```

### Claim Winnings Compliance Flow

```
User                    RWAPredictionMarket         PolicyEngine         CompliancePolicyRules
  |                            |                        |                        |
  |--- claimWinnings() ------->|                        |                        |
  |                            |                        |                        |
  |                            |  [Verify MarketStatus == Resolved]              |
  |                            |  [Calculate proportional payout]                |
  |                            |                        |                        |
  |                            |--- runPolicy --------->|                        |
  |                            |                        |                        |
  |                            |                        |--- checkWithdrawAllowed>|
  |                            |                        |                        |
  |                            |                        |                  [Check sanctions]
  |                            |                        |                        |
  |                            |                        |                  [Check payout
  |                            |                        |                        <= singleMax]
  |                            |                        |                        |
  |                            |                        |                  [Check dailyUsed +
  |                            |                        |                        payout <= limit]
  |                            |                        |                        |
  |                            |                        |                  [Check holdPeriod]
  |                            |                        |                        |
  |                            |                        |<--- OK / Revert -------|
  |                            |                        |                        |
  |                            |<--- Policy passed -----|                        |
  |                            |                        |                        |
  |                            |  [Transfer winnings to user]                    |
  |                            |  [Mark shares as claimed]                       |
  |                            |                        |                        |
  |<--- WinningsClaimed -------|                        |                        |
```

---

## Configuration Reference

| Parameter            | Default       | Function to Update            | Description                         |
|----------------------|---------------|-------------------------------|-------------------------------------|
| Daily Volume Limit   | Set at deploy | `setDailyTransferLimit()`     | Max volume per address per day      |
| Single Transfer Max  | Set at deploy | `setSingleTransferMax()`      | Max amount per transaction          |
| Hold Period          | Set at deploy | `setHoldPeriod()`             | Seconds before withdrawal allowed   |
| Sanctions List       | Empty         | `addSanctionedAddress()`      | Blocked addresses                   |
| Pause State          | Unpaused      | `pause()` / `unpause()`       | Global circuit breaker              |
| PolicyEngine         | Set at deploy | `setPolicyEngine()` (factory) | ACE PolicyEngine contract address   |
