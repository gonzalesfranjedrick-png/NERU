import pefile
import pandas as pd
import math
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to calculate entropy of a section
def calculate_entropy(data):
    """Calculate Shannon entropy of data"""
    if not data or len(data) == 0:
        return 0.0
    
    # Count byte frequencies
    byte_counts = [0] * 256
    for byte in data:
        byte_counts[byte] += 1
    
    # Calculate entropy
    entropy = 0.0
    data_len = len(data)
    for count in byte_counts:
        if count > 0:
            probability = count / data_len
            entropy -= probability * math.log2(probability)
    
    return entropy

def extract_features(file_path):
    """
    Extract 23 PE file features for malware detection
    
    Args:
        file_path: Path to PE file
        
    Returns:
        pandas.DataFrame with extracted features
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
            
        # Load PE file
        pe = pefile.PE(file_path)
        
        # Initialize features dictionary with default values
        features = {}
        
        # Feature 1: MajorLinkerVersion
        features['MajorLinkerVersion'] = getattr(pe.OPTIONAL_HEADER, 'MajorLinkerVersion', 0)
        
        # Feature 2: MinorOperatingSystemVersion  
        features['MinorOperatingSystemVersion'] = getattr(pe.OPTIONAL_HEADER, 'MinorOperatingSystemVersion', 0)
        
        # Feature 3: MajorSubsystemVersion
        features['MajorSubsystemVersion'] = getattr(pe.OPTIONAL_HEADER, 'MajorSubsystemVersion', 0)
        
        # Feature 4: SizeOfStackReserve
        features['SizeOfStackReserve'] = getattr(pe.OPTIONAL_HEADER, 'SizeOfStackReserve', 0)
        
        # Feature 5: TimeDateStamp
        features['TimeDateStamp'] = getattr(pe.FILE_HEADER, 'TimeDateStamp', 0)
        
        # Feature 6: MajorOperatingSystemVersion
        features['MajorOperatingSystemVersion'] = getattr(pe.OPTIONAL_HEADER, 'MajorOperatingSystemVersion', 0)
        
        # Feature 7: Characteristics
        features['Characteristics'] = getattr(pe.FILE_HEADER, 'Characteristics', 0)
        
        # Feature 8: ImageBase
        features['ImageBase'] = getattr(pe.OPTIONAL_HEADER, 'ImageBase', 0)
        
        # Feature 9: Subsystem
        features['Subsystem'] = getattr(pe.OPTIONAL_HEADER, 'Subsystem', 0)
        
        # Feature 10: MinorImageVersion
        features['MinorImageVersion'] = getattr(pe.OPTIONAL_HEADER, 'MinorImageVersion', 0)
        
        # Feature 11: MinorSubsystemVersion
        features['MinorSubsystemVersion'] = getattr(pe.OPTIONAL_HEADER, 'MinorSubsystemVersion', 0)
        
        # Feature 12: SizeOfInitializedData
        features['SizeOfInitializedData'] = getattr(pe.OPTIONAL_HEADER, 'SizeOfInitializedData', 0)
        
        # Feature 13: DllCharacteristics
        features['DllCharacteristics'] = getattr(pe.OPTIONAL_HEADER, 'DllCharacteristics', 0)
        
        # Feature 14: DirectoryEntryExport (binary)
        features['DirectoryEntryExport'] = 1 if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT') and pe.DIRECTORY_ENTRY_EXPORT else 0
        
        # Feature 15: ImageDirectoryEntryExport (size)
        if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT') and pe.DIRECTORY_ENTRY_EXPORT:
            features['ImageDirectoryEntryExport'] = pe.OPTIONAL_HEADER.DATA_DIRECTORY[0].Size
        else:
            features['ImageDirectoryEntryExport'] = 0
            
        # Feature 16: CheckSum
        features['CheckSum'] = getattr(pe.OPTIONAL_HEADER, 'CheckSum', 0)
        
        # Feature 17: DirectoryEntryImportSize
        if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT') and pe.DIRECTORY_ENTRY_IMPORT:
            features['DirectoryEntryImportSize'] = pe.OPTIONAL_HEADER.DATA_DIRECTORY[1].Size
        else:
            features['DirectoryEntryImportSize'] = 0
            
        # Feature 18: SectionMaxChar (number of sections)
        features['SectionMaxChar'] = len(pe.sections) if pe.sections else 0
        
        # Feature 19: MajorImageVersion
        features['MajorImageVersion'] = getattr(pe.OPTIONAL_HEADER, 'MajorImageVersion', 0)
        
        # Feature 20: AddressOfEntryPoint
        features['AddressOfEntryPoint'] = getattr(pe.OPTIONAL_HEADER, 'AddressOfEntryPoint', 0)
        
        # Feature 21: SectionMinEntropy (calculated from sections)
        if pe.sections:
            entropies = []
            for section in pe.sections:
                try:
                    section_data = section.get_data()
                    if section_data:
                        entropy = calculate_entropy(section_data)
                        entropies.append(entropy)
                except Exception as e:
                    logger.warning(f"Error calculating entropy for section: {e}")
                    continue
            
            features['SectionMinEntropy'] = min(entropies) if entropies else 0.0
        else:
            features['SectionMinEntropy'] = 0.0
            
        # Feature 22: SizeOfHeaders
        features['SizeOfHeaders'] = getattr(pe.OPTIONAL_HEADER, 'SizeOfHeaders', 0)
        
        # Feature 23: SectionMinVirtualsize
        if pe.sections:
            virtual_sizes = []
            for section in pe.sections:
                try:
                    virtual_size = getattr(section, 'Misc_VirtualSize', 0)
                    if virtual_size > 0:
                        virtual_sizes.append(virtual_size)
                except Exception as e:
                    logger.warning(f"Error getting virtual size for section: {e}")
                    continue
            
            features['SectionMinVirtualsize'] = min(virtual_sizes) if virtual_sizes else 0
        else:
            features['SectionMinVirtualsize'] = 0
        
        # Close PE file
        pe.close()
        
        # Create DataFrame with features in the correct order
        feature_order = [
            'MajorLinkerVersion', 'MinorOperatingSystemVersion', 'MajorSubsystemVersion',
            'SizeOfStackReserve', 'TimeDateStamp', 'MajorOperatingSystemVersion',
            'Characteristics', 'ImageBase', 'Subsystem', 'MinorImageVersion',
            'MinorSubsystemVersion', 'SizeOfInitializedData', 'DllCharacteristics',
            'DirectoryEntryExport', 'ImageDirectoryEntryExport', 'CheckSum',
            'DirectoryEntryImportSize', 'SectionMaxChar', 'MajorImageVersion',
            'AddressOfEntryPoint', 'SectionMinEntropy', 'SizeOfHeaders',
            'SectionMinVirtualsize'
        ]
        
        # Ensure all features are present and in correct order
        ordered_features = {}
        for feature in feature_order:
            ordered_features[feature] = features.get(feature, 0)
        
        logger.info(f"Successfully extracted features from {os.path.basename(file_path)}")
        return pd.DataFrame([ordered_features])
        
    except Exception as e:
        logger.error(f"Error extracting features from {file_path}: {str(e)}")
        # Return default features if extraction fails
        default_features = {
            'MajorLinkerVersion': 0, 'MinorOperatingSystemVersion': 0, 'MajorSubsystemVersion': 0,
            'SizeOfStackReserve': 0, 'TimeDateStamp': 0, 'MajorOperatingSystemVersion': 0,
            'Characteristics': 0, 'ImageBase': 0, 'Subsystem': 0, 'MinorImageVersion': 0,
            'MinorSubsystemVersion': 0, 'SizeOfInitializedData': 0, 'DllCharacteristics': 0,
            'DirectoryEntryExport': 0, 'ImageDirectoryEntryExport': 0, 'CheckSum': 0,
            'DirectoryEntryImportSize': 0, 'SectionMaxChar': 0, 'MajorImageVersion': 0,
            'AddressOfEntryPoint': 0, 'SectionMinEntropy': 0.0, 'SizeOfHeaders': 0,
            'SectionMinVirtualsize': 0
        }
        return pd.DataFrame([default_features])
