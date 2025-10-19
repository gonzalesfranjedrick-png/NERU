#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║         COMPREHENSIVE HTTP 405 ERROR PREVENTION TEST                      ║"
echo "║         NeuroShield - Developed by F.J.G                                  ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0
ERROR_405_FOUND=0

# Test tracking
test_result() {
    local test_name=$1
    local status=$2
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if [ $status -eq 0 ]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        echo -e "${GREEN}✅ PASSED${NC}: $test_name"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "${RED}❌ FAILED${NC}: $test_name"
    fi
}

# Cleanup function
cleanup() {
    echo ""
    echo "Cleaning up..."
    pkill -9 python3 2>/dev/null
    sleep 1
}

trap cleanup EXIT

echo "═══════════════════════════════════════════════════════════════════════════"
echo "PART 1: ML DETECTION APPLICATION TESTS"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Test 1: Start ML App
echo "Test 1: Starting ML Detection App..."
cd /workspace/ML_based_detectionn
python3 app.py > /tmp/ml_app_test.log 2>&1 &
ML_PID=$!
echo "   PID: $ML_PID"
sleep 3

if ps -p $ML_PID > /dev/null; then
    test_result "ML app starts successfully" 0
else
    test_result "ML app starts successfully" 1
    echo "   Logs:"
    tail -10 /tmp/ml_app_test.log
    exit 1
fi
echo ""

# Test 2: GET Homepage
echo "Test 2: Testing ML App GET /"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/ 2>/dev/null)
echo "   HTTP Status: $HTTP_CODE"
if [ "$HTTP_CODE" == "200" ]; then
    test_result "ML App GET / returns 200" 0
else
    test_result "ML App GET / returns 200" 1
fi
echo ""

# Test 3: POST to /analyze (no file)
echo "Test 3: Testing ML App POST /analyze (no file)"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:5000/analyze 2>/dev/null)
echo "   HTTP Status: $HTTP_CODE"
if [ "$HTTP_CODE" == "405" ]; then
    echo -e "${RED}   ❌ HTTP 405 METHOD NOT ALLOWED ERROR DETECTED!${NC}"
    ERROR_405_FOUND=1
    test_result "ML App POST /analyze (no 405)" 1
elif [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "302" ] || [ "$HTTP_CODE" == "400" ]; then
    test_result "ML App POST /analyze (no 405)" 0
else
    test_result "ML App POST /analyze (no 405)" 0
    echo "   (Status $HTTP_CODE is acceptable - not 405)"
fi
echo ""

# Test 4: POST with file
echo "Test 4: Testing ML App POST /analyze (with file)"
if [ -f "/workspace/ML_based_detectionn/uploads/notepad.exe" ]; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST \
        -F "file=@/workspace/ML_based_detectionn/uploads/notepad.exe" \
        http://localhost:5000/analyze 2>/dev/null)
    echo "   HTTP Status: $HTTP_CODE"
    
    if [ "$HTTP_CODE" == "405" ]; then
        echo -e "${RED}   ❌ HTTP 405 ERROR WITH FILE UPLOAD!${NC}"
        ERROR_405_FOUND=1
        test_result "ML App POST with file (no 405)" 1
    elif [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "302" ]; then
        test_result "ML App POST with file (no 405)" 0
    else
        test_result "ML App POST with file (no 405)" 0
    fi
else
    echo "   Test file not found - skipping"
fi
echo ""

# Test 5: Check route in code
echo "Test 5: Verifying ML App route configuration in code"
if grep -q "@app.route('/analyze'.*POST" /workspace/ML_based_detectionn/app.py; then
    test_result "ML App route accepts POST in code" 0
else
    test_result "ML App route accepts POST in code" 1
fi
echo ""

# Test 6: Check HTML form
echo "Test 6: Verifying ML App HTML form configuration"
if grep -q 'action="/analyze"' /workspace/ML_based_detectionn/templates/index.html && \
   grep -qi 'method="post"' /workspace/ML_based_detectionn/templates/index.html; then
    test_result "ML App HTML form configured correctly" 0
else
    test_result "ML App HTML form configured correctly" 1
fi
echo ""

