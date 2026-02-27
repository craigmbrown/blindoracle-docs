# Deployment Guide

Step-by-step instructions for deploying BlindOracle RWA Stock Prediction Markets to Robinhood Chain.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Chain Details](#chain-details)
- [Environment Variables](#environment-variables)
- [Deployment Script Walkthrough](#deployment-script-walkthrough)
- [Deploy Command](#deploy-command)
- [Token Addresses on Robinhood Chain](#token-addresses-on-robinhood-chain)
- [Post-Deployment Configuration](#post-deployment-configuration)

---

## Prerequisites

| Tool    | Purpose                              | Install                                      |
|---------|--------------------------------------|----------------------------------------------|
| Foundry | Smart contract compilation & deploy  | `curl -L https://foundry.paradigm.xyz \| bash && foundryup` |
| forge   | Compile & deploy contracts           | Included with Foundry                        |
| cast    | Interact with deployed contracts     | Included with Foundry                        |
| anvil   | Local testnet for development        | Included with Foundry                        |

Additionally, you need:

- A **private key** with testnet ETH on Robinhood Chain for gas fees
- Access to **Chainlink Data Streams** for price feed verification
- An **ACE PolicyEngine** contract address (deploy separately or use existing)

---

## Chain Details

| Property         | Value                                          |
|------------------|------------------------------------------------|
| Chain Name       | Robinhood Chain                                |
| Chain ID         | 46630                                          |
| Network Type     | Arbitrum Orbit L2                              |
| RPC URL          | `https://rpc.testnet.chain.robinhood.com`      |
| Block Explorer   | Blockscout (testnet)                           |

Robinhood Chain is an Arbitrum Orbit L2 that hosts tokenized real-world assets (stocks). Native gas is paid in ETH bridged to the L2.

---

## Environment Variables

Create a `.env` file in the project root or export these variables before running the deploy script:

```bash
# Required
PRIVATE_KEY=0x...                                    # Deployer private key (with testnet ETH)
RPC_URL=https://rpc.testnet.chain.robinhood.com      # Robinhood Chain RPC endpoint

# ACE Compliance
POLICY_ENGINE=0x...                                  # Chainlink ACE PolicyEngine contract address

# Chainlink Data Streams
VERIFIER_PROXY=0x...                                 # Chainlink Data Streams verifier proxy address

# Collateral
USDC_ADDRESS=0x...                                   # USDC (or mock USDC) address on Robinhood Chain

# Optional (defaults shown)
STALENESS_THRESHOLD=3600                             # Maximum price age in seconds (default: 3600 = 1 hour)
```

| Variable             | Required | Default | Description                                        |
|----------------------|----------|---------|----------------------------------------------------|
| `PRIVATE_KEY`        | Yes      | --      | Private key of the deploying account               |
| `RPC_URL`            | Yes      | --      | Robinhood Chain RPC endpoint                       |
| `POLICY_ENGINE`      | Yes      | --      | ACE PolicyEngine address for compliance            |
| `VERIFIER_PROXY`     | Yes      | --      | Chainlink Data Streams verifier proxy              |
| `USDC_ADDRESS`       | Yes      | --      | Collateral token address (can be mock for testnet) |
| `STALENESS_THRESHOLD`| No       | 3600    | Max seconds before a price is considered stale     |

---

## Deployment Script Walkthrough

The deployment is handled by `script/DeployRWAMarkets.s.sol`. The script executes four sequential steps:

### Step 1: Deploy DataStreamConsumer and Register Feeds

```solidity
// Deploy the DataStreamConsumer with the Chainlink verifier proxy
DataStreamConsumer dataStream = new DataStreamConsumer(
    msg.sender,           // initialOwner
    VERIFIER_PROXY,       // Chainlink verifier proxy address
    STALENESS_THRESHOLD   // e.g., 3600 seconds
);

// Register all 5 stock price feeds
dataStream.registerFeed(TSLA_FEED_ID, "TSLA");
dataStream.registerFeed(AMZN_FEED_ID, "AMZN");
dataStream.registerFeed(HOOD_FEED_ID, "HOOD");
dataStream.registerFeed(PLTR_FEED_ID, "PLTR");
dataStream.registerFeed(AMD_FEED_ID,  "AMD");
```

This deploys the oracle consumer and registers Chainlink Data Streams feeds for all five supported stocks: TSLA, AMZN, HOOD, PLTR, and AMD.

### Step 2: Deploy or Reference Collateral Token

```solidity
// Option A: Deploy mock USDC for testnet
SimpleToken mockUSDC = new SimpleToken("Mock USDC", "USDC", 6);

// Option B: Use existing USDC address
address collateral = USDC_ADDRESS;
```

For testnet deployment, a `SimpleToken` (ERC20 + ERC-2612 permit) is deployed as mock USDC. For production, reference the existing USDC contract address on Robinhood Chain.

### Step 3: Deploy RWAMarketFactory

```solidity
// Deploy the factory with ACE PolicyEngine and DataStreamConsumer
RWAMarketFactory factory = new RWAMarketFactory(
    msg.sender,           // initialOwner
    POLICY_ENGINE,        // ACE PolicyEngine address
    address(dataStream)   // DataStreamConsumer address
);

// Approve the collateral token
factory.approveCollateral(address(collateral));
```

The factory is deployed with references to the PolicyEngine (for ACE compliance) and DataStreamConsumer (for price resolution). The collateral token is added to the approved whitelist.

### Step 4: Create Initial Markets

```solidity
// Create TSLA market: "TSLA above $250 by expiration"
address tslaMarket = factory.createMarket(
    address(collateral),    // collateral token
    TSLA_FEED_ID,           // Chainlink feed ID
    "TSLA",                 // symbol
    250_00000000,           // strikePrice (int192, 8 decimals)
    block.timestamp + 30 days,  // expirationTime
    true                    // isAbove (YES wins if price > strike)
);

// Create HOOD market: "HOOD above $50 by expiration"
address hoodMarket = factory.createMarket(
    address(collateral),
    HOOD_FEED_ID,
    "HOOD",
    50_00000000,            // strikePrice (int192, 8 decimals)
    block.timestamp + 30 days,
    true
);
```

Two initial markets are created: TSLA above $250 and HOOD above $50, both with 30-day expiration windows.

---

## Deploy Command

Run the full deployment with a single Foundry command:

```bash
# Load environment variables
source .env

# Deploy to Robinhood Chain
forge script script/DeployRWAMarkets.s.sol:DeployRWAMarkets \
    --rpc-url $RPC_URL \
    --broadcast \
    --verify
```

### Command Flags

| Flag          | Description                                            |
|---------------|--------------------------------------------------------|
| `--rpc-url`   | Target chain RPC endpoint                              |
| `--broadcast` | Actually send transactions (omit for dry run)          |
| `--verify`    | Verify contracts on Blockscout after deployment        |

### Dry Run (Simulation Only)

To simulate the deployment without broadcasting transactions:

```bash
forge script script/DeployRWAMarkets.s.sol:DeployRWAMarkets \
    --rpc-url $RPC_URL
```

### Local Testing with Anvil

To test the deployment against a local fork of Robinhood Chain:

```bash
# Start a local fork
anvil --fork-url https://rpc.testnet.chain.robinhood.com

# Deploy to local fork (in another terminal)
forge script script/DeployRWAMarkets.s.sol:DeployRWAMarkets \
    --rpc-url http://localhost:8545 \
    --broadcast
```

---

## Token Addresses on Robinhood Chain

The following are real token contract addresses deployed on Robinhood Chain testnet:

| Token | Address                                        | Type             |
|-------|------------------------------------------------|------------------|
| TSLA  | `0xC9f9028bF3E2e3c5cB5594cF1F57b2053DBd4E`    | Tokenized Stock  |
| AMZN  | `0x5884eCCB84D6BEf77E5df8A5990b3a31fC09E02`   | Tokenized Stock  |
| PLTR  | `0x1FBE999BCF2912cE49c72d50dc8f36DA2b8298d0`   | Tokenized Stock  |
| WETH  | `0x7943001e6Cd148a87b7F31aF54c9F7BB06052Fa`   | Wrapped ETH      |

These addresses can be verified on the Robinhood Chain Blockscout explorer.

---

## Post-Deployment Configuration

After successful deployment, complete the following configuration steps:

### 1. Configure ACE PolicyEngine

Connect the deployed `CompliancePolicyRules` contract to the ACE PolicyEngine so that the `runPolicy` modifier on market functions routes compliance checks correctly.

```bash
# Register the compliance rules with the PolicyEngine
cast send $POLICY_ENGINE "registerRules(address)" $COMPLIANCE_RULES_ADDRESS \
    --rpc-url $RPC_URL \
    --private-key $PRIVATE_KEY
```

### 2. Update Chainlink Data Streams Verifier

Ensure the `DataStreamConsumer` is configured with the correct verifier proxy address. If the verifier proxy changes:

```bash
cast send $DATA_STREAM_CONSUMER "setVerifier(address)" $NEW_VERIFIER_PROXY \
    --rpc-url $RPC_URL \
    --private-key $PRIVATE_KEY
```

### 3. Verify Contracts on Blockscout

If `--verify` did not complete during deployment, manually verify each contract:

```bash
# Verify DataStreamConsumer
forge verify-contract $DATA_STREAM_ADDRESS DataStreamConsumer \
    --chain-id 46630 \
    --constructor-args $(cast abi-encode "constructor(address,address,uint256)" \
        $DEPLOYER $VERIFIER_PROXY $STALENESS_THRESHOLD)

# Verify RWAMarketFactory
forge verify-contract $FACTORY_ADDRESS RWAMarketFactory \
    --chain-id 46630 \
    --constructor-args $(cast abi-encode "constructor(address,address,address)" \
        $DEPLOYER $POLICY_ENGINE $DATA_STREAM_ADDRESS)
```

### 4. Verify Deployment State

Run these verification commands to confirm the deployment is correctly configured:

```bash
# Check factory market count
cast call $FACTORY_ADDRESS "getMarketCount()" --rpc-url $RPC_URL

# Check collateral is approved
cast call $FACTORY_ADDRESS "approvedCollateral(address)" $USDC_ADDRESS --rpc-url $RPC_URL

# Check DataStreamConsumer feed count
cast call $DATA_STREAM_ADDRESS "feedCount()" --rpc-url $RPC_URL

# Check a specific market's summary
cast call $TSLA_MARKET "getMarketSummary()" --rpc-url $RPC_URL
```

### 5. Create Additional Markets

After initial deployment, create markets for the remaining supported assets:

```bash
# Create AMZN market
cast send $FACTORY_ADDRESS \
    "createMarket(address,bytes32,string,int192,uint256,bool)" \
    $USDC_ADDRESS $AMZN_FEED_ID "AMZN" 200_00000000 $EXPIRATION_TIMESTAMP true \
    --rpc-url $RPC_URL \
    --private-key $PRIVATE_KEY

# Create PLTR market
cast send $FACTORY_ADDRESS \
    "createMarket(address,bytes32,string,int192,uint256,bool)" \
    $USDC_ADDRESS $PLTR_FEED_ID "PLTR" 100_00000000 $EXPIRATION_TIMESTAMP true \
    --rpc-url $RPC_URL \
    --private-key $PRIVATE_KEY

# Create AMD market
cast send $FACTORY_ADDRESS \
    "createMarket(address,bytes32,string,int192,uint256,bool)" \
    $USDC_ADDRESS $AMD_FEED_ID "AMD" 150_00000000 $EXPIRATION_TIMESTAMP true \
    --rpc-url $RPC_URL \
    --private-key $PRIVATE_KEY
```

---

## Deployment Checklist

Use this checklist to verify a complete deployment:

- [ ] Environment variables set (PRIVATE_KEY, RPC_URL, POLICY_ENGINE, VERIFIER_PROXY, USDC_ADDRESS)
- [ ] DataStreamConsumer deployed and all 5 feeds registered (TSLA, AMZN, HOOD, PLTR, AMD)
- [ ] Collateral token deployed or referenced (SimpleToken / existing USDC)
- [ ] RWAMarketFactory deployed with correct PolicyEngine and DataStreamConsumer
- [ ] Collateral token approved on factory
- [ ] Initial markets created (TSLA, HOOD minimum)
- [ ] ACE PolicyEngine configured with CompliancePolicyRules
- [ ] Chainlink Data Streams verifier proxy confirmed
- [ ] All contracts verified on Blockscout
- [ ] Factory `getMarketCount()` returns expected number
- [ ] DataStreamConsumer `feedCount()` returns 5
- [ ] Test `getMarketSummary()` on at least one market
