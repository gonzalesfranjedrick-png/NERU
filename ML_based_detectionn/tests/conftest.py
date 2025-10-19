"""
Test configuration and fixtures
"""
import pytest
import os
import tempfile
import numpy as np
from typing import Dict, Any

@pytest.fixture
def test_dir():
    """Create a temporary directory for test files"""
    test_dir = tempfile.mkdtemp()
    yield test_dir
    # Cleanup after tests
    for root, dirs, files in os.walk(test_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(test_dir)

@pytest.fixture
def sample_pe_file(test_dir):
    """Create a sample PE file for testing"""
    pe_path = os.path.join(test_dir, "test.exe")
    with open(pe_path, "wb") as f:
        f.write(b"MZ")  # DOS header
        f.write(b"\x00" * 58)
        f.write(b"PE\x00\x00")  # PE header
        f.write(os.urandom(1024))  # Random content
    return pe_path

@pytest.fixture
def sample_malware_features() -> Dict[str, Any]:
    """Generate sample malware features for testing"""
    return {
        'avg_section_entropy': 7.2,
        'max_section_entropy': 7.8,
        'min_section_entropy': 6.5,
        'has_high_entropy_sections': True,
        'section_entropy_ratio': 0.92,
        'num_sections': 5,
        'num_executable_sections': 2,
        'writable_executable_sections': 1,
        'avg_comp_ratio': 0.89,
        'max_comp_ratio': 0.95,
        'packed_like_sections': 2,
        'max_window_entropy': 7.5,
        'avg_high_window_frac': 0.75,
        'suspicious_imports': 3,
        'total_imports': 45,
        'has_resources': True
    }