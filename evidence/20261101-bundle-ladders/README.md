# Evidence pack — bundle ladders, dogfood proof runs (2026-11-01)

Campaign `bundles-receipt-proof` (RQ-GTM-BUNDLES-RECEIPT-01). Four BlindOracle **bundle ladders** were bought by
`claude-82eee642`, the claude.ai BlindOracle connector agent **we operate**, under a person-signed grant, from a
Claude session. These are **dogfood runs**: the buyer is fleet-internal, the money is ours, and nothing here is
revenue. What they prove is the mechanism: one payment, each step runs only if the one before it earned it, and the
unrun steps' share comes back on the rail you paid with.

Bundle digest (sha256 of `SHA256SUMS`): `539ffb2feef1a5d2642326dbcbefa87c37ceb42b10e31a7ecc26deae30db67e0`

## The four runs

| # | Bundle | Job | Paid | What happened | Refund |
|---|---|---|---|---|---|
| A1 | `bundle.reputation-badge` on agent `work-bot` | `3af3be6ce79a` | $0.018 starter credit | both steps ran (agent exists; badge UNVERIFIED) | $0 |
| A2 | `bundle.prehire-ladder` on `work-bot` | `e7f801f3d436` | $4.734 prepaid USDC | reputation + pre-hire check ran (verdict CAUTION); the $5 MASSAT audit was skipped (high_stakes not set) | **$4.50 back to the balance** |
| B1 | `bundle.trust-paperwork` on "Coinbase" @ Companies House search | `b79feb3ba6e0` | $0.099 starter credit | registry step named COINBASE UK, LTD and nine other filings; the trust-record step returned no-charge (Coinbase is not a BO-registered agent) | $0.009 |
| B2 | `bundle.due-diligence` on "Zorblax Fictional Holdings" (deliberately non-existent) @ Companies House search | `05f493341481` | $0.999 prepaid USDC | **stopped at step 1**: the registry page does not name the entity; the trust record and the $1 due-diligence scan never ran | **$0.909 back to the balance** |

Per job: witness pool: WITNESSED pass=2 fail=0 inconclusive=2 trust=0.925 (A1) · witness pool: WITNESSED pass=4 fail=0 inconclusive=0 trust=0.88 (A2) · witness pool: WITNESSED pass=2 fail=1 inconclusive=1 trust=0.647 (B1) · witness pool: WITNESSED pass=2 fail=0 inconclusive=2 trust=0.925 (B2)

## Check it without trusting us

1. **Results and content hashes.** `result_<job>.md` is byte-identical to `https://api.craigmbrown.com/v1/services/result/<job>?format=md`
   (no key). Each deliverable carries `content_sha256`; recompute it with the recipe printed inside the deliverable.
2. **The grant.** `GET https://api.craigmbrown.com/a2a/grants/6edb75385722dd3288cdfb99c48b8da5` returns the signed message, the signature and a
   verify recipe. The person wallet `0x98EC9cAff3D6C555b462957d2390D274aec8a25B` is a Coinbase smart wallet: ask it on Base
   whether it signed the message (ERC-1271 `isValidSignature`, one `eth_call`), and ask the Coinbase Verifications EAS
   indexer `0x2c7eE1E5f416dfF40054c27A62f7B357C4E8619C` whether that wallet carries a Verified Account attestation.
   Every result above names this grant in its `grant` block with `reason: within_grant` and `credential_check: match`.
3. **The money.** `onchain_txs.json` lists the four USDC transfers on Base (fund the fleet wallet, deposit to the treasury,
   the refused deployer path, the return). Read them on basescan. The deposit tx is the one named in `prepaid_ledger_rows.jsonl`
   as the connector's top-up; the refunds for A2 and B2 are `kind: refund` rows in the same file.
4. **Witness scores.** `witness_attestations.jsonl` holds the pool's verdict rows for these jobs (four roles, three vendors'
   models, judges never told what the score is used for). The same rows are mirrored to Nostr (kind 30013) by the fleet's
   publisher; the row carries the content hash it scored.
5. **Checksums.** `sha256sum -c SHA256SUMS` from inside this folder.

## What this pack does NOT show

- No external buyer. The buyer, the funding wallet and the person wallet are ours; `revenue_ledger_rows.jsonl` and the
  internal-identity lists mark them internal. The campaign metric counts only external payers.
- The A2 refund came from `skipped_by_option` (no high-stakes target was given), not from an AVOID verdict. The AVOID stop
  was not exercised.
- B1's second step is weak for a *company*: `procurement.trust-layer` resolves BlindOracle-registered agents, so for an
  arbitrary entity it returns no-charge. Copy must not promise a "trust record" for any company.
- Three defects were found and fixed during the run (`bo_fixes.json`): the gate counted a deposit as spend; the gate did
  not count MCP pay-first purchases at all; prepaid purchases were invisible to the campaign's attribution-based metric.
- Witness scoring lags the job by up to 15 minutes; a job listed as "not yet scored" above was built before the pool ran.
