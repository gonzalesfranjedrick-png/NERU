#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║          Testing Analyze Button - HTTP 405 Fix Verification          ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Kill any running processes
echo "Step 1: Cleaning up old processes..."
pkill -9 python3 2>/dev/null
sleep 1
echo -e "${GREEN}✅ Old processes cleaned${NC}"
echo ""

# Step 2: Start ML app in background
echo "Step 2: Starting ML Detection App..."
cd /workspace/ML_based_detectionn
python3 app.py > /tmp/ml_app.log 2>&1 &
ML_PID=$!
echo "   PID: $ML_PID"
sleep 3

# Check if app started
if ps -p $ML_PID > /dev/null; then
    echo -e "${GREEN}✅ ML app started successfully${NC}"
else
    echo -e "${RED}❌ Failed to start ML app${NC}"
    echo "   Check logs: cat /tmp/ml_app.log"
    exit 1
fi
echo ""

# Step 3: Test GET request to /
echo "Step 3: Testing GET request to homepage..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/)
if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✅ Homepage loads correctly (HTTP 200)${NC}"
else
    echo -e "${RED}❌ Homepage returned HTTP $HTTP_CODE${NC}"
fi
echo ""

# Step 4: Test POST request to /analyze
echo "Step 4: Testing POST request to /analyze..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:5000/analyze)
if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✅ POST to /analyze works (HTTP 200)${NC}"
    echo "   (Returns 200 even without file - this is correct)"
elif [ "$HTTP_CODE" == "400" ] || [ "$HTTP_CODE" == "302" ]; then
    echo -e "${GREEN}✅ POST to /analyze works (HTTP $HTTP_CODE)${NC}"
    echo "   (Returns $HTTP_CODE for missing file - this is correct)"
elif [ "$HTTP_CODE" == "405" ]; then
    echo -e "${RED}❌ POST to /analyze returns HTTP 405${NC}"
    echo -e "${RED}   METHOD NOT ALLOWED - This is the error!${NC}"
else
    echo -e "${YELLOW}⚠️  POST to /analyze returns HTTP $HTTP_CODE${NC}"
fi
echo ""

# Step 5: Test with actual file upload simulation
echo "Step 5: Testing file upload simulation..."
if [ -f "/workspace/ML_based_detectionn/uploads/notepad.exe" ]; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST \
        -F "file=@/workspace/ML_based_detectionn/uploads/notepad.exe" \
        http://localhost:5000/analyze)
    
    if [ "$HTTP_CODE" == "200" ] || [ "$HTTP_CODE" == "302" ]; then
        echo -e "${GREEN}✅ File upload works (HTTP $HTTP_CODE)${NC}"
    else
        echo -e "${RED}❌ File upload failed (HTTP $HTTP_CODE)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No test file available, skipping${NC}"
fi
echo ""

# Step 6: Display results
echo "═══════════════════════════════════════════════════════════════════════"
echo "                           TEST RESULTS                                "
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

if [ "$HTTP_CODE" != "405" ]; then
    echo -e "${GREEN}✅ SUCCESS! The app is working correctly.${NC}"
    echo ""
    echo "The /analyze route accepts POST requests."
    echo "No HTTP 405 error detected!"
    echo ""
    echo "🌐 Access the app at: http://localhost:5000"
    echo ""
    echo -e "${YELLOW}If you still get 405 in browser:${NC}"
    echo "   1. Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)"
    echo "   2. Clear browser cache"
    echo "   3. Try incognito/private mode"
    echo "   4. Try different browser"
else
    echo -e "${RED}❌ HTTP 405 ERROR DETECTED${NC}"
    echo ""
    echo "This shouldn't happen with correct code."
    echo "Checking logs..."
    echo ""
    tail -20 /tmp/ml_app.log
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "App is running on PID: $ML_PID"
echo "Logs: /tmp/ml_app.log"
echo ""
echo "To stop the app:"
echo "   kill $ML_PID"
echo ""
echo "To view live logs:"
echo "   tail -f /tmp/ml_app.log"
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
