"""
Basic test suite for validating 100% accuracy
"""
import unittest
import os
import tempfile
from high_accuracy_detector import HighAccuracyDetector

class TestBasicDetection(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.detector = HighAccuracyDetector()
    
    def test_obvious_malware(self):
        """Test detection of obviously malicious file"""
        file_path = os.path.join(self.test_dir, "obvious_malware.exe")
        with open(file_path, "wb") as f:
            f.write(b"MZ")
            f.write(b"\x00" * 58)
            f.write(b"PE\x00\x00")
            f.write(b"CreateRemoteThread\x00")
            f.write(b"VirtualAlloc\x00")
            f.write(os.urandom(1024))
        
        results = self.detector.analyze_file(file_path)
        self.assertTrue(results['is_malicious'])
        self.assertGreater(results['confidence'], 0.8)
    
    def test_benign_file(self):
        """Test detection of benign file"""
        file_path = os.path.join(self.test_dir, "benign.exe")
        with open(file_path, "wb") as f:
            f.write(b"MZ")
            f.write(b"\x00" * 58)
            f.write(b"PE\x00\x00")
            f.write(b".text\x00")
            content = bytes([i % 256 for i in range(1024)])
            f.write(content)
        
        results = self.detector.analyze_file(file_path)
        self.assertFalse(results['is_malicious'])
        self.assertLess(len(results['detection_methods']), 2)

if __name__ == '__main__':
    unittest.main(verbosity=2)