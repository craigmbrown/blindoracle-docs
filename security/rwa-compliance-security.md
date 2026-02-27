# RWA Markets Security & Compliance Model

> Security architecture, threat model, and compliance enforcement for BlindOracle's RWA prediction markets on Robinhood Chain.

---

## Table of Contents

- [Security Architecture](#security-architecture)
- [Security Layers](#security-layers)
- [Threat Model](#threat-model)
- [Access Control Matrix](#access-control-matrix)
- [ACE Policy Integration](#ace-policy-integration)
- [Emergency Procedures](#emergency-procedures)
- [Test Coverage](#test-coverage)
- [Planned Audits](#planned-audits)
- [Incident Response](#incident-response)

---

## Security Architecture

The RWA prediction market system operates on Robinhood Chain, which inherits Arbitrum's security model while adding its own compliance requirements for tokenized securities. BlindOracle's contracts enforce four independent layers of security, each addressing different threat categories.

The fundamental design principle: **no single layer failure should compromise user funds or market integrity.** If the policy engine goes down, reentrancy guards still protect. If reentrancy is somehow bypassed, the fixed-price model limits economic damage. If all on-chain protections fail, the owner can emergency-resolve and the L2 sequencer provides ordering guarantees.

```
+--------------------------------------------------------------+
|                     Robinhood Chain (L2)                      |
|  Sequencer ordering | L1 finality | Native compliance hooks  |
+--------------------------------------------------------------+
        |                    |                    |
+----------------+  +------------------+  +----------------+
| ACE Policy     |  | OpenZeppelin     |  | Ownable        |
| Protected      |  | ReentrancyGuard  |  | Access Control |
| (Chainlink)    |  | (per-function)   |  | (admin ops)    |
+----------------+  +------------------+  +----------------+
        |                    |                    |
        +--------------------+--------------------+
                             |
                   +-------------------+
                   | RWAPrediction-    |
                   | Market Contract   |
                   | (user-facing)     |
                   +-------------------+
                             |
                   +-------------------+
                   | DataStream-       |
                   | Consumer          |
                   | (oracle layer)    |
                   +-------------------+
```

---

## Security Layers

### Layer 1: ACE PolicyProtected

The Chainlink ACE (Autonomous Compliance Engine) provides on-chain compliance enforcement. Every user-facing function that touches funds runs through the `runPolicy` modifier before executing.

```solidity
// Inherited by RWAPredictionMarket
abstract contract PolicyProtected {
    IPolicyEngine public policyEngine;

    modifier runPolicy() {
        if (address(policyEngine) != address(0)) {
            policyEngine.checkPolicy(msg.sender, msg.data);
        }
        _;
    }
}
```

**What the policy engine checks:**
- Caller identity against KYC/AML registries
- Transaction amount limits (per-tx and cumulative)
- Geographic restrictions
- Sanctioned address lists
- Custom compliance rules defined in `CompliancePolicyRules`

**Key property:** The policy engine is modular. Different jurisdictions can deploy different `CompliancePolicyRules` implementations. The market contract itself does not know or care about the specific rules -- it just calls `checkPolicy()` and reverts if the policy engine says no.

### Layer 2: CompliancePolicyRules

The specific rule set enforced by the policy engine. This is the contract that encodes the actual compliance logic.

```solidity
contract CompliancePolicyRules is IPolicyRules {
    function checkPolicy(address caller, bytes calldata data) external view {
        // Decode function selector from data
        bytes4 selector = bytes4(data[:4]);

        // Apply function-specific rules
        if (selector == RWAPredictionMarket.buyShares.selector) {
            _checkBuyRules(caller, data);
        } else if (selector == RWAPredictionMarket.claimWinnings.selector) {
            _checkClaimRules(caller);
        }
        // ... additional rules
    }
}
```

**Enforcement points:**
- `buyShares()` -- checks before any collateral transfer
- `sellShares()` -- checks before returning collateral
- `claimWinnings()` -- checks before payout distribution

### Layer 3: OpenZeppelin ReentrancyGuard

The `nonReentrant` modifier prevents reentrancy attacks on all functions that transfer tokens.

```solidity
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract RWAPredictionMarket is PolicyProtected, ReentrancyGuard, Ownable {
    function buyShares(bool isYes, uint256 amount) external runPolicy nonReentrant {
        // Safe: cannot re-enter during token transfer
    }

    function sellShares(bool isYes, uint256 amount) external runPolicy nonReentrant {
        // Safe: cannot re-enter during token transfer
    }

    function claimWinnings() external runPolicy nonReentrant {
        // Safe: cannot re-enter during token transfer
    }
}
```

**Protected functions:** `buyShares`, `sellShares`, `claimWinnings`, `withdrawFees`

### Layer 4: Ownable Access Control

Administrative functions are restricted to the contract owner using OpenZeppelin's `Ownable`.

```solidity
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

// Only owner can:
function emergencyResolve(bool _yesWins, string calldata reason) external onlyOwner { ... }
function withdrawFees(address to) external onlyOwner { ... }
function setPolicyEngine(address engine) external onlyOwner { ... }
```

---

## Threat Model

### Attack Surface Analysis

| Threat | Severity | Mitigation | Contract | Notes |
|--------|----------|------------|----------|-------|
| Front-running share purchases | Medium | L2 sequencer ordering provides FIFO guarantees; fixed 1:1 pricing eliminates MEV from price slippage | Robinhood Chain (L2) | Unlike AMM-based markets, fixed pricing means front-running yields no economic advantage |
| Reentrancy on token transfers | Critical | OpenZeppelin `ReentrancyGuard` on all fund-moving functions; checks-effects-interactions pattern | RWAPredictionMarket | `nonReentrant` modifier applied to `buyShares`, `sellShares`, `claimWinnings`, `withdrawFees` |
| Oracle price manipulation | Critical | Data Streams DON consensus (multiple nodes must agree); staleness threshold rejects old data; `verifyAndStore` validates report structure | DataStreamConsumer | An attacker would need to compromise a majority of DON nodes to manipulate a price |
| Stale oracle data used for resolution | High | Configurable staleness threshold (default 3600s); `isPriceFresh()` check available pre-resolution; `StalePrice` revert on expired data | DataStreamConsumer | Resolver should call `isPriceFresh()` before submitting report |
| Compliance evasion (sanctioned users) | High | `runPolicy` modifier on all user-facing fund operations; policy engine called before any state changes | PolicyProtected | Even if a user bypasses the frontend, the contract-level check blocks them |
| Unauthorized admin actions | High | `Ownable` restricts `emergencyResolve`, `withdrawFees`, `setPolicyEngine`, `setDataStreamConsumer`, `createMarket` | All contracts | Owner key management is critical -- see [Emergency Procedures](#emergency-procedures) |
| Market manipulation via wash trading | Medium | 1-share-1-USDC fixed pricing eliminates price manipulation; policy engine can enforce per-address limits | RWAPredictionMarket | No AMM curve means wash trading does not move prices |
| Collateral token rug pull | Medium | Collateral whitelist on factory; only owner-approved tokens accepted; USDC is primary collateral | RWAMarketFactory | `approveCollateral`/`revokeCollateral` managed by owner |
| Replay attacks with old reports | Medium | `expiresAt` field in PremiumReport; `validFromTimestamp` enforced; staleness check | DataStreamConsumer | Each report has a bounded validity window |
| Integer overflow/underflow | Low | Solidity 0.8.24 built-in overflow checks; no unchecked blocks in critical math | All contracts | Compiler-level protection |
| Denial of service on resolution | Low | `resolve()` is permissionless -- anyone can call it; no single party can block resolution | RWAPredictionMarket | If one resolver is blocked, any other address can resolve |
| Flash loan attacks | Low | Fixed 1:1 pricing model; no AMM pool to drain; no price oracle that reads on-chain reserves | RWAPredictionMarket | Flash loans offer no advantage in a fixed-price model |

---

## Access Control Matrix

Comprehensive function-level permissions across all contracts.

### RWAMarketFactory

| Function | Owner | User | Anyone | Modifiers |
|----------|:-----:|:----:|:------:|-----------|
| `createMarket` | yes | no | no | `onlyOwner` |
| `approveCollateral` | yes | no | no | `onlyOwner` |
| `revokeCollateral` | yes | no | no | `onlyOwner` |
| `setPolicyEngine` | yes | no | no | `onlyOwner` |
| `setDataStreamConsumer` | yes | no | no | `onlyOwner` |
| `getMarket` | yes | yes | yes | `view` |
| `getMarketPage` | yes | yes | yes | `view` |
| `getMarketsByFeed` | yes | yes | yes | `view` |
| `getMarketCount` | yes | yes | yes | `view` |

### RWAPredictionMarket

| Function | Owner | User (passes policy) | User (fails policy) | Anyone | Modifiers |
|----------|:-----:|:--------------------:|:--------------------:|:------:|-----------|
| `buyShares` | yes | yes | no | no | `runPolicy`, `nonReentrant` |
| `sellShares` | yes | yes | no | no | `runPolicy`, `nonReentrant` |
| `claimWinnings` | yes | yes | no | no | `runPolicy`, `nonReentrant` |
| `resolve` | yes | no | no | yes (post-expiration) | none |
| `emergencyResolve` | yes | no | no | no | `onlyOwner` |
| `withdrawFees` | yes | no | no | no | `onlyOwner` |
| `getMarketStatus` | yes | yes | yes | yes | `view` |
| `getShareBalances` | yes | yes | yes | yes | `view` |
| `getMarketSummary` | yes | yes | yes | yes | `view` |

### DataStreamConsumer

| Function | Owner | User | Anyone | Modifiers |
|----------|:-----:|:----:|:------:|-----------|
| `verifyAndStore` | yes | yes | yes | none |
| `registerFeed` | yes | no | no | `onlyOwner` |
| `deregisterFeed` | yes | no | no | `onlyOwner` |
| `setStalenessThreshold` | yes | no | no | `onlyOwner` |
| `getLatestPrice` | yes | yes | yes | `view` |
| `getFullPriceData` | yes | yes | yes | `view` |
| `isPriceFresh` | yes | yes | yes | `view` |

**Key observations:**
- All fund-moving functions require both `runPolicy` and `nonReentrant`
- `resolve()` is intentionally permissionless (post-expiration) -- this prevents the operator from blocking resolution
- `verifyAndStore()` is permissionless -- anyone can submit valid oracle data
- All view functions are unrestricted

---

## ACE Policy Integration

### How PolicyProtected Works

The ACE integration follows a simple pattern: the `runPolicy` modifier calls the external policy engine before the function body executes. If the policy engine reverts, the entire transaction reverts.

```
User calls buyShares(true, 100)
    |
    v
runPolicy modifier fires
    |
    v
policyEngine.checkPolicy(msg.sender, msg.data)
    |
    +-- Policy engine decodes msg.data
    |   +-- Extracts function selector: buyShares
    |   +-- Extracts parameters: isYes=true, amount=100
    |   +-- Checks caller against compliance rules
    |
    +-- PASS: continue to buyShares logic
    |
    +-- FAIL: revert entire transaction
```

### CompliancePolicyRules Configuration

The compliance rules contract supports multiple rule categories:

```solidity
struct PolicyConfig {
    bool kycRequired;           // Require KYC verification
    bool amlCheckRequired;      // Run AML screening
    uint256 maxTransactionSize; // Per-transaction limit
    uint256 maxDailyVolume;     // Per-address daily limit
    bool geoRestricted;         // Enable geographic restrictions
    bytes32[] blockedRegions;   // Blocked jurisdiction codes
    address sanctionsList;      // Address of sanctions oracle
}
```

### Upgrading Compliance Rules

The policy engine can be updated without redeploying markets:

```bash
# Deploy new compliance rules
forge create CompliancePolicyRulesV2 --rpc-url $RPC_URL --private-key $PK

# Update factory (affects new markets only)
cast send $FACTORY "setPolicyEngine(address)" $NEW_ENGINE --rpc-url $RPC_URL --private-key $PK
```

**Note:** Existing markets retain their original policy engine reference. To update compliance on a live market, the market contract must expose a `setPolicyEngine()` function (owner-only).

---

## Emergency Procedures

### Emergency Resolution

When oracle data is unavailable, stale beyond recovery, or demonstrably incorrect, the owner can force-resolve a market.

```bash
# Emergency resolve with documented reason
cast send $MARKET "emergencyResolve(bool,string)" \
  true \
  "Data Streams feed offline for 48h due to provider outage. Resolving based on NYSE closing price from Bloomberg terminal at 2026-03-31T20:00:00Z. TSLA closed at $312.45, above $300 strike." \
  --rpc-url $RPC_URL --private-key $PK
```

**Emergency resolution checklist:**
1. Document the reason for emergency resolution (on-chain in the reason string)
2. Cross-reference with at least 2 independent off-chain price sources
3. Notify users via frontend banner and social channels before executing
4. Record the emergency resolution in the incident log
5. Post-incident review within 48 hours

### Emergency Resolution Criteria

Emergency resolution should only be used when:

| Scenario | Action | Example |
|----------|--------|---------|
| Oracle feed offline > 24h past expiration | Emergency resolve using off-chain data | Data Streams provider outage |
| Oracle reports clearly wrong price | Emergency resolve using correct data | Reported TSLA at $3 instead of $300 |
| Smart contract bug discovered | Emergency resolve to protect user funds | Logic error in resolution |
| Regulatory order | Emergency resolve per legal requirement | Court order to halt market |

### Pause Mechanism

If a critical vulnerability is discovered mid-market, the owner can prevent new trades by updating the policy engine to reject all calls:

```solidity
// Emergency policy that blocks everything
contract EmergencyPausePolicy is IPolicyRules {
    function checkPolicy(address, bytes calldata) external pure {
        revert("Market paused - emergency");
    }
}
```

Deploy and set as the policy engine to effectively pause the market without modifying the market contract itself.

---

## Test Coverage

### Test Suite Summary

| Category | Tests | Status | Description |
|----------|------:|:------:|-------------|
| Unit: RWAMarketFactory | 18 | PASS | Market creation, collateral mgmt, pagination |
| Unit: RWAPredictionMarket | 32 | PASS | Buy/sell, resolution, claims, edge cases |
| Unit: DataStreamConsumer | 22 | PASS | Report decoding, staleness, feed management |
| Unit: CompliancePolicyRules | 15 | PASS | Policy enforcement, rule configuration |
| Integration: Full lifecycle | 8 | PASS | Create -> trade -> resolve -> claim flows |
| Integration: Multi-market | 5 | PASS | Multiple concurrent markets, shared oracle |
| Fork: Robinhood Chain | 3 | PASS | On-chain fork validation against live state |
| Edge: Boundary conditions | 2 | PASS | Zero amounts, max uint256, exact strike |
| **Total** | **105** | **PASS** | **100% passing** |

### Running the Test Suite

```bash
# Full test suite
forge test -vv

# With gas reporting
forge test --gas-report

# Specific test file
forge test --match-path test/RWAPredictionMarket.t.sol -vvv

# Fork tests against live Robinhood Chain
forge test --match-path test/fork/ --fork-url https://robin-rpc.lavish.dev -vv
```

### Key Test Scenarios

**Resolution correctness:**
- Price exactly at strike (boundary): YES wins when `isAbove == true`
- Price 1 wei below strike: NO wins when `isAbove == true`
- Price 1 wei above strike: NO wins when `isAbove == false`
- Emergency resolution overrides oracle

**Reentrancy protection:**
- Malicious ERC-20 callback during `buyShares` -- reverts
- Malicious ERC-20 callback during `claimWinnings` -- reverts

**Policy enforcement:**
- Blocked address attempts `buyShares` -- reverts with policy error
- Same address passes after being unblocked
- Policy engine set to address(0) -- all calls pass (no compliance)

**Oracle staleness:**
- Fresh report: accepted
- Report at exact threshold boundary: accepted
- Report 1 second past threshold: rejected with `StalePrice`

### Fork Test Validation

The fork tests deploy the full system against a fork of live Robinhood Chain state to verify:
- Contract deployment succeeds with live chain gas parameters
- Collateral token (USDC) integration works with the real token contract
- Gas costs remain under $0.001 per transaction
- Chain ID 46630 is correctly recognized

---

## Planned Audits

### Pre-Mainnet Audit Plan

| Phase | Timeline | Scope | Auditor |
|-------|----------|-------|---------|
| Internal review | Complete | All contracts, 105 tests | BlindOracle team |
| Static analysis | Complete | Slither, Mythril, Aderyn | Automated tooling |
| Formal verification | Pre-mainnet | Critical paths (resolution, claims) | TBD |
| External audit | Pre-mainnet | Full contract system | TBD (targeting Chainlink-recommended auditors) |
| Bug bounty | Post-audit | Public bounty program | Immunefi (planned) |

### Static Analysis Results

```bash
# Slither analysis
slither . --config slither.config.json

# Current findings:
# - 0 High severity
# - 0 Medium severity
# - 3 Low severity (informational: naming conventions, unused return values)
# - 12 Informational
```

### Known Limitations

These are documented design decisions, not vulnerabilities:

1. **Owner centralization**: The owner can `emergencyResolve` and `withdrawFees`. This is intentional for the current phase. Future versions will migrate to a multi-sig or DAO governance.

2. **Policy engine single point**: If the policy engine contract is compromised, all policy-protected functions are affected. Mitigation: the policy engine is upgradeable by the owner.

3. **Fixed pricing model**: The 1-share-1-USDC model is simple and manipulation-resistant but does not support price discovery. This is a deliberate trade-off for security.

4. **Oracle dependency**: Markets cannot resolve without oracle data (except via emergency resolution). If Chainlink Data Streams is permanently unavailable for a feed, the owner must emergency-resolve.

---

## Incident Response

### Severity Levels

| Level | Description | Response Time | Example |
|-------|-------------|--------------|---------|
| P0 - Critical | Active exploit, funds at risk | Immediate (< 1 hour) | Reentrancy bypass, oracle manipulation |
| P1 - High | Vulnerability discovered, no active exploit | < 4 hours | Potential attack vector in untested path |
| P2 - Medium | Non-critical bug affecting UX | < 24 hours | Incorrect event emission, view function error |
| P3 - Low | Minor issue, no security impact | < 1 week | Gas optimization, code style |

### P0 Response Playbook

1. **Contain**: Deploy `EmergencyPausePolicy` to halt all user-facing functions
2. **Assess**: Determine scope of compromise (which markets, how much funds)
3. **Communicate**: Notify users via all channels (frontend, Discord, Twitter)
4. **Remediate**: Emergency-resolve affected markets if needed
5. **Fix**: Deploy patched contracts
6. **Restore**: Update policy engine to resume operations
7. **Review**: Post-incident report within 48 hours

### Contact

Security issues: security@blindoracle.xyz (planned) or via GitHub Security Advisories on the repository.

---

*Security model version: 1.0 | Last updated: 2026-02-27 | Chain: Robinhood Chain (46630) | Compiler: Solidity 0.8.24*
