# 🚀 How to Run NeuroShield on Port 5000

**Quick guide to starting NeuroShield**

---

## ⚡ **QUICKEST WAY (Already Running!)**

**NeuroShield is already running on port 5000!**

Just open your browser and go to:
```
http://127.0.0.1:5000
```

---

## 🔧 **IF YOU NEED TO START IT:**

### **Option 1: Simple Start (Foreground)**

```bash
cd /workspace/ML_based_detectionn
python3 app.py
```

**What happens:**
- App starts on port 5000
- You see output in terminal
- Press `Ctrl+C` to stop

**You'll see:**
```
* Running on http://127.0.0.1:5000
* Running on http://172.30.0.2:5000
```

---

### **Option 2: Background Mode (Recommended)**

```bash
cd /workspace/ML_based_detectionn
nohup python3 app.py > /tmp/neuroshield.log 2>&1 &
```

**What happens:**
- App runs in background
- Logs saved to `/tmp/neuroshield.log`
- Terminal is free for other commands
- Keeps running if you close terminal

**Check it started:**
```bash
tail -10 /tmp/neuroshield.log
```

---

### **Option 3: Use Startup Script (Easiest!)**

```bash
bash /workspace/START_NEUROSHIELD.sh
```

**What happens:**
- Checks if already running
- Starts app in background
- Shows status and access URL
- Provides useful commands

---

## 🔄 **RESTART THE APP**

### **Method 1: Kill and Restart**
```bash
pkill -f "python3 app.py"
cd /workspace/ML_based_detectionn
python3 app.py
```

### **Method 2: One-line Restart**
```bash
pkill -f "python3 app.py" && sleep 2 && cd /workspace/ML_based_detectionn && nohup python3 app.py > /tmp/neuroshield.log 2>&1 &
```

---

## 🛑 **STOP THE APP**

```bash
pkill -f "python3 app.py"
```

**Or if you know the process ID:**
```bash
kill 36225
```

---

## 📊 **CHECK IF RUNNING**

```bash
# Check process
ps aux | grep "python3 app.py"

# Test port
curl http://127.0.0.1:5000

# View logs
tail -20 /tmp/neuroshield.log
```

---

## 🎯 **COMPLETE WORKFLOW**

### **Starting Fresh:**
```bash
# 1. Stop any running instance
pkill -f "python3 app.py"

# 2. Wait a moment
sleep 2

# 3. Go to app directory
cd /workspace/ML_based_detectionn

# 4. Start in background
nohup python3 app.py > /tmp/neuroshield.log 2>&1 &

# 5. Check logs
tail -10 /tmp/neuroshield.log

# 6. Test it works
curl -s http://127.0.0.1:5000 | head -5
```

---

## 🔍 **VERIFY IT'S ON PORT 5000**

**After starting, run:**
```bash
# Should show "Running on http://127.0.0.1:5000"
tail /tmp/neuroshield.log | grep "Running on"
```

**Expected output:**
```
* Running on http://127.0.0.1:5000
```

---

## ⚙️ **ADVANCED: SPECIFY PORT MANUALLY**

**If you want to change the port:**

```bash
cd /workspace/ML_based_detectionn
export FLASK_PORT=5000
python3 app.py
```

**Or edit the code:**
```python
# In app.py, change:
port = int(os.getenv('FLASK_PORT', 5000))
```

---

## 🎯 **RECOMMENDED COMMAND**

**For most users, use this:**

```bash
cd /workspace/ML_based_detectionn && nohup python3 app.py > /tmp/neuroshield.log 2>&1 & echo "Started! Check: tail -f /tmp/neuroshield.log"
```

**Then access:**
```
http://127.0.0.1:5000
```

---

## ✅ **SUMMARY**

### **To Start:**
```bash
cd /workspace/ML_based_detectionn
python3 app.py
```

### **To Start in Background:**
```bash
cd /workspace/ML_based_detectionn
nohup python3 app.py > /tmp/neuroshield.log 2>&1 &
```

### **To Stop:**
```bash
pkill -f "python3 app.py"
```

### **To Access:**
```
http://127.0.0.1:5000
```

---

**Developed by F.J.G**  
**© 2025 NeuroShield**
