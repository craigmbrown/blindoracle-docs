# Research Brief: Who Verifies the Human Behind an AI Agent in 2026, and What Each Mechanism Proves

## 1. Executive summary

Three mechanisms are examined, each drawn only from the three buyer-supplied primary sources. ERC-8004 provides an on-chain identity, reputation, and validation registry for agents, but it registers an agent handle and does not itself attest to any human operator [1]. World ID issues a unique, privacy-preserving Proof of Human credential tied to a biometric enrollment via the Orb, designed to prove a unique human without revealing identity [2]. Coinbase Verifications issues EAS-based onchain attestations representing the status of a Coinbase customer's account at issuance time, explicitly described as informational and not guaranteed current [3]. None of the three, on the evidence in these sources, binds a named human to a named agent.

## 2. Background & definitions

- **ERC-8004 (Trustless Agents)**: a Standards Track ERC in Draft status, authored by Marco De Rossi, Davide Crapis, Jordan Ellis, and Erik Reppel, created 2025-08-13 [1].
- **Identity Registry**: "a minimal on-chain handle based on ERC-721 with URIStorage extension that resolves to an agent's registration file" [1].
- **Proof of Human (PoH)**: described by World as a mechanism to distinguish humans from AI agents in digital interaction [2].
- **Ethereum Attestation Service (EAS)**: "an open-source public good that is included as a predeploy in the OP Stack" [3].
- **Coinbase Verifications**: "a set of Coinbase-verified onchain attestations that enable access to apps and other onchain benefits" [3].

## 3. How it works / key mechanisms

**ERC-8004.** The protocol has three registries. The Identity Registry gives each agent a portable identifier [1]. The Reputation Registry provides "a standard interface for posting and fetching feedback signals" [1]. The Validation Registry provides "generic hooks for requesting and recording independent validators checks (e.g. stakers re-running the job, zkML verifiers, TEE oracles, trusted judges)" [1]. Payments are stated as orthogonal and not covered [1].

**World ID.** World states that PoH alone is insufficient without uniqueness, since otherwise it is vulnerable to relay attacks in which "a small group of humans could authenticate repeatedly to serve millions of automated agents" [2]. The whitepaper states that strict uniqueness, "exactly one credential per person," is essential [2]. World describes its implementation as using the Orb, Anonymized Multi-Party Computation (AMPC), and zero-knowledge proof-based authentication [2].

**Coinbase Verifications.** Attestations are issued via EAS on Base. The Coinbase Indexer lets a caller query the latest attestation ID by recipient address and schema ID; the attestation data is then retrieved from EAS [3]. A Coinbase Attester address is the stated origin for verifying attestations [3].

## 4. Named alternatives with trade-offs

The three sources themselves compare mechanisms only in limited ways:

- ERC-8004 lists alternative validation trust models: "reputation systems using client feedback, validation via stake-secured re-execution, zero-knowledge machine learning (zkML) proofs, or trusted execution environment (TEE) oracles" [1]. The source does not assess trade-offs among them beyond saying security should be "proportional to value at risk" [1].
- World's whitepaper evaluates "candidate approaches to establishing a root of trust" and states its design prioritises privacy and individual empowerment [2]. Specific competing products are not compared in the retrieved text (unverified — no source).
- Coinbase's README states its attestations "should not be relied upon... for any legal, compliance, or contractual purpose" [3]. Comparative trade-offs with other attestation providers are (unverified — no source).

Not relevant: [4] — ERC (European Research Council) funding body; unrelated to the ERC-8004 standard or to agent verification.
Not relevant: [5] — IRS Employee Retention Credit FAQ; unrelated tax subject.
Not relevant: [6] — guidance on ERC grant proposals; unrelated.
Not relevant: [7] — AICPA material on the Employee Retention Credit; unrelated.
Not relevant: [8] — Journal of Accountancy article on the Employee Retention Credit; unrelated.
Not relevant: [9] — tax-law article on Employee Retention Credit eligibility; unrelated.

## 5. Per-mechanism analysis

### 5a. ERC-8004 Trustless Agents

- **What is registered or attested:** An agent's registration file, referenced by an ERC-721 token in the Identity Registry; feedback signals in the Reputation Registry; validation results in the Validation Registry [1].
- **Who issues it:** The protocol is an on-chain standard; the registrations and feedback are posted by the agent operator and clients, and validators perform checks [1]. The precise issuer role for the Identity Registry entry is not specified in the retrieved excerpt (unverified — no source).
- **What a third party can verify:** The on-chain handle, the registration file it resolves to, and posted feedback and validation records [1].
- **What it does NOT prove:** The source does not state that any registry entry is linked to a verified human operator. Payments are explicitly out of scope [1]. The standard is in Draft status [1].

### 5b. World ID (Proof of Human)

- **What is registered or attested:** A unique human credential, described as one credential per person, authenticated through zero-knowledge proofs [2].
- **Who issues it:** World, via the Orb and its enrollment process [2].
- **What a third party can verify:** That the authenticating party holds a credential representing a unique human, without the verifier learning identity, per the privacy-preserving design described [2].
- **What it does NOT prove:** The whitepaper frames PoH as privacy-preserving, which implies it does not disclose the human's identity to the verifier [2]. It does not, per the excerpt, prove that a given credential holder controls or operates a particular AI agent (unverified — no source). The excerpt does not address whether a credential holder is operating an agent at all.

### 5c. Coinbase Verifications (EAS on Base)

- **What is registered or attested:** Onchain attestations representing an individual's Coinbase account status [3].
- **Who issues it:** Coinbase, from the Coinbase Attester contract/address [3].
- **What a third party can verify:** The attestation exists, its origin via the Coinbase Attester address, and its data via EAS, looked up through the Coinbase Indexer [3].
- **What it does NOT prove:** Coinbase states the attestation "represents the status of the relevant individual's Coinbase account as of the time of issuance," that later changes may not be reflected, and that Coinbase "does not represent, warrant or guarantee" completeness, accuracy, or currency [3]. It is explicitly not for legal, compliance, or contractual reliance [3]. It does not, per the source, link any Coinbase account to any AI agent.

## 6. Open risks & unknowns

- Whether ERC-8004 registration files can contain or be linked to a human operator identity is not stated in the source (unverified — no source).
- World's PoH is described as a human check, but the excerpt does not show a mechanism binding that check to a specific agent (unverified — no source).
- Coinbase attestations can become stale; the source acknowledges this lag [3].
- The ERC-8004 standard is in Draft, so its interfaces may change [1].
- Attesting to an individual's account status does not establish that the individual is the agent's operator (inference from [3]'s scope).

## 7. Direct answer

No, none of the three mechanisms, on the evidence in these three sources, binds a named human to a named agent. ERC-8004 binds an agent to an on-chain identifier and to reputation and validation records, but it does not attest to a human operator [1]. World ID binds a unique, privacy-preserving human credential to a person, not to an agent, and is designed to hide identity from verifiers [2]. Coinbase Verifications binds an account-status attestation to an individual's Coinbase account, but makes no guarantee of currency or completeness and disclaims reliance for any legal or contractual purpose [3]. A composition of the three could in principle connect a human credential to an agent handle, but no source here describes such a binding, so that conclusion is ASSUMED — not retrieved.

## Sources:

[1] https://eips.ethereum.org/EIPS/eip-8004
[2] https://whitepaper.world.org/achieving-proof-of-human
[3] https://github.com/coinbase/verifications