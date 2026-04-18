# BlindOracle Bold Hook Cards — Marketing Asset Set (2026-04-18)

Production-ready visual assets for GTM. Green-on-black theme (#0a0a0a background, #00ff41 accent), Lulu-magazine hierarchy (eyebrow → big hook → subhead → value pills → CTA strip). All assets self-contained, DPR-2 PNGs + 6-second animated GIF loops.

## Asset inventory

| File | Size | Dims | Use |
|---|---|---|---|
| `card1-hero-exploit-wave.png` | 642 KB | 1400×900 @ 2× | LinkedIn hero, blog OG, email banner |
| `card1-hero-exploit-wave.gif` | 629 KB | 800w 6s loop | LinkedIn autoplay, Telegram |
| `card2-square-28k-contrarian.png` | 528 KB | 900×1100 @ 2× | X thread card-1, Telegram pin |
| `card3-alert-router-drain.png` | 582 KB | 900×1100 @ 2× | Cold-email inline alert, breaking-news reply |
| `card4-value-stack.png` | 569 KB | 900×1100 @ 2× | Website hero, pinned X, Nostr |
| `card5-email-hero-3hooks.png` | 561 KB | 1400×900 @ 2× | Email hero (outbound + newsletter) |
| `card5-email-hero-3hooks.gif` | 493 KB | 800w 6s loop | LinkedIn post cover |
| `card6-bank-four-reply-cards.png` | 1.1 MB | 1200×1400 @ 2× | Bank of 4 small stat cards |
| `card6-bank-four-reply-cards.gif` | 243 KB | 800w 6s loop | Email sig, X replies, Telegram stickers |

## Source + workflow

- `source.html` — original HTML with 6 cards + embedded CSS/JS animations. Edit copy, re-render.
- `gallery.html` — review gallery showing all rendered outputs with channel-assignment plan.
- Scripts (in main Project repo): `scripts/card_exporter.py` (PNG) · `scripts/card_gif_exporter.py` (GIF).
- Render pipeline: Chromium (Playwright 1.47) at DPR 2 → screenshots → ffmpeg palette-quantized GIF.

## Design system

- **Colors**: bg `#0a0a0a`, primary `#00ff41`, soft-green `#b0ffc0`, alert `#ff5050` (card 3 only)
- **Type**: Arial Black for headlines, Courier New for eyebrows/metadata, system-ui for body
- **Motion**: typewriter for headlines, rise-up staggered for bullets, count-up for stats, ticker for context, glitch for alerts
- **Hook stack**: every card is eyebrow → big hook → subhead → value pills → CTA strip

## Trend pegs (Apr 2026)

- **Card 1** — 12 DeFi protocols attacked in 14 days since $280M Drift exploit (Cointelegraph, Apr 2-18); Anthropic Mythos autonomous 0-days
- **Card 2** — ERC-8004 + x402 narrative vs. $28K/day on-chain reality (CoinDesk, Mar 11)
- **Card 3** — 26 LLM routers drained $500K client wallet (CoinDesk, Apr 13)
- **Card 4/6** — Evergreen value + stat bank
- **Card 5** — Three actionable CTAs in magazine-grid format

## Integration notes

Drop these into:
- Web: `<img src="assets/brand/card*.png">` with `object-fit:cover` for heroes
- Email (HTML): inline as base64 or hosted URL; Gmail/iOS render GIFs, Outlook shows first frame
- Social: PNGs for X/LinkedIn; GIFs for LinkedIn autoplay and Telegram
- README badges: use `card6-*-bank.png` cropped to individual 540×540 stat cards

Regenerate from `source.html` if copy changes. All assets are license-free for BlindOracle GTM use.
