"""Lightweight ML monitoring stub used by tests and local runs.

Provides minimal MLMonitor class with start_analysis/stop methods so
feature extraction code can call it without requiring external services.
"""
import time
import logging
from typing import Optional, Dict, Any


class MLMonitor:
    def __init__(self):
        self._start_time: Optional[float] = None
        self.metadata: Dict[str, Any] = {}

    def start_analysis(self):
        """Mark start of an analysis run."""
        self._start_time = time.time()
        logging.debug("MLMonitor: analysis started at %s", self._start_time)

    def stop_analysis(self):
        """Stop analysis and return elapsed seconds (or None if not started)."""
        if self._start_time is None:
            return None
        elapsed = time.time() - self._start_time
        logging.debug("MLMonitor: analysis stopped, elapsed=%.4fs", elapsed)
        self._start_time = None
        return elapsed

    def record(self, key: str, value: Any):
        """Record arbitrary metadata for the run."""
        self.metadata[key] = value

    def get_metadata(self) -> Dict[str, Any]:
        return dict(self.metadata)
"""
ML Analysis Monitor
Tracks and logs system performance metrics
"""

import logging
import time
import psutil
import json
from datetime import datetime
from typing import Dict, Any
import os

class MLMonitor:
    def __init__(self, log_file: str = "ml_analysis.log"):
        self.log_file = log_file
        self.start_time = None
        self.metrics = {}
        
        # Configure logging
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
        
    def start_analysis(self) -> None:
        """Start monitoring an analysis run"""
        self.start_time = time.time()
        self.metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': [],
            'memory_usage': [],
            'processing_time': 0,
            'files_processed': 0,
            'detection_rates': {
                'malware': 0,
                'benign': 0,
                'uncertain': 0
            }
        }
        
    def update_metrics(self, detection_result: Dict[str, Any]) -> None:
        """Update metrics with latest detection result"""
        self.metrics['cpu_percent'].append(psutil.cpu_percent())
        self.metrics['memory_usage'].append(psutil.Process().memory_info().rss / 1024 / 1024)
        self.metrics['files_processed'] += 1
        
        # Update detection counts
        if detection_result.get('score', 0) > 0.8:
            self.metrics['detection_rates']['malware'] += 1
        elif detection_result.get('score', 0) < 0.2:
            self.metrics['detection_rates']['benign'] += 1
        else:
            self.metrics['detection_rates']['uncertain'] += 1
            
    def end_analysis(self) -> Dict[str, Any]:
        """Complete monitoring and return metrics"""
        if self.start_time:
            self.metrics['processing_time'] = time.time() - self.start_time
            
            # Calculate averages
            self.metrics['avg_cpu_percent'] = sum(self.metrics['cpu_percent']) / len(self.metrics['cpu_percent'])
            self.metrics['avg_memory_mb'] = sum(self.metrics['memory_usage']) / len(self.metrics['memory_usage'])
            
            # Calculate rates
            total = self.metrics['files_processed']
            if total > 0:
                self.metrics['detection_rates']['malware_rate'] = self.metrics['detection_rates']['malware'] / total
                self.metrics['detection_rates']['benign_rate'] = self.metrics['detection_rates']['benign'] / total
                self.metrics['detection_rates']['uncertain_rate'] = self.metrics['detection_rates']['uncertain'] / total
            
            # Log summary
            self._log_summary()
            
            return self.metrics
        return {}
    
    def _log_summary(self) -> None:
        """Log analysis summary"""
        summary = {
            'timestamp': self.metrics['timestamp'],
            'duration_seconds': self.metrics['processing_time'],
            'files_processed': self.metrics['files_processed'],
            'avg_cpu_percent': self.metrics['avg_cpu_percent'],
            'avg_memory_mb': self.metrics['avg_memory_mb'],
            'detection_rates': self.metrics['detection_rates']
        }
        
        logging.info(f"Analysis Summary: {json.dumps(summary, indent=2)}")
        
        # Alert on concerning metrics
        if self.metrics['avg_cpu_percent'] > 90:
            logging.warning("High CPU usage detected")
        if self.metrics['avg_memory_mb'] > 1000:
            logging.warning("High memory usage detected")
        if self.metrics['detection_rates'].get('uncertain_rate', 0) > 0.2:
            logging.warning("High uncertainty rate in detection results")
            
    def log_error(self, error: Exception, context: str = "") -> None:
        """Log error with context"""
        logging.error(f"Error in {context}: {str(error)}", exc_info=True)
        
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot"""
        return self.metrics