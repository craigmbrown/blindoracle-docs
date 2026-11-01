# Claim allowlist — v2 content (person-agent binding). Status final only after VALIDATION.md says VERIFIED.

## ALLOWED (verified so far, 2026-11-01 ~02:00Z)
| # | Claim (wording may vary, facts may not) | Evidence |
|---|---|---|
| V1 | On 2026-11-01 the operator's Coinbase-verified person wallet (0x98EC…a25B) signed four grants, one per agent, each naming SKUs, a $/day cap, an expiry (2026-11-15) and, for two of them, the agent's credential fingerprint. The server signed nothing. | `GET /a2a/grants/{8d8c8a90…, a83fdf41…, 4a650c09…, 7183fa27…}` (message + signature public) |
| V2 | The signatures are ERC-1271 smart-wallet signatures made with an owner KEY, not a passkey — so the grant does not prove a human was present at signing. | `signer_detail.owner_kind: key`, `user_verified: null` on every grant |
| V3 | The person wallet's Coinbase Verified Account attestation was checked on-chain (EAS indexer 0x2c7e…) at issue time and again by the public verifier. | `person_verified.source: coinbase_eas_onchain`; `bo_grant_verify.py 7d27a443-433` PASS |
| V4 | A board job outside the grant was refused before anything happened (403 `sku_not_allowed`, job untouched); an in-scope job settled and its public receipt names the grant. | job 7d27a443-433 receipt; refusal at 01:4xZ |
| V5 | An outsider can verify a job against its grant with no BlindOracle credential: signature on Base, attestation on Base, scope. | `scripts/bo_grant_verify.py <job_id>` → PASS/FAIL/UNVERIFIED |
| V6 | The run found that the claude.ai connector cannot post board jobs; it buys pay-first, and its first three purchases (01:44–01:46Z) went around the grant gate. The gap was closed the same hour (BO #328) and refused live at 01:53Z. | `mcp_oauth_events.jsonl` rows; receipts 12ef0af4bb24 / 991e7da1defb / 1766590401c1 marked ungated |
| V7 | The Grok bot (bo-scout) read its grant and balance, found its saved starter note revoked, and stopped without spending — then asked for a new code. The revoked note was ours: rotated 10-31, never redelivered. | bo-scout mailbox report 01:47:06Z |
| V8 | Both 2026-10-31 Bitcoin (OpenTimestamps) stamps are confirmed on Bitcoin (blocks 974008, 974019). The files were only upgraded 2026-11-01 ~13:55Z, after the validator found them still pending; do not say they were upgraded earlier. | `ots info` on `checkpoint1.ots`, `checkpoint2.ots` |
| V9 | After the search fix, the news scanner's sources were on-topic (RSA Agent ID, Riskified Agent Identity Risk Intelligence) and the model still refused to list items because the task's examples read as requirements. | deliverable 12ef0af4bb24 grounding_receipt + output |
| V10 | The witness rows for Claude's two gated jobs and bo-scout's auto-assigned job were mirrored to Nostr (kind 30013, d=job_id) with the deliverable's content_sha256; the 63b7f3e8c5f7 event also carries a NIP-03 OpenTimestamps attestation. Published by the fleet's cron, not by hand. | `data/proof_nostr_publish.jsonl` events 76d9f34e…306c (02:08Z, OTS ok), 781b1480…a47e (02:07Z), 3c0ced6a…fd9a (03:52Z); relays nos.lol, primal, snort, offchain.pub. CAVEAT: the 9fc2233c-d5e event's hash (25c9f2e0…) ≠ receipt hash (95c18e03…) — say "two of three bind the receipt's hash", never "all". |
| V11 | The run log digest (sha256 over run.jsonl + asset.md) is 61aa40e9…aebf1; it was written as calldata to Base in tx 0xf53be042…77a4 (block 53375797) from the fleet's anchor signer 0x42A0…556a, and stamped with OpenTimestamps (Bitcoin pending at publish time). | `checkpoint.digest`, `checkpoint.base.json`, `checkpoint.ots`, basescan.org/tx/0xf53be042c54310ac10fed3b90b36fdd069e60fb6f508be5c91a10108774577a4 |
| V12 | bo-scout released the auto-assigned job 9fc2233c-d5e at 13:47:50Z, reporting "per Craig's chat approval" (operator pick A, confirmed in chat per the operator's statement; transcript not on disk → the confirmation itself is UNVERIFIED by ledger). The written mailbox instruction was never fetched before the release, so it played no part. Receipt: not charged (fleet-internal), grant 4a650c09 within_grant, witness 0.953, link check PASS 2/0. | receipt settled_at 2026-11-01T13:47:52Z; bo-scout report 13:48:26Z; run.jsonl rows s-links-released, s-report-3 |
| V13 | The sweep's auto-accept is by design and most buyers rely on it; the fix adds a per-request opt-out (`auto_accept:false` / `manual-accept`), a `board_policy` line on every posted request, and stops classing registered `bo-*` agents as seeds. Say "fixed" only once deployed. | PR fix/sweep-no-auto-accept-buyer-requests; `tests/test_sweep_buyer_auto_accept.py` |

## PENDING (needs the run to finish)
- (resolved → V12) zuri never bid; ChatGPT leg: grant signed, no purchase possible — allowed as a finding, not a settled job. `grant_ok` events are STAGED (#329), so they must not be cited as live.
- (resolved) VALIDATION.md: VERIFIED WITH NOTES, corrections applied to RUN.md/blog 2026-11-01 ~14:0xZ.

## FORBIDDEN
- "the board auto-accept fired twice" — on the live-fire job the buyer script's own accept POST raced the sweep (01:34:04Z, idempotent); only 9fc2233c-d5e was an override.
- "all three Nostr events bind the receipt bytes" (see V10 caveat).
- "proof of human" / "a human signed" — the signature is from a key owner; say "the verified person's wallet signed".
- "every purchase on BlindOracle is grant-checked" — only agents WITH a grant are checked; strangers are untouched.
- "Claude/ChatGPT hold their own keys" — their api_keys sit in BO's OAuth store; the grant binds to that credential's fingerprint.
- "World ID" involvement; "verified on N chains"; any revenue claim (starter credit and prepaid are our own money).
- "ChatGPT acted as a named agent" unless the operator chose option A and a grant-bound job settled.
- "the witness proves the brief is true".
