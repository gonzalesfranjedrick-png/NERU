from pathlib import Path
import sys
sys.path.append(r"c:\SIP FRAN\NERU\ML_based_detectionn")
from app import analyze_text_content

p = Path(r"c:\SIP FRAN\NERU\ML_based_detectionn\uploads\EICAR TEST FILE.txt")
if not p.exists():
    print('EICAR test file not found at', p)
    raise SystemExit(1)

content = p.read_text(errors='ignore')
result = analyze_text_content(content, p.name)
print('Result:')
for k,v in result.items():
    print(f'{k}: {v}')
