import unittest
import os
import tempfile
import joblib
import numpy as np
from feature_extraction import extract_features

class TestMalwarePrediction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load the model from a known good state
        model_paths = [
            os.path.join('ML_model', 'malwareclassifier-V2.pkl'),
            os.path.join('ML_based_detectionn', 'ML_model', 'malwareclassifier-V2.pkl'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ML_model', 'malwareclassifier-V2.pkl')
        ]
        
        for path in model_paths:
            if os.path.exists(path):
                cls.model = joblib.load(path)
                break
        else:
            raise FileNotFoundError("Could not find malware classifier model")
    
    def test_prediction_confidence(self):
        """Test that the model makes predictions with reasonable confidence"""
        # Create test data with known characteristics
        test_data = {
            'MajorLinkerVersion': 14,
            'MinorOperatingSystemVersion': 0,
            'MajorSubsystemVersion': 6,
            'SizeOfStackReserve': 1048576,
            'TimeDateStamp': 1696726400,  # Recent timestamp
            'MajorOperatingSystemVersion': 6,
            'Characteristics': 271,
            'ImageBase': 4194304,
            'Subsystem': 2,
            'MinorImageVersion': 0,
            'MinorSubsystemVersion': 0,
            'SizeOfInitializedData': 512000,
            'DllCharacteristics': 0x4160,  # Common DLL characteristics
            'DirectoryEntryExport': 1,
            'ImageDirectoryEntryExport': 0,
            'CheckSum': 0,
            'DirectoryEntryImportSize': 1024,
            'SectionMaxChar': 5,
            'MajorImageVersion': 0,
            'AddressOfEntryPoint': 4096,
            'SectionMinEntropy': 6.2,  # High entropy often indicates packed/malicious code
            'SizeOfHeaders': 512,
            'SectionMinVirtualsize': 4096
        }

        import pandas as pd
        test_df = pd.DataFrame([test_data])
        
        # Get list of expected features from feature_extraction module
        from feature_extraction import EXPECTED_COLUMNS
        test_df = test_df.reindex(columns=EXPECTED_COLUMNS, fill_value=0)
        
        # Make prediction
        prediction = self.model.predict_proba(test_df)
        
        # Check prediction shape and basic properties
        self.assertEqual(len(prediction), 1)  # VotingClassifier returns a list
        self.assertTrue(0 <= prediction[0][1] <= 1)  # Check malware probability
        
        # Get confidence scores
        malware_confidence = prediction[0][1]  # Assuming 1 is malware class
        
        # Log the confidence for inspection
        print(f"\nMalware confidence: {malware_confidence:.4f}")
        print(f"Benign confidence: {prediction[0][0]:.4f}")
        
        # The model should make clear predictions (not too uncertain)
        self.assertNotAlmostEqual(malware_confidence, 0.5, places=2)
        
    def test_feature_importance(self):
        """Test feature extraction with key features"""
        from feature_extraction import EXPECTED_COLUMNS
        
        # Key features we know should be important
        key_features = ['SectionMinEntropy', 'SizeOfInitializedData', 'DllCharacteristics']
        
        # Verify key features are included in extraction
        for feature in key_features:
            self.assertIn(feature, EXPECTED_COLUMNS,
                         f"Expected {feature} to be included in feature extraction")

if __name__ == '__main__':
    unittest.main()