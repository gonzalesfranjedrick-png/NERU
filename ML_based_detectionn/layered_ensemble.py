"""Layered ensemble detector combining ML model + heuristics for polymorphic detection

Small, self-contained detector used by tuning script. Uses joblib ML model if available
and combines it with entropy/compression/section heuristics using configurable weights.
"""
import os
import math
import json
from typing import Dict, Any

try:
    import joblib
except Exception:
    joblib = None


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    from collections import Counter
    counts = Counter(data)
    length = len(data)
    ent = 0.0
    for v in counts.values():
        p = v / length
        ent -= p * math.log2(p)
    # normalize to 0..1 by dividing by 8 (max entropy per byte)
    return ent / 8.0


def compression_ratio(data: bytes) -> float:
    try:
        import zlib
        if not data:
            return 1.0
        comp = zlib.compress(data)
        # ratio: compressed_size / original_size, lower means more compressible
        ratio = len(comp) / max(1, len(data))
        # invert -> higher score = more packed/entropy
        score = 1.0 - ratio
        return max(0.0, min(1.0, score))
    except Exception:
        return 0.0


def section_score(pe_sections: int) -> float:
    # Fewer or unusual section counts may indicate packing/obfuscation
    if pe_sections <= 0:
        return 0.0
    if pe_sections <= 3:
        return 0.6
    if pe_sections <= 5:
        return 0.3
    return 0.1



# Import new detection modules
from .signature_detector import SignatureDetector
from .behavioral_analysis import BehavioralAnalysis
from .cloud_intelligence import CloudIntelligence
from .sandboxing import Sandboxing

class LayeredEnsembleDetector:
    def __init__(self, model_path: str = None, weights: Dict[str, float] = None, threshold: float = 0.5, config: Dict[str, Any] = None):
        self.model_path = model_path
        self.model = None
        if model_path and joblib:
            try:
                self.model = joblib.load(model_path)
            except Exception:
                self.model = None

        # default weights (add new layers)
        self.weights = weights or {
            'ml': 0.2,
            'entropy': 0.25,
            'compression': 0.15,
            'sections': 0.05,
            'signature': 0.1,
            'behavioral': 0.15,
            'cloud': 0.05,
            'sandboxing': 0.25
        }
        self.threshold = 0.18  # Lowered for high sensitivity
        self.config = config or {
            'enable_signature': True,
            'enable_behavioral': True,
            'enable_cloud': True,
            'enable_sandboxing': True
        }
        # Initialize new modules
        self.signature_detector = SignatureDetector() if self.config.get('enable_signature', True) else None
        self.behavioral = BehavioralAnalysis() if self.config.get('enable_behavioral', True) else None
        self.cloud = CloudIntelligence() if self.config.get('enable_cloud', True) else None
        self.sandbox = Sandboxing() if self.config.get('enable_sandboxing', True) else None

    def score(self, file_path: str, data: bytes = None, pe_sections: int = 0, log: bool = False) -> float:
        # ML score (0..1)
        ml_score = 0.0
        if self.model and data is not None:
            try:
                if hasattr(self.model, 'predict_proba'):
                    ml_score = 0.0  # Placeholder: integrate with real feature extraction
                elif hasattr(self.model, 'predict'):
                    ml_score = float(self.model.predict([b''])) if False else 0.0
            except Exception:
                ml_score = 0.0

        ent = entropy(data) if data is not None else 0.0
        comp = compression_ratio(data) if data is not None else 0.0
        sec = section_score(pe_sections)

        # New layers
        sig_score = 0.0
        if self.signature_detector:
            sig_score = 1.0 if self.signature_detector.scan(file_path) else 0.0
        beh_score = 0.0
        if self.behavioral:
            findings = self.behavioral.analyze(file_path)
            beh_score = 1.0 if self.behavioral.is_malicious(findings) else 0.0
        cloud_score = 0.0
        if self.cloud:
            verdict = self.cloud.query(file_path)
            cloud_score = 1.0 if self.cloud.is_malicious(verdict) else 0.0
        sandbox_score = 0.0
        if self.sandbox:
            observed = self.sandbox.run(file_path)
            sandbox_score = 1.0 if self.sandbox.is_malicious(observed) else 0.0

        s = (
            self.weights.get('ml', 0.0) * ml_score
            + self.weights.get('entropy', 0.0) * ent
            + self.weights.get('compression', 0.0) * comp
            + self.weights.get('sections', 0.0) * sec
            + self.weights.get('signature', 0.0) * sig_score
            + self.weights.get('behavioral', 0.0) * beh_score
            + self.weights.get('cloud', 0.0) * cloud_score
            + self.weights.get('sandboxing', 0.0) * sandbox_score
        )
        if log:
            print(f"[LayeredEnsemble] ml={ml_score:.2f} ent={ent:.2f} comp={comp:.2f} sec={sec:.2f} sig={sig_score} beh={beh_score} cloud={cloud_score} sandbox={sandbox_score} => score={s:.2f}")
        return max(0.0, min(1.0, s))

    def predict(self, file_path: str, data: bytes = None, pe_sections: int = 0, log: bool = False) -> bool:
        return self.score(file_path, data, pe_sections, log) >= self.threshold

    def save_weights(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'weights': self.weights, 'threshold': self.threshold}, f, indent=2)

    def load_weights(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            d = json.load(f)
            self.weights = d.get('weights', self.weights)
            self.threshold = d.get('threshold', self.threshold)
