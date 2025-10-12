import pefile
import pandas as pd
import math
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to calculate entropy of a section
def calculate_entropy(data):
    """Calculate Shannon entropy of data bytes"""
    if not data or len(data) == 0:
        return 0.0
    
    # Count byte frequencies
    byte_counts = np.bincount(np.frombuffer(data, dtype=np.uint8), minlength=256)
    
    # Calculate probabilities
    probabilities = byte_counts / len(data)
    
    # Calculate entropy
    entropy = 0.0
    for p in probabilities:
        if p > 0:
            entropy -= p * math.log2(p)
    
    return entropy

def extract_features(file_path):
    """
    Extract comprehensive PE file features for malware detection.
    Returns a DataFrame with 23 carefully selected features.
    """
    try:
        logger.info(f"Extracting features from: {file_path}")
        pe = pefile.PE(file_path)
        
        # Initialize all features with safe defaults
        features = {}
        
        # Basic PE Header features
        features['MajorLinkerVersion'] = getattr(pe.OPTIONAL_HEADER, 'MajorLinkerVersion', 0)
        features['MinorOperatingSystemVersion'] = getattr(pe.OPTIONAL_HEADER, 'MinorOperatingSystemVersion', 0)
        features['MajorSubsystemVersion'] = getattr(pe.OPTIONAL_HEADER, 'MajorSubsystemVersion', 0)
        features['SizeOfStackReserve'] = getattr(pe.OPTIONAL_HEADER, 'SizeOfStackReserve', 0)
        features['TimeDateStamp'] = getattr(pe.FILE_HEADER, 'TimeDateStamp', 0)
        features['MajorOperatingSystemVersion'] = getattr(pe.OPTIONAL_HEADER, 'MajorOperatingSystemVersion', 0)
        features['Characteristics'] = getattr(pe.FILE_HEADER, 'Characteristics', 0)
        features['ImageBase'] = getattr(pe.OPTIONAL_HEADER, 'ImageBase', 0)
        features['Subsystem'] = getattr(pe.OPTIONAL_HEADER, 'Subsystem', 0)
        features['MinorImageVersion'] = getattr(pe.OPTIONAL_HEADER, 'MinorImageVersion', 0)
        features['MinorSubsystemVersion'] = getattr(pe.OPTIONAL_HEADER, 'MinorSubsystemVersion', 0)
        features['SizeOfInitializedData'] = getattr(pe.OPTIONAL_HEADER, 'SizeOfInitializedData', 0)
        features['DllCharacteristics'] = getattr(pe.OPTIONAL_HEADER, 'DllCharacteristics', 0)
        features['MajorImageVersion'] = getattr(pe.OPTIONAL_HEADER, 'MajorImageVersion', 0)
        features['AddressOfEntryPoint'] = getattr(pe.OPTIONAL_HEADER, 'AddressOfEntryPoint', 0)
        features['SizeOfHeaders'] = getattr(pe.OPTIONAL_HEADER, 'SizeOfHeaders', 0)
        features['CheckSum'] = getattr(pe.OPTIONAL_HEADER, 'CheckSum', 0)
        
        # Directory entry features
        try:
            features['DirectoryEntryExport'] = 1 if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT') else 0
            features['ImageDirectoryEntryExport'] = (
                pe.OPTIONAL_HEADER.DATA_DIRECTORY[0].Size 
                if len(pe.OPTIONAL_HEADER.DATA_DIRECTORY) > 0 else 0
            )
            features['DirectoryEntryImportSize'] = (
                pe.OPTIONAL_HEADER.DATA_DIRECTORY[1].Size 
                if len(pe.OPTIONAL_HEADER.DATA_DIRECTORY) > 1 else 0
            )
        except (AttributeError, IndexError):
            features['DirectoryEntryExport'] = 0
            features['ImageDirectoryEntryExport'] = 0
            features['DirectoryEntryImportSize'] = 0
        
        # Section-based features
        if pe.sections:
            # Calculate entropy for all sections
            entropies = []
            virtual_sizes = []
            
            for section in pe.sections:
                try:
                    section_data = section.get_data()
                    if section_data:
                        entropy = calculate_entropy(section_data)
                        entropies.append(entropy)
                    
                    # Get virtual size safely
                    virtual_size = getattr(section, 'Misc_VirtualSize', 0)
                    if virtual_size > 0:
                        virtual_sizes.append(virtual_size)
                        
                except Exception as e:
                    logger.warning(f"Error processing section: {e}")
                    continue
            
            # Set section-based features
            features['SectionMinEntropy'] = min(entropies) if entropies else 0.0
            features['SectionMinVirtualsize'] = min(virtual_sizes) if virtual_sizes else 0
            features['SectionMaxChar'] = len(pe.sections)
        else:
            features['SectionMinEntropy'] = 0.0
            features['SectionMinVirtualsize'] = 0
            features['SectionMaxChar'] = 0
        
        # Validate and normalize features
        for key, value in features.items():
            if value is None:
                features[key] = 0
            elif isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                features[key] = 0.0
            # Normalize very large values to prevent overflow
            elif isinstance(value, (int, float)) and abs(value) > 1e15:
                features[key] = 1e15 if value > 0 else -1e15
        
        logger.info(f"Successfully extracted {len(features)} features")
        
        # Ensure consistent feature order and names
        expected_order = [
            'MajorLinkerVersion', 'MinorOperatingSystemVersion', 'MajorSubsystemVersion',
            'SizeOfStackReserve', 'TimeDateStamp', 'MajorOperatingSystemVersion',
            'Characteristics', 'ImageBase', 'Subsystem', 'MinorImageVersion',
            'MinorSubsystemVersion', 'SizeOfInitializedData', 'DllCharacteristics',
            'DirectoryEntryExport', 'ImageDirectoryEntryExport', 'CheckSum',
            'DirectoryEntryImportSize', 'SectionMaxChar', 'MajorImageVersion',
            'AddressOfEntryPoint', 'SectionMinEntropy', 'SizeOfHeaders',
            'SectionMinVirtualsize'
        ]
        
        # Reorder features to match expected order
        ordered_features = {}
        for feature_name in expected_order:
            ordered_features[feature_name] = features.get(feature_name, 0)
        
        return pd.DataFrame([ordered_features])
        
    except Exception as e:
        logger.error(f"Error extracting features from {file_path}: {str(e)}")
        # Return a DataFrame with zero features as fallback in correct order
        expected_order = [
            'MajorLinkerVersion', 'MinorOperatingSystemVersion', 'MajorSubsystemVersion',
            'SizeOfStackReserve', 'TimeDateStamp', 'MajorOperatingSystemVersion',
            'Characteristics', 'ImageBase', 'Subsystem', 'MinorImageVersion',
            'MinorSubsystemVersion', 'SizeOfInitializedData', 'DllCharacteristics',
            'DirectoryEntryExport', 'ImageDirectoryEntryExport', 'CheckSum',
            'DirectoryEntryImportSize', 'SectionMaxChar', 'MajorImageVersion',
            'AddressOfEntryPoint', 'SectionMinEntropy', 'SizeOfHeaders',
            'SectionMinVirtualsize'
        ]
        
        zero_features = {}
        for feature_name in expected_order:
            zero_features[feature_name] = 0.0 if 'Entropy' in feature_name else 0
            
        return pd.DataFrame([zero_features])
