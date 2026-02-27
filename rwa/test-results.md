# Test Results

Comprehensive test results for the BlindOracle RWA Stock Prediction Markets contracts. All tests pass across three test suites with a total of 105 tests.

---

## Table of Contents

- [Summary](#summary)
- [Test Suites](#test-suites)
  - [CompliancePolicyRules.t.sol (44 tests)](#compliancepolicyruletsol-44-tests)
  - [RWAPredictionMarket.t.sol (41 tests)](#rwapredictionmarketsol-41-tests)
  - [RWAForkIntegration.t.sol (20 tests)](#rwaforkintegrationtsol-20-tests)
- [On-Chain Fork Validation](#on-chain-fork-validation)
- [Gas Benchmarks](#gas-benchmarks)
- [Test Commands](#test-commands)

---

## Summary

| Metric             | Value                                    |
|--------------------|------------------------------------------|
| Total Tests        | 105                                      |
| Passing            | 105                                      |
| Failing            | 0                                        |
| Test Suites        | 3                                        |
| Fork Test Duration | 1.76s                                    |
| Chain Validated    | Robinhood Chain testnet (ID: 46630)      |

---

## Test Suites

### CompliancePolicyRules.t.sol (44 tests)

Tests for the ACE compliance policy engine covering sanctions, volume limits, hold periods, pausing, batch operations, and event emissions.

| #  | Test Name                                              | Category    | Status |
|----|--------------------------------------------------------|-------------|--------|
| 1  | test_constructor_sets_parameters                       | Setup       | PASS   |
| 2  | test_constructor_zero_owner_reverts                    | Setup       | PASS   |
| 3  | test_addSanctionedAddress                              | Sanctions   | PASS   |
| 4  | test_addSanctionedAddress_zero_reverts                 | Sanctions   | PASS   |
| 5  | test_addSanctionedAddress_duplicate                    | Sanctions   | PASS   |
| 6  | test_removeSanctionedAddress                           | Sanctions   | PASS   |
| 7  | test_removeSanctionedAddress_not_found                 | Sanctions   | PASS   |
| 8  | test_sanctioned_deposit_reverts                        | Sanctions   | PASS   |
| 9  | test_sanctioned_withdraw_reverts                       | Sanctions   | PASS   |
| 10 | test_sanctioned_private_transfer_reverts               | Sanctions   | PASS   |
| 11 | test_deposit_within_single_max                         | Limits      | PASS   |
| 12 | test_deposit_exceeds_single_max_reverts                | Limits      | PASS   |
| 13 | test_deposit_within_daily_limit                        | Limits      | PASS   |
| 14 | test_deposit_exceeds_daily_limit_reverts               | Limits      | PASS   |
| 15 | test_daily_limit_multiple_deposits                     | Limits      | PASS   |
| 16 | test_daily_limit_reset_at_midnight                     | Limits      | PASS   |
| 17 | test_remainingDailyVolume_fresh_day                    | Limits      | PASS   |
| 18 | test_remainingDailyVolume_partial_used                 | Limits      | PASS   |
| 19 | test_remainingDailyVolume_fully_used                   | Limits      | PASS   |
| 20 | test_withdraw_within_limits                            | Limits      | PASS   |
| 21 | test_withdraw_exceeds_single_max_reverts               | Limits      | PASS   |
| 22 | test_withdraw_exceeds_daily_limit_reverts              | Limits      | PASS   |
| 23 | test_holdPeriod_not_elapsed_reverts                    | Hold        | PASS   |
| 24 | test_holdPeriod_elapsed_allows_withdraw                | Hold        | PASS   |
| 25 | test_holdPeriod_exact_boundary                         | Hold        | PASS   |
| 26 | test_isHoldPeriodElapsed_true                          | Hold        | PASS   |
| 27 | test_isHoldPeriodElapsed_false                         | Hold        | PASS   |
| 28 | test_pause_blocks_deposits                             | Pause       | PASS   |
| 29 | test_pause_blocks_withdrawals                          | Pause       | PASS   |
| 30 | test_unpause_restores_operations                       | Pause       | PASS   |
| 31 | test_pause_only_owner                                  | Pause       | PASS   |
| 32 | test_unpause_only_owner                                | Pause       | PASS   |
| 33 | test_batch_validate_all_valid                          | Batch       | PASS   |
| 34 | test_batch_validate_zero_recipient_reverts             | Batch       | PASS   |
| 35 | test_batch_validate_zero_amount_reverts                | Batch       | PASS   |
| 36 | test_batch_validate_unapproved_token_reverts           | Batch       | PASS   |
| 37 | test_batch_hash_deterministic                          | Batch       | PASS   |
| 38 | test_batch_hash_different_inputs                       | Batch       | PASS   |
| 39 | test_event_DailyTransferLimitUpdated                   | Events      | PASS   |
| 40 | test_event_SingleTransferMaxUpdated                    | Events      | PASS   |
| 41 | test_event_HoldPeriodUpdated                           | Events      | PASS   |
| 42 | test_event_AddressSanctioned_Added                     | Events      | PASS   |
| 43 | test_event_AddressSanctioned_Removed                   | Events      | PASS   |
| 44 | test_event_DepositRecorded                             | Events      | PASS   |

**Category Breakdown:**

| Category   | Count | Status   |
|------------|-------|----------|
| Setup      | 2     | All PASS |
| Sanctions  | 8     | All PASS |
| Limits     | 11    | All PASS |
| Hold       | 5     | All PASS |
| Pause      | 5     | All PASS |
| Batch      | 6     | All PASS |
| Events     | 7     | All PASS |

---

### RWAPredictionMarket.t.sol (41 tests)

Tests for the core prediction market contract covering DataStream integration, factory deployment, trading mechanics, resolution, payouts, and view functions.

| #  | Test Name                                              | Category     | Status |
|----|--------------------------------------------------------|--------------|--------|
| 1  | test_dataStream_constructor                            | DataStream   | PASS   |
| 2  | test_dataStream_registerFeed                           | DataStream   | PASS   |
| 3  | test_dataStream_deregisterFeed                         | DataStream   | PASS   |
| 4  | test_dataStream_verifyAndStore                         | DataStream   | PASS   |
| 5  | test_dataStream_stalePrice_reverts                     | DataStream   | PASS   |
| 6  | test_dataStream_unregistered_feed_reverts              | DataStream   | PASS   |
| 7  | test_dataStream_invalidPrice_reverts                   | DataStream   | PASS   |
| 8  | test_dataStream_getLatestPrice                         | DataStream   | PASS   |
| 9  | test_dataStream_getFullPriceData                       | DataStream   | PASS   |
| 10 | test_dataStream_isPriceFresh                           | DataStream   | PASS   |
| 11 | test_dataStream_feedCount                              | DataStream   | PASS   |
| 12 | test_factory_constructor                               | Factory      | PASS   |
| 13 | test_factory_createMarket                              | Factory      | PASS   |
| 14 | test_factory_createMarket_duplicate_reverts            | Factory      | PASS   |
| 15 | test_factory_approveCollateral                         | Factory      | PASS   |
| 16 | test_factory_revokeCollateral                          | Factory      | PASS   |
| 17 | test_factory_unapproved_collateral_reverts             | Factory      | PASS   |
| 18 | test_factory_getMarketsByFeed                          | Factory      | PASS   |
| 19 | test_factory_getMarketPage                             | Factory      | PASS   |
| 20 | test_factory_marketId_derivation                       | Factory      | PASS   |
| 21 | test_buyShares_yes                                     | Trading      | PASS   |
| 22 | test_buyShares_no                                      | Trading      | PASS   |
| 23 | test_buyShares_zero_reverts                            | Trading      | PASS   |
| 24 | test_buyShares_after_expiry_reverts                    | Trading      | PASS   |
| 25 | test_sellShares_yes                                    | Trading      | PASS   |
| 26 | test_sellShares_no                                     | Trading      | PASS   |
| 27 | test_sellShares_insufficient_reverts                   | Trading      | PASS   |
| 28 | test_sellShares_platform_fee_deducted                  | Trading      | PASS   |
| 29 | test_resolve_yes_wins                                  | Resolution   | PASS   |
| 30 | test_resolve_no_wins                                   | Resolution   | PASS   |
| 31 | test_resolve_before_expiry_reverts                     | Resolution   | PASS   |
| 32 | test_resolve_already_resolved_reverts                  | Resolution   | PASS   |
| 33 | test_emergencyResolve                                  | Resolution   | PASS   |
| 34 | test_emergencyResolve_non_owner_reverts                | Resolution   | PASS   |
| 35 | test_claimWinnings_proportional                        | Payouts      | PASS   |
| 36 | test_claimWinnings_not_resolved_reverts                | Payouts      | PASS   |
| 37 | test_claimWinnings_no_shares_reverts                   | Payouts      | PASS   |
| 38 | test_withdrawFees                                      | Payouts      | PASS   |
| 39 | test_getMarketStatus                                   | Views        | PASS   |
| 40 | test_getShareBalances                                  | Views        | PASS   |
| 41 | test_getMarketSummary                                  | Views        | PASS   |

**Category Breakdown:**

| Category   | Count | Status   |
|------------|-------|----------|
| DataStream | 11    | All PASS |
| Factory    | 9     | All PASS |
| Trading    | 8     | All PASS |
| Resolution | 6     | All PASS |
| Payouts    | 4     | All PASS |
| Views      | 3     | All PASS |

---

### RWAForkIntegration.t.sol (20 tests)

Integration tests run against a live fork of Robinhood Chain testnet, validating real chain environment, deployment, factory operations, full market lifecycle, multi-user scenarios, emergency flows, oracle integration, edge cases, and gas usage.

| #  | Test Name                                              | Category     | Status |
|----|--------------------------------------------------------|--------------|--------|
| 1  | test_fork_chainId                                      | Chain Env    | PASS   |
| 2  | test_fork_blockNumber                                  | Chain Env    | PASS   |
| 3  | test_fork_tokenContracts_exist                         | Chain Env    | PASS   |
| 4  | test_fork_deploy_dataStreamConsumer                    | Deployment   | PASS   |
| 5  | test_fork_deploy_factory                               | Deployment   | PASS   |
| 6  | test_fork_deploy_full_stack                            | Deployment   | PASS   |
| 7  | test_fork_factory_createMarket                         | Factory      | PASS   |
| 8  | test_fork_factory_multipleMarkets                      | Factory      | PASS   |
| 9  | test_fork_factory_pagination                           | Factory      | PASS   |
| 10 | test_fork_fullLifecycle_yesWins                        | Lifecycle    | PASS   |
| 11 | test_fork_fullLifecycle_noWins                         | Lifecycle    | PASS   |
| 12 | test_fork_multiUser_trading                            | Multi-User   | PASS   |
| 13 | test_fork_multiUser_proportionalPayouts                | Multi-User   | PASS   |
| 14 | test_fork_trading_buyAndSell                           | Trading      | PASS   |
| 15 | test_fork_trading_platformFeeAccumulation              | Trading      | PASS   |
| 16 | test_fork_emergencyResolve                             | Emergency    | PASS   |
| 17 | test_fork_emergencyResolve_afterExpiry                 | Emergency    | PASS   |
| 18 | test_fork_oracle_priceVerification                     | Oracle       | PASS   |
| 19 | test_fork_edgeCase_resolveAtExactExpiry                | Edge Cases   | PASS   |
| 20 | test_fork_gas_benchmarks                               | Gas          | PASS   |

**Category Breakdown:**

| Category   | Count | Status   |
|------------|-------|----------|
| Chain Env  | 3     | All PASS |
| Deployment | 3     | All PASS |
| Factory    | 3     | All PASS |
| Lifecycle  | 2     | All PASS |
| Multi-User | 2     | All PASS |
| Trading    | 2     | All PASS |
| Emergency  | 2     | All PASS |
| Oracle     | 1     | All PASS |
| Edge Cases | 1     | All PASS |
| Gas        | 1     | All PASS |

---

## On-Chain Fork Validation

The fork integration tests validated against the live Robinhood Chain testnet state:

| Validation                  | Expected                  | Actual                    | Status |
|-----------------------------|---------------------------|---------------------------|--------|
| Chain ID                    | 46630                     | 46630                     | PASS   |
| Block Number                | >= 5,226,496              | 5,226,496                 | PASS   |
| TSLA contract bytecode size | > 0                       | 283 bytes                 | PASS   |
| AMZN contract bytecode size | > 0                       | 283 bytes                 | PASS   |
| PLTR contract bytecode size | > 0                       | 283 bytes                 | PASS   |

### Verified Token Contracts

| Token | Address                                        | Bytecode Size | On-Chain |
|-------|------------------------------------------------|---------------|----------|
| TSLA  | `0xC9f9028bF3E2e3c5cB5594cF1F57b2053DBd4E`    | 283 bytes     | Verified |
| AMZN  | `0x5884eCCB84D6BEf77E5df8A5990b3a31fC09E02`   | 283 bytes     | Verified |
| PLTR  | `0x1FBE999BCF2912cE49c72d50dc8f36DA2b8298d0`   | 283 bytes     | Verified |

All three tokenized stock contracts exist on-chain with matching bytecode sizes (283 bytes each), confirming they are proxy contracts pointing to a shared implementation.

---

## Gas Benchmarks

Gas usage measured during fork integration tests on Robinhood Chain:

| Operation       | Gas Used   | Description                                         |
|-----------------|------------|-----------------------------------------------------|
| `createMarket`  | 1,705,471  | Deploy new RWAPredictionMarket via factory           |
| `buyShares`     | 104,949    | Purchase YES or NO shares with collateral deposit    |
| `resolve`       | 47,338     | Resolve market using DataStreamConsumer oracle price |
| `claimWinnings` | 34,125     | Claim proportional winnings after resolution         |

### Gas Cost Analysis

At typical Robinhood Chain gas prices (Arbitrum Orbit L2 with low fees):

| Operation       | Gas Used   | Estimated Cost (at 0.1 gwei) |
|-----------------|------------|------------------------------|
| `createMarket`  | 1,705,471  | ~0.00017 ETH                 |
| `buyShares`     | 104,949    | ~0.00001 ETH                 |
| `resolve`       | 47,338     | ~0.000005 ETH                |
| `claimWinnings` | 34,125     | ~0.000003 ETH                |

Market creation is the most gas-intensive operation (deploying a new contract), while user-facing operations (trading, claiming) are efficient for an L2 environment.

---

## Test Commands

### Run All Tests (Local)

```bash
forge test
```

### Run All Tests with Verbosity

```bash
forge test -vv
```

### Run Specific Test Suite

```bash
# Compliance tests only
forge test --match-contract CompliancePolicyRulesTest

# Market tests only
forge test --match-contract RWAPredictionMarketTest

# Fork integration tests only
forge test --match-contract RWAForkIntegrationTest
```

### Run Fork Tests Against Live Robinhood Chain

```bash
forge test --fork-url https://rpc.testnet.chain.robinhood.com -vv
```

### Run a Single Test

```bash
forge test --match-test test_fork_fullLifecycle_yesWins -vvvv
```

### Gas Report

```bash
forge test --gas-report
```

### Test Coverage

```bash
forge coverage
```

---

## Performance

| Metric                     | Value    |
|----------------------------|----------|
| Full suite (local)         | < 1s     |
| Full suite (fork)          | 1.76s    |
| Compilation time           | ~3s      |
| Total test assertions      | 500+     |
| Fuzz runs (where applied)  | 256      |
