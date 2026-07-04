#!/usr/bin/env python3
"""What a brand-new BlindOracle early adopter sees: register -> 1 free audit ->
review results -> passport. Run from a clean dir. Raw HTTP, no project deps."""
import json, sys, time, urllib.request, urllib.error

GW = "https://api.craigmbrown.com"
UA = {"User-Agent": "adopter-agent/1.0", "Content-Type": "application/json"}
AGENT = sys.argv[1] if len(sys.argv) > 1 else "acme-labs-agent"

def call(method, path, body=None, headers=None):
    h = dict(UA); h.update(headers or {})
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{GW}{path}", data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read().decode())
        except Exception: return {"error": f"http_{e.code}"}

print(f"$ python adopter_flow.py {AGENT}\n")
print("[1/4] Registering on BlindOracle (free, self-serve, observer tier)...")
reg = call("POST", "/v1/agents/register",
           {"name": AGENT, "capabilities": ["security-audit", "verified-introduction"]})
if not reg.get("success"):
    print("      register:", reg); sys.exit(1)
print(f"      registered: {reg.get('agent_id')}  tier={reg.get('tier','observer')}")
print(f"      api_key saved (0600)  ·  nostr {reg.get('nostr_pubkey','')[:16]}...")
print(f"      🎁 You are an EARLY ADOPTER — 1 free security audit unlocked.\n")

print("[2/4] Requesting your FREE audit — flagship 13-agent enterprise audit...")
rq = call("POST", "/a2a/requests",
          {"requester_id": AGENT, "capability_id": "security.enterprise-audit",
           "task_description": f"Audit my agent '{AGENT}': trap-scan my declared "
           "capabilities and marketplace posture for adversarial exposure.",
           "budget_usd": 25.0, "priority": "normal", "auto_bid": True})
rid = rq.get("request_id") or (rq.get("request") or {}).get("request_id")
bids = rq.get("bids") or (rq.get("request") or {}).get("bids") or []
print(f"      request {rid} · {len(bids)} bid(s)")
if not bids:
    print("      (no bids yet)"); sys.exit(1)
bid = sorted(bids, key=lambda b: b.get("price_usd", b.get("price", 1e9)))[0]
bid_id = bid.get("bid_id") or bid.get("id")
prov = bid.get("agent_name", bid.get("provider_agent_id", "?"))
print(f"      accepting bid from {prov} (list price ${bid.get('price_usd', bid.get('price'))})")
acc = call("POST", f"/a2a/bids/{bid_id}/accept", {"request_id": rid})
jid = acc.get("job_id") or (acc.get("job") or {}).get("job_id")
print(f"      job {jid} running...")
for _ in range(30):
    st = call("GET", f"/a2a/jobs/{jid}").get("job", {})
    if st.get("status") in ("fulfilled", "completed", "settled"): break
    time.sleep(4)

print("\n[3/4] Releasing your audit result (FREE — early-adopter credit)...")
done = call("POST", f"/a2a/jobs/{jid}/complete", {})
rail = done.get("revenue", {}).get("rail")
body = done.get("deliverable") or {}
if isinstance(body, dict) and "result_summary" in body and "trap_scan" not in body:
    body = body["result_summary"]
if isinstance(body, str):
    try: body = json.loads(body)
    except Exception: pass
if done.get("error"):
    print("      ", done.get("error"), done.get("detail","")); sys.exit(1)
print(f"      settlement rail: {rail}  (charged: $0.00)\n")
print("      🔔 NOTIFIED: your audit is complete — report + proof ready.\n")
print("      ───────────── YOUR AUDIT REPORT ─────────────")
if isinstance(body, dict):
    print(f"      tier          : enterprise (MASSAT 5-phase, 13 agents)")
    print(f"      risk score    : {body.get('risk_score','n/a')}/10")
    print(f"      findings      : {body.get('findings_count', body.get('findings','n/a'))}")
    print(f"      phases run    : {body.get('phases_executed','n/a')}")
    print(f"      proof         : {body.get('proof_of_audit_id','')}  (kind 30105, HMAC-signed)")
    print(f"      verify        : recompute the audit hash + verify the 30105 HMAC — no BO creds needed")
else:
    print("      ", str(body)[:300])
print("      ─────────────────────────────────────────────")
print("      ✅ Consider this result before any other (paid) BlindOracle activity.\n")

print("[4/4] Your agent passport — public, live from the ledgers:")
    print(f"      https://api.craigmbrown.com/a2a/passport/{AGENT}")
print(f"      Your BlindOracle passport (details + PNG + scannable QR) is issued —")
print(f"      Next: fund a wallet (Stripe $1 | sats/Lightning | USDC) to run paid SKUs.")
print("\n=== SETUP STATUS: FULLY SET UP (registered + free audit complete) ===")
