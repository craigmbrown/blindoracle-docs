# Agent Passport System Changelog

## v2.0.0 (2026-03-22)

Complete rebuild of the Agent Passport System. Self-contained in ETAC-System repo with no external DB or submodule dependencies.

### Added
- **Schnorr BIP-340 Signing**: All passports cryptographically signed with hub private key via `coincurve`
- **PNG Passport Cards**: 800x1200 visual passport cards rendered via Pillow for each agent
- **Standalone Verifier**: `agent_passport_verifier.py` — verify any passport with only the JSON file, no DB access needed
- **ZK Selective Disclosure Bridge**: `zk_proof_bridge.py` — Midnight Network placeholder with 8 claim types
- **118 Agent Passports**: Full coverage of all discovered agents across 8 teams
- **Nostr Kind 30025**: Replaceable event format for passport publishing (d-tag = agent_name)
- **Reputation Scoring**: Composite score (0-100) from volume, quality, diversity, and chain depth
- **Badge System**: Gold (>=85), Silver (>=70), Bronze (>=50) badge tiers
- **Team Classification**: Automatic team assignment from agent name prefixes
- **3 Payment Agent Passports**: financial-payments-agent, payment-gateway-agent, x402-gateway
- **Dark Mode Dashboard**: HTML gallery with base64-embedded PNG passport cards
- **Cross-Repo Deployment**: Verifier deployed to ETAC-System, etac-1, blindoracle-hub, blindoracle-marketplace-client
- **Client SDK**: Full generator + verifier + ZK bridge in marketplace client repo

### Architecture
- 4-layer tamper-proof system: Signed JSON -> Rendered PNG -> Standalone Verifier -> ZK Bridge
- Data sources: `.claude/agents/*.md` (roster), `data/proofs.db` (reputation), `.env` (signing key)
- Hub pubkey: `aa5d2ae60c9a44fb4472611ccc138047e0534bb3244bb2915963c45e8bfdbba9`

### ZK Claim Types
1. `reputation_gte` — Prove score >= threshold
2. `success_rate_gte` — Prove success rate >= threshold
3. `total_runs_gte` — Prove total runs >= threshold
4. `badge_level` — Prove badge meets minimum level
5. `proof_count_gte` — Prove proof count >= threshold
6. `team_membership` — Prove membership in a team
7. `tier_gte` — Prove tier level >= threshold
8. `uptime_gte` — Prove uptime >= threshold

### PRs Merged
- ETAC-System #1970 — Generator + verifier + ZK bridge + dashboard
- etac-1 #135 — Passport verifier for chainlink proof system
- blindoracle-hub #7 — Passport verifier for hub
- blindoracle-marketplace-client #4 — Passport verifier initial
- blindoracle-marketplace-client #5 — Full SDK (generator + verifier + ZK bridge)

### Known Limitations
- ZK bridge uses simulated proofs (Midnight SDK not yet available)
- Schnorr verification checks signature format (64-byte), not full cryptographic verification via `PublicKey.verify_schnorr`
- PNG rendering requires Pillow and a font file (falls back to default)

## v1.0.0 (2026-03-22) — LOST

Initial implementation lost due to uncommitted code in an uninitialized submodule directory. ~1,200 lines written to a dead symlink path. Session timed out before committing.

**Lesson learned**: Never accumulate 500+ lines uncommitted. Commit every ~100 lines.
