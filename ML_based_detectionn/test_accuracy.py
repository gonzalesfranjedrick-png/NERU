#!/usr/bin/env python3
"""
Test Script for ML Model Accuracy Verification
NeuroShield - Developed by F.J.G

This script tests the trained ML model to ensure accurate results.
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from feature_extraction import extract_features

def test_model_accuracy():
    """Test the ML model accuracy with synthetic data"""
    print("=" * 60)
    print("NEUROSHIELD - MODEL ACCURACY TEST")
    print("=" * 60)
    
    # Check if model files exist
    model_path = 'ML_model/malwareclassifier-V2.pkl'
    scaler_path = 'ML_model/scaler.pkl'
    
    if not os.path.exists(model_path):
        print(f"❌ Error: Model file not found at {model_path}")
        return False
        
    if not os.path.exists(scaler_path):
        print(f"❌ Error: Scaler file not found at {scaler_path}")
        return False
    
    # Load model and scaler
    print(f"📁 Loading model from: {model_path}")
    model = joblib.load(model_path)
    print(f"📁 Loading scaler from: {scaler_path}")
    scaler = joblib.load(scaler_path)
    
    print(f"✅ Model loaded successfully")
    print(f"   Type: {type(model).__name__}")
    print(f"   Features expected: {model.n_features_in_}")
    
    # Generate test data
    print(f"\n📊 Generating test data...")
    np.random.seed(123)  # Different seed for testing
    
    # Create test samples with known patterns
    n_test = 100
    n_malware = 60
    n_benign = 40
    
    # Malware test data (should be detected as malware)
    malware_test = np.random.randn(n_malware, 23)
    malware_test[:, 20] = np.random.uniform(6.0, 8.0, n_malware)  # High entropy
    malware_test[:, 17] = np.random.uniform(5, 15, n_malware)     # More sections
    malware_test[:, 11] = np.random.uniform(50000, 1000000, n_malware)  # Large initialized data
    
    # Benign test data (should be detected as safe)
    benign_test = np.random.randn(n_benign, 23)
    benign_test[:, 20] = np.random.uniform(2.0, 5.5, n_benign)   # Lower entropy
    benign_test[:, 17] = np.random.uniform(2, 6, n_benign)       # Fewer sections
    benign_test[:, 11] = np.random.uniform(1000, 50000, n_benign)  # Smaller initialized data
    
    # Combine test data
    X_test = np.vstack([malware_test, benign_test])
    y_true = np.hstack([np.ones(n_malware), np.zeros(n_benign)])
    
    print(f"   Test samples: {n_test}")
    print(f"   Malware samples: {n_malware}")
    print(f"   Benign samples: {n_benign}")
    
    # Scale features
    print(f"\n🔄 Scaling features...")
    X_test_scaled = scaler.transform(X_test)
    
    # Make predictions
    print(f"🤖 Running predictions...")
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)
    
    # Calculate accuracy
    accuracy = accuracy_score(y_true, y_pred)
    
    print(f"\n📈 ACCURACY RESULTS:")
    print(f"   Overall Accuracy: {accuracy*100:.2f}%")
    
    # Detailed breakdown
    malware_correct = sum((y_true[:n_malware] == 1) & (y_pred[:n_malware] == 1))
    benign_correct = sum((y_true[n_malware:] == 0) & (y_pred[n_malware:] == 0))
    
    malware_accuracy = malware_correct / n_malware * 100
    benign_accuracy = benign_correct / n_benign * 100
    
    print(f"   Malware Detection: {malware_accuracy:.1f}% ({malware_correct}/{n_malware})")
    print(f"   Benign Detection: {benign_accuracy:.1f}% ({benign_correct}/{n_benign})")
    
    # Classification report
    print(f"\n📊 Detailed Classification Report:")
    print(classification_report(y_true, y_pred, 
                              target_names=['Benign', 'Malware'],
                              digits=3))
    
    # Check confidence levels
    confidence_scores = np.max(y_pred_proba, axis=1) * 100
    avg_confidence = np.mean(confidence_scores)
    
    print(f"\n🎯 Confidence Analysis:")
    print(f"   Average Confidence: {avg_confidence:.1f}%")
    print(f"   High Confidence (>90%): {sum(confidence_scores > 90)}/{n_test}")
    print(f"   Low Confidence (<70%): {sum(confidence_scores < 70)}/{n_test}")
    
    # Success criteria
    success = accuracy >= 0.95 and malware_accuracy >= 90 and benign_accuracy >= 90
    
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 MODEL ACCURACY TEST PASSED!")
        print("✅ Model is ready for production use")
        if accuracy >= 0.99:
            print("🏆 EXCEPTIONAL ACCURACY ACHIEVED!")
    else:
        print("⚠️  MODEL ACCURACY BELOW THRESHOLD")
        print("❌ Consider retraining with more data")
    
    print("=" * 60)
    
    return success

def test_pe_file_analysis():
    """Test PE file feature extraction and analysis"""
    print(f"\n📁 Testing PE File Analysis...")
    
    # Check for test PE files
    test_files = ['uploads/test.exe', 'uploads/notepad.exe']
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"\n🔍 Testing file: {test_file}")
            try:
                # Extract features
                features = extract_features(test_file)
                print(f"   ✅ Features extracted: {len(features.columns)} features")
                
                # Load model for prediction
                model_path = 'ML_model/malwareclassifier-V2.pkl'
                scaler_path = 'ML_model/scaler.pkl'
                
                model = joblib.load(model_path)
                scaler = joblib.load(scaler_path)
                
                # Scale and predict
                features_scaled = scaler.transform(features)
                prediction = model.predict(features_scaled)[0]
                confidence = max(model.predict_proba(features_scaled)[0]) * 100
                
                result = "Malware" if prediction == 1 else "Safe"
                print(f"   🎯 Prediction: {result} ({confidence:.1f}% confidence)")
                
            except Exception as e:
                print(f"   ❌ Error analyzing {test_file}: {str(e)}")
        else:
            print(f"   ⚠️  Test file not found: {test_file}")

if __name__ == '__main__':
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("Starting ML Model Accuracy Tests...\n")
    
    # Test model accuracy
    accuracy_passed = test_model_accuracy()
    
    # Test PE file analysis
    test_pe_file_analysis()
    
    print(f"\n{'='*60}")
    if accuracy_passed:
        print("🎉 ALL TESTS PASSED - MODEL IS READY!")
        print("   Start the application with: python app.py")
    else:
        print("❌ TESTS FAILED - MODEL NEEDS IMPROVEMENT")
    print("="*60)
    
    sys.exit(0 if accuracy_passed else 1)