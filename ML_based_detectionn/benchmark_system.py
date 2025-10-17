"""
NeuroShield Benchmarking System
Compare performance against commercial antivirus products

Developer: F.J.G
Project: NeuroShield - Malware Detection with Machine Learning
"""

import os
import json
import logging
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AVBenchmark:
    """Benchmark NeuroShield against commercial AVs"""
    
    def __init__(self, results_dir='benchmark_results'):
        """Initialize benchmarking system"""
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
        
        self.results = {
            'neuroshield': {},
            'competitors': {}
        }
        
        logging.info("AVBenchmark initialized")
    
    def record_neuroshield_results(self, detection_rate, fp_rate, test_samples, 
                                   malware_samples, benign_samples, test_name='Test'):
        """
        Record NeuroShield test results
        
        Args:
            detection_rate: Detection rate (0-1)
            fp_rate: False positive rate (0-1)
            test_samples: Total test samples
            malware_samples: Number of malware samples
            benign_samples: Number of benign samples
            test_name: Name of the test
        """
        self.results['neuroshield'][test_name] = {
            'detection_rate': detection_rate,
            'fp_rate': fp_rate,
            'detection_percent': detection_rate * 100,
            'fp_percent': fp_rate * 100,
            'test_samples': test_samples,
            'malware_samples': malware_samples,
            'benign_samples': benign_samples,
            'timestamp': datetime.now().isoformat()
        }
        
        logging.info(f"NeuroShield results recorded for '{test_name}'")
        logging.info(f"  Detection Rate: {detection_rate*100:.2f}%")
        logging.info(f"  FP Rate: {fp_rate*100:.2f}%")
    
    def add_competitor_results(self, av_name, detection_rate, fp_rate, 
                               test_samples, malware_samples, benign_samples, 
                               test_name='Test', source='Manual'):
        """
        Add competitor AV results for comparison
        
        Args:
            av_name: Name of the antivirus (e.g., 'Windows Defender', 'Norton')
            detection_rate: Detection rate (0-1)
            fp_rate: False positive rate (0-1)
            test_samples: Total test samples
            malware_samples: Number of malware samples
            benign_samples: Number of benign samples
            test_name: Name of the test
            source: Source of data (e.g., 'AV-TEST', 'Manual')
        """
        if av_name not in self.results['competitors']:
            self.results['competitors'][av_name] = {}
        
        self.results['competitors'][av_name][test_name] = {
            'detection_rate': detection_rate,
            'fp_rate': fp_rate,
            'detection_percent': detection_rate * 100,
            'fp_percent': fp_rate * 100,
            'test_samples': test_samples,
            'malware_samples': malware_samples,
            'benign_samples': benign_samples,
            'source': source,
            'timestamp': datetime.now().isoformat()
        }
        
        logging.info(f"{av_name} results recorded for '{test_name}'")
    
    def generate_comparison_report(self, test_name='Test', filename='benchmark_report.txt'):
        """Generate detailed comparison report"""
        report_path = os.path.join(self.results_dir, filename)
        
        with open(report_path, 'w') as f:
            f.write("=" * 90 + "\n")
            f.write("NeuroShield vs Commercial Antivirus - Benchmark Report\n")
            f.write("=" * 90 + "\n\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Test Name: {test_name}\n")
            f.write(f"Developer: F.J.G\n\n")
            
            # NeuroShield results
            if test_name in self.results['neuroshield']:
                ns_results = self.results['neuroshield'][test_name]
                
                f.write("=" * 90 + "\n")
                f.write("NEUROSHIELD RESULTS\n")
                f.write("=" * 90 + "\n\n")
                f.write(f"Detection Rate:       {ns_results['detection_percent']:.2f}%\n")
                f.write(f"False Positive Rate:  {ns_results['fp_percent']:.2f}%\n")
                f.write(f"Test Samples:         {ns_results['test_samples']}\n")
                f.write(f"  - Malware:          {ns_results['malware_samples']}\n")
                f.write(f"  - Benign:           {ns_results['benign_samples']}\n\n")
            
            # Competitor results
            f.write("=" * 90 + "\n")
            f.write("COMPETITOR ANTIVIRUS RESULTS\n")
            f.write("=" * 90 + "\n\n")
            
            for av_name, tests in self.results['competitors'].items():
                if test_name in tests:
                    comp_results = tests[test_name]
                    
                    f.write(f"{av_name}:\n")
                    f.write(f"  Detection Rate:       {comp_results['detection_percent']:.2f}%\n")
                    f.write(f"  False Positive Rate:  {comp_results['fp_percent']:.2f}%\n")
                    f.write(f"  Test Samples:         {comp_results['test_samples']}\n")
                    f.write(f"  Source:               {comp_results['source']}\n\n")
            
            # Comparison
            if test_name in self.results['neuroshield']:
                f.write("=" * 90 + "\n")
                f.write("COMPARISON\n")
                f.write("=" * 90 + "\n\n")
                
                ns_dr = self.results['neuroshield'][test_name]['detection_percent']
                ns_fp = self.results['neuroshield'][test_name]['fp_percent']
                
                f.write(f"{'Antivirus':<25} {'Detection Rate':<20} {'FP Rate':<20} {'Status'}\n")
                f.write("-" * 90 + "\n")
                f.write(f"{'NeuroShield':<25} {ns_dr:>6.2f}% {'':<13} {ns_fp:>6.2f}% {'':<13} {'[THIS PRODUCT]'}\n")
                
                for av_name, tests in self.results['competitors'].items():
                    if test_name in tests:
                        comp_dr = tests[test_name]['detection_percent']
                        comp_fp = tests[test_name]['fp_percent']
                        
                        dr_diff = ns_dr - comp_dr
                        fp_diff = ns_fp - comp_fp
                        
                        dr_status = f"({dr_diff:+.2f}%)" if dr_diff != 0 else "(same)"
                        fp_status = f"({fp_diff:+.2f}%)" if fp_diff != 0 else "(same)"
                        
                        f.write(f"{av_name:<25} {comp_dr:>6.2f}% {dr_status:<13} {comp_fp:>6.2f}% {fp_status:<13}\n")
                
                f.write("\n")
                f.write("Interpretation:\n")
                f.write("  + Detection Rate: Positive difference = NeuroShield is better\n")
                f.write("  + FP Rate: Negative difference = NeuroShield has fewer false positives (better)\n\n")
            
            f.write("=" * 90 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 90 + "\n")
        
        logging.info(f"Benchmark report saved to: {report_path}")
        
        return report_path
    
    def plot_comparison(self, test_name='Test', filename='benchmark_comparison.png'):
        """Generate visual comparison chart"""
        
        # Collect data
        products = ['NeuroShield']
        detection_rates = []
        fp_rates = []
        
        if test_name in self.results['neuroshield']:
            detection_rates.append(self.results['neuroshield'][test_name]['detection_percent'])
            fp_rates.append(self.results['neuroshield'][test_name]['fp_percent'])
        else:
            return None
        
        for av_name, tests in self.results['competitors'].items():
            if test_name in tests:
                products.append(av_name)
                detection_rates.append(tests[test_name]['detection_percent'])
                fp_rates.append(tests[test_name]['fp_percent'])
        
        # Create subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Detection rate comparison
        colors = ['#1d8cf8'] + ['#gray'] * (len(products) - 1)
        bars1 = ax1.bar(products, detection_rates, color=colors, alpha=0.8)
        ax1.set_ylabel('Detection Rate (%)')
        ax1.set_title('Detection Rate Comparison')
        ax1.set_ylim([80, 100])
        ax1.axhline(y=95, color='green', linestyle='--', label='95% Target', alpha=0.5)
        ax1.axhline(y=99, color='blue', linestyle='--', label='99% Target', alpha=0.5)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}%',
                    ha='center', va='bottom')
        
        # False positive rate comparison
        bars2 = ax2.bar(products, fp_rates, color=colors, alpha=0.8)
        ax2.set_ylabel('False Positive Rate (%)')
        ax2.set_title('False Positive Rate Comparison (Lower is Better)')
        ax2.axhline(y=1, color='green', linestyle='--', label='1% Target', alpha=0.5)
        ax2.axhline(y=5, color='orange', linestyle='--', label='5% Threshold', alpha=0.5)
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}%',
                    ha='center', va='bottom')
        
        plt.tight_layout()
        
        plot_path = os.path.join(self.results_dir, filename)
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.info(f"Comparison chart saved to: {plot_path}")
        
        return plot_path
    
    def export_results(self, filename='benchmark_results.json'):
        """Export results to JSON"""
        json_path = os.path.join(self.results_dir, filename)
        
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logging.info(f"Results exported to: {json_path}")
        
        return json_path
    
    def load_av_test_data(self):
        """
        Load reference data from AV-TEST (example format)
        
        Note: This is example data. Replace with actual AV-TEST or AV-Comparatives data
        """
        logging.info("Loading reference AV data...")
        
        # Example data (replace with actual published results)
        reference_data = {
            'Windows Defender': {'detection': 0.997, 'fp': 0.01},
            'Norton 360': {'detection': 0.998, 'fp': 0.005},
            'Bitdefender': {'detection': 0.999, 'fp': 0.008},
            'Kaspersky': {'detection': 0.998, 'fp': 0.012},
            'Avast': {'detection': 0.995, 'fp': 0.015},
            'AVG': {'detection': 0.994, 'fp': 0.018},
            'McAfee': {'detection': 0.996, 'fp': 0.010}
        }
        
        for av_name, scores in reference_data.items():
            self.add_competitor_results(
                av_name=av_name,
                detection_rate=scores['detection'],
                fp_rate=scores['fp'],
                test_samples=10000,
                malware_samples=5000,
                benign_samples=5000,
                test_name='Offline Test',
                source='Reference Data (Example)'
            )
        
        logging.info(f"Loaded reference data for {len(reference_data)} antivirus products")


def example_usage():
    """Example benchmarking workflow"""
    
    # Initialize benchmark
    benchmark = AVBenchmark()
    
    # Record NeuroShield results (from your evaluation)
    benchmark.record_neuroshield_results(
        detection_rate=0.995,  # 99.5%
        fp_rate=0.02,          # 2%
        test_samples=1000,
        malware_samples=500,
        benign_samples=500,
        test_name='Offline Test'
    )
    
    # Load reference AV data
    benchmark.load_av_test_data()
    
    # Generate reports
    benchmark.generate_comparison_report(test_name='Offline Test')
    benchmark.plot_comparison(test_name='Offline Test')
    benchmark.export_results()
    
    logging.info("Benchmarking complete!")


if __name__ == '__main__':
    example_usage()
