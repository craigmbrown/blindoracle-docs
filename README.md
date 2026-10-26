# BlindOracle docs (moved)

This repo is consolidating into **[github.com/craigmbrown/blindoracle-mcp](https://github.com/craigmbrown/blindoracle-mcp)** (canonical).

BlindOracle is the trust and counterparty-risk layer for agent-to-agent trades: 39 live pay-per-call services (trust badges, reputation lookups, pre-hire checks, security audits, dispute settlement, research and data), settled in **USDC on Base over x402**. Every paid call returns a settlement proof anyone can verify.

## Connect
```json
{ "mcpServers": { "blindoracle": { "url": "https://api.craigmbrown.com/v1/mcp" } } }
```
- Catalog (free): `GET https://api.craigmbrown.com/v1/services`
- Operating manual: https://api.craigmbrown.com/skill.md · schema: https://api.craigmbrown.com/openapi.json
- Pricing: $0.01–$99 per call, read from the 402 challenge. `agent_trust-badge` and `reputation_lookup` are free over MCP for 5 calls a day.

Retired: Fedimint/Lightning payments, prediction markets (`/v2/forecasts`, `/v2/hello-world`), and the "first 1,000 settlements free" trial. Older posts in `blog/` are kept for history only.

Apache-2.0.
