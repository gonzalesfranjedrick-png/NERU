import os
import tempfile
import importlib.util
import sys
import shutil

# Ensure repository root is on sys.path so top-level imports inside the
# module-under-test (like `from ml_monitor import MLMonitor`) resolve when
# the test is executed from the tests/ directory.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Helper to load module by path (robust against package layout)
def load_module_from_path(path, name="polymorphic_detection_mod"):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

MODULE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'ML_based_detectionn', 'polymorphic_detection.py'))
pd = load_module_from_path(MODULE_PATH, 'polymorphic_detection')


def write_temp_file(data: bytes, suffix=".bin"):
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tf.write(data)
    tf.flush()
    tf.close()
    return tf.name


def test_high_entropy_packed_like():
    # Create a high-entropy file that should look packed/encrypted
    data = os.urandom(64 * 1024)  # 64KB of random data
    path = write_temp_file(data)
    try:
        features = pd.extract_polymorphic_features(path)
        assert isinstance(features, dict)
        # fallback raw-byte analysis should set avg_comp_ratio near 1.0
        assert features.get('avg_comp_ratio', 0) >= 0.8
        # sliding window entropy should be high
        assert features.get('max_window_entropy', 0) > 6.0
        # packed_like_sections should be set (fallback uses comp_ratio)
        assert features.get('packed_like_sections', 0) >= 1
        is_poly, score, indicators = pd.analyze_polymorphic_indicators(features, path)
        # Should be flagged as likely polymorphic by heuristics
        assert is_poly is True
        assert score > 0.25
    finally:
        os.unlink(path)


def test_low_entropy_benign():
    # Create a low-entropy benign file (repetitive)
    data = b'A' * (32 * 1024)
    path = write_temp_file(data)
    try:
        features = pd.extract_polymorphic_features(path)
        assert features.get('avg_comp_ratio', 0) < 0.5
        is_poly, score, indicators = pd.analyze_polymorphic_indicators(features, path)
        # Should NOT be flagged as polymorphic
        assert is_poly is False
        assert score < 0.3
    finally:
        os.unlink(path)


def test_png_signature_downgrade():
    # Create a PNG-like signature with some entropy but mostly benign
    png_header = b"\x89PNG\r\n\x1a\n"
    data = png_header + (b'\x00' * 1024) + (b'A' * 2048)
    path = write_temp_file(data, suffix=".png")
    try:
        features = pd.extract_polymorphic_features(path)
        is_poly, score, indicators = pd.analyze_polymorphic_indicators(features, path)
        # The analysis should detect benign signature and dampen risk
        assert 'File signature indicates benign type' in ' '.join(indicators) or score < 0.4
    finally:
        os.unlink(path)


def test_dynamic_stub_behavior_integration():
    # Create a file that contains suspicious API names to trigger dynamic stub
    data = b"This sample contains VirtualAlloc and CreateRemoteThread and LoadLibrary" + os.urandom(1024)
    path = write_temp_file(data)
    try:
        # Enable dynamic stub temporarily
        old = pd.PolymorphicConfig.ENABLE_DYNAMIC
        pd.PolymorphicConfig.ENABLE_DYNAMIC = True
        try:
            features = pd.extract_polymorphic_features(path)
            # call analysis with dynamic enabled
            is_poly, score, indicators = pd.analyze_polymorphic_indicators(features, path)
            # dynamic stub should add an indicator when suspicious strings are present
            assert any('dynamic' in (str(i)).lower() or 'dynamic analysis reported suspicious behavior' in (str(i)).lower() for i in indicators)
        finally:
            pd.PolymorphicConfig.ENABLE_DYNAMIC = old
    finally:
        os.unlink(path)


if __name__ == '__main__':
    import pytest
    sys.exit(pytest.main([__file__]))
