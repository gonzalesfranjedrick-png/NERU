"""
NeuroShield Advanced Training System
Professional-grade ML training with public datasets and proper evaluation

Developer: F.J.G
Project: NeuroShield - Malware Detection with Machine Learning
"""

import os
import numpy as np
import pandas as pd
import joblib
import logging
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns
from feature_extraction import extract_features
import glob

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AdvancedTrainer:
    """Professional training system for NeuroShield"""
    
    def __init__(self, model_dir='ML_model', results_dir='evaluation_results'):
        """Initialize the advanced trainer"""
        self.model_dir = model_dir
        self.results_dir = results_dir
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(results_dir, exist_ok=True)
        
        self.model = None
        self.scaler = None
        self.training_history = []
        
        logging.info("AdvancedTrainer initialized")
    
    def load_dataset_from_directory(self, malware_dir, benign_dir, limit=None):
        """
        Load dataset from directories of malware and benign files
        
        Args:
            malware_dir: Directory containing malware samples
            benign_dir: Directory containing benign samples
            limit: Maximum files to load per class (None = all)
            
        Returns:
            X (features), y (labels)
        """
        logging.info("Loading dataset from directories...")
        
        X = []
        y = []
        
        # Load malware samples
        malware_files = glob.glob(os.path.join(malware_dir, '*'))[:limit]
        logging.info(f"Processing {len(malware_files)} malware samples...")
        
        for i, file_path in enumerate(malware_files):
            try:
                features = extract_features(file_path)
                X.append(features[0])
                y.append(1)  # Malware
                
                if (i + 1) % 100 == 0:
                    logging.info(f"Processed {i + 1}/{len(malware_files)} malware files")
            except Exception as e:
                logging.warning(f"Error processing {file_path}: {e}")
        
        # Load benign samples
        benign_files = glob.glob(os.path.join(benign_dir, '*'))[:limit]
        logging.info(f"Processing {len(benign_files)} benign samples...")
        
        for i, file_path in enumerate(benign_files):
            try:
                features = extract_features(file_path)
                X.append(features[0])
                y.append(0)  # Benign
                
                if (i + 1) % 100 == 0:
                    logging.info(f"Processed {i + 1}/{len(benign_files)} benign files")
            except Exception as e:
                logging.warning(f"Error processing {file_path}: {e}")
        
        X = np.array(X)
        y = np.array(y)
        
        logging.info(f"Dataset loaded: {len(X)} samples ({np.sum(y)} malware, {len(y) - np.sum(y)} benign)")
        
        return X, y
    
    def prepare_data(self, X, y, test_size=0.3, validation_size=0.15, random_state=42):
        """
        Prepare data with proper train/validation/test split (NO DATA LEAKAGE)
        
        Args:
            X: Features
            y: Labels
            test_size: Proportion for test set
            validation_size: Proportion of training data for validation
            random_state: Random seed for reproducibility
            
        Returns:
            X_train, X_val, X_test, y_train, y_val, y_test
        """
        logging.info("Preparing data with stratified split (no data leakage)...")
        
        # First split: training + validation vs test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Second split: training vs validation
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=validation_size, random_state=random_state, stratify=y_temp
        )
        
        logging.info(f"Train set: {len(X_train)} samples ({np.sum(y_train)} malware, {len(y_train) - np.sum(y_train)} benign)")
        logging.info(f"Validation set: {len(X_val)} samples ({np.sum(y_val)} malware, {len(y_val) - np.sum(y_val)} benign)")
        logging.info(f"Test set: {len(X_test)} samples ({np.sum(y_test)} malware, {len(y_test) - np.sum(y_test)} benign)")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def create_advanced_ensemble(self):
        """
        Create state-of-the-art ensemble model
        
        Returns:
            VotingClassifier with multiple strong learners
        """
        logging.info("Creating advanced ensemble model...")
        
        # Individual models with optimized hyperparameters
        rf = RandomForestClassifier(
            n_estimators=300,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        )
        
        gb = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=7,
            min_samples_split=5,
            min_samples_leaf=2,
            subsample=0.8,
            random_state=42
        )
        
        ada = AdaBoostClassifier(
            n_estimators=150,
            learning_rate=1.0,
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
        
        logging.info("Advanced ensemble created: RF(300) + GB(200) + AdaBoost(150)")
        
        return ensemble
    
    def train_model(self, X_train, y_train, X_val, y_val):
        """
        Train the ensemble model with validation
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            
        Returns:
            Trained model, scaler, training metrics
        """
        logging.info("Starting model training...")
        
        # Feature scaling
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Create and train model
        self.model = self.create_advanced_ensemble()
        
        logging.info("Training ensemble model...")
        self.model.fit(X_train_scaled, y_train)
        
        # Validation predictions
        y_val_pred = self.model.predict(X_val_scaled)
        y_val_proba = self.model.predict_proba(X_val_scaled)[:, 1]
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_val, y_val_pred),
            'precision': precision_score(y_val, y_val_pred),
            'recall': recall_score(y_val, y_val_pred),
            'f1': f1_score(y_val, y_val_pred),
            'auc': roc_auc_score(y_val, y_val_proba)
        }
        
        logging.info(f"Validation Accuracy: {metrics['accuracy']:.4f}")
        logging.info(f"Validation Precision: {metrics['precision']:.4f}")
        logging.info(f"Validation Recall: {metrics['recall']:.4f}")
        logging.info(f"Validation F1-Score: {metrics['f1']:.4f}")
        logging.info(f"Validation AUC: {metrics['auc']:.4f}")
        
        return self.model, self.scaler, metrics
    
    def evaluate_on_test_set(self, X_test, y_test):
        """
        Comprehensive evaluation on test set (unseen data)
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Comprehensive evaluation metrics
        """
        logging.info("Evaluating on test set (completely unseen data)...")
        
        X_test_scaled = self.scaler.transform(X_test)
        
        # Predictions
        y_pred = self.model.predict(X_test_scaled)
        y_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        # Calculate comprehensive metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),  # Detection rate
            'f1': f1_score(y_test, y_pred),
            'auc': roc_auc_score(y_test, y_proba),
            
            # Detailed metrics
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            
            # Rates
            'detection_rate': recall_score(y_test, y_pred),  # Same as recall
            'false_positive_rate': fp / (fp + tn) if (fp + tn) > 0 else 0,
            'false_negative_rate': fn / (fn + tp) if (fn + tp) > 0 else 0,
            'specificity': tn / (tn + fp) if (tn + fp) > 0 else 0,
            
            # Counts
            'total_malware': int(np.sum(y_test)),
            'total_benign': int(len(y_test) - np.sum(y_test)),
            'total_samples': len(y_test)
        }
        
        logging.info("=" * 70)
        logging.info("TEST SET EVALUATION (COMPLETELY UNSEEN DATA)")
        logging.info("=" * 70)
        logging.info(f"Accuracy:          {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
        logging.info(f"Precision:         {metrics['precision']:.4f} ({metrics['precision']*100:.2f}%)")
        logging.info(f"Recall (Detection):{metrics['recall']:.4f} ({metrics['recall']*100:.2f}%)")
        logging.info(f"F1-Score:          {metrics['f1']:.4f}")
        logging.info(f"AUC:               {metrics['auc']:.4f}")
        logging.info("-" * 70)
        logging.info(f"Detection Rate:    {metrics['detection_rate']:.4f} ({metrics['detection_rate']*100:.2f}%)")
        logging.info(f"FP Rate:           {metrics['false_positive_rate']:.4f} ({metrics['false_positive_rate']*100:.2f}%)")
        logging.info(f"FN Rate:           {metrics['false_negative_rate']:.4f} ({metrics['false_negative_rate']*100:.2f}%)")
        logging.info(f"Specificity:       {metrics['specificity']:.4f} ({metrics['specificity']*100:.2f}%)")
        logging.info("-" * 70)
        logging.info(f"True Positives:    {metrics['true_positives']} / {metrics['total_malware']}")
        logging.info(f"False Positives:   {metrics['false_positives']} / {metrics['total_benign']}")
        logging.info(f"True Negatives:    {metrics['true_negatives']} / {metrics['total_benign']}")
        logging.info(f"False Negatives:   {metrics['false_negatives']} / {metrics['total_malware']}")
        logging.info("=" * 70)
        
        return metrics
    
    def cross_validate(self, X, y, cv=5):
        """
        Perform k-fold cross-validation
        
        Args:
            X: Features
            y: Labels
            cv: Number of folds
            
        Returns:
            Cross-validation scores
        """
        logging.info(f"Performing {cv}-fold cross-validation...")
        
        X_scaled = self.scaler.transform(X) if self.scaler else StandardScaler().fit_transform(X)
        
        skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
        
        scores = cross_val_score(self.model, X_scaled, y, cv=skf, scoring='accuracy', n_jobs=-1)
        
        logging.info(f"Cross-validation scores: {scores}")
        logging.info(f"Mean CV Accuracy: {np.mean(scores):.4f} (±{np.std(scores):.4f})")
        
        return scores
    
    def save_model(self, filename='malwareclassifier-V3.pkl'):
        """Save trained model and scaler"""
        model_path = os.path.join(self.model_dir, filename)
        scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        logging.info(f"Model saved to: {model_path}")
        logging.info(f"Scaler saved to: {scaler_path}")
        
        return model_path, scaler_path
    
    def generate_evaluation_report(self, metrics, filename='evaluation_report.txt'):
        """Generate comprehensive evaluation report"""
        report_path = os.path.join(self.results_dir, filename)
        
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("NeuroShield - Advanced Model Evaluation Report\n")
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
        
        logging.info(f"Evaluation report saved to: {report_path}")
        
        return report_path
    
    def plot_confusion_matrix(self, y_test, y_pred, filename='confusion_matrix.png'):
        """Generate and save confusion matrix plot"""
        cm = confusion_matrix(y_test, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=['Benign', 'Malware'],
                    yticklabels=['Benign', 'Malware'])
        plt.title('Confusion Matrix - NeuroShield')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        
        plot_path = os.path.join(self.results_dir, filename)
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.info(f"Confusion matrix saved to: {plot_path}")
        
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
        plt.title('ROC Curve - NeuroShield')
        plt.legend(loc="lower right")
        plt.grid(True, alpha=0.3)
        
        plot_path = os.path.join(self.results_dir, filename)
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.info(f"ROC curve saved to: {plot_path}")
        
        return plot_path


def main():
    """Main training pipeline"""
    logging.info("=" * 80)
    logging.info("NeuroShield Advanced Training System")
    logging.info("=" * 80)
    
    # Initialize trainer
    trainer = AdvancedTrainer()
    
    # NOTE: Replace these paths with your actual dataset paths
    # You should use public benchmark datasets like:
    # - VirusShare
    # - MalwareBazaar
    # - EMBER dataset
    # - Sorel-20M
    # - CIC-MalMem-2022
    
    malware_dir = 'datasets/malware'
    benign_dir = 'datasets/benign'
    
    # For demonstration, we'll use synthetic data
    # REPLACE THIS WITH ACTUAL DATA LOADING
    logging.info("Creating synthetic dataset for demonstration...")
    logging.info("⚠️  IMPORTANT: Replace with actual public benchmark datasets!")
    
    # Synthetic data (replace with real data)
    np.random.seed(42)
    X_malware = np.random.randn(500, 23) + np.array([1, 2, 3, 1, 2, 1, 3, 2, 1, 2, 3, 1, 2, 3, 1, 2, 1, 3, 2, 1, 2, 3, 1])
    X_benign = np.random.randn(500, 23)
    X = np.vstack([X_malware, X_benign])
    y = np.array([1] * 500 + [0] * 500)
    
    # Prepare data
    X_train, X_val, X_test, y_train, y_val, y_test = trainer.prepare_data(X, y)
    
    # Train model
    model, scaler, val_metrics = trainer.train_model(X_train, y_train, X_val, y_val)
    
    # Evaluate on test set
    test_metrics = trainer.evaluate_on_test_set(X_test, y_test)
    
    # Cross-validation
    cv_scores = trainer.cross_validate(X, y)
    
    # Generate visualizations
    X_test_scaled = scaler.transform(X_test)
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    trainer.plot_confusion_matrix(y_test, y_pred)
    trainer.plot_roc_curve(y_test, y_proba)
    
    # Generate report
    trainer.generate_evaluation_report(test_metrics)
    
    # Save model
    trainer.save_model()
    
    logging.info("=" * 80)
    logging.info("Training and evaluation complete!")
    logging.info("=" * 80)


if __name__ == '__main__':
    main()
