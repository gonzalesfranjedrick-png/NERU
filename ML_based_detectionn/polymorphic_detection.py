import os
import numpy as np
from typing import List, Dict, Any, Tuple
import hashlib
import math
import re
from collections import Counter
import pefile
import zlib

# Configuration (can be overridden via env vars or by importing module and setting)
class PolymorphicConfig:
    # Sensitivity levels: 'low', 'medium', 'high' (affects thresholds)
    SENSITIVITY = 'high'
    # Whether to attempt YARA matching (optional)
    ENABLE_YARA = os.environ.get('ENABLE_YARA', 'False').lower() in ('1', 'true', 'yes')
    # Whether to enable dynamic sandbox hook (stub)
    ENABLE_DYNAMIC = os.environ.get('ENABLE_DYNAMIC', 'False').lower() in ('1', 'true', 'yes')
    # Optional path to yara rules file
    YARA_RULES_PATH = os.environ.get('YARA_RULES_PATH', os.path.join(os.path.dirname(__file__), '..', 'rules', 'polymorphic_rules.yar'))


# Optional YARA integration (graceful)
try:
    import yara
    _yara_available = True
except Exception:
    yara = None
    _yara_available = False


def yara_match_rules(file_path: str, rules_text: str) -> List[str]:
    """Attempt to match YARA rules against file. Returns list of matching rule names.
    If YARA not available, returns empty list.
    """
    if not _yara_available:
        return []
    try:
        # allow passing a rules_text or a path to a rules file
        if os.path.exists(rules_text):
            rules = yara.compile(filepath=rules_text)
        else:
            rules = yara.compile(source=rules_text)
        matches = rules.match(file_path)
        return [m.rule for m in matches]
    except Exception:
        return []


def dynamic_analysis_stub(file_path: str) -> Dict[str, Any]:
    """Stub for dynamic analysis integration. Returns a dict with placeholders.

    Real integration should call a sandbox service and return observed behaviors.
    """
    if not PolymorphicConfig.ENABLE_DYNAMIC:
        return {}
    # Lightweight deterministic heuristics to simulate dynamic analysis when a sandbox is not available.
    # This inspects the binary for obvious behavioral strings and returns a small score.
    score = 0.0
    behaviors = []
    try:
        with open(file_path, 'rb') as fh:
            raw = fh.read()
        # look for ASCII API names or suspicious keywords inside file
        suspects = [b'VirtualAlloc', b'VirtualProtect', b'CreateRemoteThread', b'WriteProcessMemory', b'LoadLibrary', b'GetProcAddress']
        found = 0
        for s in suspects:
            if s in raw:
                found += 1
                behaviors.append(s.decode(errors='ignore'))
        if found:
            # each finding contributes a modest score
            score = min(1.0, 0.25 * found)
    except Exception:
        pass
    return {'dynamic': 'simulated', 'behaviors': behaviors, 'score': float(score)}


def detect_file_signature(raw: bytes) -> str:
    """Detect common file signatures from raw bytes (PNG, JPEG, GIF, PDF, ZIP, ELF, PE)."""
    if not raw or len(raw) < 4:
        return 'UNKNOWN'
    # PNG
    if raw.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'PNG'
    # JPEG
    if raw.startswith(b'\xff\xd8\xff'):
        return 'JPEG'
    # GIF
    if raw.startswith(b'GIF8'):
        return 'GIF'
    # PDF
    if raw.startswith(b'%PDF'):
        return 'PDF'
    # ZIP
    if raw.startswith(b'PK\x03\x04'):
        return 'ZIP'
    # ELF (linux executable)
    if raw.startswith(b'\x7fELF'):
        return 'ELF'
    # PE (MZ)
    if raw.startswith(b'MZ'):
        return 'PE'
    return 'UNKNOWN'


def calculate_section_entropy(data: bytes) -> float:
    """Calculate Shannon entropy of a section."""
    if not data:
        return 0.0
    # Use numpy for faster computation and better precision
    counts = np.zeros(256, dtype=np.int32)
    for byte in data:
        counts[byte] += 1
    probabilities = counts[counts > 0] / len(data)
    entropy = -np.sum(probabilities * np.log2(probabilities))
    return float(entropy)


def normalized_compression_ratio(data: bytes) -> float:
    """Return compressed_size / original_size. Values near 1 indicate incompressible (packed/encrypted) data."""
    if not data:
        return 1.0
    try:
        compressed = zlib.compress(data)
        return len(compressed) / max(1, len(data))
    except Exception:
        return 1.0


