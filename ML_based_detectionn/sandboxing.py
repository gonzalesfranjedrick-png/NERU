"""
sandboxing.py
Simulated sandbox runner for dynamic behavior analysis.
"""
import random

class Sandboxing:
    def __init__(self):
        self.behaviors = [
            'Spawns cmd.exe',
            'Downloads file from internet',
            'Encrypts user files',
            'Attempts privilege escalation',
            'Deletes shadow copies',
        ]

    def run(self, file_path):
        # Simulate by randomly logging behaviors
        observed = []
        for behavior in self.behaviors:
            if random.random() < 0.15:  # 15% chance per behavior
                observed.append(behavior)
        return observed

    def is_malicious(self, observed):
        # If any dangerous behavior observed, flag as malicious
        return bool(observed)
