# 🚀 NeuroShield - Quick Run Guide

**How to run everything in NeuroShield**

---

## ✅ **MAIN APP (Already Running!)**

### **Access the Web Interface:**
```
http://127.0.0.1:5000
```

### **Features:**
- ✅ Upload & analyze files (.exe, .dll, .txt, .pdf)
- ✅ Quarantine malicious files
- ✅ Clean infected files
- ✅ Quarantine manager

### **If NOT running, start with:**
```bash
cd /workspace/ML_based_detectionn
python3 app.py
```

---

## 🧪 **PROFESSIONAL EVALUATION SYSTEM**

### **Quick Demo (Recommended First!):**
```bash
cd /workspace/ML_based_detectionn
python3 demo_professional_system.py
```

**What it does:**
- Trains advanced model
- Evaluates on test data
- Generates reports & charts
- Benchmarks vs commercial AVs

**Takes:** ~30 seconds

**Output:**
- `evaluation_results/evaluation_report.txt`
- `evaluation_results/confusion_matrix.png`
- `evaluation_results/roc_curve.png`
- `benchmark_results/benchmark_report.txt`
- `benchmark_results/benchmark_comparison.png`

---

### **Individual Components:**

**1. Advanced Training:**
```bash
cd /workspace/ML_based_detectionn
python3 advanced_training.py
```

**2. Benchmarking:**
```bash
cd /workspace/ML_based_detectionn
python3 benchmark_system.py
```

**3. False Positive Testing:**
```bash
cd /workspace/ML_based_detectionn
python3 false_positive_tester.py
```

---

## 📊 **View Results:**

**Evaluation Report:**
```bash
cat /workspace/ML_based_detectionn/evaluation_results/evaluation_report.txt
```

**Benchmark Report:**
```bash
cat /workspace/ML_based_detectionn/benchmark_results/benchmark_report.txt
```

**List all results:**
```bash
ls -la /workspace/ML_based_detectionn/evaluation_results/
ls -la /workspace/ML_based_detectionn/benchmark_results/
```

---

## 🎯 **RECOMMENDED WORKFLOW**

### **For General Use (Detection & Removal):**
1. Open browser: `http://127.0.0.1:5000`
2. Upload files to scan
3. Use quarantine/clean/delete features

### **For Professional Evaluation:**
1. Run demo: `python3 demo_professional_system.py`
2. Review reports in `evaluation_results/` and `benchmark_results/`
3. (Optional) Download real datasets and retrain

### **For Production Deployment:**
1. See: `PROFESSIONAL_GRADE_UPGRADE.md`
2. Download public datasets (EMBER, VirusShare)
3. Train with real data
4. Test FP rate
5. Benchmark vs commercial AVs

---

## 📁 **File Locations:**

**Main App:**
- `/workspace/ML_based_detectionn/app.py`

**Professional System:**
- `/workspace/ML_based_detectionn/advanced_training.py`
- `/workspace/ML_based_detectionn/benchmark_system.py`
- `/workspace/ML_based_detectionn/false_positive_tester.py`
- `/workspace/ML_based_detectionn/demo_professional_system.py`

**Results:**
- `/workspace/ML_based_detectionn/evaluation_results/`
- `/workspace/ML_based_detectionn/benchmark_results/`
- `/workspace/ML_based_detectionn/ML_model/`

**Documentation:**
- `/workspace/PROFESSIONAL_GRADE_UPGRADE.md`
- `/workspace/COMPLETE_UPGRADE_SUMMARY.md`
- `/workspace/VIRUS_REMOVAL_COMPLETE.md`
- `/workspace/QUICK_START_GUIDE.md`

---

**Developed by F.J.G**  
**© 2025 NeuroShield. All Rights Reserved.**