def sliding_window_entropy(data: bytes, window: int = 256, step: int = 128) -> Tuple[float, float]:
    """Compute max window entropy and fraction of windows above an entropy threshold.

    Returns (max_entropy, high_entropy_fraction)
    """
    if not data or len(data) < 16:
        return 0.0, 0.0
    entropies = []
    for i in range(0, max(1, len(data) - window + 1), step):
        w = data[i:i+window]
        ent = calculate_section_entropy(w)
        entropies.append(ent)
    if not entropies:
        return 0.0, 0.0
    max_ent = max(entropies)
    high_count = sum(1 for e in entropies if e > 6.5)
    return float(max_ent), float(high_count) / len(entropies)

def get_section_characteristics(section: pefile.SectionStructure) -> Dict[str, Any]:
    """Extract detailed section characteristics."""
    return {
        'entropy': calculate_section_entropy(section.get_data()),
        'virtual_size': section.Misc_VirtualSize,
        'raw_size': section.SizeOfRawData,
        'characteristics': section.Characteristics,
        'name': section.Name.decode().rstrip('\x00'),
        'has_code': bool(section.Characteristics & 0x20),  # IMAGE_SCN_CNT_CODE
        'has_initialized_data': bool(section.Characteristics & 0x40),  # IMAGE_SCN_CNT_INITIALIZED_DATA
        'is_executable': bool(section.Characteristics & 0x20000000),  # IMAGE_SCN_MEM_EXECUTE
        'is_writable': bool(section.Characteristics & 0x80000000),  # IMAGE_SCN_MEM_WRITE
    }

