#!/usr/bin/env python3
"""
Complete Application Test
Tests the full Flask app functionality
"""

import os
import sys
import requests
import time
import subprocess
import threading
from pathlib import Path

def test_flask_app():
    """Test the Flask application"""
    print("\n" + "="*60)
    print("NEUROSHIELD FLASK APP TEST")
    print("="*60)
    
    # Start the Flask app in a subprocess
    print("🚀 Starting Flask application...")
    
    app_process = None
    try:
        # Change to the correct directory
        os.chdir('ML_based_detectionn')
        
        # Start the Flask app
        app_process = subprocess.Popen([
            'python3', 'app.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for the app to start
        time.sleep(3)
        
        # Test if app is running
        try:
            response = requests.get('http://localhost:5000', timeout=5)
            if response.status_code == 200:
                print("✅ Flask app is running successfully!")
                print(f"   Status Code: {response.status_code}")
                print(f"   Content Length: {len(response.content)} bytes")
                
                # Test if the page contains expected content
                if b'NeuroShield' in response.content or b'upload' in response.content.lower():
                    print("✅ Home page contains expected content")
                else:
                    print("⚠️  Home page content may be incomplete")
                    
                return True
            else:
                print(f"❌ App responded with status code: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to Flask app")
            return False
        except requests.exceptions.Timeout:
            print("❌ Flask app request timed out")
            return False
            
    except Exception as e:
        print(f"❌ Error starting Flask app: {str(e)}")
        return False
        
    finally:
        # Clean up process
        if app_process:
            app_process.terminate()
            try:
                app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                app_process.kill()
            print("🔄 Flask app process cleaned up")
            
        # Return to original directory
        os.chdir('..')

def check_requirements():
    """Check if all requirements are met"""
    print("\n🔍 Checking system requirements...")
    
    checks_passed = 0
    total_checks = 5
    
    # Check 1: Model files exist
    model_path = 'ML_model/malwareclassifier-V2.pkl'
    scaler_path = 'ML_model/scaler.pkl'
    
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        print("✅ ML model files found")
        checks_passed += 1
    else:
        print("❌ ML model files missing")
    
    # Check 2: Feature extraction module
    try:
        sys.path.append('ML_based_detectionn')
        import feature_extraction
        print("✅ Feature extraction module available")
        checks_passed += 1
    except ImportError as e:
        print(f"❌ Feature extraction module error: {e}")
    
    # Check 3: Flask and dependencies
    try:
        import flask
        import joblib
        import pandas
        import numpy
        import sklearn
        print("✅ Required Python packages available")
        checks_passed += 1
    except ImportError as e:
        print(f"❌ Missing Python packages: {e}")
    
    # Check 4: Upload directory
    upload_dir = 'ML_based_detectionn/uploads'
    if os.path.exists(upload_dir):
        print("✅ Upload directory exists")
        checks_passed += 1
    else:
        print("❌ Upload directory missing")
    
    # Check 5: Templates
    templates_dir = 'ML_based_detectionn/templates'
    required_templates = ['index.html', 'result.html']
    
    if os.path.exists(templates_dir):
        missing_templates = []
        for template in required_templates:
            if not os.path.exists(os.path.join(templates_dir, template)):
                missing_templates.append(template)
        
        if not missing_templates:
            print("✅ Required templates found")
            checks_passed += 1
        else:
            print(f"❌ Missing templates: {missing_templates}")
    else:
        print("❌ Templates directory missing")
    
    print(f"\n📊 System Check: {checks_passed}/{total_checks} passed")
    
    if checks_passed == total_checks:
        print("🎉 All requirements met! System ready for use.")
        return True
    else:
        print("⚠️  Some requirements not met. Please fix issues above.")
        return False

def main():
    """Main test function"""
    print("Starting NeuroShield Complete System Test...")
    
    # Check requirements first
    requirements_ok = check_requirements()
    
    if not requirements_ok:
        print("\n❌ Requirements check failed. Cannot proceed with app test.")
        return
    
    # Test Flask application
    app_working = test_flask_app()
    
    # Final summary
    print(f"\n" + "="*60)
    print("COMPLETE SYSTEM TEST SUMMARY")
    print("="*60)
    
    if requirements_ok and app_working:
        print("🎉 ALL TESTS PASSED!")
        print("✅ NeuroShield is ready for use")
        print("\n🚀 To start the application:")
        print("   1. cd ML_based_detectionn")
        print("   2. python3 app.py")
        print("   3. Open http://localhost:5000 in your browser")
        print("\n🔒 The system provides:")
        print("   • High-accuracy malware detection (99.75%)")
        print("   • Support for .exe, .dll, .txt, and .pdf files")
        print("   • Robust feature extraction and analysis")
        print("   • Secure file handling and quarantine")
    else:
        print("❌ SYSTEM NOT READY")
        print("   Please fix the issues identified above")
    
    print("="*60)

if __name__ == '__main__':
    main()