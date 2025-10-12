import pefile
import pandas as pd
import math
import os

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

def extract_features(file_path):
    """
    Extract 23 features from PE file for malware detection.
    Returns features in the exact order expected by the trained model.
    """
    try:
        pe = pefile.PE(file_path)
        
        # Calculate entropy for all sections
        entropies = []
        virtual_sizes = []
        for section in pe.sections:
            try:
                section_data = section.get_data()
                if section_data:
                    entropy = calculate_entropy(section_data)
                    entropies.append(entropy)
                    virtual_sizes.append(section.Misc_VirtualSize)
            except:
                continue
        
        # Calculate section statistics
        min_entropy = min(entropies) if entropies else 0
        max_entropy = max(entropies) if entropies else 0
        avg_entropy = sum(entropies) / len(entropies) if entropies else 0
        min_virtual_size = min(virtual_sizes) if virtual_sizes else 0
        
        # Extract the 23 features in the exact order expected by the model
        features = {
            'MajorLinkerVersion': pe.OPTIONAL_HEADER.MajorLinkerVersion,
            'MinorOperatingSystemVersion': pe.OPTIONAL_HEADER.MinorOperatingSystemVersion,
            'MajorSubsystemVersion': pe.OPTIONAL_HEADER.MajorSubsystemVersion,
            'SizeOfStackReserve': pe.OPTIONAL_HEADER.SizeOfStackReserve,
            'TimeDateStamp': pe.FILE_HEADER.TimeDateStamp,
            'MajorOperatingSystemVersion': pe.OPTIONAL_HEADER.MajorOperatingSystemVersion,
            'Characteristics': pe.FILE_HEADER.Characteristics,
            'ImageBase': pe.OPTIONAL_HEADER.ImageBase,
            'Subsystem': pe.OPTIONAL_HEADER.Subsystem,
            'MinorImageVersion': pe.OPTIONAL_HEADER.MinorImageVersion,
            'MinorSubsystemVersion': pe.OPTIONAL_HEADER.MinorSubsystemVersion,
            'SizeOfInitializedData': pe.OPTIONAL_HEADER.SizeOfInitializedData,
            'DllCharacteristics': pe.OPTIONAL_HEADER.DllCharacteristics,
            'DirectoryEntryExport': 1 if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT') and pe.DIRECTORY_ENTRY_EXPORT else 0,
            'ImageDirectoryEntryExport': pe.OPTIONAL_HEADER.DATA_DIRECTORY[0].Size if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT') and pe.DIRECTORY_ENTRY_EXPORT else 0,
            'CheckSum': pe.OPTIONAL_HEADER.CheckSum,
            'DirectoryEntryImportSize': pe.OPTIONAL_HEADER.DATA_DIRECTORY[1].Size if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT') and pe.DIRECTORY_ENTRY_IMPORT else 0,
            'SectionMaxChar': len(pe.sections),
            'MajorImageVersion': pe.OPTIONAL_HEADER.MajorImageVersion,
            'AddressOfEntryPoint': pe.OPTIONAL_HEADER.AddressOfEntryPoint,
            'SectionMinEntropy': min_entropy,
            'SizeOfHeaders': pe.OPTIONAL_HEADER.SizeOfHeaders,
            'SectionMinVirtualsize': min_virtual_size
        }
        
        # Ensure all features are numeric and handle any None values
        for key, value in features.items():
            if value is None:
                features[key] = 0
            elif isinstance(value, (int, float)):
                features[key] = float(value)
            else:
                features[key] = 0
        
        return pd.DataFrame([features])
        
    except Exception as e:
        # Return default features if extraction fails
        print(f"Error extracting features from {file_path}: {str(e)}")
        default_features = {
            'MajorLinkerVersion': 0,
            'MinorOperatingSystemVersion': 0,
            'MajorSubsystemVersion': 0,
            'SizeOfStackReserve': 0,
            'TimeDateStamp': 0,
            'MajorOperatingSystemVersion': 0,
            'Characteristics': 0,
            'ImageBase': 0,
            'Subsystem': 0,
            'MinorImageVersion': 0,
            'MinorSubsystemVersion': 0,
            'SizeOfInitializedData': 0,
            'DllCharacteristics': 0,
            'DirectoryEntryExport': 0,
            'ImageDirectoryEntryExport': 0,
            'CheckSum': 0,
            'DirectoryEntryImportSize': 0,
            'SectionMaxChar': 0,
            'MajorImageVersion': 0,
            'AddressOfEntryPoint': 0,
            'SectionMinEntropy': 0,
            'SizeOfHeaders': 0,
            'SectionMinVirtualsize': 0
        }
        return pd.DataFrame([default_features])
