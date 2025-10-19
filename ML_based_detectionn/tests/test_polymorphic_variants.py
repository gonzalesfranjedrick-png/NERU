"""
Advanced test cases for polymorphic malware detection.
Tests various edge cases and adversarial scenarios.
"""

import unittest
import os
import numpy as np
from polymorphic_detection import extract_polymorphic_features, PolymorphicConfig
import tempfile
import struct

class TestPolymorphicDetection(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def create_test_pe(self, data, sections=None):
        """Helper to create a test PE file"""
        pe_path = os.path.join(self.test_dir, "test.exe")
        with open(pe_path, "wb") as f:
            # Write MZ header
            f.write(b"MZ")
            f.write(b"\x00" * 58)
            # PE header offset
            f.write(struct.pack("<I", 0x80))
            f.write(b"\x00" * 124)
            # PE\0\0
            f.write(b"PE\x00\x00")
            if sections:
                for section in sections:
                    f.write(section)
            f.write(data)
        return pe_path

    def test_high_entropy_benign(self):
        """Test benign file with legitimately high entropy"""
        # Create compressed but benign data
        data = os.urandom(1024)  # Random data to simulate compression
        pe_path = self.create_test_pe(data)
        
        features = extract_polymorphic_features(pe_path)
        self.assertGreater(features["max_section_entropy"], 7.5)
        self.assertLess(features["suspicious_imports"], 3)

    def test_encrypted_section(self):
        """Test file with encrypted section detection"""
        encrypted_data = os.urandom(4096)  # Simulate encrypted section
        normal_data = b"A" * 4096
        
        sections = [
            # Normal section
            struct.pack("<8s6I", b".text\x00\x00\x00", 
                      0x1000, 0x1000, len(normal_data), 0x400, 0, 0x60000020),
            # Encrypted section  
            struct.pack("<8s6I", b".enc\x00\x00\x00\x00", 
                      0x2000, 0x2000, len(encrypted_data), 0x1400, 0, 0xE0000020)
        ]
        
        pe_path = self.create_test_pe(normal_data + encrypted_data, sections)
        features = extract_polymorphic_features(pe_path)
        
        self.assertGreater(features["max_section_entropy"], 7.8)
        self.assertGreater(features["packed_like_sections"], 0)

    def test_packed_code(self):
        """Test packed code detection"""
        packed_data = np.random.bytes(8192)
        sections = [
            struct.pack("<8s6I", b"UPX0\x00\x00\x00\x00",
                      0x1000, 0x1000, len(packed_data), 0x400, 0, 0xE0000020)
        ]
        
        pe_path = self.create_test_pe(packed_data, sections)
        features = extract_polymorphic_features(pe_path)
        
        self.assertGreater(features["avg_comp_ratio"], 0.85)
        self.assertGreater(features["max_window_entropy"], 7.0)

    def test_polymorphic_variants(self):
        """Test detection of polymorphic code variants"""
        variants = []
        base_code = b"MZ" + os.urandom(1024)
        
        # Create several variants with small mutations
        for i in range(5):
            variant = bytearray(base_code)
            # Mutate random positions while preserving functionality
            for _ in range(10):
                pos = np.random.randint(2, len(variant))
                variant[pos] = np.random.randint(0, 256)
            variants.append(bytes(variant))
        
        # Test each variant
        features_list = []
        for variant in variants:
            pe_path = self.create_test_pe(variant)
            features = extract_polymorphic_features(pe_path)
            features_list.append(features)
        
        # Verify variants are detected as related
        entropies = [f["avg_section_entropy"] for f in features_list]
        ratios = [f["avg_comp_ratio"] for f in features_list]
        
        # Check entropy and compression patterns are consistent
        self.assertLess(np.std(entropies), 0.5)  # Similar entropy profiles
        self.assertLess(np.std(ratios), 0.1)     # Similar compression ratios

    def test_adversarial_benign(self):
        """Test benign files that might trigger false positives"""
        # Create legitimate looking file with high entropy sections
        code_section = b"".join([bytes([i % 256]) for i in range(4096)])
        data_section = os.urandom(2048)  # Simulated encrypted data (config, etc)
        
        sections = [
            struct.pack("<8s6I", b".text\x00\x00\x00",
                      0x1000, 0x1000, len(code_section), 0x400, 0, 0x60000020),
            struct.pack("<8s6I", b".data\x00\x00\x00",
                      0x2000, 0x2000, len(data_section), 0x1400, 0, 0x40000040)
        ]
        
        pe_path = self.create_test_pe(code_section + data_section, sections)
        features = extract_polymorphic_features(pe_path)
        
        # Verify benign characteristics are preserved
        self.assertLess(features["suspicious_imports"], 2)
        self.assertLess(features["writable_executable_sections"], 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)