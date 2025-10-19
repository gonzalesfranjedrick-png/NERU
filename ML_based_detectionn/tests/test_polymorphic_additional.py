import unittest
import os
import tempfile
import shutil
from polymorphic_detection import extract_polymorphic_features, analyze_polymorphic_indicators

class AdditionalPolymorphicTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def make_file(self, name, data: bytes):
        path = os.path.join(self.tempdir, name)
        with open(path, 'wb') as f:
            f.write(data)
        return path

    def test_packed_like_small(self):
        # Create a small file that's incompressible (simulates packed payload)
        data = os.urandom(4096)
        path = self.make_file('packed_like.bin', data)
        features = extract_polymorphic_features(path)
        is_poly, score, indicators = analyze_polymorphic_indicators(features, file_path=path)
        # Packed-like should be flagged with high entropy and compression ratio
        self.assertTrue(is_poly or score > 0.5, "Packed-like sample not detected")

    def test_benign_high_entropy(self):
        # Create a binary blob containing PNG header and repeated pattern (high entropy but known benign signature)
        png_sig = b"\x89PNG\r\n\x1a\n" + os.urandom(1024)
        path = self.make_file('benign_image.png', png_sig)
        features = extract_polymorphic_features(path)
        is_poly, score, indicators = analyze_polymorphic_indicators(features, file_path=path)
        # We allow some risk but aim to avoid 100% detection for benign files
        self.assertFalse(score == 1.0, "Benign file should not be marked with maximal risk")

if __name__ == '__main__':
    unittest.main()
