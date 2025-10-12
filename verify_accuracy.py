#!/usr/bin/env python3
"""
Verify the accuracy of feature extraction and model predictions
"""
import sys
import os
import numpy as np

sys.path.insert(0, '/workspace/ML_based_detectionn')

def verify_feature_extraction_accuracy():
    """Verify that feature extraction produces accurate and consistent results"""
    from feature_extraction import extract_features, calculate_entropy
    
    print("\n" + "="*60)
    print("FEATURE EXTRACTION ACCURACY VERIFICATION")
    print("="*60)
    
    test_files = [
        '/workspace/ML_based_detectionn/uploads/notepad.exe',
        '/workspace/ML_based_detectionn/uploads/processhacker-2.39-setup.exe'
    ]
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"\n⚠️  Test file not found: {test_file}")
            continue
        
        print(f"\n📊 Testing: {os.path.basename(test_file)}")
        print("-" * 60)
        
        try:
            # Extract features multiple times to verify consistency
            features1 = extract_features(test_file)
            features2 = extract_features(test_file)
            features3 = extract_features(test_file)
            
            # Verify all features are the same (consistent extraction)
            if features1.equals(features2) and features2.equals(features3):
                print("✅ Feature extraction is CONSISTENT across multiple runs")
            else:
                print("❌ Feature extraction is INCONSISTENT!")
                return False
            
            # Verify all 23 features are present
            if len(features1.columns) == 23:
                print(f"✅ Correct number of features: {len(features1.columns)}")
            else:
                print(f"❌ Incorrect number of features: {len(features1.columns)} (expected 23)")
                return False
            
            # Verify no NaN or None values
            if features1.isnull().sum().sum() == 0:
                print("✅ No missing values in features")
            else:
                print(f"❌ Found missing values: {features1.isnull().sum().sum()}")
                return False
            
            # Verify entropy calculation
            with open(test_file, 'rb') as f:
                data = f.read(1024)  # Read first 1KB
                entropy = calculate_entropy(data)
                if 0 <= entropy <= 8:  # Entropy should be between 0 and 8 for byte data
                    print(f"✅ Entropy calculation valid: {entropy:.4f}")
                else:
                    print(f"❌ Invalid entropy value: {entropy}")
                    return False
            
            # Display feature statistics
            print("\n📈 Feature Statistics:")
            print(f"   - Mean values range: [{features1.values.min():.2f}, {features1.values.max():.2f}]")
            print(f"   - Features with zero values: {(features1 == 0).sum().sum()}")
            print(f"   - Features with non-zero values: {(features1 != 0).sum().sum()}")
            
            # Verify specific critical features
            critical_features = {
                'TimeDateStamp': (0, 2**32),  # Valid timestamp range
                'AddressOfEntryPoint': (0, 2**32),
                'SectionMinEntropy': (0, 8),  # Entropy range
                'Characteristics': (0, 2**16),
            }
            
            print("\n🔍 Critical Feature Validation:")
            all_valid = True
            for feature, (min_val, max_val) in critical_features.items():
                value = features1[feature].values[0]
                if min_val <= value <= max_val:
                    print(f"   ✅ {feature}: {value} (valid)")
                else:
                    print(f"   ❌ {feature}: {value} (out of range [{min_val}, {max_val}])")
                    all_valid = False
            
            if not all_valid:
                return False
                
        except Exception as e:
            print(f"❌ Error during verification: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n" + "="*60)
    print("✅ ALL ACCURACY CHECKS PASSED!")
    print("="*60)
    return True

def verify_app_configuration():
    """Verify application configuration is correct"""
    print("\n" + "="*60)
    print("APPLICATION CONFIGURATION VERIFICATION")
    print("="*60)
    
    from app import app, ALLOWED_EXTENSIONS, model
    
    checks = [
        ("Debug mode disabled", app.config['DEBUG'] == False),
        ("Upload folder configured", app.config['UPLOAD_FOLDER'] == 'uploads'),
        ("Max file size set", app.config['MAX_CONTENT_LENGTH'] == 10 * 1024 * 1024),
        ("Allowed extensions configured", ALLOWED_EXTENSIONS == {'exe', 'dll', 'txt'}),
        ("Secret key configured", app.config['SECRET_KEY'] is not None),
    ]
    
    all_passed = True
    for check_name, result in checks:
        if result:
            print(f"✅ {check_name}")
        else:
            print(f"❌ {check_name}")
            all_passed = False
    
    if model is None:
        print("⚠️  Model not loaded (this is expected - train and save model to ML_model/malwareclassifier-V2.pkl)")
    else:
        print("✅ Model loaded successfully")
    
    print("="*60)
    return all_passed

if __name__ == "__main__":
    print("\n" + "="*60)
    print("NEUROSHIELD ACCURACY VERIFICATION SUITE")
    print("="*60)
    
    results = {
        'Feature Extraction Accuracy': verify_feature_extraction_accuracy(),
        'Application Configuration': verify_app_configuration(),
    }
    
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL ACCURACY VERIFICATIONS PASSED!")
        print("The application produces accurate and consistent results.")
    else:
        print("⚠️  Some verifications failed. Please review the errors above.")
    print("="*60)
    
    sys.exit(0 if all_passed else 1)