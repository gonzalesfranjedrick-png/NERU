#!/bin/bash

echo "═══════════════════════════════════════════════════════════════════════════"
echo "FORCE FIX HTTP 405 ERROR - COMPLETE RESET"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# Kill ALL Python processes
echo "Step 1: Killing all Python processes..."
pkill -9 python3
pkill -9 python
sleep 2
echo "✅ All Python processes killed"
echo ""

# Clear any cached .pyc files
echo "Step 2: Clearing Python cache..."
find /workspace -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find /workspace -name "*.pyc" -delete 2>/dev/null
echo "✅ Python cache cleared"
echo ""

# Check route definitions
echo "Step 3: Verifying route definitions..."
echo ""
echo "ML App routes:"
grep -A 1 "@app.route.*analyze" /workspace/ML_based_detectionn/app.py | head -3
echo ""
echo "API App routes:"
grep -A 1 "@app.route.*analyze" /workspace/Virus_total_based/app.py | head -3
echo ""

# Check HTML forms
echo "Step 4: Verifying HTML form actions..."
echo ""
echo "ML App form:"
grep "action=" /workspace/ML_based_detectionn/templates/index.html | head -1
echo ""
echo "API App form:"
grep "action=" /workspace/Virus_total_based/templates/index.html | head -1
echo ""

# Ensure app.py has correct syntax
echo "Step 5: Syntax check..."
cd /workspace/ML_based_detectionn
python3 -m py_compile app.py 2>&1 | grep -v "^$" || echo "✅ ML app.py syntax OK"
cd /workspace/Virus_total_based
python3 -m py_compile app.py 2>&1 | grep -v "^$" || echo "✅ API app.py syntax OK"
echo ""

# Start fresh ML app
echo "Step 6: Starting ML Detection App (Fresh)..."
cd /workspace/ML_based_detectionn
python3 -c "
from app import app
print('Routes in app:')
for rule in app.url_map.iter_rules():
    if 'analyze' in str(rule):
        print(f'  {rule} -> Methods: {rule.methods}')
"
echo ""

# Actually start the app
echo "Step 7: Starting application on port 5000..."
cd /workspace/ML_based_detectionn
nohup python3 app.py > /tmp/ml_app_fixed.log 2>&1 &
APP_PID=$!
echo "App PID: $APP_PID"
echo "Waiting 3 seconds for startup..."
sleep 3

if ps -p $APP_PID > /dev/null; then
    echo "✅ App is running"
else
    echo "❌ App failed to start. Logs:"
    cat /tmp/ml_app_fixed.log
    exit 1
fi
echo ""

# Test the route
echo "Step 8: Testing POST to /analyze..."
HTTP_CODE=$(curl -s -o /tmp/test_response.html -w "%{http_code}" -X POST http://localhost:5000/analyze)
echo "HTTP Status Code: $HTTP_CODE"

if [ "$HTTP_CODE" = "405" ]; then
    echo "❌ STILL GETTING 405 ERROR!"
    echo ""
    echo "Response body:"
    cat /tmp/test_response.html
    echo ""
    echo "This means there's a configuration issue. Let me check..."
    
    # Print the actual route
    python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/ML_based_detectionn')
from app import app

print("\nAll routes in the Flask app:")
for rule in app.url_map.iter_rules():
    print(f"  {rule.endpoint:20s} {str(rule):30s} -> {sorted(rule.methods - {'HEAD', 'OPTIONS'})}")
PYEOF
    
elif [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ POST request works! (Status $HTTP_CODE)"
else
    echo "⚠️  Status $HTTP_CODE (not 405, so method is allowed)"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════════════════"
echo "FINAL INSTRUCTIONS"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "The app is running on: http://localhost:5000"
echo "App PID: $APP_PID"
echo "Logs: /tmp/ml_app_fixed.log"
echo ""
echo "TO STOP THE APP:"
echo "  kill $APP_PID"
echo ""
echo "IN YOUR BROWSER:"
echo "  1. Close all browser windows completely"
echo "  2. Reopen browser"
echo "  3. Go to: http://localhost:5000"
echo "  4. Do NOT use back button or cached page"
echo "  5. Upload file and click Analyze"
echo ""
echo "OR:"
echo "  1. Open Incognito/Private window: Ctrl+Shift+N"
echo "  2. Go to: http://localhost:5000"
echo "  3. Upload file and click Analyze"
echo ""
echo "If you STILL get 405:"
echo "  1. Check browser DevTools -> Network tab"
echo "  2. See what URL the form is posting to"
echo "  3. Send me a screenshot"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
