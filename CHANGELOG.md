# Changelog

## 2026-06-07

- **Agent Audit & Governance attestation (MCP)** — published the `get_audit_credential`
  MCP tool via the public server card (`/.well-known/mcp-server-card.json`). Returns a
  W3C Verifiable Credential (eddsa-jcs-2022) + verify URL for a BlindOracle agent-security
  audit, given its `proof_id` (ProofOfAuditReport kind 30105). No wallet or RPC required;
  did:web is self-asserted (issuer controls the domain), not a third-party-rooted PKI.
- **`translation.zh-en` SKU live** — Chinese↔English translation (LEV-11) now dispatches
  end-to-end through the marketplace; routed to the cost-optimized open-weight lane.
