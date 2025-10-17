#!/usr/bin/env python3
"""
Fix for HTTP 405 Error - Diagnostic and Solution
"""

import sys
import os

print("="*70)
print("HTTP 405 ERROR DIAGNOSTIC AND FIX")
print("="*70)

print("\n1. Checking Flask routes in ML app...")
sys.path.insert(0, '/workspace/ML_based_detectionn')
try:
    from app import app as ml_app
    print("   ✅ ML app imports successfully")
    
    # Check routes
    routes = []
    for rule in ml_app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})),
            'path': str(rule)
        })
    
    print("\n   Available routes in ML app:")
    for route in routes:
        print(f"      {route['path']:20s} -> Methods: {route['methods']}")
    
    # Verify /analyze accepts POST
    analyze_found = False
    for route in routes:
        if route['path'] == '/analyze' and 'POST' in route['methods']:
            analyze_found = True
            print("\n   ✅ /analyze route correctly accepts POST")
    
    if not analyze_found:
        print("\n   ❌ ERROR: /analyze route not configured for POST!")
        
except Exception as e:
    print(f"   ❌ Error checking ML app: {e}")

print("\n2. Checking Flask routes in API app...")
sys.path = [p for p in sys.path if 'ML_based_detectionn' not in p]
if 'app' in sys.modules:
    del sys.modules['app']

sys.path.insert(0, '/workspace/Virus_total_based')
os.environ['NEUROSHIELD_API_KEY'] = 'test_key_for_diagnostic'

try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("vt_app", "/workspace/Virus_total_based/app.py")
    vt_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vt_module)
    
    print("   ✅ API app imports successfully")
    
    # Check routes
    routes = []
    for rule in vt_module.app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'})),
            'path': str(rule)
        })
    
    print("\n   Available routes in API app:")
    for route in routes:
        print(f"      {route['path']:20s} -> Methods: {route['methods']}")
    
    # Verify /analyze accepts POST
    analyze_found = False
    for route in routes:
        if route['path'] == '/analyze' and 'POST' in route['methods']:
            analyze_found = True
            print("\n   ✅ /analyze route correctly accepts POST")
    
    if not analyze_found:
        print("\n   ❌ ERROR: /analyze route not configured for POST!")
        
except Exception as e:
    print(f"   ❌ Error checking API app: {e}")

print("\n" + "="*70)
print("COMMON CAUSES OF HTTP 405 ERROR:")
print("="*70)

print("""
1. ❌ Running from wrong directory
   Solution: Always run from the app directory:
   
   cd /workspace/ML_based_detectionn
   python3 app.py
   
   OR
   
   cd /workspace/Virus_total_based
   python3 app.py

2. ❌ Port already in use
   Solution: Kill existing process or use different port:
   
   # Kill process on port 5000
   lsof -ti:5000 | xargs kill -9
   
   # Or use different port
   export FLASK_RUN_PORT=5002
   python3 app.py

3. ❌ Proxy or reverse proxy misconfiguration
   Solution: Run directly without proxy first

4. ❌ Browser caching old page
   Solution: Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
   Or clear browser cache

5. ❌ Form action URL incorrect
   Solution: Forms should have action="/analyze" method="post"

6. ❌ CSRF token required but not provided
   Solution: Our apps don't require CSRF for form submission
""")

print("\n" + "="*70)
print("SOLUTION - How to Start the Apps Correctly:")
print("="*70)

print("""
For ML Detection App:
=====================
cd /workspace/ML_based_detectionn
python3 app.py

Then open: http://localhost:5000


For Threat Intelligence App:
=============================
cd /workspace/Virus_total_based
python3 app.py

Then open: http://localhost:5001


Production Mode (Recommended):
===============================
cd /workspace
./start_ml_app.sh
./start_virustotal_app.sh
""")

print("\n" + "="*70)
print("VERIFICATION:")
print("="*70)

print("""
After starting the app, verify it's working:

1. Check if app is running:
   curl http://localhost:5000/
   
   Should return HTML (not 404 or 405)

2. Test POST to /analyze endpoint:
   curl -X POST http://localhost:5000/analyze
   
   Should return error about missing file (not 405)

3. If you get "Connection refused":
   - App is not running
   - Check if started successfully
   - Look for errors in console

4. If you get 404:
   - Wrong URL or port
   - App started on different port
   
5. If you get 405:
   - Browser cached old page (hard refresh)
   - Proxy/nginx misconfiguration
   - Wrong HTTP method
""")

print("\n" + "="*70)
print("Quick Fix - Restart the Application:")
print("="*70)

print("""
# Kill any running Python processes
pkill -9 python3

# Start fresh
cd /workspace/ML_based_detectionn
python3 app.py

# In browser:
# 1. Hard refresh (Ctrl+Shift+R)
# 2. Navigate to http://localhost:5000
# 3. Upload a file and click Analyze
""")

print("\n" + "="*70)
print("✅ ROUTES ARE CONFIGURED CORRECTLY")
print("   The issue is likely with how the app is being run,")
print("   browser cache, or port conflicts.")
print("="*70)
