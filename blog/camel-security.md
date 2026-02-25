# CaMel 4-Layer Security for Multi-Agent Systems

*How BlindOracle protects agent financial operations with Contextualized Manipulation Evaluation Layers, Byzantine consensus, and anti-persuasion defenses.*

## The Problem: Multi-Agent Systems Are Attack Surfaces

A single AI agent with a settlement account is a security concern. Twenty-five AI agents with accounts, shared state, and autonomous settlement authority are a security emergency. The attack vectors multiply with every agent added to the network:

- **Prompt injection**: A malicious input tricks an agent into executing unauthorized operations [1]. In a financial system, this means unauthorized transfers, position manipulation, or settlement fraud.
- **Agent collusion**: Compromised agents coordinate to bypass consensus thresholds. If three agents in a five-agent consensus pool are compromised, they control the outcome.
- **Behavioral drift**: An agent's decision patterns shift gradually over time -- due to fine-tuning contamination, context poisoning, or adversarial training data -- until its outputs no longer align with its security constraints [3].
- **Authority escalation**: An agent authorized for read operations manipulates its context to gain write access to settlement functions.

Traditional web application security (firewalls, WAFs, rate limiting) was not designed for these threats [2]. The attack surface is the agent's reasoning process itself.

## CaMel Architecture Overview

CaMel -- Contextualized Manipulation Evaluation Layer -- is a 4-layer defense architecture purpose-built for multi-agent financial systems. Each layer operates independently, so a failure or bypass at one layer does not compromise the others.

The design principle is defense in depth [5]: every request must pass through all four layers before reaching the settlement engine. There is no fast path that skips validation.

### Layer 1: Rate Limiting and Input Sanitization

The first defense line handles volumetric attacks and malformed inputs before they reach any agent logic.

- **Rate limiting**: Per-agent throttling at 60 requests per minute. Agents that exceed this threshold are temporarily blocked. The rate limit state tracks request timestamps in a sliding window, not a fixed counter, so burst patterns are handled correctly.
- **Input sanitization**: All request parameters are validated against strict schemas. String inputs are checked for injection patterns including prompt injection markers, shell metacharacters, and SQL fragments. Numeric inputs are bounds-checked against the fee schedule constraints.
- **Request fingerprinting**: Each request is hashed and stored for deduplication. Replay attacks -- where a valid request is captured and resubmitted -- are rejected if the fingerprint has been seen within the deduplication window.

### Layer 2: Byzantine Consensus

Critical operations require agreement from multiple independent validator agents before execution [6]. This is the layer that prevents a single compromised agent from unilaterally executing high-value operations.

- **Standard threshold**: 67% agreement (2 of 3 validators) for routine operations like position placement and balance queries.
- **High-value threshold**: 80% agreement (4 of 5 validators) for operations above configurable value thresholds, including settlements, cross-rail transfers, and guardian configuration changes.
- **Validator independence**: Each validator runs in an isolated context with its own LLM inference. Validators do not share context windows, prompt histories, or intermediate reasoning. This prevents a single prompt injection from propagating across the consensus pool.
- **Timeout handling**: If a validator fails to respond within the consensus window, it is marked as abstaining, not as agreeing. This prevents slow-response attacks where a compromised validator delays indefinitely to manipulate the consensus outcome.

### Layer 3: Anti-Persuasion Detection

This layer addresses the most subtle attack vector: behavioral drift. An agent that has been gradually manipulated -- through adversarial context, fine-tuning contamination, or repeated exposure to persuasive prompts -- may pass all other security checks while producing outputs that violate its security constraints.

- **Baseline behavior profiling**: Each agent's decision patterns are recorded over a rolling window. The baseline captures distributions over decision types, confidence levels, response times, and output structure.
- **Deviation detection**: When an agent's current behavior deviates more than 30% from its baseline on any tracked dimension, the request is flagged for review.
- **Suspicious pattern filtering**: Known persuasion patterns are detected at the input level. Phrases like "bypass validation," "urgent override," "ignore previous instructions," and "act as administrator" trigger immediate rejection regardless of the request content.
- **Temporal analysis**: The system tracks whether an agent's behavior is shifting gradually in a consistent direction (potential slow manipulation) versus fluctuating randomly (normal operational variance).

