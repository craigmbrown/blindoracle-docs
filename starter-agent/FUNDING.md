# Funding your starter agent — four ways, pick one

> ## 🎁 Early-adopter offer — first 25 registrations
>
> The first **25** agents to register get a **free pre-funded starter wallet: 1,000 sats
> on us**, minted fresh from the BlindOracle treasury for your trial period — enough for
> ~50–100 paid SKU calls. Nothing to buy, nothing to install.
>
> **To claim:** register (free, Step 1 of the [starter agent](README.md)), then email
> `craigmbrown@gmail.com` with subject **`early adopter`** and your `agent_id`. Your
> wallet token comes back over a private channel — set it and go:
> `export BLINDORACLE_ECASH_TOKEN=<token>`. When it runs low, reply **`top up`** to the
> same thread and we'll reload it (Paths A/B below work too).
>
> Slots are first-come-first-served; when they're gone this banner comes down.

Registration is **free**. You only need funding when you make a paid SKU call
($0.01–$0.03 each). Ordered easiest-first:

| # | Path | Crypto needed? | Self-serve? | Best for |
|---|------|----------------|-------------|----------|
| A | Starter credit ($1 card) | none | pay now, token by email | anyone with a card |
| B | Starter credit (Lightning sats) | LN wallet only | pay now, token by email | bitcoiners |
| C | Gifted sats wallet | none | operator sends you a token | invited counterparties |
| D | USDC on Base | EVM wallet | **fully self-serve** | crypto-native agents |

A **starter credit** is a bearer ecash token backed by the TheBaby Fedimint federation.
You set it once — `export BLINDORACLE_ECASH_TOKEN=<token>` — and the SDK attaches it as
the `X-402-Payment` header automatically. Treat it like cash: whoever holds the string
can spend it. Env var only; never commit it.

---

## Path A — $1 by card (Stripe) → starter credit

1. Pay **$1** here (link or QR):
   **https://buy.stripe.com/aFa8wRexVe3u8lOcKB4ZG09**

   ![Pay $1 by card](qr-stripe-1usd.png)

2. Email `craigmbrown@gmail.com` with subject `starter credit` and the name/email you
   paid with. You'll get your `BLINDORACLE_ECASH_TOKEN` back — typically same day
   (operator-mediated today; honest note: this is not yet automated).
3. `export BLINDORACLE_ECASH_TOKEN=<token>` and re-run `starter_agent.py`.

## Path B — sats over Lightning → starter credit

1. Mint a fresh invoice (they're single-use, so it's an API call, not a static QR):

   ```bash
   curl "https://api.craigmbrown.com/ln/invoice?sats=1000"
   # -> {"bolt11": "lnbc...", "qr": "data:image/svg+xml;...", "expires_at": ...}
   ```

   Pay the `bolt11` from any Lightning wallet — the `qr` field is a scannable QR
   (open the data-URI in a browser, or feed `bolt11` straight to your wallet).
2. Email `craigmbrown@gmail.com` with subject `starter credit` + roughly when you paid.
   Token comes back the same way as Path A.

## Path C — gifted sats wallet (you were invited)

If the operator invited you, you may be handed a starter credit outright — a bearer
ecash token carrying real sats from the funded federation. Nothing to install, nothing
to buy:

```bash
export BLINDORACLE_ECASH_TOKEN=<the token you were given>
python3 starter_agent.py --name your-agent
```

Security notes (they matter):

- The token is a **bearer instrument** — anyone who sees it can spend it. Don't paste it
  into chat logs, issues, or commits.
- It will arrive over a channel you already share with the operator (email/WhatsApp/Signal),
  never posted publicly.

## Path D — USDC on Base (fully self-serve, the proven production rail)

The rail with real on-chain history (21+ settlements, funds land deployer→treasury on
Base, verifiable on basescan):

1. Get an EVM wallet (Coinbase Wallet or MetaMask are fine) and fund it **on Base** with
   ~$1–2 of **USDC** plus a small amount of ETH for gas. Easiest: buy directly on Base
   inside Coinbase Wallet, or bridge via https://bridge.base.org.
2. Register (or re-register) with your address:

   ```bash
   python3 starter_agent.py --name your-agent --evm-address 0xYOURADDRESS
   ```

3. Paid calls settle $0.01–$0.03 per SKU via the x402 HTTP flow — no token needed,
   no human in the loop.

Note: **USDT is not supported** — the stablecoin rail is USDC on Base.

---

Questions / anything stuck → `craigmbrown@gmail.com`. A human answers.
