"""
Initialize test environment and data
"""
import os
import sys
import shutil
import numpy as np
import zlib

def init_test_data():
    """Initialize test data directory with sample files"""
    test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
    os.makedirs(test_data_dir, exist_ok=True)
    
    # Create sample PE files
    create_sample_pe_file(test_data_dir, "benign.exe", is_malware=False)
    create_sample_pe_file(test_data_dir, "malware.exe", is_malware=True)
    create_sample_pe_file(test_data_dir, "packed.exe", is_packed=True)
    create_polymorphic_variants(test_data_dir)

def create_sample_pe_file(directory: str, filename: str, is_malware: bool = False, is_packed: bool = False):
    """Create a sample PE file with specific characteristics"""
    file_path = os.path.join(directory, filename)
    with open(file_path, "wb") as f:
        # DOS header
        f.write(b"MZ")
        f.write(b"\x00" * 58)
        
        # PE header offset
        f.write((0x80).to_bytes(4, 'little'))
        f.write(b"\x00" * 124)
        
        # PE header
        f.write(b"PE\x00\x00")
        
        if is_malware:
            # Add suspicious patterns
            f.write(b"CreateRemoteThread\x00")
            f.write(b"VirtualAlloc\x00")
            f.write(os.urandom(1024))  # Random encrypted-like data
        elif is_packed:
            # Simulate packed data
            f.write(b"UPX0\x00")
            f.write(zlib.compress(os.urandom(4096)))
        else:
            # Regular code-like data
            f.write(b"".join(bytes([i % 256]) for i in range(1024)))

def create_polymorphic_variants(directory: str, num_variants: int = 5):
    """Create a set of polymorphic variants from base code"""
    base_code = b"MZ" + os.urandom(1024)
    
    for i in range(num_variants):
        variant = bytearray(base_code)
        # Make small mutations while preserving structure
        for _ in range(10):
            pos = np.random.randint(2, len(variant))
            variant[pos] = np.random.randint(0, 256)
            
        file_path = os.path.join(directory, f"variant_{i}.exe")
        with open(file_path, "wb") as f:
            f.write(variant)

if __name__ == "__main__":
    init_test_data()