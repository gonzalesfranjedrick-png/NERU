"""
signature_detector.py
A simple signature-based detection layer for known malware patterns.
If YARA is available, use it; otherwise, use basic byte-pattern matching.
"""
import os
try:
    import yara
    YARA_AVAILABLE = True
except ImportError:
    YARA_AVAILABLE = False

class SignatureDetector:
    def __init__(self, signature_dir=None):
        self.signature_dir = signature_dir or os.path.join(os.path.dirname(__file__), 'signatures')
        self.rules = None
        if YARA_AVAILABLE:
            self._load_yara_rules()
        else:
            self.patterns = self._load_basic_patterns()

    def _load_yara_rules(self):
        rule_files = [os.path.join(self.signature_dir, f) for f in os.listdir(self.signature_dir) if f.endswith('.yar') or f.endswith('.yara')]
        if rule_files:
            self.rules = yara.compile(filepaths={str(i): f for i, f in enumerate(rule_files)})

    def _load_basic_patterns(self):
        patterns = []
        pat_file = os.path.join(self.signature_dir, 'patterns.txt')
        if os.path.exists(pat_file):
            with open(pat_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(bytes.fromhex(line))
        return patterns

    def scan(self, file_path):
        if YARA_AVAILABLE and self.rules:
            matches = self.rules.match(file_path)
            return bool(matches)
        elif self.patterns:
            with open(file_path, 'rb') as f:
                data = f.read()
                for pat in self.patterns:
                    if pat in data:
                        return True
        return False