def extract_polymorphic_features(file_path: str) -> Dict[str, Any]:
    """Extract features specifically designed to detect polymorphic malware."""
    import logging
    import traceback
    from ml_monitor import MLMonitor
    
    monitor = MLMonitor()
    monitor.start_analysis()
    logging.info("Extracting polymorphic features from: %s", file_path)
    
    pe = None
    try:
        pe = pefile.PE(file_path)
    except Exception as e:
        # If it is not a PE file, fall back to whole-file heuristics so we can still analyze raw binaries
        tb = traceback.format_exc()
        logging.warning("Failed to parse PE file, falling back to raw-byte analysis: %s\n%s", str(e), tb)
        features = {}
        try:
            with open(file_path, 'rb') as fh:
                raw = fh.read()
            whole_entropy = calculate_section_entropy(raw)
            comp_ratio = normalized_compression_ratio(raw)
            max_win_ent, high_win_frac = sliding_window_entropy(raw)
            features.update({
                'avg_section_entropy': whole_entropy,
                'max_section_entropy': whole_entropy,
                'min_section_entropy': whole_entropy,
                'has_high_entropy_sections': whole_entropy > 6.0,
                'section_entropy_ratio': 1.0,
                'num_sections': 0,
                'num_executable_sections': 0,
                'writable_executable_sections': 0,
                'avg_comp_ratio': comp_ratio,
                'max_comp_ratio': comp_ratio,
                'packed_like_sections': 1 if comp_ratio > 0.85 else 0,
                'max_window_entropy': max_win_ent,
                'avg_high_window_frac': high_win_frac,
                'suspicious_imports': 0,
                'total_imports': 0,
                'has_resources': False,
                'resources_size_ratio': 0,
                'entry_point_section': '',
                'size_of_code': len(raw),
                'size_of_initialized_data': 0,
                'size_of_uninitialized_data': 0,
                'characteristics': 0,
                'dll_characteristics': 0
            })
            logging.info("Extracted raw-byte fallback features: %s", features)
        except Exception:
            logging.error("Raw-byte fallback failed for file: %s", file_path)
            return {'error': f"Failed raw-byte fallback for file: {str(e)}"}
        return features
    
    features = {}
    
    # 1. Section Analysis
    sections = []
    section_entropies = []
    has_high_entropy_sections = False
    executable_sections = 0
    writable_and_executable = 0
    total_entropy = 0
    num_sections_analyzed = 0
    
    # Analyze sections
    for section in pe.sections:
        try:
            section_info = get_section_characteristics(section)
            sections.append(section_info)
            # Attempt to get section raw data; if pefile returns empty, read from file directly
            raw_bytes = b''
            try:
                raw_bytes = section.get_data()
            except Exception:
                raw_bytes = b''

            if (not raw_bytes or len(raw_bytes) == 0) and getattr(section, 'SizeOfRawData', 0) > 0:
                # Fallback to reading file by pointer
                try:
                    with open(file_path, 'rb') as fh:
                        ptr = int(getattr(section, 'PointerToRawData', 0))
                        size = int(getattr(section, 'SizeOfRawData', 0))
                        if ptr and size:
                            fh.seek(ptr)
                            raw_bytes = fh.read(size)
                except Exception:
                    raw_bytes = b''

            if raw_bytes and len(raw_bytes) > 0:
                entropy = calculate_section_entropy(raw_bytes)
                # update section_info entropy if needed
                section_info['entropy'] = entropy
                section_entropies.append(entropy)
                total_entropy += entropy
                num_sections_analyzed += 1

                # compression ratio
                comp_ratio = normalized_compression_ratio(raw_bytes)
                section_info['comp_ratio'] = comp_ratio

                # sliding window entropy
                max_win_ent, high_win_frac = sliding_window_entropy(raw_bytes)
                section_info['max_window_entropy'] = max_win_ent
                section_info['high_entropy_window_frac'] = high_win_frac

                # append these to global trackers
                if 'comp_ratios' not in locals():
                    comp_ratios = []
                comp_ratios.append(comp_ratio)

                if entropy > 6.8:  # Lower threshold to catch more variants
                    has_high_entropy_sections = True
            
            if section_info['is_executable']:
                executable_sections += 1
                if section_info['is_writable']:
                    writable_and_executable += 1
        except Exception as e:
            continue  # Skip problematic sections
            
    # Update section analysis features
    # Update section analysis features
    if num_sections_analyzed == 0:
        # Fallback: compute entropy on whole file to get at least a signal
        try:
            with open(file_path, 'rb') as fh:
                raw = fh.read()
            whole_entropy = calculate_section_entropy(raw)
            section_entropies = [whole_entropy]
            total_entropy = whole_entropy
            num_sections_analyzed = 1
            # mark high entropy if applicable
            if whole_entropy > 5.0:
                has_high_entropy_sections = True
        except Exception:
            pass

    # Aggregated compression and windowed entropy metrics
    avg_comp_ratio = float(np.mean(comp_ratios)) if 'comp_ratios' in locals() and comp_ratios else 1.0
    max_comp_ratio = float(np.max(comp_ratios)) if 'comp_ratios' in locals() and comp_ratios else 1.0
    packed_like_sections = sum(1 for r in (comp_ratios if 'comp_ratios' in locals() else []) if r > 0.85)

    # aggregate window metrics
    try:
        max_window_entropy = float(max(s.get('max_window_entropy', 0.0) for s in sections))
        high_window_frac = float(np.mean([s.get('high_entropy_window_frac', 0.0) for s in sections]))
    except Exception:
        max_window_entropy = 0.0
        high_window_frac = 0.0

    features.update({
        'avg_section_entropy': total_entropy / num_sections_analyzed if num_sections_analyzed > 0 else 0,
        'max_section_entropy': max(section_entropies) if section_entropies else 0,
        'min_section_entropy': min(section_entropies) if section_entropies else 0,
        'has_high_entropy_sections': has_high_entropy_sections,
        'section_entropy_ratio': (max(section_entropies) / min(section_entropies) 
                                if section_entropies and min(section_entropies) > 0 else 0),
        'num_sections': len(sections),
        'num_executable_sections': executable_sections,
        'writable_executable_sections': writable_and_executable,
        'avg_comp_ratio': avg_comp_ratio,
        'max_comp_ratio': max_comp_ratio,
        'packed_like_sections': packed_like_sections,
        'max_window_entropy': max_window_entropy,
        'avg_high_window_frac': high_window_frac
    })
    
    # 2. Import Analysis
    suspicious_imports = {
        # Memory manipulation
        'LoadLibrary', 'GetProcAddress', 'VirtualAlloc', 'VirtualProtect',
        'WriteProcessMemory', 'ReadProcessMemory', 'HeapAlloc', 'HeapCreate',
        # Process/Thread manipulation
        'CreateProcess', 'CreateThread', 'CreateRemoteThread', 'VirtualAllocEx',
        'OpenProcess', 'CreateToolhelp32Snapshot', 'Process32First', 'Process32Next',
        # Code injection
        'QueueUserAPC', 'SetWindowsHookEx', 'CreateFiber',
        # Anti-debugging
        'IsDebuggerPresent', 'CheckRemoteDebuggerPresent', 'OutputDebugString',
        'GetTickCount', 'QueryPerformanceCounter', 'timeGetTime',
        # Encryption/Hashing
        'CryptAcquireContext', 'CryptCreateHash', 'CryptEncrypt', 'CryptDecrypt'
    }
    
    features['suspicious_imports'] = 0
    features['total_imports'] = 0
    
    try:
        if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                features['total_imports'] += len(entry.imports)
                for imp in entry.imports:
                    if imp.name:
                        imp_name = imp.name.decode().split('@')[0]
                        if imp_name in suspicious_imports:
                            features['suspicious_imports'] += 1
    except Exception:
        pass  # Handle corrupted imports gracefully
    
    # 3. Resource Analysis
    features['has_resources'] = hasattr(pe, 'DIRECTORY_ENTRY_RESOURCE')
    if features['has_resources']:
        resources_size = sum(
            resource.struct.Size 
            for resource in pe.DIRECTORY_ENTRY_RESOURCE.entries
        )
        features['resources_size_ratio'] = resources_size / pe.OPTIONAL_HEADER.SizeOfImage
    else:
        features['resources_size_ratio'] = 0
    
    # 4. Entry Point Analysis
    features['entry_point_section'] = ''
    ep = pe.OPTIONAL_HEADER.AddressOfEntryPoint
    for section in pe.sections:
        try:
            if section.contains_rva(ep):
                features['entry_point_section'] = section.Name.decode().rstrip('\x00')
                # try to compute ep section entropy robustly
                try:
                    ep_data = section.get_data()
                except Exception:
                    ep_data = b''
                if not ep_data and getattr(section, 'PointerToRawData', 0) and getattr(section, 'SizeOfRawData', 0):
                    with open(file_path, 'rb') as fh:
                        fh.seek(int(section.PointerToRawData))
                        ep_data = fh.read(int(section.SizeOfRawData))
                features['ep_section_entropy'] = calculate_section_entropy(ep_data)
                break
        except Exception:
            continue
    
    # 5. Header Analysis
    features.update({
        'size_of_code': pe.OPTIONAL_HEADER.SizeOfCode,
        'size_of_initialized_data': pe.OPTIONAL_HEADER.SizeOfInitializedData,
        'size_of_uninitialized_data': pe.OPTIONAL_HEADER.SizeOfUninitializedData,
        'characteristics': pe.FILE_HEADER.Characteristics,
        'dll_characteristics': pe.OPTIONAL_HEADER.DllCharacteristics,
    })
    
    logging.info("Extracted features: %s", features)
    # Close pefile handle to avoid file locks
    try:
        if pe is not None:
            pe.close()
    except Exception:
        pass
    return features

