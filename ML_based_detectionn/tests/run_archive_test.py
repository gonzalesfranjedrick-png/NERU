import zipfile, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import analyze_text_content

uploads = Path(__file__).resolve().parents[1] / 'uploads'
eicar = uploads / 'EICAR TEST FILE.txt'
zip_path = uploads / 'eicar_test.zip'

# create zip
with zipfile.ZipFile(zip_path, 'w') as z:
    z.write(eicar, arcname='EICAR TEST FILE.txt')

# scan zip member
with zipfile.ZipFile(zip_path, 'r') as z:
    for zi in z.infolist():
        if zi.is_dir():
            continue
        with z.open(zi) as fh:
            data = fh.read()
            try:
                text = data.decode('latin-1', errors='ignore')
            except Exception:
                text = ''
            res = analyze_text_content(text, zi.filename)
            print('member:', zi.filename, '->', res['prediction'], res['confidence'])

# cleanup
os.remove(zip_path)
print('done')
