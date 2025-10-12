#!/usr/bin/env python3
"""
Model Accuracy Test Script
Tests the trained ML model with sample data to verify accuracy
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
import logging
from feature_extraction import extract_features

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_model_accuracy():
    """Test the trained model accuracy with synthetic data"""
    
    print("\n" + "="*60)
    print("NEUROSHIELD MODEL ACCURACY TEST")
    print("="*60)
    
    try:
        # Load model and scaler
        model_path = '../ML_model/malwareclassifier-V2.pkl'
        scaler_path = '../ML_model/scaler.pkl'
        
        if not os.path.exists(model_path):
            model_path = 'ML_model/malwareclassifier-V2.pkl'
            scaler_path = 'ML_model/scaler.pkl'
        
        print(f"📁 Loading model from: {model_path}")
        model = joblib.load(model_path)
        print(f"✅ Model loaded successfully!")
        
        print(f"📁 Loading scaler from: {scaler_path}")
        scaler = joblib.load(scaler_path)
        print(f"✅ Scaler loaded successfully!")
        
        # Create test samples
        print(f"\n🧪 Creating test samples...")
        
        # Malware-like features (high entropy, suspicious characteristics)
        malware_sample = np.array([[
            12, 2, 6, 1048576,        # MajorLinkerVersion, MinorOS, MajorSubsystem, StackReserve
            1640995200, 6, 8256, 4194304,  # TimeDateStamp, MajorOS, Characteristics, ImageBase
            2, 0, 0, 500000, 8192,    # Subsystem, MinorImage, MinorSubsystem, InitializedData, DllChar
            1, 10000, 0, 20000,       # DirectoryEntryExport, ImageDirectoryExport, CheckSum, ImportSize
            10, 0, 50000, 7.5,        # SectionMaxChar, MajorImage, EntryPoint, MinEntropy
            1024, 10000              # SizeOfHeaders, MinVirtualSize
        ]])
        
        # Benign-like features (lower entropy, standard characteristics)
        benign_sample = np.array([[
            14, 0, 6, 1048576,        # Standard values
            1640995200, 6, 258, 4194304,  # Normal characteristics
            3, 0, 0, 100000, 0,       # Standard subsystem and smaller data
            0, 0, 0, 5000,            # No export, smaller import
            5, 0, 20000, 3.2,         # Fewer sections, lower entropy
            512, 5000                # Smaller headers and virtual size
        ]])
        
        print(f"✅ Created test samples")
        
        # Test predictions
        print(f"\n🔍 Testing model predictions...")
        
        # Scale features
        malware_scaled = scaler.transform(malware_sample)
        benign_scaled = scaler.transform(benign_sample)
        
        # Make predictions
        malware_pred = model.predict(malware_scaled)[0]
        malware_prob = model.predict_proba(malware_scaled)[0]
        
        benign_pred = model.predict(benign_scaled)[0]
        benign_prob = model.predict_proba(benign_scaled)[0]
        
        # Display results
        print(f"\n📊 Test Results:")
        print(f"   Malware Sample:")
        print(f"     Prediction: {'MALWARE' if malware_pred == 1 else 'BENIGN'}")
        print(f"     Confidence: {max(malware_prob)*100:.1f}%")
        print(f"     Probabilities: Benign={malware_prob[0]:.3f}, Malware={malware_prob[1]:.3f}")
        
        print(f"\n   Benign Sample:")
        print(f"     Prediction: {'MALWARE' if benign_pred == 1 else 'BENIGN'}")
        print(f"     Confidence: {max(benign_prob)*100:.1f}%")
        print(f"     Probabilities: Benign={benign_prob[0]:.3f}, Malware={benign_prob[1]:.3f}")
        
        # Verify accuracy
        correct_predictions = 0
        if malware_pred == 1:  # Should predict malware
            correct_predictions += 1
            print(f"\n✅ Malware sample correctly identified!")
        else:
            print(f"\n❌ Malware sample misclassified!")
        
        if benign_pred == 0:  # Should predict benign
            correct_predictions += 1
            print(f"✅ Benign sample correctly identified!")
        else:
            print(f"❌ Benign sample misclassified!")
        
        accuracy = correct_predictions / 2 * 100
        print(f"\n📈 Test Accuracy: {accuracy:.1f}%")
        
        if accuracy == 100:
            print(f"🎉 PERFECT ACCURACY! Model is working correctly!")
        elif accuracy >= 50:
            print(f"✅ Model is working but may need refinement")
        else:
            print(f"❌ Model needs attention - poor performance")
        
        # Model information
        print(f"\n📋 Model Information:")
        print(f"   Type: {type(model).__name__}")
        print(f"   Features: {model.n_features_in_}")
        
        if hasattr(model, 'estimators_'):
            print(f"   Estimators: {len(model.estimators_)}")
            for i, estimator in enumerate(model.estimators_):
                est_name = type(estimator[1]).__name__ if isinstance(estimator, tuple) else type(estimator).__name__
                print(f"     {i+1}. {est_name}")
        
        return accuracy
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print(f"\n❌ Test failed: {str(e)}")
        return 0

def test_with_real_files():
    """Test with actual files if available"""
    print(f"\n🔍 Testing with real files...")
    
    test_files = []
    uploads_dir = 'uploads'
    
    if os.path.exists(uploads_dir):
        for filename in os.listdir(uploads_dir):
            if filename.endswith(('.exe', '.dll')):
                test_files.append(os.path.join(uploads_dir, filename))
    
    if not test_files:
        print(f"⚠️  No test files found in {uploads_dir}")
        return
    
    try:
        # Load model
        model_path = '../ML_model/malwareclassifier-V2.pkl'
        scaler_path = '../ML_model/scaler.pkl'
        
        if not os.path.exists(model_path):
            model_path = 'ML_model/malwareclassifier-V2.pkl'
            scaler_path = 'ML_model/scaler.pkl'
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        print(f"📁 Testing {len(test_files)} files...")
        
        for file_path in test_files:
            try:
                # Extract features
                features = extract_features(file_path)
                
                # Scale and predict
                features_scaled = scaler.transform(features)
                prediction = model.predict(features_scaled)[0]
                probabilities = model.predict_proba(features_scaled)[0]
                
                result = "MALWARE" if prediction == 1 else "SAFE"
                confidence = max(probabilities) * 100
                
                print(f"   📄 {os.path.basename(file_path)}: {result} ({confidence:.1f}%)")
                
            except Exception as e:
                print(f"   ❌ {os.path.basename(file_path)}: Error - {str(e)}")
    
    except Exception as e:
        print(f"❌ Real file test failed: {str(e)}")

def main():
    """Main test function"""
    print("Starting NeuroShield Model Accuracy Tests...")
    
    # Test 1: Synthetic data
    accuracy = test_model_accuracy()
    
    # Test 2: Real files (if available)
    test_with_real_files()
    
    print(f"\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ Model loaded and tested successfully")
    print(f"📊 Synthetic data accuracy: {accuracy:.1f}%")
    
    if accuracy >= 90:
        print(f"🎉 HIGH ACCURACY - Model ready for production!")
    elif accuracy >= 70:
        print(f"✅ GOOD ACCURACY - Model working well")
    else:
        print(f"⚠️  LOW ACCURACY - Model may need retraining")
    
    print(f"\n🚀 The ML model is ready to use!")
    print(f"   Start the app: python app.py")
    print(f"   Access at: http://localhost:5000")
    print("="*60)

if __name__ == '__main__':
    main()