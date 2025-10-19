"""Simple tuner for LayeredEnsembleDetector using synthetic samples.

Generates benign and polymorphic-like synthetic byte blobs. Sweeps a small
space of weights and thresholds and selects the configuration that maximizes
TPR while keeping FPR <= target_fp.
"""
import os
import json
import random
from itertools import product
from layered_ensemble import LayeredEnsembleDetector, entropy, compression_ratio


def make_polymorphic_like(size=2048):
    # high entropy + low compressibility + random section count
    data = bytearray(random.getrandbits(8) for _ in range(size))
    # inject small repeated header patterns to mimic modified PE header
    for i in range(0, min(64, size), 8):
        data[i:i+4] = b'PE\x00\x00'[:min(4, size-i)]
    return bytes(data), random.choice([1,2,3])


def make_benign(size=2048):
    # lower entropy, more compressible
    base = (b'ABCDEFGH' * (size // 8 + 1))[:size]
    # small randomized padding
    padding = bytearray(random.getrandbits(8) & 0x0F for _ in range(size//10))
    return base + bytes(padding), random.choice([3,4,5,6])


def evaluate_config(weights, threshold, n_pos=200, n_neg=200, target_fp=0.03):
    det = LayeredEnsembleDetector(weights=weights, threshold=threshold)
    tp = fp = tn = fn = 0

    for _ in range(n_pos):
        data, sections = make_polymorphic_like()
        pred = det.predict(data, sections)
        if pred:
            tp += 1
        else:
            fn += 1

    for _ in range(n_neg):
        data, sections = make_benign()
        pred = det.predict(data, sections)
        if pred:
            fp += 1
        else:
            tn += 1

    tpr = tp / max(1, (tp + fn))
    fpr = fp / max(1, (fp + tn))
    score = tpr - (fpr * 0.5)  # penalize FP moderately
    return {'tpr': tpr, 'fpr': fpr, 'score': score, 'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn}


def tune_and_save(out_path=None):
    # small grid over ml/entropy/compression/sections weights that sum to 1
    base_vals = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
    best = None
    tested = 0

    for ml_w in base_vals:
        for ent_w in base_vals:
            for comp_w in base_vals:
                for sec_w in base_vals:
                    s = ml_w + ent_w + comp_w + sec_w
                    if s == 0:
                        continue
                    weights = {
                        'ml': ml_w / s,
                        'entropy': ent_w / s,
                        'compression': comp_w / s,
                        'sections': sec_w / s
                    }
                    # sweep thresholds
                    for thr in [0.4, 0.45, 0.5, 0.55, 0.6]:
                        res = evaluate_config(weights, thr)
                        tested += 1
                        # require FPR under 5% to consider
                        if res['fpr'] <= 0.05:
                            if best is None or res['score'] > best['res']['score']:
                                best = {'weights': weights, 'threshold': thr, 'res': res}

    if best is None:
        # fallback: balanced weights
        best = {'weights': {'ml': 0.4, 'entropy': 0.3, 'compression': 0.2, 'sections': 0.1}, 'threshold': 0.5, 'res': {}}

    out_path = out_path or os.path.join('ML_model', 'tuned_ensemble.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'weights': best['weights'], 'threshold': best['threshold'], 'metrics': best['res']}, f, indent=2)

    print(f"Tuning complete. Tested {tested} configs. Best TPR={best['res'].get('tpr',0):.3f}, FPR={best['res'].get('fpr',0):.3f}")
    print(f"Saved tuned ensemble to: {out_path}")
    return out_path


if __name__ == '__main__':
    tune_and_save()
