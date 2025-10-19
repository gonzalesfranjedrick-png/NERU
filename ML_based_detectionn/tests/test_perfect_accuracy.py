"""
Validation tests for 100% accuracy detection
"""
import unittest
import os
import tempfile
import shutil
from typing import Dict, Any, List
from high_accuracy_detector import HighAccuracyDetector

class TestPerfectAccuracy(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_dir = tempfile.mkdtemp()
        cls.detector = HighAccuracyDetector()
        cls.test_files = cls.create_test_files()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        shutil.rmtree(cls.test_dir)
    
    @classmethod
    def create_test_files(cls) -> Dict[str, str]:
        """Create test files for validation"""
        files = {}
        
        # Create benign samples
        files['benign_normal'] = cls._create_benign_file("normal")
        files['benign_packed'] = cls._create_benign_file("packed")
        files['benign_encrypted'] = cls._create_benign_file("encrypted")
        
        # Create malicious samples
        files['malware_obvious'] = cls._create_malicious_file("obvious")
        files['malware_stealthy'] = cls._create_malicious_file("stealthy")
        files['malware_polymorphic'] = cls._create_malicious_file("polymorphic")
        
        return files
    
    @classmethod
    def _create_benign_file(cls, type_: str) -> str:
        """Create a benign test file"""
        path = os.path.join(cls.test_dir, f"benign_{type_}.exe")
        with open(path, "wb") as f:
            # Write MZ header
            f.write(b"MZ")
            f.write(b"\x00" * 58)
            f.write(b"PE\x00\x00")
            
            if type_ == "normal":
                # Normal benign code
                f.write(b".text\x00")
                f.write(bytes([i % 256 for i in range(1024)]))
                
            elif type_ == "packed":
                # Legitimately packed
                f.write(b"UPX!")
                import zlib
                f.write(zlib.compress(bytes([i % 256 for i in range(1024)])))
                
            elif type_ == "encrypted":
                # Legitimate encryption
                f.write(b"SECTION\x00")
                content = bytes([i % 256 for i in range(1024)])
                f.write(bytes([b ^ 0x55 for b in content]))
        
        return path
    
    @classmethod
    def _create_malicious_file(cls, type_: str) -> str:
        """Create a malicious test file"""
        path = os.path.join(cls.test_dir, f"malware_{type_}.exe")
        with open(path, "wb") as f:
            # Write MZ header
            f.write(b"MZ")
            f.write(b"\x00" * 58)
            f.write(b"PE\x00\x00")
            
            if type_ == "obvious":
                # Obviously malicious
                f.write(b"CreateRemoteThread\x00")
                f.write(b"VirtualAlloc\x00")
                f.write(os.urandom(1024))
                
            elif type_ == "stealthy":
                # Stealthy malware
                f.write(b"kernel32.dll\x00")
                f.write(bytes([b ^ 0x55 for b in os.urandom(1024)]))
                
            elif type_ == "polymorphic":
                # Polymorphic malware
                base = os.urandom(1024)
                f.write(bytes([b ^ (i % 256) for i, b in enumerate(base)]))
        
        return path
    
    def test_perfect_benign_detection(self):
        """Test 100% accurate detection of benign files"""
        for name, path in self.test_files.items():
            if name.startswith('benign'):
                results = self.detector.analyze_file(path)
                self.assertFalse(
                    results['is_malicious'],
                    f"False positive on benign file {name}"
                )
    
    def test_perfect_malware_detection(self):
        """Test 100% accurate detection of malicious files"""
        for name, path in self.test_files.items():
            if name.startswith('malware'):
                results = self.detector.analyze_file(path)
                self.assertTrue(
                    results['is_malicious'],
                    f"False negative on malicious file {name}"
                )
                self.assertGreater(
                    results['confidence'],
                    0.8,
                    f"Low confidence ({results['confidence']}) on {name}"
                )
    
    def test_detection_methods(self):
        """Test multiple detection methods are working"""
        for name, path in self.test_files.items():
            results = self.detector.analyze_file(path)
            
            if name.startswith('malware'):
                # Malicious files should be detected by multiple methods
                self.assertGreaterEqual(
                    len(results['detection_methods']),
                    2,
                    f"Too few detection methods ({results['detection_methods']}) for {name}"
                )
            else:
                # Benign files should have minimal or no detections
                self.assertLess(
                    len(results['detection_methods']),
                    2,
                    f"Too many detection methods ({results['detection_methods']}) for benign file {name}"
                )

if __name__ == '__main__':
    unittest.main(verbosity=2)