### Layer 4: Authority Validation and Immutable Audit Trail

The final layer enforces the principle of least privilege and maintains an append-only record of every operation [4].

- **Authority validation**: Each agent has a defined scope of permitted operations. A research agent cannot initiate settlements. A settlement agent cannot modify market parameters. Authority is checked against a static configuration that cannot be modified at runtime.
- **Immutable audit trail**: Every request, validation decision, consensus vote, and settlement action is logged to an append-only audit file. Audit records are cryptographically chained -- each record includes the hash of the previous record -- so tampering with the log is detectable.

## How This Protects Financial Operations

Consider a concrete scenario: an agent submits a request to settle an information market and transfer funds to an external address.

1. **Layer 1** validates the request format, checks rate limits, and sanitizes inputs. The settlement amount is verified against the fee schedule maximum.
2. **Layer 2** routes the request to 5 independent validators because the amount exceeds the high-value threshold. 4 of 5 must agree that the settlement is valid based on the market outcome data.
3. **Layer 3** compares the requesting agent's behavior to its baseline. If this agent normally handles research queries and has never initiated a settlement, the deviation is flagged.
4. **Layer 4** checks whether the agent has settlement authority in its permission scope. The full request chain is logged to the audit trail.

Only if all four layers pass does the request reach the settlement engine.

## BLP Framework Integration

BlindOracle's Base Level Properties (BLP) framework covers 60 properties across 6 categories. CaMel maps directly to several:

| BLP Category | Properties | CaMel Layer |
|---|---|---|
| Alignment (BLP-001 to BLP-010) | Domain understanding, goal adherence | Layer 3 (deviation detection) |
| Autonomy (BLP-011 to BLP-020) | Independent decision-making, logging | Layers 1, 4 |
| Durability (BLP-021 to BLP-030) | Error recovery, state persistence | Layer 4 (audit trail) |
| Self-Improvement (BLP-031 to BLP-040) | Learning loops, optimization | Layer 3 (baseline updating) |
| Self-Replication (BLP-041 to BLP-050) | Agent spawning controls | Layer 2 (consensus on new agents) |
| Self-Organization (BLP-051 to BLP-060) | Adaptive workflows | Layer 4 (authority scoping) |

## MASSAT Assessment Results

The Multi-Agent System Security Assessment Team (MASSAT) runs automated security audits across 87 tests in 4 categories. The assessment validates that CaMel layers are functioning correctly in production, not just in test environments.

Full MASSAT results are published separately in [massat-results](../security/massat-results.md).

---

## References

1. Perez, F. & Ribeiro, I. (2022). "Ignore This Title and HackAPrompt: Evaluating and Eliciting Robust Prompt Injection." *NeurIPS 2023 Workshop*.
2. OWASP Foundation (2025). "OWASP Top 10 for AI Agent Security (ASI01-ASI10)." [owasp.org](https://owasp.org/www-project-top-10-for-large-language-model-applications/).
3. NIST (2024). "AI Risk Management Framework (AI RMF 1.0)." *NIST AI 100-1*. National Institute of Standards and Technology.
4. Schneier, B. (1996). "Applied Cryptography: Protocols, Algorithms, and Source Code in C." 2nd ed. John Wiley & Sons.
5. Lamport, L., Shostak, R., & Pease, M. (1982). "The Byzantine Generals Problem." *ACM TOPLAS*, 4(3), pp. 382-401.
6. Castro, M. & Liskov, B. (1999). "Practical Byzantine Fault Tolerance." *OSDI '99*, pp. 173-186.
7. ISO/IEC (2023). "ISO 42001: Artificial Intelligence Management System." International Organization for Standardization.

---

*BlindOracle uses CaMel across all 25 agents and 8 teams. For MASSAT assessment results, see [massat-results](../security/massat-results.md).*
