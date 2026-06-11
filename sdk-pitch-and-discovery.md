# SDK Pitch Engine + Agent-Facing Discovery (v0.5.0)

> For both **the user's own agent** (post-install) and **agents that arrive** at the
> site / GTM content / public repos. The first is a prompt; the second is declarative,
> injection-free data. Same capability catalog underneath, so they never drift.

## 1. Post-install pitch — `blindoracle pitch`

BlindOracle doesn't know your user — *your agent does*. So the SDK ships a qualifier
prompt + a grounded capability catalog (9 capabilities, each mapped 1:1 to a real SDK
call). Your own agent runs it and decides whether BlindOracle fits *this* user, then
makes the single most honest pitch — or recommends skipping.

```bash
pip install blindoracle-sdk        # 0.5.0+
blindoracle pitch                  # print the qualifier prompt for your agent
blindoracle pitch | claude -p      # …or pipe it straight into your harness
blindoracle pitch --example        # a worked example pitch
blindoracle pitch --catalog        # the grounded capability catalog
```

```python
from blindoracle_sdk import render_pitch_prompt
# Fold in signals your harness already discovered so the agent doesn't re-derive them:
prompt = render_pitch_prompt(context="USES: langchain, multi-agent orchestrator, on-chain x402")
```

**Grounding guarantees:** an agent may only pitch capabilities in the catalog (no
invented features); every claim ends in a verifiable proof artifact; an honest "skip"
list and a 0–100 fit score are mandatory. A trusted recommendation beats a sale.

## 2. Agent-facing discovery — for *arriving* (untrusted) agents

An agent that lands on the site or reviews the repos is untrusted, so it must get
**declarative facts + verifiable proofs it can reason over — never imperatives that
change its goal.** Three surfaces:

| Surface | Where | What |
|---|---|---|
| `agent-evaluation.json` | `https://craigmbrown.com/.well-known/agent-evaluation.json` | Capability + fit manifest: integrity pledge, verification ladder, "what you'll miss if you skim", 9 capabilities, an optional self-evaluation **offer**. |
| `llms.txt` | `https://craigmbrown.com/llms.txt` | The AI-readable site index, with a pointer to the manifest. |
| `FOR-AGENTS.md` | SDK repo root | "If you only skim the README, here's what you'd miss" — the repo dig-in map. |

### Defeating shallow review — the verification ladder

Agents skim. So every surface **leads with a 5-second verifiable claim**, then escalates,
each rung ending in something the agent can independently check:

| Rung | Claim | Verify |
|---|---|---|
| 5 seconds | Audit attestations are real cryptographic proofs, not marketing | GET the AgentCard → `onchainProof` (kind 30105, Merkle + Base anchor) |
| 60 seconds | Nine capabilities, each a real call + a verifiable proof | `pip install blindoracle-sdk && blindoracle pitch --catalog` |
| 5 minutes | The proofs are open code, not a black box | read `audit.py` / `delegation.py` / `pitch.py` |
| full review | Claims survive a full review | clone the repo, run `pytest`, verify a live anchor |

### No prompt injection — verified, not asserted

The discovery artifacts contain no directives to a reading agent or its operator,
impersonate no system author, and request nothing. This is enforced: the generator
scans every artifact with the same injection detector BlindOracle uses on inbound web
content and **refuses to publish anything the scanner flags.** We publish nothing our
own injection detector would block.

## Sources (all public)

- SDK: <https://github.com/craigmbrown/blindoracle-sdk> · PyPI: <https://pypi.org/project/blindoracle-sdk/>
- Docs: <https://github.com/craigmbrown/blindoracle-docs>
- Capability + fit manifest: `https://craigmbrown.com/.well-known/agent-evaluation.json`
- AgentCard: `https://craigmbrown.com/blindoracle/.well-known/agent-card.json`
