"""
cloud_intelligence.py
Simulated cloud reputation check module with local cache.
"""
import hashlib
import random

class CloudIntelligence:
    def __init__(self):
        self.local_cache = {}

    def query(self, file_path):
        # Simulate cloud check by hashing file and returning a random verdict
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        if file_hash in self.local_cache:
            return self.local_cache[file_hash]
        # Simulate: 5% chance of being flagged as malicious
        verdict = 'malicious' if random.random() < 0.05 else 'benign'
        self.local_cache[file_hash] = verdict
        return verdict

    def is_malicious(self, verdict):
        return verdict == 'malicious'
