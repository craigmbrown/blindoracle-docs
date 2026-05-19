#### Changelog -- blindoracle-agentkit

###### [0.2.0] -- 2026-05-13

######## Changed
- License: Proprietary -> Apache-2.0 (community-pickup unblocker, 2026-05-13)
- Version bumped to 0.2.0 for coinbase/agentkit ecosystem-registry PR
- Development status: Alpha -> Beta
- __version__ synced to 0.2.0 in blindoracle/__init__.py

######## Added
- INSTALL.md -- VCS-install command + 30-second quickstart (no PyPI)
- tests/conftest.py -- coinbase_agentkit stub (no real package needed)
- tests/test_actions.py -- 15 unit tests (7 happy-path + 5 error-path + 3 metadata)
- tests/test_live_smoke.py -- 3 live smoke tests (pytest @pytest.mark.slow)
- CHANGELOG.md (this file)

######## Notes
- No PyPI. VCS-install is the canonical distribution channel.
- No CDP Builder Grant application (dropped 2026-05-13)

######## [0.1.0] -- 2026-05-10

######## Added
- Initial 7-action provider: hello_world, list_markets, get_market_odds,
  create_market, place_position, resolve_market, verify_credential
- Pydantic v2 input schemas for all actions
- x402 payment integration (X-Agent-Id header, craigmbrown.com/api)
- ERC-8004 passport identity layer via verify_credential
- Base mainnet + Base Sepolia network support
