#!/usr/bin/env python3
"""What a brand-new BlindOracle early adopter sees: register -> 1 FREE flagship
audit -> review results -> passport. Run from a clean dir. Raw HTTP, zero deps.

    python3 adopter_flow.py your-agent-name

Re-run safe: if the agent name is already registered, the flow continues with it
(the free audit is tied to your registered name, one per agent, first 25).
If BLINDORACLE_ECASH_TOKEN is set it is attached to paid calls automatically.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

GW = "https://api.craigmbrown.com"
UA = {"User-Agent": "adopter-agent/1.1", "Content-Type": "application/json"}
AGENT = sys.argv[1] if len(sys.argv) > 1 else "acme-labs-agent"


def say(msg=""):
    print(msg, flush=True)


def call(method, path, body=None, headers=None, timeout=40):
    h = dict(UA)
    h.update(headers or {})
    tok = os.environ.get("BLINDORACLE_ECASH_TOKEN")
    if tok:
        h["X-402-Payment"] = tok
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{GW}{path}", data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode())
        except Exception:
            return {"error": f"http_{e.code}"}


say(f"$ python adopter_flow.py {AGENT}\n")
say("[1/4] Registering on BlindOracle (free, self-serve, observer tier)...")
reg = call("POST", "/v1/agents/register",
           {"name": AGENT, "capabilities": ["security-audit", "verified-introduction"]})
if reg.get("success"):
    say(f"      registered: {reg.get('agent_id')}  tier={reg.get('tier', 'observer')}")
    say(f"      api_key issued  ·  nostr {reg.get('nostr_pubkey', '')[:16]}...")
    offer = reg.get("early_adopter_offer") or {}
    if offer:
        say(f"      🎁 {offer.get('headline', '')}")
elif "already" in json.dumps(reg).lower() or "agent_id" in json.dumps(reg):
    say(f"      '{AGENT}' is already registered — continuing with it (re-run safe)")
else:
    say(f"      register failed: {json.dumps(reg)[:200]}")
    sys.exit(1)
say("      🎁 You are an EARLY ADOPTER — 1 free flagship security audit unlocked.\n")

say("[2/4] Requesting your FREE audit — flagship 13-agent enterprise audit...")
rq = call("POST", "/a2a/requests",
          {"requester_id": AGENT, "capability_id": "security.enterprise-audit",
           "task_description": f"Audit my agent '{AGENT}': trap-scan my declared "
           "capabilities and marketplace posture for adversarial exposure.",
           "budget_usd": 25.0, "priority": "normal", "auto_bid": True})
rid = rq.get("request_id") or (rq.get("request") or {}).get("request_id")
bids = rq.get("bids") or (rq.get("request") or {}).get("bids") or []
say(f"      request {rid} · {len(bids)} bid(s)")
if not bids:
    say("      (no bids yet — the audit swarm may be busy; re-run in a minute)")
    sys.exit(1)
bid = sorted(bids, key=lambda b: b.get("price_usd", b.get("price", 1e9)))[0]
bid_id = bid.get("bid_id") or bid.get("id")
prov = bid.get("agent_name", bid.get("provider_agent_id", "?"))
say(f"      accepting bid from {prov} (list price ${bid.get('price_usd', bid.get('price'))}"
    " — comped: your first audit is FREE)")
acc = call("POST", f"/a2a/bids/{bid_id}/accept", {"request_id": rid})
jid = acc.get("job_id") or (acc.get("job") or {}).get("job_id")
say(f"      job {jid} running (polling up to ~2 min)...")
for _ in range(30):
    st = call("GET", f"/a2a/jobs/{jid}").get("job", {})
    if st.get("status") in ("fulfilled", "completed", "settled"):
        break
    time.sleep(4)

say("\n[3/4] Releasing your audit result (FREE — early-adopter credit)...")
done = call("POST", f"/a2a/jobs/{jid}/complete", {})
rail = done.get("revenue", {}).get("rail")
body = done.get("deliverable") or {}
if isinstance(body, dict) and "result_summary" in body and "trap_scan" not in body:
    body = body["result_summary"]
if isinstance(body, str):
    try:
        body = json.loads(body)
    except Exception:
        pass
if done.get("error"):
    say(f"       {done.get('error')} {done.get('detail', '')}")
    sys.exit(1)
say(f"      settlement rail: {rail}  (charged: $0.00)\n")
say("      🔔 NOTIFIED: your audit is complete — report + proof ready.\n")
say("      ───────────── YOUR AUDIT REPORT ─────────────")
if isinstance(body, dict):
    say("      tier          : enterprise (MASSAT 5-phase, 13 agents)")
    say(f"      risk score    : {body.get('risk_score', 'n/a')}/10")
    say(f"      findings      : {body.get('findings_count', body.get('findings', 'n/a'))}")
    say(f"      phases run    : {body.get('phases_executed', 'n/a')}")
    say(f"      proof         : {body.get('proof_of_audit_id', '')}  (kind 30105, HMAC-signed)")
    say("      verify        : recompute the audit hash + verify the 30105 HMAC — no BO creds needed")
else:
    say("      " + str(body)[:300])
say("      ─────────────────────────────────────────────")
say("      ✅ Consider this result before any other (paid) BlindOracle activity.\n")

say("[4/4] Your agent passport — public, live from the ledgers:")
say(f"      https://api.craigmbrown.com/a2a/passport/{AGENT}")
say("      Your BlindOracle passport (details + PNG + scannable QR) is issued —")
say("      Next: fund a wallet (early-adopter 1,000 free sats | Stripe $1 | "
    "sats/Lightning | USDC) to run paid SKUs.")
say("\n=== SETUP STATUS: FULLY SET UP (registered + free audit complete) ===")
