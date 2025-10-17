#!/bin/bash

echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║              HTTP 405 DETAILED DIAGNOSTIC                              ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check what's running
echo "1. Checking running Python processes..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ps aux | grep -E "python.*app" | grep -v grep | head -5 || echo "No Python processes found"
echo ""

# Check ports
echo "2. Checking what's listening on ports 5000 and 5001..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
lsof -i :5000 2>/dev/null || echo "Nothing on port 5000"
lsof -i :5001 2>/dev/null || echo "Nothing on port 5001"
echo ""

# Test with curl
echo "3. Testing with curl (this bypasses browser)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Test A: GET /"
HTTP_GET=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/ 2>/dev/null)
echo "   Status: $HTTP_GET"

echo ""
echo "Test B: POST /analyze (no data)"
HTTP_POST=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:5000/analyze 2>/dev/null)
echo "   Status: $HTTP_POST"

if [ "$HTTP_POST" = "405" ]; then
    echo "   ❌ GETTING 405 FROM SERVER ITSELF!"
    echo "   This means the server code has an issue."
fi

echo ""
echo "Test C: POST /analyze with form data"
HTTP_POST_FORM=$(curl -s -o /dev/null -w "%{http_code}" -X POST -F "test=1" http://localhost:5000/analyze 2>/dev/null)
echo "   Status: $HTTP_POST_FORM"

echo ""

# Check the actual Flask routes
echo "4. Checking Flask routes in running app..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/ML_based_detectionn')
try:
    from app import app
    print("Routes registered in Flask app:")
    for rule in app.url_map.iter_rules():
        methods = sorted(rule.methods - {'HEAD', 'OPTIONS'})
        print(f"  {str(rule):30s} -> {methods}")
except Exception as e:
    print(f"Error loading app: {e}")
PYEOF
echo ""

# Show the actual route decorator
echo "5. Checking route decorator in code..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -A 2 "@app.route.*analyze" /workspace/ML_based_detectionn/app.py
echo ""

# Check logs
echo "6. Checking recent app logs..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f /tmp/ml_app_fixed.log ]; then
    echo "Last 10 lines of app log:"
    tail -10 /tmp/ml_app_fixed.log
else
    echo "No log file found"
fi
echo ""

# Create test HTML file
echo "7. Creating test page to check exact error..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat > /tmp/test_405.html << 'HTMLEOF'
<!DOCTYPE html>
<html>
<head>
    <title>Test 405 Error</title>
</head>
<body>
    <h1>Test Form Submission</h1>
    
    <h2>Test 1: Form POST to /analyze</h2>
    <form action="http://localhost:5000/analyze" method="post">
        <button type="submit">Submit Test 1</button>
    </form>
    
    <h2>Test 2: JavaScript POST</h2>
    <button onclick="testPost()">Submit Test 2</button>
    <div id="result"></div>
    
    <script>
    function testPost() {
        fetch('http://localhost:5000/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'test=1'
        })
        .then(response => {
            document.getElementById('result').innerHTML = 
                'Status: ' + response.status + ' ' + response.statusText;
        })
        .catch(error => {
            document.getElementById('result').innerHTML = 'Error: ' + error;
        });
    }
    </script>
</body>
</html>
HTMLEOF
echo "Test page created: file:///tmp/test_405.html"
echo "Open this in your browser to test!"
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                           DIAGNOSTIC SUMMARY                           ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

if [ "$HTTP_POST" = "405" ]; then
    echo "❌ SERVER IS RETURNING 405!"
    echo ""
    echo "This means the route is NOT configured correctly in the running app."
    echo "Possible causes:"
    echo "  1. Wrong app.py file is running"
    echo "  2. Old version of code is cached"
    echo "  3. Route decorator is wrong"
    echo "  4. Flask is configured incorrectly"
    echo ""
    echo "SOLUTION: Restart with correct file:"
    echo "  pkill -9 python3"
    echo "  cd /workspace/ML_based_detectionn"
    echo "  python3 app.py"
    
elif [ "$HTTP_POST" = "200" ] || [ "$HTTP_POST" = "302" ]; then
    echo "✅ SERVER IS WORKING CORRECTLY!"
    echo ""
    echo "The server accepts POST and returns: $HTTP_POST"
    echo ""
    echo "If you're still getting 405 in browser, it's definitely a browser issue."
    echo ""
    echo "SOLUTIONS:"
    echo "  1. Open file:///tmp/test_405.html in your browser"
    echo "  2. Click the test buttons - they should work"
    echo "  3. If they work, the issue is with the cached main page"
    echo ""
    echo "TO ACCESS THE REAL APP:"
    echo "  - DO NOT type 'localhost:5000' in address bar"
    echo "  - DO NOT use bookmarks"
    echo "  - Copy and paste this EXACT URL: http://localhost:5000/"
    echo "  - Press Enter"
    echo "  - Do a hard refresh: Ctrl+Shift+R"
else
    echo "⚠️  UNEXPECTED STATUS: $HTTP_POST"
    echo ""
    echo "Check if app is running on a different port"
fi

echo ""
echo "For more help, send me:"
echo "  1. Screenshot of the 405 error page"
echo "  2. Screenshot of browser DevTools Network tab"
echo "  3. What URL you're accessing (copy from address bar)"
echo ""
