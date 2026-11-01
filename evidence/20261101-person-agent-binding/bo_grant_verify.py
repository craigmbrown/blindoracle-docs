#!/usr/bin/env python3
"""Verify a BlindOracle job against the person-signed grant it names — from the outside.

RQ-BO-PERSON-AGENT-BINDING-01 task 7. Needs NO BlindOracle credential: it reads the public
receipt, the public grant, recomputes the EIP-191 signature against the person wallet (ECDSA
locally; ERC-1271 by an eth_call on Base for a smart wallet), checks that the person wallet
holds a live Coinbase Verified Account attestation on Base, and checks the job sits inside the
grant's SKU list, window and day cap. Every check prints PASS / FAIL / UNVERIFIED with why.

    python3 scripts/bo_grant_verify.py <job_id> [--api https://api.craigmbrown.com] [--rpc URL] [--json]

What a PASS proves: the person wallet signed these limits for this agent, that wallet is
Coinbase-verified, and this receipt is inside the limits. What it does NOT prove: that a human
was present at signing (read signer_detail.user_verified), or who drove the agent afterwards.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

API = "https://api.craigmbrown.com"
RPC = "https://mainnet.base.org"
INDEXER = "0x2c7eE1E5f416dfF40054c27A62f7B357C4E8619C"
EAS = "0x4200000000000000000000000000000000000021"
ATTESTER = "0x357458739F90461b99789350868CD7CF330Dd7EE"
SCHEMA = "0xf8b05c79f090979bf4a80270aba232dff11a10d9ca55c4f88de95317970f0de9"
ERC1271_MAGIC = "0x1626ba7e"


def _get(url: str) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "bo-grant-verify/1", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def _ts(s: str) -> int:
    return int(datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp())


def check_signature(message: str, signature: str, wallet: str, rpc: str = RPC,
                    erc1271: Optional[Callable[[str, bytes, bytes], Optional[bool]]] = None) -> Dict[str, Any]:
    """ECDSA recover first; else isValidSignature on Base. None = could not decide."""
    try:
        from eth_account import Account
        from eth_account.messages import encode_defunct
        from eth_utils import keccak
    except Exception as e:  # noqa: BLE001
        return {"ok": None, "method": "unavailable", "why": f"eth_account missing: {e}"}
    sig = bytes.fromhex(signature[2:] if signature.startswith("0x") else signature)
    msg = encode_defunct(text=message)
    if len(sig) == 65:
        try:
            if Account.recover_message(msg, signature=sig).lower() == wallet.lower():
                return {"ok": True, "method": "ecdsa"}
        except Exception:  # noqa: BLE001
            pass
    digest = keccak(b"\x19Ethereum Signed Message:\n" + str(len(message.encode())).encode() + message.encode())
    try:
        if erc1271 is None:
            from web3 import Web3
            w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 20}))
            abi = [{"name": "isValidSignature", "type": "function", "stateMutability": "view",
                    "inputs": [{"name": "hash", "type": "bytes32"}, {"name": "signature", "type": "bytes"}],
                    "outputs": [{"name": "", "type": "bytes4"}]}]
            c = w3.eth.contract(address=Web3.to_checksum_address(wallet), abi=abi)
            out = c.functions.isValidSignature(digest, sig).call()
            ok = ("0x" + bytes(out).hex()) == ERC1271_MAGIC
        else:
            ok = erc1271(wallet, digest, sig)
        if ok is None:
            return {"ok": None, "method": "erc1271", "why": "rpc undecided"}
        return {"ok": bool(ok), "method": "erc1271"}
    except Exception as e:  # noqa: BLE001
        return {"ok": None, "method": "erc1271", "why": f"{type(e).__name__}: {str(e)[:120]}"}


def check_coinbase_verified(wallet: str, rpc: str = RPC,
                            reader: Optional[Callable[[str], Optional[Dict[str, Any]]]] = None) -> Dict[str, Any]:
    """{ok, uid, attester, revoked} from the Coinbase indexer + EAS on Base. None = could not read."""
    try:
        if reader is None:
            from web3 import Web3
            w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={"timeout": 20}))
            idx = w3.eth.contract(address=INDEXER, abi=[{
                "name": "getAttestationUid", "type": "function", "stateMutability": "view",
                "inputs": [{"name": "recipient", "type": "address"}, {"name": "schemaUid", "type": "bytes32"}],
                "outputs": [{"name": "", "type": "bytes32"}]}])
            uid = idx.functions.getAttestationUid(Web3.to_checksum_address(wallet), bytes.fromhex(SCHEMA[2:])).call()
            if not uid or uid == b"\x00" * 32:
                return {"ok": False, "why": "no Coinbase Verified Account attestation for this wallet"}
            eas = w3.eth.contract(address=EAS, abi=[{
                "name": "getAttestation", "type": "function", "stateMutability": "view",
                "inputs": [{"name": "uid", "type": "bytes32"}],
                "outputs": [{"components": [
                    {"name": "uid", "type": "bytes32"}, {"name": "schema", "type": "bytes32"},
                    {"name": "time", "type": "uint64"}, {"name": "expirationTime", "type": "uint64"},
                    {"name": "revocationTime", "type": "uint64"}, {"name": "refUID", "type": "bytes32"},
                    {"name": "recipient", "type": "address"}, {"name": "attester", "type": "address"},
                    {"name": "revocable", "type": "bool"}, {"name": "data", "type": "bytes"}],
                    "name": "", "type": "tuple"}]}])
            a = eas.functions.getAttestation(uid).call()
            att = {"uid": "0x" + bytes(a[0]).hex(), "attester": a[7], "revocation_time": int(a[4]),
                   "expiration_time": int(a[3])}
        else:
            att = reader(wallet)
            if not att:
                return {"ok": False, "why": "no Coinbase Verified Account attestation for this wallet"}
        ok = (att["attester"].lower() == ATTESTER.lower() and int(att.get("revocation_time") or 0) == 0
              and (int(att.get("expiration_time") or 0) == 0 or att["expiration_time"] > datetime.now(timezone.utc).timestamp()))
        return {"ok": ok, "uid": att["uid"], "attester": att["attester"], "revoked": int(att.get("revocation_time") or 0) != 0}
    except Exception as e:  # noqa: BLE001
        return {"ok": None, "why": f"{type(e).__name__}: {str(e)[:120]}"}


def check_scope(receipt: Dict[str, Any], grant: Dict[str, Any], day_total_usd: Optional[float] = None) -> Dict[str, Any]:
    reasons: List[str] = []
    sku, settled = receipt.get("sku"), receipt.get("settled_at") or ""
    allow = grant.get("allow_skus") or []
    if allow and sku not in allow:
        reasons.append(f"sku {sku} not in allow_skus {allow}")
    try:
        t = _ts(settled[:19] + "Z") if settled else None
    except Exception:  # noqa: BLE001
        t = None
    if t is not None:
        if not (_ts(grant["not_before"]) <= t < _ts(grant["not_after"])):
            reasons.append(f"settled_at {settled} outside {grant['not_before']}..{grant['not_after']}")
        if grant.get("revoked_at") and t >= _ts(grant["revoked_at"]):
            reasons.append(f"settled after revocation at {grant['revoked_at']}")
    else:
        reasons.append("receipt has no settled_at")
    amt = float(receipt.get("amount_usd") or 0)
    cap = float(grant.get("max_usd_per_day") or 0)
    if amt > cap + 1e-9:
        reasons.append(f"amount {amt} exceeds daily cap {cap}")
    if day_total_usd is not None and day_total_usd > cap + 1e-9:
        reasons.append(f"day total {day_total_usd} exceeds daily cap {cap}")
    if grant.get("agent_name") and receipt.get("grant", {}).get("person_wallet", "").lower() != grant["person_wallet"].lower():
        reasons.append("receipt's person_wallet differs from the grant's")
    return {"ok": not reasons, "reasons": reasons}


def verify(job_id: str, api: str = API, rpc: str = RPC, fetch: Callable[[str], Dict[str, Any]] = _get,
           erc1271=None, eas_reader=None) -> Dict[str, Any]:
    out: Dict[str, Any] = {"job_id": job_id, "checks": {}}
    receipt = fetch(f"{api}/a2a/jobs/{job_id}/receipt")
    out["receipt"] = {k: receipt.get(k) for k in ("sku", "settled_at", "amount_usd", "charged", "settlement_status")}
    g = receipt.get("grant") or {}
    if not g.get("grant_id"):
        out["checks"]["receipt_names_grant"] = {"ok": False, "why": "this job was not bought under a person-signed grant"}
        out["verdict"] = "FAIL"
        return out
    out["checks"]["receipt_names_grant"] = {"ok": True, "grant_id": g["grant_id"]}
    grant = fetch(f"{api}/a2a/grants/{g['grant_id']}")
    out["grant"] = {k: grant.get(k) for k in ("agent_name", "person_wallet", "allow_skus", "max_usd_per_day",
                                                "not_before", "not_after", "revoked_at", "signature_method")}
    out["checks"]["signature"] = check_signature(grant["message"], grant["signature"], grant["person_wallet"], rpc, erc1271)
    out["checks"]["person_coinbase_verified"] = check_coinbase_verified(grant["person_wallet"], rpc, eas_reader)
    out["checks"]["job_within_grant"] = check_scope(receipt, grant)
    sd = grant.get("signer_detail") or {}
    out["human_present_at_signing"] = (sd.get("user_verified") if sd.get("owner_kind") == "passkey"
                                       else "not provable: signed with a key, not a passkey")
    oks = [c.get("ok") for c in out["checks"].values()]
    out["verdict"] = "PASS" if all(o is True for o in oks) else "UNVERIFIED" if any(o is None for o in oks) else "FAIL"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("job_id")
    ap.add_argument("--api", default=API)
    ap.add_argument("--rpc", default=RPC)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    r = verify(a.job_id, a.api, a.rpc)
    if a.json:
        print(json.dumps(r, indent=1))
    else:
        print(f"job {a.job_id}: {r['verdict']}")
        for k, v in r["checks"].items():
            tag = "PASS" if v.get("ok") is True else "UNVERIFIED" if v.get("ok") is None else "FAIL"
            print(f"  {tag:<10} {k}  {v.get('why') or v.get('reasons') or v.get('method') or ''}")
        print(f"  human present at signing: {r.get('human_present_at_signing')}")
    return 0 if r["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
