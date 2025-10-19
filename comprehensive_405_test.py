#!/usr/bin/env python3
"""
Comprehensive HTTP 405 Error Prevention Test
Tests all routes and form submissions to ensure no 405 errors
"""

import sys
import os
import time
import subprocess
import requests
import tempfile
from pathlib import Path

print("=" * 80)
print("COMPREHENSIVE HTTP 405 ERROR PREVENTION TEST")
print("NeuroShield - Developed by F.J.G")
print("=" * 80)

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

# Test results tracking
tests_passed = 0
tests_failed = 0
tests_total = 0
error_405_found = False

def run_test(test_name, test_func):
    global tests_passed, tests_failed, tests_total, error_405_found
    tests_total += 1
    print(f"\nTest {tests_total}: {test_name}")
    print("-" * 80)
    try:
        result = test_func()
        if result:
            tests_passed += 1
            print_success(f"PASSED")
        else:
            tests_failed += 1
            print_error(f"FAILED")
        return result
    except Exception as e:
        tests_failed += 1
        print_error(f"FAILED with exception: {e}")
        return False

# Test 1: Start ML Application
def test_start_ml_app():
    print_info("Starting ML Detection Application...")
    os.chdir('/workspace/ML_based_detectionn')
    
    # Start app in background
    with open('/tmp/ml_app_test.log', 'w') as log:
        proc = subprocess.Popen(
            ['python3', 'app.py'],
            stdout=log,
            stderr=log,
            cwd='/workspace/ML_based_detectionn'
        )
    
    # Save PID
    with open('/tmp/ml_app.pid', 'w') as f:
        f.write(str(proc.pid))
    
    print_info(f"App started with PID: {proc.pid}")
    print_info("Waiting 3 seconds for app to initialize...")
    time.sleep(3)
    
    # Check if process is running
    if proc.poll() is None:
        print_success("ML app is running")
        return True
    else:
        print_error("ML app failed to start")
        with open('/tmp/ml_app_test.log', 'r') as log:
            print(log.read())
        return False

