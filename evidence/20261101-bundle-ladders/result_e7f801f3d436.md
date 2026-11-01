# bundle.prehire-ladder

Job `e7f801f3d436` · receipt: https://api.craigmbrown.com/v1/proofs/settlement/e7f801f3d436

---

```json
{
  "deliverable_type": "sku_bundle",
  "bundle_id": "bundle.prehire-ladder",
  "status": "completed_partial",
  "price_usd": 4.734,
  "steps": [
    {
      "order": 1,
      "sku_id": "reputation.lookup",
      "list_price_usd": 0.01,
      "share_usd": 0.009,
      "child_job_id": "e7f801f3d436-s1",
      "status": null,
      "content_sha256": "228d6dc79e509c44f7a31ddffed0aaa2235c18f7320789725c1f3ca51ed3a28f",
      "deliverable": {
        "deliverable_type": "reputation_record",
        "trust_layer": "BlindOracle ProofDB (settled-job ledger) + ERC-8004 identity",
        "score_basis": "Derived from settled BlindOracle jobs recorded in an append-only ledger. This is NOT the on-chain ERC-8004 ReputationRegistry aggregate, which is an unweighted mean movable by a single feedback and independently measured as Sybil-saturated (arXiv:2606.26028). ERC-8004 supplies identity here, not the score. An agent with no settled history scores an honest zero.",
        "runs_basis": "total_runs / successful_runs count recorded agent executions (logs/blindoracle-outputs + proof-chain logs) in any role \u2014 they are NOT marketplace deliveries or settled jobs; for those use agent.prehire-check (deliveries vs purchases) or procurement.trust-layer (settled_jobs)",
        "roster_size": 324,
        "computed_at": "2026-11-01T18:13:03.157218+00:00",
        "generated_at": "2026-11-01T18:23:21.327557+00:00",
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
      "sku_id": "agent.prehire-check",
      "list_price_usd": 0.25,
      "share_usd": 0.225,
      "child_job_id": "e7f801f3d436-s2",
      "status": null,
      "content_sha256": "4e8900383294cdecd1269a75442ab5a361a20e009a4695f8666300b1b606beb6",
      "deliverable": {
        "deliverable_type": "prehire_check",
        "verdict": "CAUTION",
        "subject": {
          "agent_name": "work-bot",
          "wallet": null,
          "task_id": null
        },
        "reasons": [
          "no BlindOracle audit on record for this agent",
          "zero recorded completed deliveries as provider",
          "never seen in any local ledger"
        ],
        "red_flags": [
          "not_audited",
          "no_delivery_history",
          "no_local_history"
        ],
        "audit_status": null,
        "audit_proof_id": null,
        "deliveries": 0,
        "purchases": 0,
        "counts_basis": {
          "deliveries": "distinct settled jobs where the agent was the provider (revenue ledger) plus approved claw deliverables",
          "purchases": "distinct ledger rows where the agent was the requester (buyer activity, never counted as delivery)"
        },
        "first_seen": null,
        "sources_available": {
          "audited_agents_registry": true,
          "wallet_roster": true,
          "revenue_ledger": true,
          "claw_completions": true
        },
        "method": "deterministic ledger lookup \u2014 zero LLM, reproducible",
        "generated_at": "2026-11-01T18:23:21.444578+00:00",
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
      "order": 3,
      "sku_id": "security.massat-audit",
      "list_price_usd": 5.0,
      "share_usd": 4.5,
      "child_job_id": "e7f801f3d436-s3",
      "outcome": "skipped_by_option",
      "status": null,
      "why": "audit only for high-stakes delegation with a target"
    }
  ],
  "steps_delivered": 2,
  "stopped_by": null,
  "refund_due_usd": 4.5,
  "refund_basis": "share of the paid price for steps that did not run, were skipped by option, or returned a no-charge result; shares proportional to list price",
  "refund_promise": "One payment covers every step. If a gate stops the ladder early, or a step returns a no-charge result, the unexecuted and no-charge steps' share of what you paid is refunded on the rail you paid with (USDC to the paying wallet, starter credit to the note, prepaid back to the balance). Shares are proportional to each step's list price.",
  "controls": "each step ran as its own job through job_executor.execute \u2014 allowlist, breaker, input content-trap scan, SoD gate, LLM daily cap, offshore refusal and the provider policy all applied per step",
  "content_sha256": "4c7f8874074a63945a011d55343c0fd84eeb3372d8ff2d3a571266b7cf518c0e",
  "generated_at": "2026-11-01T18:23:21.450862+00:00"
}
```

---

## How to use this

- **Check it:** each [n] points to a page in the source list. Open the ones your decision rests on.
- **Prove it:** https://api.craigmbrown.com/v1/proofs/settlement/e7f801f3d436 is a receipt anyone can fetch, no key needed; this result's content hash is `4c7f8874074a63945a011d55343c0fd84eeb3372d8ff2d3a571266b7cf518c0e`.
- **Share it:** this document works without a key: https://api.craigmbrown.com/v1/services/result/e7f801f3d436?format=md
- **Not useful?** A job that could not be done is not charged (`insufficient_subject`). To anchor a re-run, pass the pages you trust as `"urls": [...]`.

Powered by BlindOracle · https://api.craigmbrown.com/skill.md
