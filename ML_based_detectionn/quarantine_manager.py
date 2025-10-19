"""
NeuroShield Quarantine Manager
Handles secure quarantine, encryption, and management of malicious files

Developer: F.J.G
Project: NeuroShield - Malware Detection with Machine Learning
"""

import os
import json
import shutil
import hashlib
import logging
from datetime import datetime
from pathlib import Path
import base64

class QuarantineManager:
    """Manages quarantined malicious files with encryption and metadata"""
    
    def __init__(self, quarantine_dir='quarantine'):
        """
        Initialize the quarantine manager
        
        Args:
            quarantine_dir: Directory to store quarantined files
        """
        self.quarantine_dir = quarantine_dir
        self.metadata_dir = os.path.join(quarantine_dir, 'metadata')
        self.files_dir = os.path.join(quarantine_dir, 'files')
        
        # Create quarantine directories
        os.makedirs(self.metadata_dir, exist_ok=True)
        os.makedirs(self.files_dir, exist_ok=True)
        
        logging.info(f"Quarantine manager initialized at: {self.quarantine_dir}")
    
    def _encrypt_file(self, file_path):
        """
        Simple XOR encryption to prevent accidental execution
        
        Args:
            file_path: Path to file to encrypt
            
        Returns:
            Encrypted file data as bytes
        """
        # Simple XOR key (in production, use proper encryption like AES)
        key = b'NeuroShield_Quarantine_Key_2025'
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # XOR encryption
        encrypted = bytearray()
        for i, byte in enumerate(data):
            encrypted.append(byte ^ key[i % len(key)])
        
        return bytes(encrypted)
    
    def _decrypt_file(self, encrypted_data):
        """
        Decrypt XOR encrypted file
        
        Args:
            encrypted_data: Encrypted bytes
            
        Returns:
            Decrypted bytes
        """
        # Same key as encryption
        key = b'NeuroShield_Quarantine_Key_2025'
        
        # XOR decryption (same as encryption for XOR)
        decrypted = bytearray()
        for i, byte in enumerate(encrypted_data):
            decrypted.append(byte ^ key[i % len(key)])
        
        return bytes(decrypted)
    
    def _calculate_hash(self, file_path):
        """
        Calculate SHA256 hash of file
        
        Args:
            file_path: Path to file
            
        Returns:
            SHA256 hash as hex string
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def quarantine_file(self, file_path, threat_info):
        """
        Move file to quarantine with encryption and metadata
        
        Args:
            file_path: Path to malicious file
            threat_info: Dict with threat information (type, confidence, findings, etc.)
            
        Returns:
            Dict with quarantine status and ID
        """
        try:
            # Generate unique ID for quarantined file
            file_hash = self._calculate_hash(file_path)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            quarantine_id = f"{timestamp}_{file_hash[:8]}"
            
            # Encrypt the file
            encrypted_data = self._encrypt_file(file_path)
            
            # Save encrypted file
            quarantine_file_path = os.path.join(self.files_dir, f"{quarantine_id}.quar")
            with open(quarantine_file_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Create metadata
            metadata = {
                'id': quarantine_id,
                'original_name': os.path.basename(file_path),
                'original_path': os.path.abspath(file_path),
                'file_hash': file_hash,
                'file_size': os.path.getsize(file_path),
                'quarantine_date': datetime.now().isoformat(),
                'threat_type': threat_info.get('prediction', 'Unknown'),
                'confidence': threat_info.get('confidence', 'N/A'),
                'threat_details': threat_info.get('findings', []),
                'file_type': threat_info.get('type', 'Unknown'),
                'encrypted': True,
                'status': 'quarantined'
            }
            
            # Save metadata
            metadata_path = os.path.join(self.metadata_dir, f"{quarantine_id}.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Delete original file
            os.remove(file_path)
            
            logging.info(f"File quarantined successfully: {quarantine_id}")
            
            return {
                'success': True,
                'quarantine_id': quarantine_id,
                'message': f'File quarantined successfully with ID: {quarantine_id}'
            }
            
        except Exception as e:
            logging.error(f"Error quarantining file: {e}")
            return {
                'success': False,
                'message': f'Failed to quarantine file: {str(e)}'
            }
    
    def list_quarantined_files(self):
        """
        Get list of all quarantined files
        
        Returns:
            List of metadata dicts for quarantined files
        """
        quarantined_files = []
        
        try:
            for metadata_file in os.listdir(self.metadata_dir):
                if metadata_file.endswith('.json'):
                    metadata_path = os.path.join(self.metadata_dir, metadata_file)
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        quarantined_files.append(metadata)
            
            # Sort by quarantine date (newest first)
            quarantined_files.sort(key=lambda x: x['quarantine_date'], reverse=True)
            
        except Exception as e:
            logging.error(f"Error listing quarantined files: {e}")
        
        return quarantined_files
    
    def restore_file(self, quarantine_id, restore_path=None):
        """
        Restore a quarantined file (decrypt and move back)
        
        Args:
            quarantine_id: ID of quarantined file
            restore_path: Optional path to restore to (defaults to original location)
            
        Returns:
            Dict with restoration status
        """
        try:
            # Load metadata
            metadata_path = os.path.join(self.metadata_dir, f"{quarantine_id}.json")
            if not os.path.exists(metadata_path):
                return {
                    'success': False,
                    'message': 'Quarantined file not found'
                }
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Load encrypted file
            quarantine_file_path = os.path.join(self.files_dir, f"{quarantine_id}.quar")
            with open(quarantine_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt
            decrypted_data = self._decrypt_file(encrypted_data)
            
            # Determine restore location
            if restore_path is None:
                restore_path = os.path.join('restored', metadata['original_name'])
            
            # Create restore directory if needed
            os.makedirs(os.path.dirname(restore_path), exist_ok=True)
            
            # Write decrypted file
            with open(restore_path, 'wb') as f:
                f.write(decrypted_data)
            
            # Update metadata
            metadata['status'] = 'restored'
            metadata['restore_date'] = datetime.now().isoformat()
            metadata['restore_path'] = restore_path
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logging.info(f"File restored successfully: {quarantine_id} -> {restore_path}")
            
            return {
                'success': True,
                'message': f'File restored to: {restore_path}',
                'restore_path': restore_path
            }
            
        except Exception as e:
            logging.error(f"Error restoring file: {e}")
            return {
                'success': False,
                'message': f'Failed to restore file: {str(e)}'
            }
    
    def delete_quarantined_file(self, quarantine_id):
        """
        Permanently delete a quarantined file
        
        Args:
            quarantine_id: ID of quarantined file
            
        Returns:
            Dict with deletion status
        """
        try:
            # Delete encrypted file
            quarantine_file_path = os.path.join(self.files_dir, f"{quarantine_id}.quar")
            if os.path.exists(quarantine_file_path):
                os.remove(quarantine_file_path)
            
            # Delete metadata
            metadata_path = os.path.join(self.metadata_dir, f"{quarantine_id}.json")
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            logging.info(f"Quarantined file deleted permanently: {quarantine_id}")
            
            return {
                'success': True,
                'message': 'File deleted permanently from quarantine'
            }
            
        except Exception as e:
            logging.error(f"Error deleting quarantined file: {e}")
            return {
                'success': False,
                'message': f'Failed to delete file: {str(e)}'
            }
    
    def get_quarantine_stats(self):
        """
        Get statistics about quarantine
        
        Returns:
            Dict with quarantine statistics
        """
        files = self.list_quarantined_files()
        
        total_files = len(files)
        total_size = sum(f.get('file_size', 0) for f in files)
        
        # Count by threat type
        threat_types = {}
        for f in files:
            threat_type = f.get('threat_type', 'Unknown')
            threat_types[threat_type] = threat_types.get(threat_type, 0) + 1
        
        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'threat_types': threat_types,
            'quarantined': len([f for f in files if f.get('status') == 'quarantined']),
            'restored': len([f for f in files if f.get('status') == 'restored'])
        }
