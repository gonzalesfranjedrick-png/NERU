import zipfile, os, sys
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import MAX_ARCHIVE_ENTRIES, MAX_ARCHIVE_UNCOMPRESSED_BYTES

uploads = Path(__file__).resolve().parents[1] / 'uploads'
# Create a zip with many small files to simulate limit
zip_path = uploads / 'many_files_test.zip'
with zipfile.ZipFile(zip_path, 'w') as z:
    for i in range(min(150, MAX_ARCHIVE_ENTRIES + 10)):
        z.writestr(f'file_{i}.txt', 'x' * 100)

# Simple check: open and count
with zipfile.ZipFile(zip_path, 'r') as z:
    count = len(z.infolist())
    print('entries in zip:', count)
    assert count >= MAX_ARCHIVE_ENTRIES

os.remove(zip_path)
print('archive limit test done')
