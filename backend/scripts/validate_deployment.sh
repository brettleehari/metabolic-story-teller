#!/bin/bash
# Validation script for GlucoLens AWS Lambda Demo
# Tests all API endpoints and verifies demo data

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL=${1:-}
ENVIRONMENT=${2:-demo}

if [ -z "$API_URL" ]; then
    STACK_NAME="glucolens-${ENVIRONMENT}"
    REGION=${AWS_REGION:-us-east-1}

    echo -e "${BLUE}Retrieving API URL from CloudFormation...${NC}"
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
        --output text)

    if [ -z "$API_URL" ]; then
        echo -e "${RED}❌ Could not retrieve API URL${NC}"
        echo "Usage: $0 <API_URL> [environment]"
        exit 1
    fi
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}GlucoLens Demo Validation${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}API URL:${NC} $API_URL"
echo -e "${YELLOW}Environment:${NC} $ENVIRONMENT"
echo ""

# Demo user IDs
ALICE_ID="11111111-1111-1111-1111-111111111111"
BOB_ID="22222222-2222-2222-2222-222222222222"
CAROL_ID="33333333-3333-3333-3333-333333333333"

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test function
test_endpoint() {
    local endpoint=$1
    local description=$2
    local expected_code=${3:-200}

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -ne "${YELLOW}Testing:${NC} $description... "

    HTTP_CODE=$(curl -s -o /tmp/response.json -w "%{http_code}" "$API_URL$endpoint")

    if [ "$HTTP_CODE" -eq "$expected_code" ]; then
        echo -e "${GREEN}✅ PASS (HTTP $HTTP_CODE)${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL (HTTP $HTTP_CODE, expected $expected_code)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        cat /tmp/response.json
        echo ""
        return 1
    fi
}

# Test with data validation
test_endpoint_with_data() {
    local endpoint=$1
    local description=$2
    local jq_filter=$3
    local expected_value=$4

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -ne "${YELLOW}Testing:${NC} $description... "

    HTTP_CODE=$(curl -s -o /tmp/response.json -w "%{http_code}" "$API_URL$endpoint")

    if [ "$HTTP_CODE" -ne 200 ]; then
        echo -e "${RED}❌ FAIL (HTTP $HTTP_CODE)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi

    if ! command -v jq &> /dev/null; then
        echo -e "${YELLOW}⚠️  SKIP (jq not installed)${NC}"
        return 0
    fi

    ACTUAL_VALUE=$(jq -r "$jq_filter" /tmp/response.json)

    if [ "$ACTUAL_VALUE" = "$expected_value" ]; then
        echo -e "${GREEN}✅ PASS (HTTP $HTTP_CODE, data valid)${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL (HTTP $HTTP_CODE, data mismatch)${NC}"
        echo -e "${RED}Expected: $expected_value${NC}"
        echo -e "${RED}Actual: $ACTUAL_VALUE${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo -e "${BLUE}Running endpoint tests...${NC}"
echo ""

# Test 1: Health check
test_endpoint "/" "Root endpoint health check"

# Test 2: Get all demo users
test_endpoint "/users" "Get demo users list"

# Test 3: Get Alice's insights
test_endpoint "/insights/$ALICE_ID" "Get Alice's insights"

# Test 4: Get Bob's insights
test_endpoint "/insights/$BOB_ID" "Get Bob's insights"

# Test 5: Get Carol's insights
test_endpoint "/insights/$CAROL_ID" "Get Carol's insights"

# Test 6: Get Alice's correlations
test_endpoint "/correlations/$ALICE_ID" "Get Alice's correlations"

# Test 7: Get correlations with limit
test_endpoint "/correlations/$ALICE_ID?limit=5" "Get correlations with limit"

# Test 8: Get Alice's patterns
test_endpoint "/patterns/$ALICE_ID" "Get Alice's patterns"

# Test 9: Get patterns with min confidence
test_endpoint "/patterns/$ALICE_ID?min_confidence=0.7" "Get patterns with min confidence"

# Test 10: Get Alice's dashboard (7 days)
test_endpoint "/dashboard/$ALICE_ID?period=7" "Get Alice's dashboard (7 days)"

# Test 11: Get Alice's dashboard (30 days)
test_endpoint "/dashboard/$ALICE_ID?period=30" "Get Alice's dashboard (30 days)"

# Test 12: Get Alice's dashboard (90 days)
test_endpoint "/dashboard/$ALICE_ID?period=90" "Get Alice's dashboard (90 days)"

# Test 13: Get Alice's glucose readings
test_endpoint "/glucose/readings/$ALICE_ID" "Get Alice's glucose readings"

# Test 14: Get glucose readings with limit
test_endpoint "/glucose/readings/$ALICE_ID?limit=100" "Get glucose readings with limit"

# Test 15: Get glucose readings with date range
START_DATE=$(date -u -d "30 days ago" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -v-30d +"%Y-%m-%dT%H:%M:%SZ")
END_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
test_endpoint "/glucose/readings/$ALICE_ID?start_date=$START_DATE&end_date=$END_DATE&limit=50" "Get glucose readings with date range"

# Test 16: Invalid user ID (should fail)
test_endpoint "/insights/invalid-user-id" "Invalid user ID handling" 404

echo ""
echo -e "${BLUE}Testing data validation...${NC}"
echo ""

# Only run if jq is available
if command -v jq &> /dev/null; then
    # Test 17: Verify demo users count
    test_endpoint_with_data "/users" "Demo users count" "length" "3"

    # Test 18: Verify Alice's email
    test_endpoint_with_data "/users" "Alice's email" ".[0].email" "alice@demo.glucolens.com"

    # Test 19: Verify dashboard has glucose stats
    curl -s "$API_URL/dashboard/$ALICE_ID?period=30" -o /tmp/response.json
    if jq -e '.glucose_stats.avg' /tmp/response.json > /dev/null 2>&1; then
        echo -e "${YELLOW}Testing:${NC} Dashboard glucose stats... ${GREEN}✅ PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${YELLOW}Testing:${NC} Dashboard glucose stats... ${RED}❌ FAIL${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    # Test 20: Verify glucose readings are returned
    curl -s "$API_URL/glucose/readings/$ALICE_ID?limit=10" -o /tmp/response.json
    READING_COUNT=$(jq 'length' /tmp/response.json)
    if [ "$READING_COUNT" -gt 0 ]; then
        echo -e "${YELLOW}Testing:${NC} Glucose readings returned... ${GREEN}✅ PASS ($READING_COUNT readings)${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${YELLOW}Testing:${NC} Glucose readings returned... ${RED}❌ FAIL (0 readings)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
else
    echo -e "${YELLOW}⚠️  Skipping data validation tests (jq not installed)${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Validation Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Total Tests:${NC} $TOTAL_TESTS"
echo -e "${GREEN}Passed:${NC} $PASSED_TESTS"
echo -e "${RED}Failed:${NC} $FAILED_TESTS"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    echo ""
    echo -e "${YELLOW}Demo is ready!${NC}"
    echo "  API: $API_URL"
    echo "  Demo Users:"
    echo "    - Alice Thompson (Well-controlled)"
    echo "    - Bob Martinez (Variable)"
    echo "    - Carol Chen (Active)"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please check the errors above.${NC}"
    exit 1
fi
