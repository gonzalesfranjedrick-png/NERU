"""
NeuroShield File Cleaner
Removes malicious content from infected files

Developer: F.J.G
Project: NeuroShield - Malware Detection with Machine Learning
"""

import os
import re
import logging
from datetime import datetime

class FileCleaner:
    """Cleans infected files by removing malicious content"""
    
    def __init__(self):
        """Initialize the file cleaner"""
        self.cleaned_dir = 'cleaned_files'
        os.makedirs(self.cleaned_dir, exist_ok=True)
        logging.info("File cleaner initialized")
    
    def clean_text_file(self, file_path, suspicious_keywords):
        """
        Clean a text file by removing suspicious keywords and content
        
        Args:
            file_path: Path to text file
            suspicious_keywords: List of keywords to remove
            
        Returns:
            Dict with cleaning status and cleaned file path
        """
        try:
            # Read original content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_size = len(content)
            removed_items = []
            
            # Remove suspicious keywords and surrounding context
            cleaned_content = content
            for keyword in suspicious_keywords:
                # Case-insensitive removal
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                matches = len(pattern.findall(cleaned_content))
                if matches > 0:
                    cleaned_content = pattern.sub('[REMOVED_BY_NEUROSHIELD]', cleaned_content)
                    removed_items.append(f"{keyword} ({matches} occurrences)")
            
            # Remove suspicious URLs
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, cleaned_content)
            if urls:
                cleaned_content = re.sub(url_pattern, '[URL_REMOVED_BY_NEUROSHIELD]', cleaned_content)
                removed_items.append(f"URLs ({len(urls)} found)")
            
            # Remove suspicious script tags
            script_pattern = r'<script[^>]*>.*?</script>'
            scripts = re.findall(script_pattern, cleaned_content, re.DOTALL | re.IGNORECASE)
            if scripts:
                cleaned_content = re.sub(script_pattern, '[SCRIPT_REMOVED_BY_NEUROSHIELD]', 
                                        cleaned_content, flags=re.DOTALL | re.IGNORECASE)
                removed_items.append(f"Script tags ({len(scripts)} found)")
            
            # Create cleaned file
            original_name = os.path.basename(file_path)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            cleaned_name = f"cleaned_{timestamp}_{original_name}"
            cleaned_path = os.path.join(self.cleaned_dir, cleaned_name)
            
            with open(cleaned_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            # Add cleaning report header
            report = f"""
# NeuroShield Cleaning Report
# File: {original_name}
# Cleaned: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Original size: {original_size} bytes
# Cleaned size: {len(cleaned_content)} bytes
# Items removed: {', '.join(removed_items) if removed_items else 'None'}
# ============================================

{cleaned_content}
"""
            
            with open(cleaned_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logging.info(f"Text file cleaned successfully: {cleaned_path}")
            
            return {
                'success': True,
                'cleaned_path': cleaned_path,
                'original_size': original_size,
                'cleaned_size': len(cleaned_content),
                'items_removed': removed_items,
                'message': f'File cleaned successfully. Removed: {", ".join(removed_items) if removed_items else "No malicious content"}'
            }
            
        except Exception as e:
            logging.error(f"Error cleaning text file: {e}")
            return {
                'success': False,
                'message': f'Failed to clean file: {str(e)}'
            }
    
    def clean_pdf_file(self, file_path, findings):
        """
        Clean a PDF file by removing malicious elements
        
        Args:
            file_path: Path to PDF file
            findings: List of malicious findings
            
        Returns:
            Dict with cleaning status and cleaned file path
        """
        try:
            # Read PDF content
            with open(file_path, 'rb') as f:
                pdf_data = f.read()
            
            pdf_text = pdf_data.decode('latin-1', errors='ignore')
            original_size = len(pdf_data)
            removed_items = []
            
            # Remove JavaScript
            if '/JavaScript' in pdf_text or '/JS' in pdf_text:
                # Remove JavaScript objects
                pdf_text = re.sub(r'/JavaScript\s*\([^)]*\)', '/JavaScript_REMOVED', pdf_text)
                pdf_text = pdf_text.replace('/JS', '/JS_REMOVED')
                removed_items.append('JavaScript')
            
            # Remove auto-actions
            if '/OpenAction' in pdf_text or '/AA' in pdf_text:
                pdf_text = pdf_text.replace('/OpenAction', '/OpenAction_REMOVED')
                pdf_text = pdf_text.replace('/AA', '/AA_REMOVED')
                removed_items.append('Auto-actions')
            
            # Remove launch actions (HIGH RISK)
            if '/Launch' in pdf_text:
                pdf_text = pdf_text.replace('/Launch', '/Launch_REMOVED')
                removed_items.append('Launch actions (HIGH RISK)')
            
            # Remove embedded files
            if '/EmbeddedFile' in pdf_text:
                pdf_text = re.sub(r'/EmbeddedFile[^>]*', '/EmbeddedFile_REMOVED', pdf_text)
                removed_items.append('Embedded files')
            
            # Remove suspicious URIs
            if '/URI' in pdf_text:
                pdf_text = re.sub(r'/URI\s*\([^)]*\)', '/URI_REMOVED', pdf_text)
                removed_items.append('URIs')
            
            # Convert back to bytes
            cleaned_data = pdf_text.encode('latin-1', errors='ignore')
            
            # Create cleaned file
            original_name = os.path.basename(file_path)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            cleaned_name = f"cleaned_{timestamp}_{original_name}"
            cleaned_path = os.path.join(self.cleaned_dir, cleaned_name)
            
            with open(cleaned_path, 'wb') as f:
                f.write(cleaned_data)
            
            # Create text report
            report_path = cleaned_path + '.txt'
            report = f"""NeuroShield PDF Cleaning Report
================================
File: {original_name}
Cleaned: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Original size: {original_size} bytes
Cleaned size: {len(cleaned_data)} bytes

Items Removed:
{chr(10).join('- ' + item for item in removed_items) if removed_items else '- No malicious content found'}

Findings:
{chr(10).join('- ' + str(f) for f in findings)}

WARNING: This is a cleaned version. Some functionality may be lost.
Please verify the PDF works correctly before use.
"""
            
            with open(report_path, 'w') as f:
                f.write(report)
            
            logging.info(f"PDF file cleaned successfully: {cleaned_path}")
            
            return {
                'success': True,
                'cleaned_path': cleaned_path,
                'report_path': report_path,
                'original_size': original_size,
                'cleaned_size': len(cleaned_data),
                'items_removed': removed_items,
                'message': f'PDF cleaned successfully. Removed: {", ".join(removed_items) if removed_items else "No malicious content"}'
            }
            
        except Exception as e:
            logging.error(f"Error cleaning PDF file: {e}")
            return {
                'success': False,
                'message': f'Failed to clean PDF: {str(e)}'
            }
    
    def create_safe_copy(self, file_path):
        """
        Create a safe copy of a file with security warnings
        
        Args:
            file_path: Path to original file
            
        Returns:
            Dict with copy status
        """
        try:
            original_name = os.path.basename(file_path)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = f"safe_{timestamp}_{original_name}.txt"
            safe_path = os.path.join(self.cleaned_dir, safe_name)
            
            # Create text version with warnings
            with open(safe_path, 'w') as f:
                f.write(f"""
╔═══════════════════════════════════════════════════════════════╗
║              ⚠️  NEUROSHIELD SECURITY WARNING ⚠️              ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  This file was detected as MALICIOUS by NeuroShield          ║
║                                                               ║
║  Original file: {original_name}
║  Detection date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
║                                                               ║
║  ⚠️  DO NOT attempt to restore or execute this file          ║
║  ⚠️  This copy is for reference only                         ║
║  ⚠️  The original has been quarantined                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

For your safety, the original file has been encrypted and 
quarantined by NeuroShield. 

If you believe this is a false positive, please:
1. Contact your IT security team
2. Submit the file to VirusTotal for additional analysis
3. Use professional malware analysis tools

DO NOT restore this file unless you are absolutely certain it is safe.

Developed by F.J.G
NeuroShield - Malware Detection with Machine Learning
© 2025 NeuroShield. All Rights Reserved.
""")
            
            return {
                'success': True,
                'safe_path': safe_path,
                'message': f'Safe informational copy created at: {safe_path}'
            }
            
        except Exception as e:
            logging.error(f"Error creating safe copy: {e}")
            return {
                'success': False,
                'message': f'Failed to create safe copy: {str(e)}'
            }