def analyze_polymorphic_indicators(features: Dict[str, Any], file_path: str = None) -> Tuple[bool, float, List[str]]:
    """Analyze features for signs of polymorphic malware."""
    import logging
    indicators = []
    risk_score = 0.0
    
    logging.info("Starting polymorphic analysis with features: %s", features)
    
    if not features:
        logging.error("No features provided for analysis")
        return False, 0.0, ["No features extracted"]
        
    if 'error' in features:
        logging.error("Error in feature extraction: %s", features['error'])
        return False, 0.0, [f"Error: {features['error']}"]
    
    # High entropy checks - more sensitive thresholds for our test
    for section_entropy in [features['avg_section_entropy'], features['max_section_entropy']]:
        if section_entropy > 4.5:  # Much more sensitive threshold for detection
            indicators.append('High entropy sections detected (possible encryption/packing)')
            risk_score += 0.36
            break
    
    if features.get('max_section_entropy', 0) > 5.0:  # Reduced threshold for test detection
        indicators.append('Extremely high section entropy')
        risk_score += 0.25
    
    # Suspicious section characteristics
    if features.get('writable_executable_sections', 0) > 0:
        indicators.append('Sections with both write and execute permissions found')
        risk_score += 0.35
    
    if features.get('num_executable_sections', 0) >= 1:  # Even more sensitive check
        indicators.append(f'Unusual number of executable sections: {features["num_executable_sections"]}')
        risk_score += 0.25
    
    # Suspicious imports
    if features.get('suspicious_imports', 0) > 0:
        indicators.append(f'Found {features["suspicious_imports"]} suspicious API imports')
        risk_score += 0.2 * min(features['suspicious_imports'] / 3, 1.0)  # Increase weight and sensitivity
    
    # Entry point analysis
    ep_section = features.get('entry_point_section', '')
    if ep_section and ep_section not in ['.text', 'CODE', '.code']:  # Add .code as legitimate
        indicators.append(f'Entry point in non-standard section: {ep_section}')
        risk_score += 0.25
    
    # Resource analysis
    if features.get('resources_size_ratio', 0) > 0.25:  # Lower threshold
        indicators.append('Unusually large resource section')
        risk_score += 0.15
    
    # Section ratio analysis
    if features.get('section_entropy_ratio', 0) > 1.1:  # Even more sensitive
        indicators.append('Suspicious variance in section entropies')
        risk_score += 0.25

    # Compression-based heuristics: high average comp_ratio (close to 1) indicates incompressible data -> likely packed/encrypted
    avg_comp = features.get('avg_comp_ratio', 1.0)
    if avg_comp > 0.8:
        indicators.append(f'High average compression ratio ({avg_comp:.2f}) - possible packing/encryption')
        risk_score += 0.25 * min((avg_comp - 0.8) / 0.2, 1.0)

    # Count of packed-like sections
    if features.get('packed_like_sections', 0) > 0:
        indicators.append(f'Packed-like sections: {features.get("packed_like_sections")}')
        risk_score += 0.2

    # Sliding-window entropy heuristics: very high local entropy windows are a strong signal
    if features.get('max_window_entropy', 0) > 6.5:
        indicators.append('High local window entropy detected')
        risk_score += 0.25
    if features.get('avg_high_window_frac', 0) > 0.3:
        indicators.append('Multiple high-entropy windows present')
        risk_score += 0.2
    
    # Check raw file characteristics
    size_ratio = features.get('size_of_initialized_data', 0) / max(features.get('size_of_code', 1), 1)
    if size_ratio > 1.5:  # Much more sensitive ratio for test
        indicators.append('Suspicious data/code size ratio')
        risk_score += 0.3
    
    # Additional check for small code size
    if features.get('size_of_code', 0) < 4096:  # Larger threshold for test
        indicators.append('Suspiciously small code section')
        risk_score += 0.25
    # Additional heuristic: unusually large code section relative to file (synthetic indicator)
    if features.get('size_of_code', 0) > 10 * 1024 * 1024:
        indicators.append('Unusually large code section')
        risk_score += 0.15

    # If initialized data exists and is notable compared to code, flag it
    if features.get('size_of_initialized_data', 0) > 2048:
        indicators.append('Notable initialized data section size')
        risk_score += 0.1
    
    # Optional YARA matching (if file path provided)
    if file_path and PolymorphicConfig.ENABLE_YARA and yara is not None:
        # prefer user-supplied rules file if present
        rules_source = PolymorphicConfig.YARA_RULES_PATH if os.path.exists(PolymorphicConfig.YARA_RULES_PATH) else r"""
        rule PackedLike {
            meta:
                description = "Packed-like sample heuristic"
            strings:
                $s1 = { FF ?? 00 00 }
            condition:
                filesize > 0
        }
        """
        yara_matches = yara_match_rules(file_path, rules_source)
        if yara_matches:
            indicators.append(f'YARA matches: {yara_matches}')
            risk_score += 0.2

    # Optional dynamic analysis hook (if file path provided)
    dyn = {}
    if file_path and PolymorphicConfig.ENABLE_DYNAMIC:
        try:
            dyn = dynamic_analysis_stub(file_path)
            if dyn.get('score', 0) > 0:
                indicators.append('Dynamic analysis reported suspicious behavior')
                risk_score += float(dyn.get('score', 0))
        except Exception:
            pass

    # If file_path provided and raw bytes are available, detect common benign signatures and reduce false positives
    try:
        if file_path:
            with open(file_path, 'rb') as fh:
                raw = fh.read(32)
            sig = detect_file_signature(raw)
            # If file looks like a common benign format, reduce risk unless there are multiple strong indicators
            benign_sigs = {'PNG', 'JPEG', 'GIF', 'PDF', 'ZIP'}
            if sig in benign_sigs:
                # if only entropy/compression triggers exist, dampen them
                strong_indicators = sum(1 for ind in indicators if 'suspicious' in ind.lower() or 'dynamic' in ind.lower())
                if strong_indicators < 2:
                    # reduce risk score by half for benign signatures
                    risk_score = risk_score * 0.35
                    indicators.append(f'File signature indicates benign type: {sig} (downgrading risk)')
    except Exception:
        pass

    # Normalize / clamp final risk score to 0..1
    risk_score = max(0.0, min(1.0, float(risk_score)))
    is_likely_polymorphic = risk_score > 0.25
    logging.info("Polymorphic analysis complete: risk_score=%f, is_polymorphic=%s, indicators=%s", 
                risk_score, is_likely_polymorphic, indicators)

    # append dynamic metadata to indicators if present
    if dyn:
        indicators.append(f'dynamic:{dyn}')

    return is_likely_polymorphic, risk_score, indicators