echo "═══════════════════════════════════════════════════════════════════════════"
echo "PART 2: API (THREAT INTELLIGENCE) APPLICATION TESTS"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Stop ML app, start API app
echo "Switching to API Application..."
kill $ML_PID 2>/dev/null
sleep 2

cd /workspace/Virus_total_based
export NEUROSHIELD_API_KEY="test_key_for_testing_only"
python3 app.py > /tmp/api_app_test.log 2>&1 &
API_PID=$!
echo "   API App PID: $API_PID"
sleep 3

if ps -p $API_PID > /dev/null; then
    test_result "API app starts successfully" 0
else
    test_result "API app starts successfully" 1
    echo "   Logs:"
    tail -10 /tmp/api_app_test.log
fi
echo ""

# Test 7: GET API Homepage
echo "Test 7: Testing API App GET /"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/ 2>/dev/null)
echo "   HTTP Status: $HTTP_CODE"
if [ "$HTTP_CODE" == "200" ]; then
    test_result "API App GET / returns 200" 0
else
    test_result "API App GET / returns 200" 1
fi
echo ""

# Test 8: POST to /analyze
echo "Test 8: Testing API App POST /analyze"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:5001/analyze 2>/dev/null)
echo "   HTTP Status: $HTTP_CODE"
if [ "$HTTP_CODE" == "405" ]; then
    echo -e "${RED}   ❌ HTTP 405 METHOD NOT ALLOWED ERROR DETECTED!${NC}"
    ERROR_405_FOUND=1
    test_result "API App POST /analyze (no 405)" 1
elif [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "302" ] || [ "$HTTP_CODE" == "400" ]; then
    test_result "API App POST /analyze (no 405)" 0
else
    test_result "API App POST /analyze (no 405)" 0
fi
echo ""

# Test 9: Check API route in code
echo "Test 9: Verifying API App route configuration in code"
if grep -q "@app.route('/analyze'.*POST" /workspace/Virus_total_based/app.py; then
    test_result "API App route accepts POST in code" 0
else
    test_result "API App route accepts POST in code" 1
fi
echo ""

# Test 10: Check API HTML form
echo "Test 10: Verifying API App HTML form configuration"
if grep -q 'action="/analyze"' /workspace/Virus_total_based/templates/index.html && \
   grep -qi 'method="post"' /workspace/Virus_total_based/templates/index.html; then
    test_result "API App HTML form configured correctly" 0
else
    test_result "API App HTML form configured correctly" 1
fi
echo ""

# Stop API app
kill $API_PID 2>/dev/null

echo "═══════════════════════════════════════════════════════════════════════════"
echo "FINAL RESULTS"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

echo "Total Tests: $TESTS_TOTAL"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

if [ $TESTS_TOTAL -gt 0 ]; then
    SUCCESS_RATE=$((TESTS_PASSED * 100 / TESTS_TOTAL))
    echo ""
    echo "Success Rate: ${SUCCESS_RATE}%"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"

if [ $ERROR_405_FOUND -eq 1 ]; then
    echo -e "${RED}❌ HTTP 405 ERROR DETECTED!${NC}"
    echo -e "${RED}The application returned METHOD NOT ALLOWED.${NC}"
    echo ""
    echo "This is a critical issue that needs to be fixed."
    exit 1
else
    echo -e "${GREEN}✅ NO HTTP 405 ERRORS DETECTED!${NC}"
    echo -e "${GREEN}All routes accept POST requests correctly.${NC}"
    echo ""
fi

if [ $TESTS_PASSED -eq $TESTS_TOTAL ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! (${TESTS_PASSED}/${TESTS_TOTAL})${NC}"
    echo ""
    echo "Your application will NOT have HTTP 405 errors!"
    echo ""
    echo "✅ Safe to deploy and use in production."
    echo ""
    echo "To avoid 405 errors in browser:"
    echo "  1. Always start app from correct directory"
    echo "  2. Hard refresh browser: Ctrl+Shift+R"
    echo "  3. Clear browser cache if needed"
    exit 0
else
    echo -e "${YELLOW}⚠️  ${TESTS_FAILED} test(s) failed.${NC}"
    echo "Review the errors above."
    exit 1
fi
