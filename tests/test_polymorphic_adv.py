import os
import tempfile
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from ML_based_detectionn import polymorphic_detection as pd


def write_temp(data: bytes, suffix='.bin'):
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tf.write(data)
    tf.close()
    return tf.name


def test_packed_with_valid_code_like():
    # Simulate a PE with small 'MZ' header and a high-entropy code blob
    data = b'MZ' + (b'\x00' * 128) + os.urandom(48 * 1024)
    path = write_temp(data)
    try:
        feats = pd.extract_polymorphic_features(path)
        is_poly, score, inds = pd.analyze_polymorphic_indicators(feats, path)
        assert isinstance(score, float)
        # Should be detected as potential polymorphic due to high entropy
        assert is_poly is True
    finally:
        os.unlink(path)


def test_benign_high_entropy_file_not_flagged_overly():
    # Create a large image-like file that's high entropy but has benign signature
    data = b'PNG\r\n\x1a\n' + os.urandom(128 * 1024)
    path = write_temp(data, suffix='.png')
    try:
        feats = pd.extract_polymorphic_features(path)
        is_poly, score, inds = pd.analyze_polymorphic_indicators(feats, path)
        # It can have some entropy but should be downgraded due to signature
        assert score < 0.7
    finally:
        os.unlink(path)


def test_simulated_encrypted_pattern():
    # Simulate encrypted pattern by creating repeating high-entropy blocks
    blocks = [os.urandom(1024) for _ in range(64)]
    # Insert a small low-entropy header to avoid being considered non-PE
    data = b'MZ' + b'\x00' * 64 + b''.join(blocks)
    path = write_temp(data)
    try:
        feats = pd.extract_polymorphic_features(path)
        is_poly, score, inds = pd.analyze_polymorphic_indicators(feats, path)
        assert is_poly is True
        assert score > 0.3
    finally:
        os.unlink(path)
