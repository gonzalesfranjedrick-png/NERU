"""Synthetic retraining script for the polymorphic detector.

This script generates a synthetic labeled dataset (safe random vs repetitive
files), extracts features via `extract_polymorphic_features`, and attempts to
train a RandomForest classifier if scikit-learn is available. If sklearn is not
installed, it falls back to writing a simple threshold-based model as JSON.

This is safe: no real malware is used. The produced model is intended for
local testing and demonstration only.
"""
import os
import json
import tempfile
import shutil
import random
from typing import List

from polymorphic_detection import extract_polymorphic_features


OUT_DIR = os.path.join(os.path.dirname(__file__), 'ML_model')
os.makedirs(OUT_DIR, exist_ok=True)


def generate_synthetic_samples(n_malicious=100, n_benign=100):
    samples = []
    tmpdir = tempfile.mkdtemp(prefix='poly_train_')
    try:
        # Malicious-like: high-entropy random data
        for i in range(n_malicious):
            path = os.path.join(tmpdir, f'mal_{i}.bin')
            with open(path, 'wb') as fh:
                fh.write(os.urandom(64 * 1024))
            samples.append((path, 1))

        # Benign-like: low-entropy repetitive data and small structured files
        for i in range(n_benign):
            path = os.path.join(tmpdir, f'ben_{i}.bin')
            if i % 3 == 0:
                data = b'A' * (32 * 1024)
            else:
                # small pseudo-pe header + repetitive body
                data = b'MZ' + (b'\x00' * 100) + (b'B' * 16 * 1024)
            with open(path, 'wb') as fh:
                fh.write(data)
            samples.append((path, 0))
        return samples, tmpdir
    except Exception:
        shutil.rmtree(tmpdir)
        raise


def extract_dataset(samples):
    X = []
    y = []
    meta = []
    for path, label in samples:
        feats = extract_polymorphic_features(path)
        # Flatten selected numeric features into vector in deterministic order
        vec = [
            float(feats.get('avg_section_entropy', 0)),
            float(feats.get('max_section_entropy', 0)),
            float(feats.get('avg_comp_ratio', 1.0)),
            float(feats.get('max_comp_ratio', 1.0)),
            float(feats.get('packed_like_sections', 0)),
            float(feats.get('max_window_entropy', 0)),
            float(feats.get('avg_high_window_frac', 0)),
            float(feats.get('num_executable_sections', 0)),
        ]
        X.append(vec)
        y.append(int(label))
        meta.append({'path': path})
    return X, y, meta


def train_and_save(X: List[List[float]], y: List[int], out_dir=OUT_DIR):
    # Try to use sklearn if available
    try:
        from sklearn.ensemble import RandomForestClassifier
        import joblib
        clf = RandomForestClassifier(n_estimators=50, random_state=42)
        clf.fit(X, y)
        model_path = os.path.join(out_dir, 'synthetic_rf_model.joblib')
        joblib.dump(clf, model_path)
        print('Saved sklearn RandomForest model to', model_path)
        return {'type': 'sklearn', 'path': model_path}
    except Exception:
        # Fallback: simple threshold rule saved as JSON
        # Compute average feature values for each class and set simple rule
        import statistics
        pos = [x for x, lab in zip(X, y) if lab == 1]
        neg = [x for x, lab in zip(X, y) if lab == 0]
        pos_mean = [statistics.mean(col) for col in zip(*pos)] if pos else [0]*len(X[0])
        neg_mean = [statistics.mean(col) for col in zip(*neg)] if neg else [0]*len(X[0])
        # choose a single feature (avg_comp_ratio idx=2) threshold halfway
        threshold = (pos_mean[2] + neg_mean[2]) / 2.0
        rule = {'type': 'threshold', 'feature_index': 2, 'threshold': threshold}
        out_path = os.path.join(out_dir, 'synthetic_threshold_model.json')
        with open(out_path, 'w') as fh:
            json.dump(rule, fh)
        print('Saved threshold fallback model to', out_path)
        return {'type': 'threshold', 'path': out_path}


def main():
    samples, tmpdir = generate_synthetic_samples(60, 60)
    try:
        X, y, meta = extract_dataset(samples)
        result = train_and_save(X, y)
        manifest = {
            'samples': len(samples),
            'model': result,
            'meta_dir': tmpdir
        }
        with open(os.path.join(OUT_DIR, 'manifest.json'), 'w') as fh:
            json.dump(manifest, fh, indent=2)
        print('Training complete. Manifest saved to', os.path.join(OUT_DIR, 'manifest.json'))
    finally:
        # leave tmpdir for inspection during development; don't delete
        pass


if __name__ == '__main__':
    main()
