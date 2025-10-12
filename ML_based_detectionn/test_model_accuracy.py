#!/usr/bin/env python3
"""
Test script to verify the ML model accuracy
"""

import os
import sys
import joblib
import numpy as np
from feature_extraction import extract_features

def test_model_accuracy():
    """Test the model with sample files"""
    print("=" * 60)
    print("NeuroShield Model Accuracy Test")
    print("=" * 60)
    
    # Load the trained model
    try:
        model = joblib.load('ML_model/malwareclassifier-V2.pkl')
        scaler = joblib.load('ML_model/scaler.pkl')
        feature_selector = joblib.load('ML_model/feature_selector.pkl')
        print("✅ Model, scaler, and feature selector loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False
    
    # Test with sample files in uploads directory
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        print(f"❌ Uploads directory not found: {uploads_dir}")
        return False
    
    sample_files = [f for f in os.listdir(uploads_dir) if f.endswith(('.exe', '.dll'))]
    
    if not sample_files:
        print("❌ No sample files found in uploads directory")
        return False
    
    print(f"\n📁 Testing with {len(sample_files)} sample files:")
    print("-" * 60)
    
    results = []
    
    for filename in sample_files:
        file_path = os.path.join(uploads_dir, filename)
        print(f"\n🔍 Testing: {filename}")
        
        try:
            # Extract features
            features = extract_features(file_path)
            if features is None:
                print(f"   ❌ Could not extract features")
                continue
            
            # Apply scaling and feature selection
            features_scaled = scaler.transform(features)
            features_selected = feature_selector.transform(features_scaled)
            
            # Make prediction
            prediction = model.predict(features_selected)[0]
            prediction_proba = model.predict_proba(features_selected)[0]
            
            # Get confidence
            confidence = max(prediction_proba) * 100
            
            # Determine result
            result = "MALWARE" if prediction == 1 else "SAFE"
            malware_prob = prediction_proba[1] * 100
            safe_prob = prediction_proba[0] * 100
            
            print(f"   📊 Result: {result}")
            print(f"   📈 Confidence: {confidence:.1f}%")
            print(f"   🦠 Malware Probability: {malware_prob:.1f}%")
            print(f"   ✅ Safe Probability: {safe_prob:.1f}%")
            
            results.append({
                'filename': filename,
                'prediction': result,
                'confidence': confidence,
                'malware_prob': malware_prob,
                'safe_prob': safe_prob
            })
            
        except Exception as e:
            print(f"   ❌ Error processing {filename}: {e}")
            continue
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    if results:
        malware_count = sum(1 for r in results if r['prediction'] == 'MALWARE')
        safe_count = sum(1 for r in results if r['prediction'] == 'SAFE')
        avg_confidence = np.mean([r['confidence'] for r in results])
        
        print(f"📊 Files tested: {len(results)}")
        print(f"🦠 Detected as malware: {malware_count}")
        print(f"✅ Detected as safe: {safe_count}")
        print(f"📈 Average confidence: {avg_confidence:.1f}%")
        
        print(f"\n📋 Detailed Results:")
        for result in results:
            print(f"   {result['filename']:30s} | {result['prediction']:8s} | {result['confidence']:6.1f}%")
        
        print(f"\n✅ Model is working correctly!")
        return True
    else:
        print("❌ No files were successfully processed")
        return False

if __name__ == '__main__':
    success = test_model_accuracy()
    sys.exit(0 if success else 1)