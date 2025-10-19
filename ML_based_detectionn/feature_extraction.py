import pefile
import pandas as pd
import math
from typing import Dict, Any, List

# Function to calculate entropy of a section
def calculate_entropy(data):
    if not data:
        return 0
    entropy = 0
    for x in range(256):
        p_x = float(data.count(bytes([x]))) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)
    return entropy

EXPECTED_COLUMNS: List[str] = [
    'MajorLinkerVersion', 'MinorOperatingSystemVersion', 'MajorSubsystemVersion',
    'SizeOfStackReserve', 'TimeDateStamp', 'MajorOperatingSystemVersion',
    'Characteristics', 'ImageBase', 'Subsystem', 'MinorImageVersion',
    'MinorSubsystemVersion', 'SizeOfInitializedData', 'DllCharacteristics',
    'DirectoryEntryExport', 'ImageDirectoryEntryExport', 'CheckSum',
    'DirectoryEntryImportSize', 'SectionMaxChar', 'MajorImageVersion',
    'AddressOfEntryPoint', 'SectionMinEntropy', 'SizeOfHeaders',
    'SectionMinVirtualsize'
]

def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default

def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default

def extract_features(file_path: str) -> pd.DataFrame:
    pe = pefile.PE(file_path)

    # Extract raw features with defensive defaults
    features: Dict[str, Any] = {
        'MajorLinkerVersion': _safe_int(pe.OPTIONAL_HEADER.MajorLinkerVersion),
        'MinorOperatingSystemVersion': _safe_int(pe.OPTIONAL_HEADER.MinorOperatingSystemVersion),
        'MajorSubsystemVersion': _safe_int(pe.OPTIONAL_HEADER.MajorSubsystemVersion),
        'SizeOfStackReserve': _safe_int(pe.OPTIONAL_HEADER.SizeOfStackReserve),
        'TimeDateStamp': _safe_int(pe.FILE_HEADER.TimeDateStamp),
        'MajorOperatingSystemVersion': _safe_int(pe.OPTIONAL_HEADER.MajorOperatingSystemVersion),
        'Characteristics': _safe_int(pe.FILE_HEADER.Characteristics),
        'ImageBase': _safe_int(pe.OPTIONAL_HEADER.ImageBase),
        'Subsystem': _safe_int(pe.OPTIONAL_HEADER.Subsystem),
        'MinorImageVersion': _safe_int(pe.OPTIONAL_HEADER.MinorImageVersion),
        'MinorSubsystemVersion': _safe_int(pe.OPTIONAL_HEADER.MinorSubsystemVersion),
        'SizeOfInitializedData': _safe_int(pe.OPTIONAL_HEADER.SizeOfInitializedData),
        'DllCharacteristics': _safe_int(pe.OPTIONAL_HEADER.DllCharacteristics),
        'DirectoryEntryExport': 1 if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT') else 0,
        'ImageDirectoryEntryExport': _safe_int(pe.OPTIONAL_HEADER.DATA_DIRECTORY[0].Size if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT') else 0),
        'CheckSum': _safe_int(pe.OPTIONAL_HEADER.CheckSum),
        'DirectoryEntryImportSize': _safe_int(pe.OPTIONAL_HEADER.DATA_DIRECTORY[1].Size if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT') else 0),
        'SectionMaxChar': _safe_int(len(pe.sections)),
        'MajorImageVersion': _safe_int(pe.OPTIONAL_HEADER.MajorImageVersion),
        'AddressOfEntryPoint': _safe_int(pe.OPTIONAL_HEADER.AddressOfEntryPoint),
        'SectionMinEntropy': 0.0,  # placeholder until computed
        'SizeOfHeaders': _safe_int(pe.OPTIONAL_HEADER.SizeOfHeaders),
        'SectionMinVirtualsize': 0  # placeholder until computed
    }

    # Calculate SectionMinEntropy
    entropies: List[float] = []
    try:
        for section in pe.sections:
            try:
                entropy_value = calculate_entropy(section.get_data())
                entropies.append(_safe_float(entropy_value))
            except Exception:
                continue
        if entropies:
            features['SectionMinEntropy'] = float(min(entropies))
        else:
            features['SectionMinEntropy'] = 0.0
    except Exception:
        features['SectionMinEntropy'] = 0.0

    # Calculate SectionMinVirtualsize
    try:
        min_vs = min(int(getattr(section, 'Misc_VirtualSize', 0)) for section in pe.sections) if pe.sections else 0
        features['SectionMinVirtualsize'] = _safe_int(min_vs)
    except Exception:
        features['SectionMinVirtualsize'] = 0

    # Build DataFrame and enforce exact column order/types
    df = pd.DataFrame([features])
    df = df.reindex(columns=EXPECTED_COLUMNS, fill_value=0)
    # Ensure numeric dtypes (float for entropy, int for others)
    for col in df.columns:
        if col == 'SectionMinEntropy':
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).astype(float)
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
    return df
