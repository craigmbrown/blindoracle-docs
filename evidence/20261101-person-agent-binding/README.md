# Evidence pack — four agents, one person-signed grant each (2026-11-01)

The raw files behind the BlindOracle post *What should a receipt prove when an AI agent spends your money?*
Nothing here is revenue: the money was our own starter credit and one cent of our own prepaid balance.
Human-readable index with the same recipe: `index.html` (also served at
https://craigmbrown.com/blindoracle/evidence/20261101-person-agent-binding/).

| File | What it is |
|---|---|
| `asset.md` | the delivered research brief (job `63b7f3e8c5f7`, bought by Claude from claude.ai under grant `8d8c8a90…`) |
| `run.jsonl` | the run log; with `asset.md` it is the anchored digest's preimage |
| `checkpoint.preimage` / `checkpoint.digest` | the exact byte stream `name\0bytes\0` over `run.jsonl` then `asset.md`, and its sha256 |
| `checkpoint.base.json` | Base tx `0xf53be042…77a4`, block 53375797, calldata = digest |
| `checkpoint.ots` / `checkpoint.ots.json` | OpenTimestamps stamp over `checkpoint.preimage` and its status at publish time |
| `grants.json` | the four person-signed grants (message + signature + verify recipe), live at `api.craigmbrown.com/a2a/grants/<id>` |
| `receipts.json` | the five board receipts as we saw them |
| `witness_attestations.json` | four-judge verdicts per job from BlindOracle's witness pool |
| `nostr_publish_rows.json` | the kind-30013 events (ids, relays) for three jobs |
| `deliverables/` | every deliverable the agents received |
| `trail.md` / `trail.json` | per-step REQUESTED / RECEIVED / QUALITY / MODEL SAID |
| `RUN.md` | the narrative log, including what went wrong |
| `VALIDATION.md` | independent read-only re-check (verdict: verified with notes) |
| `claims.md` | what we allow ourselves to say, with evidence per claim |
| `bo_grant_verify.py` | the verifier: `python3 bo_grant_verify.py <job_id>` (stdlib + `web3`) |
| `SHA256SUMS` | sha256 of every file above (not `index.html` / this README) |

## Verify it without us

```bash
sha256sum -c SHA256SUMS                      # every file byte-identical to what we published

# 1. digest recomputed from the files == calldata of the Base tx
python3 - <<'PY'
import hashlib
h=hashlib.sha256()
for n in ("run.jsonl","asset.md"):
    h.update(n.encode()+b"\0"+open(n,"rb").read()+b"\0")
print(h.hexdigest())
PY
curl -s https://mainnet.base.org -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"eth_getTransactionByHash","params":["0xf53be042c54310ac10fed3b90b36fdd069e60fb6f508be5c91a10108774577a4"]}'
# -> "input" is 0x + that digest, blockNumber 0x32e6c35 (53375797), from == to

# 2. Bitcoin
pip install opentimestamps-client && ots upgrade checkpoint.ots && ots verify checkpoint.ots

# 3. ERC-1271: did the person's smart wallet sign the grant?  (pip install web3)
python3 - <<'PY'
import json
from web3 import Web3
from eth_account.messages import encode_defunct, _hash_eip191_message
w3=Web3(Web3.HTTPProvider("https://mainnet.base.org"))
g=json.load(open("grants.json"))["4a650c09252afa2d5139562e66a01ade"]
d=_hash_eip191_message(encode_defunct(text=g["message"]))
abi=[{"name":"isValidSignature","type":"function","stateMutability":"view",
      "inputs":[{"name":"hash","type":"bytes32"},{"name":"signature","type":"bytes"}],"outputs":[{"name":"","type":"bytes4"}]}]
c=w3.eth.contract(address=Web3.to_checksum_address(g["person_wallet"]),abi=abi)
print(c.functions.isValidSignature(d,bytes.fromhex(g["signature"][2:])).call().hex())   # 1626ba7e
PY

# 4. Coinbase Verified Account attestation on that wallet (EAS indexer on Base)
python3 - <<'PY'
from web3 import Web3
w3=Web3(Web3.HTTPProvider("https://mainnet.base.org"))
abi=[{"name":"getAttestationUid","type":"function","stateMutability":"view",
      "inputs":[{"name":"recipient","type":"address"},{"name":"schemaUid","type":"bytes32"}],"outputs":[{"name":"","type":"bytes32"}]}]
idx=w3.eth.contract(address="0x2c7eE1E5f416dfF40054c27A62f7B357C4E8619C",abi=abi)
print(idx.functions.getAttestationUid("0x98EC9cAff3D6C555b462957d2390D274aec8a25B",
      bytes.fromhex("f8b05c79f090979bf4a80270aba232dff11a10d9ca55c4f88de95317970f0de9")).call().hex())  # non-zero
PY

# 5. receipt names the grant; SKU in allow_skus, amount under the daily cap, time inside the window
curl -s https://api.craigmbrown.com/a2a/jobs/9fc2233c-d5e/receipt | python3 -m json.tool
python3 bo_grant_verify.py 9fc2233c-d5e

# 6. witness events on relays we do not run (pip install websocket-client)
python3 - <<'PY'
import json, websocket
eid="76d9f34e3b29716411a975bc438686cafd15456369b6bb1d9f1475ce8a02306c"
for relay in ("wss://nos.lol","wss://relay.primal.net","wss://relay.snort.social","wss://offchain.pub"):
    ws=websocket.create_connection(relay,timeout=15); ws.send(json.dumps(["REQ","q",{"ids":[eid]}]))
    m=json.loads(ws.recv()); ws.close(); print(relay, m[0], m[2]["kind"] if m[0]=="EVENT" else "-")
PY
```

Limits, stated: the grant signatures are from a smart-wallet owner key, not a passkey, so they prove the verified wallet signed, not that a human was present. Witness scores are model judgements and can be wrong (the SPLIT verdict on `78428f2c-2ca` is kept). The Nostr event for `9fc2233c-d5e` carries a hash taken before release with a different serialisation and does not match that receipt (logged defect); the other two do.
