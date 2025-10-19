"""
NeuroShield False Positive Testing System
Test benign files to ensure low false positive rate

Developer: F.J.G
Project: NeuroShield - Malware Detection with Machine Learning
"""

import os
import logging
import joblib
import numpy as np
from datetime import datetime
from feature_extraction import extract_features
import glob

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FalsePositiveTester:
    """Test benign files to measure false positive rate"""
    
    def __init__(self, model_path='ML_model/malwareclassifier-V2.pkl',
                 scaler_path='ML_model/scaler.pkl',
                 results_dir='fp_test_results'):
        """
        Initialize FP tester
        
        Args:
            model_path: Path to trained model
            scaler_path: Path to scaler
            results_dir: Directory for results
        """
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path) if os.path.exists(scaler_path) else None
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        
        self.test_results = []
        
        logging.info("FalsePositiveTester initialized")
        logging.info(f"Model: {model_path}")
        logging.info(f"Scaler: {scaler_path if self.scaler else 'None'}")
    
    def test_benign_directory(self, benign_dir, file_pattern='*', limit=None):
        """
        Test a directory of benign files
        
        Args:
            benign_dir: Directory containing benign files
            file_pattern: File pattern to match (e.g., '*.exe', '*.dll')
            limit: Maximum files to test (None = all)
            
        Returns:
            Dictionary with test results
        """
        logging.info(f"Testing benign files from: {benign_dir}")
        logging.info(f"Pattern: {file_pattern}")
        
        # Find files
        pattern = os.path.join(benign_dir, file_pattern)
        files = glob.glob(pattern)[:limit]
        
        if not files:
            logging.warning(f"No files found matching pattern: {pattern}")
            return None
        
        logging.info(f"Found {len(files)} benign files to test")
        
        # Test each file
        false_positives = []
        true_negatives = []
        errors = []
        
        for i, file_path in enumerate(files):
            try:
                # Extract features
                features = extract_features(file_path)

                # Align feature order to model expectations if available
                if hasattr(self.model, 'feature_names_in_'):
                    try:
                        features = features.reindex(columns=list(self.model.feature_names_in_), fill_value=0)
                    except Exception:
                        pass

                # Scale if scaler available
                if self.scaler:
                    try:
                        features_scaled = self.scaler.transform(features)
                    except Exception:
                        features_scaled = features
                else:
                    features_scaled = features
                
                # Predict
                prediction = self.model.predict(features_scaled)[0]
                confidence = self.model.predict_proba(features_scaled)[0]
                
                # Record result
                result = {
                    'file_path': file_path,
                    'file_name': os.path.basename(file_path),
                    'prediction': int(prediction),
                    'confidence_benign': float(confidence[0]),
                    'confidence_malware': float(confidence[1]),
                    'is_false_positive': prediction == 1
                }
                
                self.test_results.append(result)
                
                if prediction == 1:
                    false_positives.append(result)
                    logging.warning(f"[FP] {os.path.basename(file_path)} flagged as malware ({confidence[1]*100:.1f}% confidence)")
                else:
                    true_negatives.append(result)
                
                if (i + 1) % 50 == 0:
                    logging.info(f"Tested {i + 1}/{len(files)} files...")
            
            except Exception as e:
                logging.error(f"Error testing {file_path}: {e}")
                errors.append({'file_path': file_path, 'error': str(e)})
        
        # Calculate metrics
        total_tested = len(files) - len(errors)
        fp_count = len(false_positives)
        tn_count = len(true_negatives)
        fp_rate = fp_count / total_tested if total_tested > 0 else 0
        
        results = {
            'directory': benign_dir,
            'pattern': file_pattern,
            'total_files': len(files),
            'tested': total_tested,
            'errors': len(errors),
            'true_negatives': tn_count,
            'false_positives': fp_count,
            'fp_rate': fp_rate,
            'fp_percentage': fp_rate * 100,
            'timestamp': datetime.now().isoformat()
        }
        
        logging.info("=" * 70)
        logging.info("FALSE POSITIVE TEST RESULTS")
        logging.info("=" * 70)
        logging.info(f"Directory:        {benign_dir}")
        logging.info(f"Total Files:      {len(files)}")
        logging.info(f"Successfully Tested: {total_tested}")
        logging.info(f"Errors:           {len(errors)}")
        logging.info(f"True Negatives:   {tn_count}")
        logging.info(f"False Positives:  {fp_count}")
        logging.info(f"FP Rate:          {fp_rate:.4f} ({fp_rate*100:.2f}%)")
        logging.info("=" * 70)
        
        if fp_rate <= 0.01:
            logging.info("✓ EXCELLENT: FP rate <= 1%")
        elif fp_rate <= 0.05:
            logging.info("✓ GOOD: FP rate <= 5%")
        elif fp_rate <= 0.10:
            logging.info("⚠ ACCEPTABLE: FP rate <= 10%")
        else:
            logging.info("✗ NEEDS IMPROVEMENT: FP rate > 10%")
        
        return results
    
    def test_system_files(self, system_dirs=None):
        """
        Test legitimate system files (Windows DLLs, EXEs)
        
        Args:
            system_dirs: List of system directories to test
            
        Returns:
            Combined test results
        """
        if system_dirs is None:
            # Default Windows system directories
            system_dirs = [
                'C:\\Windows\\System32',
                'C:\\Windows\\SysWOW64',
                'C:\\Program Files',
                'C:\\Program Files (x86)'
            ]
        
        logging.info("Testing legitimate system files...")
        
        all_results = []
        
        for sys_dir in system_dirs:
            if not os.path.exists(sys_dir):
                logging.warning(f"Directory not found: {sys_dir}")
                continue
            
            # Test DLLs
            dll_results = self.test_benign_directory(sys_dir, '*.dll', limit=100)
            if dll_results:
                all_results.append(dll_results)
            
            # Test EXEs
            exe_results = self.test_benign_directory(sys_dir, '*.exe', limit=50)
            if exe_results:
                all_results.append(exe_results)
        
        return all_results
    
    def test_popular_software(self, software_dirs=None):
        """
        Test popular legitimate software
        
        Args:
            software_dirs: List of software directories
            
        Returns:
            Test results
        """
        if software_dirs is None:
            software_dirs = [
                'C:\\Program Files\\Google\\Chrome',
                'C:\\Program Files\\Mozilla Firefox',
                'C:\\Program Files\\Microsoft Office',
                'C:\\Program Files (x86)\\Adobe'
            ]
        
        logging.info("Testing popular legitimate software...")
        
        all_results = []
        
        for soft_dir in software_dirs:
            if not os.path.exists(soft_dir):
                continue
            
            results = self.test_benign_directory(soft_dir, '*.*', limit=50)
            if results:
                all_results.append(results)
        
        return all_results
    
    def generate_fp_report(self, filename='fp_test_report.txt'):
        """Generate comprehensive FP test report"""
        report_path = os.path.join(self.results_dir, filename)
        
        # Calculate overall statistics
        total_tested = len(self.test_results)
        fp_count = sum(1 for r in self.test_results if r['is_false_positive'])
        tn_count = total_tested - fp_count
        overall_fp_rate = fp_count / total_tested if total_tested > 0 else 0
        
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("NeuroShield False Positive Test Report\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Developer: F.J.G\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("OVERALL STATISTICS\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Total Files Tested:   {total_tested}\n")
            f.write(f"True Negatives:       {tn_count}\n")
            f.write(f"False Positives:      {fp_count}\n")
            f.write(f"False Positive Rate:  {overall_fp_rate:.4f} ({overall_fp_rate*100:.2f}%)\n\n")
            
            # Assessment
            f.write("=" * 80 + "\n")
            f.write("ASSESSMENT\n")
            f.write("=" * 80 + "\n\n")
            
            if overall_fp_rate <= 0.01:
                f.write("★ EXCELLENT: FP rate <= 1% - Competitive with top AVs\n")
            elif overall_fp_rate <= 0.05:
                f.write("★ GOOD: FP rate <= 5% - Acceptable for deployment\n")
            elif overall_fp_rate <= 0.10:
                f.write("★ ACCEPTABLE: FP rate <= 10% - Needs improvement\n")
            else:
                f.write("★ NEEDS IMPROVEMENT: FP rate > 10% - Too many false alarms\n")
            
            f.write("\n")
            
            # List false positives
            if fp_count > 0:
                f.write("=" * 80 + "\n")
                f.write("FALSE POSITIVES DETECTED\n")
                f.write("=" * 80 + "\n\n")
                
                for i, result in enumerate([r for r in self.test_results if r['is_false_positive']], 1):
                    f.write(f"{i}. {result['file_name']}\n")
                    f.write(f"   Path: {result['file_path']}\n")
                    f.write(f"   Confidence (Malware): {result['confidence_malware']*100:.1f}%\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("RECOMMENDATIONS\n")
            f.write("=" * 80 + "\n\n")
            
            if overall_fp_rate > 0.05:
                f.write("1. Retrain model with more diverse benign samples\n")
                f.write("2. Adjust classification threshold for higher precision\n")
                f.write("3. Add whitelisting for common legitimate files\n")
                f.write("4. Review and tune ensemble voting weights\n")
            else:
                f.write("Model performs well on benign files.\n")
                f.write("Continue monitoring FP rate with diverse test sets.\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        logging.info(f"FP test report saved to: {report_path}")
        
        return report_path
    
    def export_results(self, filename='fp_test_results.json'):
        """Export detailed results to JSON"""
        import json
        
        json_path = os.path.join(self.results_dir, filename)
        
        with open(json_path, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logging.info(f"Results exported to: {json_path}")
        
        return json_path


def main():
    """Main FP testing workflow"""
    logging.info("=" * 80)
    logging.info("NeuroShield False Positive Testing")
    logging.info("=" * 80)
    
    # Initialize tester
    tester = FalsePositiveTester()
    
    # Test benign files from your dataset
    # REPLACE with your actual benign file directories
    benign_test_dir = 'datasets/benign_test'
    
    if os.path.exists(benign_test_dir):
        results = tester.test_benign_directory(benign_test_dir)
    else:
        logging.warning(f"Benign test directory not found: {benign_test_dir}")
        logging.warning("Please provide benign files for FP testing")
    
    # Test system files (if on Windows)
    # tester.test_system_files()
    
    # Generate reports
    tester.generate_fp_report()
    tester.export_results()
    
    logging.info("=" * 80)
    logging.info("FP testing complete!")
    logging.info("=" * 80)


if __name__ == '__main__':
    main()
