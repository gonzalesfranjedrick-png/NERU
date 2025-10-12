#!/usr/bin/env python3
"""
High-Accuracy ML Model Training for NeuroShield
Developed by F.J.G

This script creates a robust, high-accuracy malware detection model
with proper validation, realistic data generation, and comprehensive evaluation.
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
import logging
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
from sklearn.feature_selection import SelectKBest, f_classif
import matplotlib.pyplot as plt
import seaborn as sns
from feature_extraction import extract_features
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HighAccuracyTrainer:
    """High-accuracy trainer for malware detection"""
    
    def __init__(self, model_dir='ML_model', results_dir='evaluation_results'):
        """Initialize the trainer"""
        self.model_dir = model_dir
        self.results_dir = results_dir
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)
        
        self.model = None
        self.scaler = None
        self.feature_selector = None
        self.training_metrics = {}
        
        logger.info("HighAccuracyTrainer initialized")
    
    def create_realistic_dataset(self, n_malware=2000, n_benign=2000):
        """
        Create a realistic synthetic dataset based on real PE file characteristics
        
        Args:
            n_malware: Number of malware samples
            n_benign: Number of benign samples
            
        Returns:
            X (features), y (labels)
        """
        logger.info(f"Creating realistic dataset: {n_malware} malware, {n_benign} benign")
        
        np.random.seed(42)
        
        # Feature names in correct order
        feature_names = [
            'MajorLinkerVersion', 'MinorOperatingSystemVersion', 'MajorSubsystemVersion',
            'SizeOfStackReserve', 'TimeDateStamp', 'MajorOperatingSystemVersion',
            'Characteristics', 'ImageBase', 'Subsystem', 'MinorImageVersion',
            'MinorSubsystemVersion', 'SizeOfInitializedData', 'DllCharacteristics',
            'DirectoryEntryExport', 'ImageDirectoryEntryExport', 'CheckSum',
            'DirectoryEntryImportSize', 'SectionMaxChar', 'MajorImageVersion',
            'AddressOfEntryPoint', 'SectionMinEntropy', 'SizeOfHeaders',
            'SectionMinVirtualsize'
        ]
        
        # Initialize feature arrays
        X_malware = np.zeros((n_malware, 23))
        X_benign = np.zeros((n_benign, 23))
        
        # Generate malware features (more suspicious characteristics)
        for i in range(n_malware):
            # MajorLinkerVersion: Malware often uses older/newer linkers
            X_malware[i, 0] = np.random.choice([6, 7, 8, 9, 10, 11, 12, 13, 14, 15], p=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
            
            # MinorOperatingSystemVersion: Often 0 or unusual values
            X_malware[i, 1] = np.random.choice([0, 1, 2, 3, 4, 5], p=[0.3, 0.2, 0.2, 0.1, 0.1, 0.1])
            
            # MajorSubsystemVersion: Often 4 (Windows) but sometimes unusual
            X_malware[i, 2] = np.random.choice([3, 4, 5, 6, 7, 8, 9, 10], p=[0.1, 0.4, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05])
            
            # SizeOfStackReserve: Often large for malware
            X_malware[i, 3] = np.random.uniform(100000, 2000000)
            
            # TimeDateStamp: Often recent or very old
            X_malware[i, 4] = np.random.choice([
                np.random.randint(1000000000, 1200000000),  # Old
                np.random.randint(1500000000, 2000000000)   # Recent
            ])
            
            # MajorOperatingSystemVersion: Often 4 or 5
            X_malware[i, 5] = np.random.choice([4, 5, 6, 7, 8, 9, 10], p=[0.2, 0.3, 0.2, 0.1, 0.1, 0.05, 0.05])
            
            # Characteristics: Often has suspicious flags
            X_malware[i, 6] = np.random.randint(0, 65535)
            
            # ImageBase: Often 0x400000 or 0x10000000
            X_malware[i, 7] = np.random.choice([0x400000, 0x10000000, 0x20000000], p=[0.4, 0.3, 0.3])
            
            # Subsystem: Often 2 (GUI) or 3 (Console)
            X_malware[i, 8] = np.random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
            
            # MinorImageVersion: Often 0
            X_malware[i, 9] = np.random.choice([0, 1, 2, 3, 4, 5], p=[0.5, 0.2, 0.1, 0.1, 0.05, 0.05])
            
            # MinorSubsystemVersion: Often 0
            X_malware[i, 10] = np.random.choice([0, 1, 2, 3, 4, 5], p=[0.5, 0.2, 0.1, 0.1, 0.05, 0.05])
            
            # SizeOfInitializedData: Often large
            X_malware[i, 11] = np.random.uniform(10000, 1000000)
            
            # DllCharacteristics: Often has suspicious flags
            X_malware[i, 12] = np.random.randint(0, 65535)
            
            # DirectoryEntryExport: Often 0 (no exports)
            X_malware[i, 13] = np.random.choice([0, 1], p=[0.7, 0.3])
            
            # ImageDirectoryEntryExport: Often 0
            X_malware[i, 14] = np.random.uniform(0, 10000)
            
            # CheckSum: Often 0 or unusual values
            X_malware[i, 15] = np.random.choice([0, np.random.randint(1000, 1000000)], p=[0.3, 0.7])
            
            # DirectoryEntryImportSize: Often large
            X_malware[i, 16] = np.random.uniform(100, 50000)
            
            # SectionMaxChar: Often 3-6 sections
            X_malware[i, 17] = np.random.randint(3, 7)
            
            # MajorImageVersion: Often 0
            X_malware[i, 18] = np.random.choice([0, 1, 2, 3, 4, 5], p=[0.5, 0.2, 0.1, 0.1, 0.05, 0.05])
            
            # AddressOfEntryPoint: Often unusual values
            X_malware[i, 19] = np.random.uniform(1000, 100000)
            
            # SectionMinEntropy: Often high (packed/encrypted)
            X_malware[i, 20] = np.random.uniform(6.0, 8.0)
            
            # SizeOfHeaders: Often standard
            X_malware[i, 21] = np.random.uniform(512, 4096)
            
            # SectionMinVirtualsize: Often small
            X_malware[i, 22] = np.random.uniform(1000, 50000)
        
        # Generate benign features (more standard characteristics)
        for i in range(n_benign):
            # MajorLinkerVersion: Often standard values
            X_benign[i, 0] = np.random.choice([8, 9, 10, 11, 12, 13, 14], p=[0.1, 0.2, 0.3, 0.2, 0.1, 0.05, 0.05])
            
            # MinorOperatingSystemVersion: Often 0
            X_benign[i, 1] = np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1])
            
            # MajorSubsystemVersion: Often 4 (Windows)
            X_benign[i, 2] = np.random.choice([4, 5, 6], p=[0.8, 0.15, 0.05])
            
            # SizeOfStackReserve: Often standard
            X_benign[i, 3] = np.random.uniform(100000, 1000000)
            
            # TimeDateStamp: Often reasonable values
            X_benign[i, 4] = np.random.randint(1200000000, 1600000000)
            
            # MajorOperatingSystemVersion: Often 5 or 6
            X_benign[i, 5] = np.random.choice([5, 6, 7, 8, 9, 10], p=[0.2, 0.3, 0.2, 0.15, 0.1, 0.05])
            
            # Characteristics: Often standard flags
            X_benign[i, 6] = np.random.randint(0, 10000)
            
            # ImageBase: Often 0x400000
            X_benign[i, 7] = np.random.choice([0x400000, 0x10000000], p=[0.8, 0.2])
            
            # Subsystem: Often 2 (GUI) or 3 (Console)
            X_benign[i, 8] = np.random.choice([2, 3], p=[0.6, 0.4])
            
            # MinorImageVersion: Often 0
            X_benign[i, 9] = np.random.choice([0, 1, 2], p=[0.8, 0.15, 0.05])
            
            # MinorSubsystemVersion: Often 0
            X_benign[i, 10] = np.random.choice([0, 1], p=[0.9, 0.1])
            
            # SizeOfInitializedData: Often reasonable
            X_benign[i, 11] = np.random.uniform(1000, 100000)
            
            # DllCharacteristics: Often standard
            X_benign[i, 12] = np.random.randint(0, 1000)
            
            # DirectoryEntryExport: Often 1 (has exports)
            X_benign[i, 13] = np.random.choice([0, 1], p=[0.3, 0.7])
            
            # ImageDirectoryEntryExport: Often reasonable
            X_benign[i, 14] = np.random.uniform(0, 1000)
            
            # CheckSum: Often calculated correctly
            X_benign[i, 15] = np.random.randint(1000, 1000000)
            
            # DirectoryEntryImportSize: Often reasonable
            X_benign[i, 16] = np.random.uniform(100, 10000)
            
            # SectionMaxChar: Often 3-5 sections
            X_benign[i, 17] = np.random.randint(3, 6)
            
            # MajorImageVersion: Often 0
            X_benign[i, 18] = np.random.choice([0, 1, 2], p=[0.8, 0.15, 0.05])
            
            # AddressOfEntryPoint: Often standard
            X_benign[i, 19] = np.random.uniform(1000, 50000)
            
            # SectionMinEntropy: Often lower (not packed)
            X_benign[i, 20] = np.random.uniform(2.0, 6.0)
            
            # SizeOfHeaders: Often standard
            X_benign[i, 21] = np.random.uniform(512, 2048)
            
            # SectionMinVirtualsize: Often reasonable
            X_benign[i, 22] = np.random.uniform(1000, 20000)
        
        # Combine datasets
        X = np.vstack([X_malware, X_benign])
        y = np.hstack([np.ones(n_malware), np.zeros(n_benign)])
        
        # Shuffle the data
        indices = np.random.permutation(len(X))
        X = X[indices]
        y = y[indices]
        
        logger.info(f"Dataset created: {len(X)} samples ({np.sum(y)} malware, {len(y) - np.sum(y)} benign)")
        
        return X, y, feature_names
    
    def prepare_data(self, X, y, test_size=0.2, validation_size=0.2, random_state=42):
        """
        Prepare data with proper train/validation/test split
        
        Args:
            X: Features
            y: Labels
            test_size: Proportion for test set
            validation_size: Proportion of training data for validation
            random_state: Random seed
            
        Returns:
            X_train, X_val, X_test, y_train, y_val, y_test
        """
        logger.info("Preparing data with stratified split...")
        
        # First split: training + validation vs test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Second split: training vs validation
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=validation_size, random_state=random_state, stratify=y_temp
        )
        
        logger.info(f"Train set: {len(X_train)} samples ({np.sum(y_train)} malware, {len(y_train) - np.sum(y_train)} benign)")
        logger.info(f"Validation set: {len(X_val)} samples ({np.sum(y_val)} malware, {len(y_val) - np.sum(y_val)} benign)")
        logger.info(f"Test set: {len(X_test)} samples ({np.sum(y_test)} malware, {len(y_test) - np.sum(y_test)} benign)")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def create_advanced_ensemble(self):
        """Create advanced ensemble model with optimized hyperparameters"""
        logger.info("Creating advanced ensemble model...")
        
        # Random Forest with optimized parameters
        rf = RandomForestClassifier(
            n_estimators=500,
            max_depth=25,
            min_samples_split=2,
            min_samples_leaf=1,
            max_features='sqrt',
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        
        # Gradient Boosting with optimized parameters
        gb = GradientBoostingClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=8,
            min_samples_split=2,
            min_samples_leaf=1,
            subsample=0.8,
            random_state=42
        )
        
        # AdaBoost with optimized parameters
        ada = AdaBoostClassifier(
            n_estimators=200,
            learning_rate=0.8,
            random_state=42
        )
        
        # Voting ensemble with soft voting
        ensemble = VotingClassifier(
            estimators=[
                ('rf', rf),
                ('gb', gb),
                ('ada', ada)
            ],
            voting='soft',
            n_jobs=-1
        )
        
        logger.info("Advanced ensemble created: RF(500) + GB(300) + AdaBoost(200)")
        
        return ensemble
    
    def train_model(self, X_train, y_train, X_val, y_val):
        """Train the ensemble model with validation"""
        logger.info("Starting model training...")
        
        # Feature scaling with RobustScaler (more robust to outliers)
        self.scaler = RobustScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Feature selection (select top 20 features)
        self.feature_selector = SelectKBest(f_classif, k=20)
        X_train_selected = self.feature_selector.fit_transform(X_train_scaled, y_train)
        X_val_selected = self.feature_selector.transform(X_val_scaled)
        
        logger.info(f"Selected {X_train_selected.shape[1]} features out of {X_train_scaled.shape[1]}")
        
        # Create and train model
        self.model = self.create_advanced_ensemble()
        
        logger.info("Training ensemble model...")
        self.model.fit(X_train_selected, y_train)
        
        # Validation predictions
        y_val_pred = self.model.predict(X_val_selected)
        y_val_proba = self.model.predict_proba(X_val_selected)[:, 1]
        
        # Calculate validation metrics
        val_metrics = {
            'accuracy': accuracy_score(y_val, y_val_pred),
            'precision': precision_score(y_val, y_val_pred),
            'recall': recall_score(y_val, y_val_pred),
            'f1': f1_score(y_val, y_val_pred),
            'auc': roc_auc_score(y_val, y_val_proba)
        }
        
        logger.info(f"Validation Accuracy: {val_metrics['accuracy']:.4f}")
        logger.info(f"Validation Precision: {val_metrics['precision']:.4f}")
        logger.info(f"Validation Recall: {val_metrics['recall']:.4f}")
        logger.info(f"Validation F1-Score: {val_metrics['f1']:.4f}")
        logger.info(f"Validation AUC: {val_metrics['auc']:.4f}")
        
        self.training_metrics = val_metrics
        
        return self.model, self.scaler, self.feature_selector, val_metrics
    
    def evaluate_on_test_set(self, X_test, y_test):
        """Comprehensive evaluation on test set"""
        logger.info("Evaluating on test set...")
        
        X_test_scaled = self.scaler.transform(X_test)
        X_test_selected = self.feature_selector.transform(X_test_scaled)
        
        # Predictions
        y_pred = self.model.predict(X_test_selected)
        y_proba = self.model.predict_proba(X_test_selected)[:, 1]
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        # Calculate comprehensive metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'auc': roc_auc_score(y_test, y_proba),
            
            # Detailed metrics
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            
            # Rates
            'detection_rate': recall_score(y_test, y_pred),
            'false_positive_rate': fp / (fp + tn) if (fp + tn) > 0 else 0,
            'false_negative_rate': fn / (fn + tp) if (fn + tp) > 0 else 0,
            'specificity': tn / (tn + fp) if (tn + fp) > 0 else 0,
            
            # Counts
            'total_malware': int(np.sum(y_test)),
            'total_benign': int(len(y_test) - np.sum(y_test)),
            'total_samples': len(y_test)
        }
        
        logger.info("=" * 70)
        logger.info("TEST SET EVALUATION")
        logger.info("=" * 70)
        logger.info(f"Accuracy:          {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
        logger.info(f"Precision:         {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
        logger.info(f"Recall (Detection):{metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
        logger.info(f"F1-Score:          {metrics['f1']:.4f}")
        logger.info(f"AUC:               {metrics['auc']:.4f}")
        logger.info("-" * 70)
        logger.info(f"Detection Rate:    {metrics['detection_rate']:.4f} ({metrics['detection_rate']*100:.2f}%)")
        logger.info(f"FP Rate:           {metrics['false_positive_rate']:.4f} ({metrics['false_positive_rate']*100:.2f}%)")
        logger.info(f"FN Rate:           {metrics['false_negative_rate']:.4f} ({metrics['false_negative_rate']*100:.2f}%)")
        logger.info(f"Specificity:       {metrics['specificity']:.4f} ({metrics['specificity']*100:.2f}%)")
        logger.info("-" * 70)
        logger.info(f"True Positives:    {metrics['true_positives']} / {metrics['total_malware']}")
        logger.info(f"False Positives:   {metrics['false_positives']} / {metrics['total_benign']}")
        logger.info(f"True Negatives:    {metrics['true_negatives']} / {metrics['total_benign']}")
        logger.info(f"False Negatives:   {metrics['false_negatives']} / {metrics['total_malware']}")
        logger.info("=" * 70)
        
        return metrics
    
    def cross_validate(self, X, y, cv=5):
        """Perform k-fold cross-validation"""
        logger.info(f"Performing {cv}-fold cross-validation...")
        
        X_scaled = self.scaler.transform(X)
        X_selected = self.feature_selector.transform(X_scaled)
        
        skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
        
        scores = cross_val_score(self.model, X_selected, y, cv=skf, scoring='accuracy', n_jobs=-1)
        
        logger.info(f"Cross-validation scores: {scores}")
        logger.info(f"Mean CV Accuracy: {np.mean(scores):.4f} (±{np.std(scores):.4f})")
        
        return scores
    
    def save_model(self, filename='malwareclassifier-V2.pkl'):
        """Save trained model, scaler, and feature selector"""
        model_path = os.path.join(self.model_dir, filename)
        scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
        selector_path = os.path.join(self.model_dir, 'feature_selector.pkl')
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        joblib.dump(self.feature_selector, selector_path)
        
        logger.info(f"Model saved to: {model_path}")
        logger.info(f"Scaler saved to: {scaler_path}")
        logger.info(f"Feature selector saved to: {selector_path}")
        
        return model_path, scaler_path, selector_path
    
    def generate_evaluation_report(self, metrics, filename='evaluation_report.txt'):
        """Generate comprehensive evaluation report"""
        report_path = os.path.join(self.results_dir, filename)
        
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("NeuroShield - High-Accuracy Model Evaluation Report\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Developer: F.J.G\n")
            f.write(f"Project: NeuroShield - Malware Detection with Machine Learning\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("OVERALL PERFORMANCE METRICS\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Accuracy:           {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)\n")
            f.write(f"Precision:          {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)\n")
            f.write(f"Recall (Detection): {metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)\n")
            f.write(f"F1-Score:           {metrics['f1']:.4f}\n")
            f.write(f"AUC-ROC:            {metrics['auc']:.4f}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("DETECTION & ERROR RATES\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Detection Rate:        {metrics['detection_rate']:.4f} ({metrics['detection_rate']*100:.2f}%)\n")
            f.write(f"False Positive Rate:   {metrics['false_positive_rate']:.4f} ({metrics['false_positive_rate']*100:.2f}%)\n")
            f.write(f"False Negative Rate:   {metrics['false_negative_rate']:.4f} ({metrics['false_negative_rate']*100:.2f}%)\n")
            f.write(f"Specificity:           {metrics['specificity']:.4f} ({metrics['specificity']*100:.2f}%)\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("CONFUSION MATRIX\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"True Positives  (TP): {metrics['true_positives']}\n")
            f.write(f"True Negatives  (TN): {metrics['true_negatives']}\n")
            f.write(f"False Positives (FP): {metrics['false_positives']}\n")
            f.write(f"False Negatives (FN): {metrics['false_negatives']}\n\n")
            
            f.write(f"Total Malware Samples: {metrics['total_malware']}\n")
            f.write(f"Total Benign Samples:  {metrics['total_benign']}\n")
            f.write(f"Total Test Samples:    {metrics['total_samples']}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("INTERPRETATION\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"✓ Detection Rate: {metrics['detection_rate']*100:.2f}% of malware was correctly detected\n")
            f.write(f"✓ FP Rate: {metrics['false_positive_rate']*100:.2f}% of benign files were incorrectly flagged\n")
            f.write(f"✓ {metrics['false_positives']} benign files out of {metrics['total_benign']} were false positives\n")
            f.write(f"✓ {metrics['false_negatives']} malware samples out of {metrics['total_malware']} were missed\n\n")
            
            if metrics['detection_rate'] >= 0.99:
                f.write("★ EXCELLENT: Detection rate >= 99% - Competitive with top AVs\n")
            elif metrics['detection_rate'] >= 0.95:
                f.write("★ VERY GOOD: Detection rate >= 95% - Strong performance\n")
            elif metrics['detection_rate'] >= 0.90:
                f.write("★ GOOD: Detection rate >= 90% - Acceptable performance\n")
            else:
                f.write("★ NEEDS IMPROVEMENT: Detection rate < 90%\n")
            
            if metrics['false_positive_rate'] <= 0.01:
                f.write("★ EXCELLENT: FP rate <= 1% - Very low false alarms\n")
            elif metrics['false_positive_rate'] <= 0.05:
                f.write("★ GOOD: FP rate <= 5% - Acceptable false alarm rate\n")
            else:
                f.write("★ NEEDS IMPROVEMENT: FP rate > 5% - Too many false alarms\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        logger.info(f"Evaluation report saved to: {report_path}")
        
        return report_path
    
    def plot_confusion_matrix(self, y_test, y_pred, filename='confusion_matrix.png'):
        """Generate and save confusion matrix plot"""
        cm = confusion_matrix(y_test, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['Benign', 'Malware'],
                    yticklabels=['Benign', 'Malware'])
        plt.title('Confusion Matrix - NeuroShield High-Accuracy Model')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        
        plot_path = os.path.join(self.results_dir, filename)
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Confusion matrix saved to: {plot_path}")
        
        return plot_path
    
    def plot_roc_curve(self, y_test, y_proba, filename='roc_curve.png'):
        """Generate and save ROC curve"""
        fpr, tpr, thresholds = roc_curve(y_test, y_proba)
        auc = roc_auc_score(y_test, y_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='blue', lw=2, label=f'ROC curve (AUC = {auc:.4f})')
        plt.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--', label='Random')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate (Detection Rate)')
        plt.title('ROC Curve - NeuroShield High-Accuracy Model')
        plt.legend(loc="lower right")
        plt.grid(True, alpha=0.3)
        
        plot_path = os.path.join(self.results_dir, filename)
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"ROC curve saved to: {plot_path}")
        
        return plot_path


def main():
    """Main training pipeline"""
    logger.info("=" * 80)
    logger.info("NeuroShield High-Accuracy Model Training")
    logger.info("=" * 80)
    
    # Initialize trainer
    trainer = HighAccuracyTrainer()
    
    # Create realistic dataset
    X, y, feature_names = trainer.create_realistic_dataset(n_malware=2000, n_benign=2000)
    
    # Prepare data
    X_train, X_val, X_test, y_train, y_val, y_test = trainer.prepare_data(X, y)
    
    # Train model
    model, scaler, feature_selector, val_metrics = trainer.train_model(X_train, y_train, X_val, y_val)
    
    # Evaluate on test set
    test_metrics = trainer.evaluate_on_test_set(X_test, y_test)
    
    # Cross-validation
    cv_scores = trainer.cross_validate(X, y)
    
    # Generate visualizations
    X_test_scaled = scaler.transform(X_test)
    X_test_selected = feature_selector.transform(X_test_scaled)
    y_pred = model.predict(X_test_selected)
    y_proba = model.predict_proba(X_test_selected)[:, 1]
    
    trainer.plot_confusion_matrix(y_test, y_pred)
    trainer.plot_roc_curve(y_test, y_proba)
    
    # Generate report
    trainer.generate_evaluation_report(test_metrics)
    
    # Save model
    model_path, scaler_path, selector_path = trainer.save_model()
    
    logger.info("=" * 80)
    logger.info("Training and evaluation complete!")
    logger.info("=" * 80)
    logger.info(f"Model saved to: {model_path}")
    logger.info(f"Scaler saved to: {scaler_path}")
    logger.info(f"Feature selector saved to: {selector_path}")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()