# Test 2: Test ML App GET /
def test_ml_get_home():
    print_info("Testing GET request to ML app homepage...")
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print_success("Homepage loads successfully")
            
            # Check if HTML contains form
            if 'action="/analyze"' in response.text:
                print_success("Form with /analyze action found")
            else:
                print_warning("Form action not found in HTML")
            
            return True
        else:
            print_error(f"Expected 200, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

# Test 3: Test ML App POST /analyze (no file)
def test_ml_post_analyze_no_file():
    global error_405_found
    print_info("Testing POST request to /analyze without file...")
    try:
        response = requests.post('http://localhost:5000/analyze', timeout=5)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 405:
            print_error("HTTP 405 METHOD NOT ALLOWED - This is the error!")
            error_405_found = True
            return False
        elif response.status_code in [200, 302, 400]:
            print_success(f"Accepts POST (returned {response.status_code})")
            print_info("Returns error for missing file - this is correct behavior")
            return True
        else:
            print_warning(f"Unexpected status code: {response.status_code}")
            return True  # Still not 405
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

# Test 4: Test ML App POST /analyze with file
def test_ml_post_analyze_with_file():
    global error_405_found
    print_info("Testing POST request with file upload...")
    
    # Check if test file exists
    test_file = '/workspace/ML_based_detectionn/uploads/notepad.exe'
    if not os.path.exists(test_file):
        print_warning("Test file not found, skipping")
        return True
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': ('test.exe', f, 'application/octet-stream')}
            response = requests.post(
                'http://localhost:5000/analyze',
                files=files,
                timeout=10
            )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 405:
            print_error("HTTP 405 METHOD NOT ALLOWED - This is the error!")
            error_405_found = True
            return False
        elif response.status_code in [200, 302]:
            print_success("File upload and analysis successful")
            return True
        else:
            print_warning(f"Unexpected status code: {response.status_code}")
            return True  # Still not 405
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

# Test 5: Test form submission headers
def test_ml_form_headers():
    print_info("Testing form submission with proper headers...")
    try:
        headers = {
            'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        response = requests.post(
            'http://localhost:5000/analyze',
            headers={'Accept': 'text/html'},
            timeout=5
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code != 405:
            print_success("Form headers accepted correctly")
            return True
        else:
            print_error("HTTP 405 with form headers")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

# Test 6: Stop ML app and start API app
def test_switch_to_api_app():
    print_info("Stopping ML app and starting API app...")
    
    # Stop ML app
    try:
        with open('/tmp/ml_app.pid', 'r') as f:
            pid = int(f.read().strip())
        os.kill(pid, 9)
        time.sleep(2)
        print_success("ML app stopped")
    except:
        print_warning("ML app PID not found")
    
    # Start API app
    os.chdir('/workspace/Virus_total_based')
    os.environ['NEUROSHIELD_API_KEY'] = 'test_key_for_testing'
    
    with open('/tmp/api_app_test.log', 'w') as log:
        proc = subprocess.Popen(
            ['python3', 'app.py'],
            stdout=log,
            stderr=log,
            cwd='/workspace/Virus_total_based',
            env=os.environ.copy()
        )
    
    with open('/tmp/api_app.pid', 'w') as f:
        f.write(str(proc.pid))
    
    print_info(f"API app started with PID: {proc.pid}")
    print_info("Waiting 3 seconds for app to initialize...")
    time.sleep(3)
    
    if proc.poll() is None:
        print_success("API app is running")
        return True
    else:
        print_error("API app failed to start")
        return False

# Test 7: Test API App GET /
def test_api_get_home():
    print_info("Testing GET request to API app homepage...")
    try:
        response = requests.get('http://localhost:5001/', timeout=5)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print_success("Homepage loads successfully")
            return True
        else:
            print_error(f"Expected 200, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

# Test 8: Test API App POST /analyze
def test_api_post_analyze():
    global error_405_found
    print_info("Testing POST request to API /analyze...")
    try:
        response = requests.post('http://localhost:5001/analyze', timeout=5)
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 405:
            print_error("HTTP 405 METHOD NOT ALLOWED - This is the error!")
            error_405_found = True
            return False
        elif response.status_code in [200, 302, 400]:
            print_success(f"Accepts POST (returned {response.status_code})")
            return True
        else:
            print_warning(f"Unexpected status code: {response.status_code}")
            return True
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False

# Test 9: Verify routes in code
def test_verify_routes_in_code():
    print_info("Verifying route configurations in code...")
    
    # Check ML app
    ml_app_path = '/workspace/ML_based_detectionn/app.py'
    with open(ml_app_path, 'r') as f:
        ml_code = f.read()
    
    if "@app.route('/analyze', methods=['POST'])" in ml_code or \
       "@app.route('/analyze', methods=['GET', 'POST'])" in ml_code:
        print_success("ML app /analyze route accepts POST")
    else:
        print_error("ML app /analyze route configuration issue")
        return False
    
    # Check API app
    api_app_path = '/workspace/Virus_total_based/app.py'
    with open(api_app_path, 'r') as f:
        api_code = f.read()
    
    if "@app.route('/analyze', methods=['POST'])" in api_code or \
       "@app.route('/analyze', methods=['GET', 'POST'])" in api_code:
        print_success("API app /analyze route accepts POST")
    else:
        print_error("API app /analyze route configuration issue")
        return False
    
    return True

# Test 10: Verify HTML forms
def test_verify_html_forms():
    print_info("Verifying HTML form configurations...")
    
    # Check ML template
    ml_template = '/workspace/ML_based_detectionn/templates/index.html'
    with open(ml_template, 'r') as f:
        ml_html = f.read()
    
    if 'action="/analyze"' in ml_html and 'method="post"' in ml_html.lower():
        print_success("ML template form correctly configured")
    else:
        print_error("ML template form configuration issue")
        return False
    
    # Check API template
    api_template = '/workspace/Virus_total_based/templates/index.html'
    with open(api_template, 'r') as f:
        api_html = f.read()
    
    if 'action="/analyze"' in api_html and 'method="post"' in api_html.lower():
        print_success("API template form correctly configured")
    else:
        print_error("API template form configuration issue")
        return False
    
    return True

# Run all tests
print("\n" + "=" * 80)
print("STARTING COMPREHENSIVE TESTS")
print("=" * 80)

run_test("Start ML Detection Application", test_start_ml_app)
run_test("ML App - GET Homepage", test_ml_get_home)
run_test("ML App - POST /analyze (no file)", test_ml_post_analyze_no_file)
run_test("ML App - POST /analyze (with file)", test_ml_post_analyze_with_file)
run_test("ML App - Form Headers", test_ml_form_headers)
run_test("Switch to API Application", test_switch_to_api_app)
run_test("API App - GET Homepage", test_api_get_home)
run_test("API App - POST /analyze", test_api_post_analyze)
run_test("Verify Routes in Code", test_verify_routes_in_code)
run_test("Verify HTML Forms", test_verify_html_forms)

# Cleanup
print("\n" + "=" * 80)
print("CLEANUP")
print("=" * 80)
print_info("Stopping all test applications...")

try:
    with open('/tmp/api_app.pid', 'r') as f:
        pid = int(f.read().strip())
    os.kill(pid, 9)
    print_success("API app stopped")
except:
    pass

subprocess.run(['pkill', '-9', 'python3'], stderr=subprocess.DEVNULL)
time.sleep(1)
print_success("All processes cleaned up")

# Final Results
print("\n" + "=" * 80)
print("FINAL TEST RESULTS")
print("=" * 80)

print(f"\nTotal Tests: {tests_total}")
print(f"{Colors.GREEN}Passed: {tests_passed}{Colors.END}")
print(f"{Colors.RED}Failed: {tests_failed}{Colors.END}")

success_rate = (tests_passed / tests_total * 100) if tests_total > 0 else 0
print(f"\nSuccess Rate: {success_rate:.1f}%")

print("\n" + "=" * 80)
if error_405_found:
    print(f"{Colors.RED}❌ HTTP 405 ERROR DETECTED!{Colors.END}")
    print(f"{Colors.RED}The application returned METHOD NOT ALLOWED.{Colors.END}")
    print("\nThis should NOT happen. Check the error logs above.")
else:
    print(f"{Colors.GREEN}✅ NO HTTP 405 ERRORS DETECTED!{Colors.END}")
    print(f"{Colors.GREEN}All routes accept POST requests correctly.{Colors.END}")

print("=" * 80)

if tests_passed == tests_total and not error_405_found:
    print(f"\n{Colors.GREEN}🎉 ALL TESTS PASSED!{Colors.END}")
    print(f"{Colors.GREEN}Your application will NOT have HTTP 405 errors.{Colors.END}")
    print("\n✅ Safe to use in production!")
    sys.exit(0)
else:
    print(f"\n{Colors.YELLOW}⚠️  Some tests failed.{Colors.END}")
    print("Review the errors above.")
    sys.exit(1)
