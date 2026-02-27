# RWA Markets: From Zero to Prediction Market in 5 Minutes

> Deploy a full RWA prediction market system locally, create a TSLA market, buy shares, resolve it, and claim winnings. No testnet tokens. No wallet setup. Just Foundry.

---

## Prerequisites

You need two things:

- **Foundry** (forge, cast, anvil): [Install guide](https://book.getfoundry.sh/getting-started/installation)
- **git**

Verify your install:

```bash
forge --version   # forge 0.2.0 or later
cast --version
anvil --version
```

---

## Step 1: Clone and Build

```bash
git clone https://github.com/craigmbrown/blindoracle-rwa-markets.git
cd blindoracle-rwa-markets
forge build
```

You should see:

```
[+] Compiling...
[+] Compiling 6 files with solc 0.8.24
[+] Solc 0.8.24 finished in 2.1s
Compiler run successful!
```

Six contracts compiled: `RWAMarketFactory`, `RWAPredictionMarket`, `DataStreamConsumer`, `CompliancePolicyRules`, `PolicyProtected`, and `MockCollateralToken`.

---

## Step 2: Run Tests

```bash
forge test
```

Expected output:

```
[PASS] testBuyYesShares() (gas: 156789)
[PASS] testBuyNoShares() (gas: 154321)
[PASS] testSellShares() (gas: 178456)
[PASS] testResolveAboveStrike() (gas: 234567)
[PASS] testResolveBelowStrike() (gas: 231234)
[PASS] testClaimWinnings() (gas: 189012)
[PASS] testEmergencyResolve() (gas: 145678)
...
Test result: ok. 105 passed; 0 failed; 0 skipped; finished in 3.2s
```

105 tests, all green. If any fail, check your Foundry version.

For more detail:

```bash
forge test -vvv          # Show stack traces
forge test --gas-report  # Show gas usage per function
```

---

## Step 3: Start Local Anvil

Open a new terminal and start a local Ethereum node configured with Robinhood Chain's chain ID:

```bash
anvil --chain-id 46630
```

Anvil gives you 10 pre-funded accounts. Note the first two private keys -- we will use them as the deployer (Alice) and a trader (Bob).

```
Available Accounts
==================
(0) 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)
(1) 0x70997970C51812dc3A010C7d01b50e0d17dc79C8 (10000 ETH)

Private Keys
==================
(0) 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
(1) 0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d
```

Leave this terminal running.

---

## Step 4: Deploy the System

In your original terminal:

```bash
forge script script/DeployRWAMarkets.s.sol:DeployRWAMarkets \
  --rpc-url http://localhost:8545 \
  --broadcast
```

The deploy script does everything in order:

1. Deploys `MockCollateralToken` (test USDC)
2. Deploys `DataStreamConsumer` with a 3600s staleness threshold
3. Deploys `CompliancePolicyRules`
4. Deploys `RWAMarketFactory` wired to the policy engine and oracle consumer
5. Approves MockCollateralToken as collateral
6. Registers the TSLA Data Streams feed
7. Creates a sample TSLA market: "Will TSLA be above $300 by [expiration]?"

Save the deployed addresses from the output:

```
== Deployed Contracts ==
MockCollateralToken: 0x5FbDB2315678afecb367f032d93F642f64180aa3
DataStreamConsumer:  0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
CompliancePolicyRules: 0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0
RWAMarketFactory:    0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9
TSLA Market:         0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9
```

Set environment variables for convenience (use your actual deployed addresses):

```bash
export RPC_URL=http://localhost:8545
export DEPLOYER_PK=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
export BOB_PK=0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d
export DEPLOYER=0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
export BOB=0x70997970C51812dc3A010C7d01b50e0d17dc79C8
export TOKEN=0x5FbDB2315678afecb367f032d93F642f64180aa3
export CONSUMER=0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
export FACTORY=0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9
export MARKET=0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9
```

---

## Step 5: Buy YES Shares

First, mint some test tokens and approve the market to spend them.

**Mint tokens for both accounts:**

```bash
# Mint 1000 tokens for deployer (Alice)
cast send $TOKEN "mint(address,uint256)" $DEPLOYER 1000000000 \
  --rpc-url $RPC_URL --private-key $DEPLOYER_PK

# Mint 1000 tokens for Bob
cast send $TOKEN "mint(address,uint256)" $BOB 1000000000 \
  --rpc-url $RPC_URL --private-key $DEPLOYER_PK
```

**Approve the market to spend tokens:**

```bash
# Alice approves
cast send $TOKEN "approve(address,uint256)" $MARKET 1000000000 \
  --rpc-url $RPC_URL --private-key $DEPLOYER_PK

# Bob approves
cast send $TOKEN "approve(address,uint256)" $MARKET 1000000000 \
  --rpc-url $RPC_URL --private-key $BOB_PK
```

**Alice buys 100 YES shares (she thinks TSLA will be above $300):**

```bash
cast send $MARKET "buyShares(bool,uint256)" true 100000000 \
  --rpc-url $RPC_URL --private-key $DEPLOYER_PK
```

**Bob buys 100 NO shares (he thinks TSLA will stay below $300):**

```bash
cast send $MARKET "buyShares(bool,uint256)" false 100000000 \
  --rpc-url $RPC_URL --private-key $BOB_PK
```

**Check the market state:**

```bash
cast call $MARKET \
  "getMarketSummary()(string,int192,uint256,bool,uint256,uint256,address,uint8)" \
  --rpc-url $RPC_URL
```

You should see 100000000 YES shares and 100000000 NO shares, status `0` (Active).

**Check Alice's balance:**

```bash
cast call $MARKET "getShareBalances(address)(uint256,uint256)" $DEPLOYER --rpc-url $RPC_URL
```

Output: `100000000` YES, `0` NO.

---

## Step 6: Resolve and Claim

### Fast-Forward Time

The market has an expiration time in the future. On a local anvil, we can fast-forward:

```bash
# Fast-forward 30 days (2592000 seconds)
cast rpc evm_increaseTime 2592000 --rpc-url $RPC_URL
cast rpc evm_mine --rpc-url $RPC_URL
```

### Submit Oracle Price

In a real deployment, you would fetch a signed report from Chainlink Data Streams. On local anvil, we simulate this by directly setting a price in the DataStreamConsumer.

The deploy script includes a helper for this. Or you can call the test helper:

```bash
# Set TSLA price to $312.45 (above the $300 strike)
cast send $CONSUMER "setTestPrice(bytes32,int192,uint32)" \
  0x00037da06d56d083fe599397a4769a042d63aa73dc4ef57709d31e9971a5b439 \
  312450000000000000000 \
  $(cast block latest --field timestamp --rpc-url $RPC_URL) \
  --rpc-url $RPC_URL --private-key $DEPLOYER_PK
```

**Verify the price is stored:**

```bash
cast call $CONSUMER "getLatestPrice(bytes32)(int192,uint32)" \
  0x00037da06d56d083fe599397a4769a042d63aa73dc4ef57709d31e9971a5b439 \
  --rpc-url $RPC_URL
```

### Resolve the Market

```bash
cast send $MARKET "resolve()" --rpc-url $RPC_URL --private-key $DEPLOYER_PK
```

**Check market status:**

```bash
cast call $MARKET "getMarketStatus()(uint8)" --rpc-url $RPC_URL
```

Output: `2` (Resolved). TSLA was at $312.45, above the $300 strike, so YES wins.

### Alice Claims Her Winnings

```bash
cast send $MARKET "claimWinnings()" --rpc-url $RPC_URL --private-key $DEPLOYER_PK
```

**Check Alice's token balance:**

```bash
cast call $TOKEN "balanceOf(address)(uint256)" $DEPLOYER --rpc-url $RPC_URL
```

Alice started with 1000 tokens, spent 100 on YES shares, and just claimed ~200 tokens (minus fees) from the pool. She made a profit.

**Bob tries to claim (and fails):**

```bash
# This will revert with NoWinningShares()
cast send $MARKET "claimWinnings()" --rpc-url $RPC_URL --private-key $BOB_PK
```

Bob held NO shares. TSLA went above $300. Bob gets nothing.

---

## What Just Happened?

You just ran the full lifecycle of an on-chain stock prediction market:

1. **Deployed** a factory, oracle consumer, compliance engine, and market contract
2. **Created** a market: "Will TSLA be above $300?"
3. **Traded**: Alice bought YES, Bob bought NO
4. **Resolved**: Oracle price ($312.45) was above the strike ($300), so YES won
5. **Settled**: Alice claimed ~200 USDC from the pool, Bob got nothing

All of this happened on-chain. No backend server. No database. No trusted operator deciding the outcome. The oracle signed the price, the contract compared it to the strike, and math determined who won.

In production on Robinhood Chain, the only difference is:
- Real USDC instead of MockCollateralToken
- Real Chainlink Data Streams reports instead of `setTestPrice()`
- ACE compliance checks on every trade (locally, the policy engine passes everyone)
- Chainlink Automation or CRE triggering resolution instead of manual `resolve()` calls

---

## Next Steps

### Deploy to Robinhood Chain Testnet

```bash
forge script script/DeployRWAMarkets.s.sol:DeployRWAMarkets \
  --rpc-url https://robin-rpc.lavish.dev \
  --broadcast \
  --verify
```

You will need:
- Robinhood Chain testnet ETH for gas
- A real USDC address on Robinhood Chain
- Deployed Chainlink Data Streams verifier address

### Read the Full Documentation

- [On-Chain API Reference](/api/rwa-market-api.md) -- every function, parameter, event, and error code
- [Data Streams Resolution](/cre/rwa-data-streams-resolution.md) -- how oracle resolution works end to end
- [Security & Compliance](/security/rwa-compliance-security.md) -- threat model, access control, audit plan
- [Announcement Blog Post](/blog/rwa-stock-prediction-markets.md) -- the what and why

### Create Your Own Market

Modify the deploy script or call the factory directly:

```bash
# "Will AMZN be above $250 by April 30, 2026?"
cast send $FACTORY "createMarket(address,bytes32,string,int192,uint256,bool)" \
  $TOKEN \
  0x000235d7a36a1b3b6a893268509be14dce508025191a33cb2cc0764789599693 \
  "AMZN" \
  250000000000000000000 \
  1746057600 \
  true \
  --rpc-url $RPC_URL --private-key $DEPLOYER_PK
```

---

*Built with Foundry | Chainlink Data Streams V3 | Robinhood Chain (46630)*

*GitHub: [craigmbrown/blindoracle-rwa-markets](https://github.com/craigmbrown/blindoracle-rwa-markets)*
