# Test script for multi-layer NeuroShield detection on polymorphic samples
import os
from ML_based_detectionn.layered_ensemble import LayeredEnsembleDetector

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'polymorphic_samples')
ensemble = LayeredEnsembleDetector()

results = []
for fname in os.listdir(SAMPLES_DIR):
    fpath = os.path.join(SAMPLES_DIR, fname)
    with open(fpath, 'rb') as f:
        data = f.read()
    score = ensemble.score(fpath, data, pe_sections=5, log=True)
    verdict = 'Malware' if score >= ensemble.threshold else 'Benign'
    results.append((fname, score, verdict))
    print(f"{fname}: Score={score:.3f} Verdict={verdict}")

mal_count = sum(1 for _,_,v in results if v=='Malware')
print(f"\nDetected as malware: {mal_count}/{len(results)} ({mal_count/len(results)*100:.1f}%)")
