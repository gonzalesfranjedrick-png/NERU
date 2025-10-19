# This script generates synthetic polymorphic test files for evaluation.
import os
import random
import zlib
import hashlib

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), 'polymorphic_samples')
os.makedirs(SAMPLES_DIR, exist_ok=True)

PAYLOADS = [
    b"MZ" + os.urandom(100) + b"PAYLOAD1",  # Simulated PE file
    b"MZ" + os.urandom(200) + b"PAYLOAD2",
    b"MZ" + os.urandom(300) + b"PAYLOAD3",
]

for i in range(10):
    base = random.choice(PAYLOADS)
    # Polymorphic: mutate bytes, compress, add junk, shuffle
    mutated = bytearray(base)
    for _ in range(random.randint(5, 20)):
        idx = random.randint(0, len(mutated)-1)
        mutated[idx] = (mutated[idx] + random.randint(1, 255)) % 256
    if random.random() < 0.5:
        mutated = zlib.compress(mutated)
    if random.random() < 0.5:
        mutated += os.urandom(random.randint(10, 50))
    # Add a random hash as a marker
    mutated += hashlib.sha256(mutated).digest()[:8]
    fname = f"poly_sample_{i+1}.bin"
    with open(os.path.join(SAMPLES_DIR, fname), 'wb') as f:
        f.write(mutated)
print(f"Generated 10 polymorphic test files in {SAMPLES_DIR}")
