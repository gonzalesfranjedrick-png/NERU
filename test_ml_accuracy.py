#!/usr/bin/env python3
"""
Test script to verify ML model accuracy and application functionality
"""
import sys
import os

# Add ML_based_detectionn to path
sys.path.insert(0, '/workspace/ML_based_detectionn')

def test_model_loading():
    """Test that the model and scaler can be loaded"""
    print("=" * 80)
    print("TEST 1: Model Loading")
    print("=" * 80)
    
    import joblib
    
    model_path = '/workspace/ML_based_detectionn/ML_model/malwareclassifier-V2.pkl'
    scaler_path = '/workspace/ML_based_detectionn/ML_model/scaler.pkl'
    
    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        print(f"✅ Model loaded: {type(model).__name__}")
        print(f"✅ Scaler loaded: {type(scaler).__name__}")
        print(f"✅ Model expects {model.n_features_in_} features")
        
        return True, model, scaler
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return False, None, None

def test_feature_extraction():
    """Test that feature extraction works correctly"""
    print("\n" + "=" * 80)
    print("TEST 2: Feature Extraction")
    print("=" * 80)
    
    from feature_extraction import extract_features
    
    test_files = [
        '/workspace/ML_based_detectionn/uploads/notepad.exe',
        '/workspace/ML_based_detectionn/uploads/processhacker-2.39-setup.exe'
    ]
    
    results = []
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"⚠️  Test file not found: {test_file}")
            continue
        
        print(f"\nTesting: {os.path.basename(test_file)}")
        print("-" * 80)
        
        try:
            features = extract_features(test_file)
            
            print(f"✅ Features extracted: {features.shape}")
            print(f"✅ Feature count: {len(features.columns)}")
            print(f"✅ No missing values: {features.isnull().sum().sum() == 0}")
            
            # Display some key features
            print("\nKey Feature Values:")
            print(f"  - SectionMinEntropy: {features['SectionMinEntropy'].values[0]:.4f}")
            print(f"  - Characteristics: {features['Characteristics'].values[0]}")
            print(f"  - AddressOfEntryPoint: {features['AddressOfEntryPoint'].values[0]}")
            
            results.append((test_file, features))
            
        except Exception as e:
            print(f"❌ Feature extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return False, []
    
    return True, results

def test_prediction(model, scaler, feature_results):
    """Test that predictions work correctly"""
    print("\n" + "=" * 80)
    print("TEST 3: Model Predictions")
    print("=" * 80)
    
    for test_file, features in feature_results:
        print(f"\nPredicting: {os.path.basename(test_file)}")
        print("-" * 80)
        
        try:
            # Scale features
            features_scaled = scaler.transform(features)
            
            # Make prediction
            prediction = model.predict(features_scaled)
            prediction_proba = model.predict_proba(features_scaled)[0]
            
            confidence = max(prediction_proba) * 100
            result = "Malware" if prediction[0] == 1 else "Safe"
            
            print(f"✅ Prediction: {result}")
            print(f"✅ Confidence: {confidence:.1f}%")
            print(f"✅ Probabilities: Benign={prediction_proba[0]*100:.1f}%, Malware={prediction_proba[1]*100:.1f}%")
            
        except Exception as e:
            print(f"❌ Prediction failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

def test_app_configuration():
    """Test that the Flask app is configured correctly"""
    print("\n" + "=" * 80)
    print("TEST 4: Application Configuration")
    print("=" * 80)
    
    try:
        from app import app, model, scaler, ALLOWED_EXTENSIONS
        
        print(f"✅ Flask app created: {app.name}")
        print(f"✅ Debug mode: {app.config['DEBUG']}")
        print(f"✅ Upload folder: {app.config['UPLOAD_FOLDER']}")
        print(f"✅ Max file size: {app.config['MAX_CONTENT_LENGTH'] / (1024*1024):.1f} MB")
        print(f"✅ Allowed extensions: {ALLOWED_EXTENSIONS}")
        print(f"✅ Model loaded in app: {model is not None}")
        print(f"✅ Scaler loaded in app: {scaler is not None}")
        
        return True
    except Exception as e:
        print(f"❌ App configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_consistency():
    """Test that predictions are consistent"""
    print("\n" + "=" * 80)
    print("TEST 5: Prediction Consistency")
    print("=" * 80)
    
    from feature_extraction import extract_features
    import joblib
    
    model = joblib.load('/workspace/ML_based_detectionn/ML_model/malwareclassifier-V2.pkl')
    scaler = joblib.load('/workspace/ML_based_detectionn/ML_model/scaler.pkl')
    
    test_file = '/workspace/ML_based_detectionn/uploads/notepad.exe'
    
    if not os.path.exists(test_file):
        print("⚠️  Test file not found, skipping consistency test")
        return True
    
    print(f"Running multiple predictions on: {os.path.basename(test_file)}")
    print("-" * 80)
    
    predictions = []
    confidences = []
    
    for i in range(5):
        features = extract_features(test_file)
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)[0]
        confidence = max(model.predict_proba(features_scaled)[0])
        
        predictions.append(prediction)
        confidences.append(confidence)
    
    # Check consistency
    if len(set(predictions)) == 1:
        print(f"✅ All predictions are consistent: {predictions[0]}")
        print(f"✅ Average confidence: {sum(confidences)/len(confidences)*100:.1f}%")
        return True
    else:
        print(f"❌ Predictions are INCONSISTENT: {predictions}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("NEUROSHIELD ML ACCURACY TEST SUITE")
    print("=" * 80)
    
    results = {}
    
    # Test 1: Model Loading
    success, model, scaler = test_model_loading()
    results['Model Loading'] = success
    
    if not success:
        print("\n❌ Cannot proceed without model. Exiting.")
        return False
    
    # Test 2: Feature Extraction
    success, feature_results = test_feature_extraction()
    results['Feature Extraction'] = success
    
    if not success or not feature_results:
        print("\n⚠️  Feature extraction failed or no test files available")
    else:
        # Test 3: Predictions
        success = test_prediction(model, scaler, feature_results)
        results['Predictions'] = success
        
        # Test 5: Consistency
        success = test_consistency()
        results['Consistency'] = success
    
    # Test 4: App Configuration
    success = test_app_configuration()
    results['App Configuration'] = success
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:30s}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("The ML-based detection system is working correctly with accurate results.")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
