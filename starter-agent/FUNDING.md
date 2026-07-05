# Funding your starter agent — four ways, pick one

> ## 🎁 Early-adopter offer — first 25 registrations
>
> The first **25** agents to register get a **free pre-funded starter wallet: 1,000 sats
> on us**, minted fresh from the BlindOracle treasury for your trial period — enough for
> ~50–100 paid SKU calls. Nothing to buy, nothing to install.
>
> **To claim (self-serve, ~1 minute):** register (free, Step 1 of the
> [starter agent](README.md)), then mint and pay a **1-sat** tagged Lightning invoice —
> the tag is your claim form, the 1 sat is anti-spam:
>
> ```bash
> # easiest: the starter agent mints it for you and SHOWS THE QR IN YOUR TERMINAL
> python3 starter_agent.py --name YOUR-AGENT-NAME --email you@example.com
>
> # or by hand:
> curl "https://api.craigmbrown.com/ln/invoice?sats=1&product=early-adopter:YOUR-AGENT-NAME&email=you@example.com"
> # pay the returned bolt11 from any Lightning wallet — the response includes
> # "qr_ascii" (print it: a scannable QR for your terminal) and "qr" (SVG data-URI)
> ```
>
> A **free** wallet is a gift of real sats, so each early-adopter grant gets a quick
> operator review (usually same day) before your token is emailed to the address you
> tagged — we like to say hi to our first counterparties anyway. Set it and go:
> `export BLINDORACLE_ECASH_TOKEN=<token>`.
>
> **Prefer instant?** A **paid** top-up is automatic (no review): pay any amount tagged
> `product=top-up:YOUR-AGENT-NAME` and your wallet is reloaded with what you paid within
> ~5 minutes — you own those sats outright. The $1 card path (Path A) is instant too.
>
> No Lightning wallet? Email `craigmbrown@gmail.com` (subject `early adopter`, include
> your `agent_id`). Slots are first-come-first-served.

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

## Path A — $1 by card (Stripe) → starter credit, fully automatic

1. Pay **$1** here (link or QR) — checkout asks for **your registered agent name**
   (the one from `starter_agent.py`); fill it in and the rest is automatic:
   **https://buy.stripe.com/7sY5kFahF6B2atW11T4ZG0a**

   ![Pay $1 by card](qr-stripe-1usd.png)

2. An automated runbook agent matches your payment and **emails your
   `BLINDORACLE_ECASH_TOKEN` to your checkout email** — typically within 5 minutes,
   no human in the loop. ($1 loads 1,000 sats of credit; pay more, load more.)
3. `export BLINDORACLE_ECASH_TOKEN=<token>` and re-run `starter_agent.py`.

If you mistype the agent name, the payment parks for a human — email
`craigmbrown@gmail.com` and it's sorted same-day.

## Path B — sats over Lightning → wallet, fully automatic

Mint a **tagged** invoice — the tag identifies you, so no email exchange is needed:

```bash
# easiest: starter agent mints it + shows the QR in-terminal
python3 starter_agent.py --name YOUR-AGENT-NAME --email you@example.com --topup-sats 1000

# or by hand:
curl "https://api.craigmbrown.com/ln/invoice?sats=1000&product=top-up:YOUR-AGENT-NAME&email=you@example.com"
# -> {"bolt11": "lnbc...", "qr_ascii": "<terminal QR — print it>", "qr": "data:image/svg+xml;...", ...}
```

Pay the `bolt11` from any Lightning wallet (print `qr_ascii` for a scannable
in-terminal QR, or open the `qr` data-URI in a browser, or feed `bolt11` straight
to your wallet). The runbook agent
detects the payment and emails a wallet token for the amount you paid to the tagged
address, typically within 5 minutes. (First 25? Use the early-adopter claim above
instead — 1 sat gets you 1,000.)

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
