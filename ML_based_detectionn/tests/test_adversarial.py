"""
Advanced adversarial testing suite for ML-based malware detection
"""
import unittest
import os
import tempfile
import numpy as np
import shutil
from typing import List, Dict, Any
from polymorphic_detection import extract_polymorphic_features, PolymorphicConfig

class TestAdversarialScenarios(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.samples = []
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def create_adversarial_sample(self, technique: str) -> str:
        """Create an adversarial sample using specified technique"""
        sample_path = os.path.join(self.test_dir, f"{technique}_sample.exe")
        
        with open(sample_path, "wb") as f:
            # Basic PE header
            f.write(b"MZ")
            f.write(b"\x00" * 58)
            f.write(b"PE\x00\x00")
            
            if technique == "entropy_masked":
                # Create high-entropy content that looks benign
                pattern = bytes([i % 256 for i in range(1024)]) * 4
                f.write(pattern)
                
            elif technique == "split_payload":
                # Split malicious content across sections
                f.write(b"Section1\x00")
                f.write(os.urandom(512))
                f.write(b"Section2\x00")
                f.write(os.urandom(512))
                
            elif technique == "fake_benign":
                # Add benign-looking strings and content
                f.write(b"kernel32.dll\x00")
                f.write(b"user32.dll\x00")
                f.write(os.urandom(1024))
                
            elif technique == "polymorphic_engine":
                # Simulate polymorphic engine output
                base = os.urandom(1024)
                mutations = bytearray(base)
                for i in range(10):
                    pos = np.random.randint(0, len(mutations))
                    mutations[pos] = mutations[pos] ^ 0xFF
                f.write(mutations)
        
        return sample_path
    
    def test_entropy_masking(self):
        """Test detection of entropy-masked malicious content"""
        sample = self.create_adversarial_sample("entropy_masked")
        features = extract_polymorphic_features(sample)
        
        # Should detect despite entropy masking
        self.assertGreater(features["suspicious_imports"], 0)
        self.assertGreater(features["max_window_entropy"], 6.0)
    
    def test_split_payload(self):
        """Test detection of split malicious payloads"""
        sample = self.create_adversarial_sample("split_payload")
        features = extract_polymorphic_features(sample)
        
        # Should detect split patterns
        self.assertGreater(features["num_sections"], 1)
        self.assertGreater(features["avg_section_entropy"], 6.0)
    
    def test_fake_benign_characteristics(self):
        """Test detection despite benign-looking characteristics"""
        sample = self.create_adversarial_sample("fake_benign")
        features = extract_polymorphic_features(sample)
        
        # Should not be fooled by fake benign characteristics
        self.assertGreater(features["max_comp_ratio"], 0.8)
        
    def test_polymorphic_engine_variants(self):
        """Test detection of polymorphic engine outputs"""
        variants = []
        for i in range(5):
            sample = self.create_adversarial_sample("polymorphic_engine")
            features = extract_polymorphic_features(sample)
            variants.append(features)
            
        # Features should be consistent across variants
        entropies = [v["avg_section_entropy"] for v in variants]
        ratios = [v["avg_comp_ratio"] for v in variants]
        
        self.assertLess(np.std(entropies), 0.5)
        self.assertLess(np.std(ratios), 0.1)
    
    def test_resource_hiding(self):
        """Test detection of malware hidden in resources"""
        sample_path = os.path.join(self.test_dir, "resource_hidden.exe")
        
        with open(sample_path, "wb") as f:
            f.write(b"MZ")
            f.write(b"\x00" * 58)
            f.write(b"PE\x00\x00")
            f.write(b"RCDATA\x00")
            encrypted_data = bytes([b ^ 0x55 for b in os.urandom(1024)])
            f.write(encrypted_data)
            
        features = extract_polymorphic_features(sample_path)
        self.assertTrue(features["has_resources"])
        self.assertGreater(features["max_window_entropy"], 6.5)
    
    def test_multi_stage_payload(self):
        """Test detection of multi-stage payloads"""
        sample_path = os.path.join(self.test_dir, "multi_stage.exe")
        
        with open(sample_path, "wb") as f:
            f.write(b"MZ")
            f.write(b"\x00" * 58)
            f.write(b"PE\x00\x00")
            
            # Stage 1: Loader
            f.write(b"LoadLibrary\x00")
            f.write(b"VirtualAlloc\x00")
            
            # Stage 2: Encrypted payload
            f.write(os.urandom(512))
            
            # Stage 3: Final payload
            f.write(os.urandom(512))
            
        features = extract_polymorphic_features(sample_path)
        self.assertGreater(features["suspicious_imports"], 1)
        self.assertGreater(features["packed_like_sections"], 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)