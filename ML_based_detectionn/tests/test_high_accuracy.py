"""
High-accuracy test suite with comprehensive coverage
"""
import unittest
import os
import tempfile
import numpy as np
import zlib
import shutil
from typing import Dict, Any, List
from polymorphic_detection import extract_polymorphic_features
from feature_extraction import extract_advanced_features

class TestHighAccuracyDetection(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_dir = tempfile.mkdtemp()
        cls.samples = {}
        cls.create_test_samples()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        shutil.rmtree(cls.test_dir)
    
    @classmethod
    def create_test_samples(cls):
        """Create comprehensive test samples"""
        # Create benign samples
        cls.samples['benign'] = {
            'standard': cls.create_benign_sample(),
            'high_entropy': cls.create_high_entropy_benign(),
            'packed': cls.create_packed_benign(),
            'encrypted_config': cls.create_encrypted_config_benign()
        }
        
        # Create malicious samples
        cls.samples['malicious'] = {
            'standard': cls.create_malicious_sample(),
            'polymorphic': cls.create_polymorphic_sample(),
            'packed': cls.create_packed_malicious(),
            'split': cls.create_split_payload()
        }
    
    @classmethod
    def create_benign_sample(cls) -> str:
        """Create a standard benign sample"""
        path = os.path.join(cls.test_dir, "benign.exe")
        with open(path, "wb") as f:
            f.write(b"MZ")
            f.write(b"\x00" * 58)
            f.write(b"PE\x00\x00")
            # Add legitimate-looking code
            f.write(b"kernel32.dll\x00")
            f.write(b"user32.dll\x00")
            f.write(bytes([i % 256 for i in range(1024)]))
        return path
    
    @classmethod
    def create_high_entropy_benign(cls) -> str:
        """Create a benign sample with high entropy"""
        path = os.path.join(cls.test_dir, "high_entropy_benign.exe")
        with open(path, "wb") as f:
            f.write(b"MZ")
            f.write(b"\x00" * 58)
            f.write(b"PE\x00\x00")
            # Add compressed data
            f.write(zlib.compress(bytes([i % 256 for i in range(4096)])))
        return path
    
    @classmethod
    def create_packed_benign(cls) -> str:
        """Create a legitimately packed benign sample"""
        path = os.path.join(cls.test_dir, "packed_benign.exe")
        with open(path, "wb") as f:
            f.write(b"MZ")
            f.write(b"\x00" * 58)
            f.write(b"PE\x00\x00")
            # Add UPX-like header
            f.write(b"UPX!")
            # Add packed content
            original = bytes([i % 256 for i in range(2048)])
            f.write(zlib.compress(original))
        return path
    
    @classmethod
    def create_encrypted_config_benign(cls) -> str:
        """Create benign sample with encrypted configuration"""
        path = os.path.join(cls.test_dir, "encrypted_config_benign.exe")
        with open(path, "wb") as f:
            f.write(b"MZ")
            f.write(b"\x00" * 58)
            f.write(b"PE\x00\x00")
            # Add normal code
            f.write(bytes([i % 256 for i in range(1024)]))
            # Add encrypted config
            config = b"{\n  \"api_key\": \"12345\",\n  \"server\": \"example.com\"\n}"
            f.write(bytes([b ^ 0x55 for b in config]))
        return path
    
    @classmethod
    def create_malicious_sample(cls) -> str:
        """Create a standard malicious sample"""
        path = os.path.join(cls.test_dir, "malicious.exe")
        with open(path, "wb") as f:
            f.write(b"MZ")
            f.write(b"\x00" * 58)
            f.write(b"PE\x00\x00")
            # Add suspicious imports
            f.write(b"VirtualAlloc\x00")
            f.write(b"WriteProcessMemory\x00")
            f.write(os.urandom(1024))
        return path
    
    @classmethod
    def create_polymorphic_sample(cls) -> str:
        """Create a polymorphic malicious sample"""
        path = os.path.join(cls.test_dir, "polymorphic.exe")
        with open(path, "wb") as f:
            f.write(b"MZ")
            f.write(b"\x00" * 58)
            f.write(b"PE\x00\x00")
            # Create polymorphic code
            base = os.urandom(1024)
            mutations = bytearray(base)
            for i in range(10):
                pos = np.random.randint(0, len(mutations))
                mutations[pos] ^= 0xFF
            f.write(mutations)
        return path
    
    @classmethod
    def create_packed_malicious(cls) -> str:
        """Create a maliciously packed sample"""
        path = os.path.join(cls.test_dir, "packed_malicious.exe")
        with open(path, "wb") as f:
            f.write(b"MZ")
            f.write(b"\x00" * 58)
            f.write(b"PE\x00\x00")
            # Add custom packer signature
            f.write(b"PACK")
            # Add packed malicious content
            payload = b"CreateRemoteThread" + os.urandom(1024)
            f.write(zlib.compress(payload))
        return path
    
    @classmethod
    def create_split_payload(cls) -> str:
        """Create a sample with split malicious payload"""
        path = os.path.join(cls.test_dir, "split_payload.exe")
        with open(path, "wb") as f:
            f.write(b"MZ")
            f.write(b"\x00" * 58)
            f.write(b"PE\x00\x00")
            # Split suspicious content
            f.write(b"Section1\x00")
            f.write(os.urandom(512))
            f.write(b"Section2\x00")
            f.write(os.urandom(512))
        return path
    
    def test_benign_detection(self):
        """Test accurate detection of benign samples"""
        for name, path in self.samples['benign'].items():
            features = extract_advanced_features(path)
            poly_features = extract_polymorphic_features(path)
            
            # Verify benign characteristics
            self.assertLess(poly_features.get('suspicious_imports', 0), 2,
                          f"Benign sample {name} flagged suspicious imports")
            self.assertLess(features.get('api_calls_count', 0), 3,
                          f"Benign sample {name} has too many suspicious API calls")
    
    def test_malicious_detection(self):
        """Test accurate detection of malicious samples"""
        for name, path in self.samples['malicious'].items():
            features = extract_advanced_features(path)
            poly_features = extract_polymorphic_features(path)
            
            # Verify malicious characteristics
            self.assertGreater(poly_features.get('max_section_entropy', 0), 6.5,
                             f"Malicious sample {name} has unexpectedly low entropy")
            self.assertGreater(features.get('api_calls_count', 0), 0,
                             f"Malicious sample {name} has no suspicious API calls")
    
    def test_polymorphic_variants(self):
        """Test detection of polymorphic variants"""
        base_features = extract_advanced_features(self.samples['malicious']['polymorphic'])
        
        # Create and test variants
        variants = []
        for i in range(5):
            variant_path = os.path.join(self.test_dir, f"variant_{i}.exe")
            shutil.copy(self.samples['malicious']['polymorphic'], variant_path)
            
            # Modify variant
            with open(variant_path, "r+b") as f:
                content = bytearray(f.read())
                for _ in range(10):
                    pos = np.random.randint(0x200, len(content))
                    content[pos] ^= 0xFF
                f.seek(0)
                f.write(content)
            
            variant_features = extract_advanced_features(variant_path)
            variants.append(variant_features)
        
        # Verify consistent detection
        for variant in variants:
            self.assertAlmostEqual(
                variant['block_entropy_mean'],
                base_features['block_entropy_mean'],
                delta=0.5,
                msg="Variant entropy differs significantly from base"
            )
    
    def test_packed_detection(self):
        """Test accurate detection of packed files"""
        benign_packed = self.samples['benign']['packed']
        malicious_packed = self.samples['malicious']['packed']
        
        # Test benign packed
        features = extract_advanced_features(benign_packed)
        self.assertGreater(features['compression_ratio'], 0.8,
                          "Failed to detect legitimate packing")
        self.assertLess(features['api_calls_count'], 2,
                       "Falsely flagged legitimate packed file")
        
        # Test malicious packed
        features = extract_advanced_features(malicious_packed)
        self.assertGreater(features['compression_ratio'], 0.8,
                          "Failed to detect malicious packing")
        self.assertGreater(features['api_calls_count'], 0,
                          "Failed to detect suspicious APIs in packed malware")
    
    def test_split_payload_detection(self):
        """Test detection of split malicious payloads"""
        features = extract_advanced_features(self.samples['malicious']['split'])
        
        self.assertGreater(len(features.get('sections', [])), 1,
                          "Failed to detect multiple sections")
        self.assertGreater(features['block_entropy_std'], 0.5,
                          "Failed to detect entropy variations across sections")

if __name__ == '__main__':
    unittest.main(verbosity=2)