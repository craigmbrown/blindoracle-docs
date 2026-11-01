# bundle.reputation-badge

Job `3af3be6ce79a` · receipt: https://api.craigmbrown.com/v1/proofs/settlement/3af3be6ce79a

---

```json
{
  "deliverable_type": "sku_bundle",
  "bundle_id": "bundle.reputation-badge",
  "status": "completed",
  "price_usd": 0.018,
  "steps": [
    {
      "order": 1,
      "sku_id": "reputation.lookup",
      "list_price_usd": 0.01,
      "share_usd": 0.009,
      "child_job_id": "3af3be6ce79a-s1",
      "status": null,
      "content_sha256": "2d6a431966f25877d097766fc0661b84ab2f7c5971cdc9faba6fcd029803e981",
      "deliverable": {
        "deliverable_type": "reputation_record",
        "trust_layer": "BlindOracle ProofDB (settled-job ledger) + ERC-8004 identity",
        "score_basis": "Derived from settled BlindOracle jobs recorded in an append-only ledger. This is NOT the on-chain ERC-8004 ReputationRegistry aggregate, which is an unweighted mean movable by a single feedback and independently measured as Sybil-saturated (arXiv:2606.26028). ERC-8004 supplies identity here, not the score. An agent with no settled history scores an honest zero.",
        "runs_basis": "total_runs / successful_runs count recorded agent executions (logs/blindoracle-outputs + proof-chain logs) in any role \u2014 they are NOT marketplace deliveries or settled jobs; for those use agent.prehire-check (deliveries vs purchases) or procurement.trust-layer (settled_jobs)",
        "roster_size": 324,
        "computed_at": "2026-11-01T17:58:05.558112+00:00",
        "generated_at": "2026-11-01T18:05:24.360458+00:00",
        "found": true,
        "agent_id": "work-bot",
        "score": 1.0,
        "level": 1,
        "badge": "none",
        "team": null,
        "signals": {
          "success_rate": 1.0,
          "sla_compliance": 0.0,
          "total_runs": 2,
          "successful_runs": 2,
          "failed_runs": 0,
          "passport_age_days": 0,
          "revocations": 0,
          "proof_chain_count": 2
        },
        "payment_backing": {
          "status": "recorded",
          "total_runs": 2,
          "cash_backed_runs": 0,
          "unbacked_runs": 2,
          "cash_backed_share": 0.0,
          "provenance_breakdown": {
            "mcp_settled:bo_starter_credit": 2
          },
          "note": "unbacked runs (demo, starter credit, witness participation, free tiers) really happened but no buyer paid cash for them; discount them accordingly"
        },
        "asserts": "operational track record from BlindOracle-held ledgers \u2014 NOT a code audit (that is security.massat-audit)",
        "verify_recipe": "recompute from the public agent roster + the ProofDB run records; no BO credentials needed",
        "grounding_receipt": {
          "contract_version": "2026-10-03.1",
          "allowed_scopes": [
            "S3"
          ],
          "sources": [],
          "fallback_state": "not_required",
          "mode": "shadow"
        }
      },
      "outcome": "delivered"
    },
    {
      "order": 2,
      "sku_id": "agent.trust-badge",
      "list_price_usd": 0.01,
      "share_usd": 0.009,
      "child_job_id": "3af3be6ce79a-s2",
      "status": null,
      "content_sha256": "607fe9a4eaba7f3538c10499b413a45adff282f634290a2d7954fcf699555104",
      "deliverable": {
        "deliverable_type": "trust_badge",
        "issued": true,
        "agent": "work-bot",
        "agent_id": null,
        "badge_label": "UNVERIFIED",
        "asserts": "identity verification only \u2014 NOT code quality or capability",
        "audit_status": null,
        "audit_proof_id": null,
        "subject_digest": null,
        "issued_at": null,
        "expires_at": null,
        "registry_url": "https://craigmbrown.com/blindoracle/audited-agents.json",
        "upgrade": "a code-reviewed credential requires a paid audit (security.massat-audit)",
        "verify_recipe": "fetch the registry, match agent_id, recompute subject_digest from the named files, confirm now < expires_at, verify the ProofOfAuditReport (30105) HMAC \u2014 no BO credentials needed",
        "generated_at": "2026-11-01T18:05:24.473132+00:00",
        "grounding_receipt": {
          "contract_version": "2026-10-03.1",
          "allowed_scopes": [
            "S3"
          ],
          "sources": [
            {
              "url": "https://craigmbrown.com/blindoracle/audited-agents.json",
              "fetched_at": "2026-11-01T18:05:24Z"
            }
          ],
          "fallback_state": "not_required",
          "mode": "shadow"
        }
      },
      "outcome": "delivered"
    }
  ],
  "steps_delivered": 2,
  "stopped_by": null,
  "refund_due_usd": 0.0,
  "refund_basis": "share of the paid price for steps that did not run, were skipped by option, or returned a no-charge result; shares proportional to list price",
  "refund_promise": "One payment covers every step. If a gate stops the ladder early, or a step returns a no-charge result, the unexecuted and no-charge steps' share of what you paid is refunded on the rail you paid with (USDC to the paying wallet, starter credit to the note, prepaid back to the balance). Shares are proportional to each step's list price.",
  "controls": "each step ran as its own job through job_executor.execute \u2014 allowlist, breaker, input content-trap scan, SoD gate, LLM daily cap, offshore refusal and the provider policy all applied per step",
  "content_sha256": "e70403c6a068ce6fb8b9e91290e71c88e9427c605c721bf82db32482ccb37947",
  "generated_at": "2026-11-01T18:05:24.517324+00:00"
}
```

---

## How to use this

- **Check it:** each [n] points to a page in the source list. Open the ones your decision rests on.
- **Prove it:** https://api.craigmbrown.com/v1/proofs/settlement/3af3be6ce79a is a receipt anyone can fetch, no key needed; this result's content hash is `e70403c6a068ce6fb8b9e91290e71c88e9427c605c721bf82db32482ccb37947`.
- **Share it:** this document works without a key: https://api.craigmbrown.com/v1/services/result/3af3be6ce79a?format=md
- **Not useful?** A job that could not be done is not charged (`insufficient_subject`). To anchor a re-run, pass the pages you trust as `"urls": [...]`.

Powered by BlindOracle · https://api.craigmbrown.com/skill.md
