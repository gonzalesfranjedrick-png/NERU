import math
import pefile
import pandas as pd

# Keep feature order EXACTLY consistent with training
FEATURE_COLUMNS = [
    'TimeDateStamp', 'Machine', 'NumberOfSections', 'SizeOfOptionalHeader',
    'Characteristics', 'SizeOfCode', 'SizeOfInitializedData', 'SizeOfUninitializedData',
    'AddressOfEntryPoint', 'BaseOfCode', 'BaseOfData', 'ImageBase',
    'SectionAlignment', 'FileAlignment', 'MajorOperatingSystemVersion',
    'MinorOperatingSystemVersion', 'SizeOfImage', 'SizeOfHeaders',
    'CheckSum', 'Subsystem', 'SectionMaxEntropy', 'SectionMinEntropy', 'SectionAvgEntropy'
]


def calculate_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    length = float(len(data))
    # Compute histogram of byte values 0..255
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    entropy = 0.0
    for c in counts:
        if c == 0:
            continue
        p_x = c / length
        entropy -= p_x * math.log(p_x, 2)
    return float(entropy)


def _safe_getattr(obj, name, default=0):
    try:
        return getattr(obj, name)
    except Exception:
        return default


def extract_features(file_path: str) -> pd.DataFrame:
    pe = pefile.PE(file_path)

    # Section entropies
    entropies = []
    for section in getattr(pe, 'sections', []) or []:
        try:
            entropies.append(calculate_entropy(section.get_data()))
        except Exception:
            # If section data can't be read, skip it
            continue

    if entropies:
        section_max_entropy = max(entropies)
        section_min_entropy = min(entropies)
        section_avg_entropy = sum(entropies) / len(entropies)
    else:
        section_max_entropy = 0.0
        section_min_entropy = 0.0
        section_avg_entropy = 0.0

    file_header = pe.FILE_HEADER
    opt_header = pe.OPTIONAL_HEADER

    # Build features aligned with FEATURE_COLUMNS
    features = {
        'TimeDateStamp': int(_safe_getattr(file_header, 'TimeDateStamp', 0)),
        'Machine': int(_safe_getattr(file_header, 'Machine', 0)),
        'NumberOfSections': int(_safe_getattr(file_header, 'NumberOfSections', len(getattr(pe, 'sections', []) or []))),
        'SizeOfOptionalHeader': int(_safe_getattr(file_header, 'SizeOfOptionalHeader', 0)),
        'Characteristics': int(_safe_getattr(file_header, 'Characteristics', 0)),
        'SizeOfCode': int(_safe_getattr(opt_header, 'SizeOfCode', 0)),
        'SizeOfInitializedData': int(_safe_getattr(opt_header, 'SizeOfInitializedData', 0)),
        'SizeOfUninitializedData': int(_safe_getattr(opt_header, 'SizeOfUninitializedData', 0)),
        'AddressOfEntryPoint': int(_safe_getattr(opt_header, 'AddressOfEntryPoint', 0)),
        'BaseOfCode': int(_safe_getattr(opt_header, 'BaseOfCode', 0)),
        'BaseOfData': int(_safe_getattr(opt_header, 'BaseOfData', 0)),  # 0 for PE32+
        'ImageBase': int(_safe_getattr(opt_header, 'ImageBase', 0)),
        'SectionAlignment': int(_safe_getattr(opt_header, 'SectionAlignment', 0)),
        'FileAlignment': int(_safe_getattr(opt_header, 'FileAlignment', 0)),
        'MajorOperatingSystemVersion': int(_safe_getattr(opt_header, 'MajorOperatingSystemVersion', 0)),
        'MinorOperatingSystemVersion': int(_safe_getattr(opt_header, 'MinorOperatingSystemVersion', 0)),
        'SizeOfImage': int(_safe_getattr(opt_header, 'SizeOfImage', 0)),
        'SizeOfHeaders': int(_safe_getattr(opt_header, 'SizeOfHeaders', 0)),
        'CheckSum': int(_safe_getattr(opt_header, 'CheckSum', 0)),
        'Subsystem': int(_safe_getattr(opt_header, 'Subsystem', 0)),
        'SectionMaxEntropy': float(section_max_entropy),
        'SectionMinEntropy': float(section_min_entropy),
        'SectionAvgEntropy': float(section_avg_entropy),
    }

    # Ensure correct column order and types
    df = pd.DataFrame([[features[c] for c in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
    return df
