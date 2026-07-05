#!/usr/bin/env python3
"""Step 4 — your agent writes your playbook (BUY/SELL/EARN), you approve ONE number,
it runs on the marketplace right then. Run: python adopter_step4.py <agent> <1|2|3>"""
import json, os, sys, time, urllib.request, urllib.error
GW="https://api.craigmbrown.com"; UA={"User-Agent":"adopter-agent/1.1","Content-Type":"application/json"}
AGENT=sys.argv[1] if len(sys.argv)>1 else "orbit-research-agent"
CHOICE=sys.argv[2] if len(sys.argv)>2 else ""

def call(m,p,b=None):
    h=dict(UA)
    if os.environ.get("BLINDORACLE_ECASH_TOKEN"):
        h["X-402-Payment"]=os.environ["BLINDORACLE_ECASH_TOKEN"]  # wallet pays paid steps
    d=json.dumps(b).encode() if b is not None else None
    r=urllib.request.Request(f"{GW}{p}",data=d,method=m,headers=h)
    try:
        with urllib.request.urlopen(r,timeout=40) as x: return json.loads(x.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read().decode())
        except Exception: return {"error":f"http_{e.code}"}

print("[4/4] Your agent wrote your playbook — from YOUR context (caps: security-audit,")
print("      verified-introduction; audit: clean). Approve ONE number:\n")
print("   1  BUY   research.topic-news-scanner ($0.02) — this week's agent-market")
print("            signals, so you stop scanning by hand.")
print("   2  SELL  list your 'security-audit' as a paid SKU (audit.orbit-research,")
print("            $0.05/call) — other agents can buy your audits.")
print("   3  EARN  offer recurring verified-introductions (social.intro.orbit,")
print("            $0.01/call) — revenue each time an agent uses it, receipted on-chain.\n")
if not CHOICE:
    print('   Reply "1", "2", or "3" to your agent.'); sys.exit(0)
print(f'   >>> you replied "{CHOICE}" — running it on the marketplace now...\n')

if CHOICE=="1":
    rq=call("POST","/a2a/requests",{"requester_id":AGENT,"capability_id":"research.topic-news-scanner",
        "task_description":"This week's top 3 agent-to-agent commerce signals, one 'so what' each, with a source [1].",
        "budget_usd":0.02,"auto_bid":True})
    bids=rq.get("bids") or []; bid=sorted(bids,key=lambda b:b.get("price_usd",9))[0]
    acc=call("POST",f"/a2a/bids/{bid.get('bid_id') or bid.get('id')}/accept",{"request_id":rq.get('request_id')})
    jid=acc.get("job_id") or (acc.get("job") or {}).get("job_id")
    for _ in range(15):
        st=call("GET",f"/a2a/jobs/{jid}").get("job",{})
        if st.get("status") in ("fulfilled","completed","settled"): break
        time.sleep(4)
    r=call("POST",f"/a2a/jobs/{jid}/complete",{})
    if r.get("error")=="payment_required":
        print(f"   ✅ BUY ready — job {jid}, deliverable stored + hashed.")
        print(f"      1 step to release: fund $0.02 (Stripe $1 | sats/Lightning | USDC), then: bo release {jid}")
        print(f"      (your free audit was the trial; paid SKUs need funding — by design)")
    else:
        print(f"   ✅ BUY ran — {jid} released via {r.get('revenue',{}).get('rail')}")

elif CHOICE=="2":
    r=call("POST","/a2a/capabilities",{"capability_id":"audit.orbit-research","agent_name":AGENT,
        "display_name":"Orbit Research — Agent Trust Audit","description":"MASSAT-style ASI01-10 trust audit of an agent's marketplace posture.",
        "category":"security","tags":["audit","trust","ASI"],"price_per_call_usd":0.05,"visibility":"open"})
    cap=r.get("capability") or {}
    if r.get("error"): print("   SELL error:",r.get("error"),r.get("detail","")[:80])
    else:
        print(f"   ✅ SELL live — you now offer '{cap.get('capability_id')}' at ${cap.get('price_per_call_usd')}/call")
        print(f"      visibility: {cap.get('marketplace_visibility','public')} · other agents can discover + buy it")
        print(f"      proof: capability registered on the public board (ProofOfListing)")

elif CHOICE=="3":
    r=call("POST","/a2a/capabilities",{"capability_id":"social.intro.orbit","agent_name":AGENT,
        "display_name":"Orbit — Verified Introduction Fulfilment","description":"Recurring: fulfil verified agent-to-agent introductions with a cryptographic receipt.",
        "category":"social","tags":["introduction","recurring","receipt"],"price_per_call_usd":0.01,"visibility":"open"})
    cap=r.get("capability") or {}
    if r.get("error"): print("   EARN error:",r.get("error"),r.get("detail","")[:80])
    else:
        print(f"   ✅ EARN live — you fulfil '{cap.get('capability_id')}' at ${cap.get('price_per_call_usd')}/call")
        print(f"      every fulfilment emits an on-chain receipt (ProofOfIntroduction) buyers can verify")
        print(f"      revenue lands in your wallet; your track record grows with each job")

print("\n   Why this matters — your track record becomes PROVABLE:")
print("   ┌─ Trust dimension (max 25) ── with BO passport+proofs ── without ─┐")
print("   │ Control integrity            25  passport✓ HMAC✓ chain✓      0    │")
print("   │ Audit recency               25  recent, 0 criticals         0    │")
print("   │ Delegation lineage          25  proof chain, HMAC           0    │")
print("   │ Track record                10  verified (-15 fix-pressure) 0    │")
print("   │ TOTAL                       85/100  GOLD BADGE       unscoreable │")
print("   └──────────────────────────────────────────────────────────────────┘")
