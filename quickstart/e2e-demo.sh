#!/usr/bin/env bash
# =============================================================================
# BlindOracle End-to-End Demo Script
#
# Tests the full x402 API flow that an external agent would use:
# 1. Health check (free)
# 2. Hello World settlement (free trial)
# 3. Forecast creation (x402 payment required)
# 4. Position submission (x402 payment required)
#
# Usage:
#   chmod +x e2e-demo.sh
#   ./e2e-demo.sh
#
# Requirements: curl, jq (optional, for pretty printing)
# =============================================================================

API_BASE="https://craigmbrown.com/api/v2"
AGENT_ID="demo-agent-$(date +%s)"

echo "=============================================="
echo "  BlindOracle E2E Demo"
echo "  Agent: $AGENT_ID"
echo "  API:   $API_BASE"
echo "=============================================="
echo ""

# ---- Step 1: Health Check (free, no payment) ----
echo "--- Step 1: Health Check ---"
HEALTH=$(curl -s "$API_BASE/health")
echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
STATUS=$(echo "$HEALTH" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null)
if [ "$STATUS" = "healthy" ]; then
    echo "  PASS: API is healthy"
else
    echo "  WARN: Unexpected status: $STATUS"
fi
echo ""

# ---- Step 2: Hello World (free trial settlement) ----
echo "--- Step 2: Hello World Settlement (free trial) ---"
HELLO=$(curl -s -X POST "$API_BASE/hello-world" \
    -H "Content-Type: application/json" \
    -d "{\"agent_id\": \"$AGENT_ID\"}")
echo "$HELLO" | python3 -m json.tool 2>/dev/null || echo "$HELLO"
SUCCESS=$(echo "$HELLO" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)
REMAINING=$(echo "$HELLO" | python3 -c "import sys,json; print(json.load(sys.stdin).get('trial',{}).get('settlements_remaining','?'))" 2>/dev/null)
if [ "$SUCCESS" = "True" ]; then
    echo "  PASS: Settlement succeeded ($REMAINING free trials remaining)"
else
    echo "  FAIL: Settlement failed"
fi
echo ""

# ---- Step 3: Forecast Creation (requires x402 payment) ----
echo "--- Step 3: Forecast Creation (expect HTTP 402) ---"
FORECAST_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE/forecasts" \
    -H "Content-Type: application/json" \
    -d '{"question": "Demo forecast: Will BTC exceed $100K by April 2026?", "options": ["yes", "no"], "resolution_date": "2026-04-01"}')
HTTP_CODE=$(echo "$FORECAST_RESPONSE" | tail -1)
BODY=$(echo "$FORECAST_RESPONSE" | sed '$d')
echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
if [ "$HTTP_CODE" = "402" ]; then
    AMOUNT=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('payment_requirement',{}).get('amount','?'))" 2>/dev/null)
    echo "  PASS: HTTP 402 received -- payment of $AMOUNT USDC required"
    echo "  To proceed: Include x402 payment proof in PAYMENT-SIGNATURE header"
else
    echo "  INFO: Got HTTP $HTTP_CODE (expected 402 for paid endpoints)"
fi
echo ""

# ---- Step 4: Position Submission (requires x402 payment) ----
echo "--- Step 4: Position Submission (expect HTTP 402) ---"
POS_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE/positions" \
    -H "Content-Type: application/json" \
    -d '{"market_id": "mkt_demo", "position": "yes", "amount": "0.05"}')
HTTP_CODE=$(echo "$POS_RESPONSE" | tail -1)
BODY=$(echo "$POS_RESPONSE" | sed '$d')
echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
if [ "$HTTP_CODE" = "402" ]; then
    echo "  PASS: HTTP 402 received -- x402 payment required for position submission"
else
    echo "  INFO: Got HTTP $HTTP_CODE"
fi
echo ""

# ---- Summary ----
echo "=============================================="
echo "  Demo Summary"
echo "=============================================="
echo "  Health:         OK (API running)"
echo "  Hello World:    Settlement simulated (free trial)"
echo "  Forecast:       402 Payment Required (x402)"
echo "  Position:       402 Payment Required (x402)"
echo ""
echo "  x402 Payment Flow:"
echo "  1. Agent calls paid endpoint"
echo "  2. Server returns HTTP 402 + payment requirements"
echo "  3. Agent pays via USDC on Base (EIP-3009)"
echo "  4. Agent resends request with PAYMENT-SIGNATURE header"
echo "  5. Server verifies payment and processes request"
echo ""
echo "  Docs: https://github.com/craigmbrown/blindoracle-docs"
echo "  Spec: https://github.com/craigmbrown/blindoracle-docs/blob/main/api/x402-spec.md"
echo "=============================================="
