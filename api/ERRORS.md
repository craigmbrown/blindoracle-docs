<!-- Copyright (c) 2026 Craig M. Brown. All rights reserved. -->
# BlindOracle API — Error Reference

<!-- @REQ-ID: RQ-STRIPE-API-DOCS -->

Every BlindOracle API error returns a JSON body with a stable shape so both
humans and agents can branch on it deterministically:

```json
{ "error": "human-readable message", "code": "machine_code", "detail": { } }
```

Branch on `code` (stable), show `error` (may change), inspect `detail` when present.

## HTTP status codes

| Status | `code` | Meaning | What to do |
|---|---|---|---|
| `200` | — | Success | Proceed. |
| `201` | — | Created (e.g. registration) | Store the returned `api_key` / `agent_id`. |
| `400` | `bad_request` | Malformed request | Fix the request shape; see `detail`. |
| `401` | `unauthorized` | Missing/invalid `X-API-Key` | Re-check your key; re-register if revoked. |
| `402` | `payment_required` | x402 settlement needed | Settle via the x402 rail / include a valid payment token, then retry. |
| `403` | `forbidden` | Key valid but tier/scope insufficient | Upgrade tier or request the capability. |
| `404` | `not_found` | No such job/agent/resource | Verify the id; jobs expire after retention window. |
| `409` | `conflict` | Duplicate (e.g. idempotency key reused) | Treat as already-done; fetch the existing resource. |
| `422` | `validation_error` | Body failed schema validation | Inspect `detail[].loc` (FastAPI validation array). |
| `429` | `rate_limited` | Too many requests | Back off; honor `Retry-After`. |
| `500` | `internal_error` | Server fault | Retry with backoff; if persistent, contact support. |
| `503` | `unavailable` | Dependency down (LLM/chain/federation) | Retry with exponential backoff. |

## The 402 payment flow

A `402 Payment Required` is normal, not a failure — it's how paid SKUs gate
work. The response carries the price + settlement instructions:

```json
{
  "error": "payment required",
  "code": "payment_required",
  "detail": { "amount_usdc": "0.02", "rail": "base_usdc_x402", "capability_id": "news-scanner" }
}
```

Settle on the named `rail`, then re-issue the request with the payment token.

## Idempotency

Mutating endpoints (`POST /api/v1/jobs/submit`, payments) accept an
`Idempotency-Key` header. Reusing a key returns the original result (`409` if
still in flight) — safe to retry on network errors without double-charging.

## Validation errors (`422`)

FastAPI returns the standard validation array under `detail`:

```json
{ "detail": [ { "loc": ["body", "job_type"], "msg": "field required", "type": "value_error.missing" } ] }
```
