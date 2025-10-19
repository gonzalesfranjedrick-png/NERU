import numpy as np
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import predict_features

class MockModelWithProbaNumeric:
    def predict(self, X):
        return [1]
    def predict_proba(self, X):
        return np.array([[0.2, 0.8]])
    classes_ = np.array([0,1])

class MockModelWithProbaString:
    def predict(self, X):
        return ['malware']
    def predict_proba(self, X):
        return np.array([[0.1, 0.9]])
    classes_ = np.array(['safe','malware'])

class MockModelWithDecisionFunction:
    def predict(self, X):
        return [1]
    def decision_function(self, X):
        return np.array([2.0])  # strong positive score


def make_features():
    return pd.DataFrame([{'SectionMinEntropy': 1.0, 'SizeOfHeaders': 512}])


def test_numeric_proba_model():
    model = MockModelWithProbaNumeric()
    features = make_features()
    is_malware, confidence, raw_label, probs = predict_features(features, model, scaler_obj=None)
    assert is_malware is True
    assert confidence > 50.0
    assert raw_label in (0,1)
    assert isinstance(probs, list)


def test_string_proba_model():
    model = MockModelWithProbaString()
    features = make_features()
    is_malware, confidence, raw_label, probs = predict_features(features, model, scaler_obj=None)
    assert is_malware is True
    assert confidence > 50.0
    assert raw_label == 'malware'
    assert isinstance(probs, list)


def test_decision_function_model():
    model = MockModelWithDecisionFunction()
    features = make_features()
    is_malware, confidence, raw_label, probs = predict_features(features, model, scaler_obj=None)
    assert is_malware is True
    assert confidence > 50.0
    assert probs is None
