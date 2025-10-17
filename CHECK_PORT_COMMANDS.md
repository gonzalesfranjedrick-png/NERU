# 🔍 Commands to Check if Port 5000 is Running

**Quick reference guide for checking NeuroShield on port 5000**

---

## ✅ **COMMAND 1: Check if Flask App is Running**

```bash
ps aux | grep "python3 app.py"
```

**What to expect:**
- ✅ **If running:** You'll see a line like:
  ```
  ubuntu  36225  0.0  1.0  560168 167176 ?  Sl  Oct09  0:03 python3 app.py
  ```
- ❌ **If NOT running:** Empty output or only the grep command

---

## ✅ **COMMAND 2: Check What's Listening on Port 5000**

```bash
lsof -i :5000
```

**What to expect:**
- ✅ **If running:** Shows Python process
  ```
  COMMAND   PID    USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
  python3  36225 ubuntu    4u  IPv4 123456      0t0  TCP *:5000 (LISTEN)
  ```
- ❌ **If NOT running:** Empty output or "command not found"

**Alternative (if lsof not available):**
```bash
python3 -c "import socket; s = socket.socket(); result = s.connect_ex(('127.0.0.1', 5000)); print('✅ Port 5000 is OPEN' if result == 0 else '❌ Port 5000 is CLOSED'); s.close()"
```

---

## ✅ **COMMAND 3: Test if Port 5000 Responds**

```bash
curl http://127.0.0.1:5000
```

**What to expect:**
- ✅ **If working:** HTML code output:
  ```html
  <!DOCTYPE html>
  <html lang="en">
  <head>
      <title>NeuroShield - AI-Powered Malware Detection</title>
  ...
  ```
- ❌ **If NOT working:** 
  ```
  curl: (7) Failed to connect to 127.0.0.1 port 5000: Connection refused
  ```

**Shorter version (just check status):**
```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5000
```
- Returns `200` if working ✅
- Returns `000` or error if not working ❌

---

## ✅ **COMMAND 4: Check App Logs**

```bash
tail -20 /tmp/neuroshield_competitive.log
```

**What to expect:**
- ✅ **If running:** Should show:
  ```
  * Running on all addresses (0.0.0.0)
  * Running on http://127.0.0.1:5000
  * Running on http://172.30.0.2:5000
  ```

**View live logs (real-time):**
```bash
tail -f /tmp/neuroshield_competitive.log
```
(Press `Ctrl+C` to stop)

---

## 🔄 **COMMAND 5: Check All Listening Ports**

```bash
lsof -i -P -n | grep LISTEN
```

**Look for:**
```
python3   36225  ubuntu    4u  IPv4  *:5000 (LISTEN)
```

---

## 📊 **ALL-IN-ONE CHECK COMMAND**

Run everything at once:

```bash
echo "=== Flask Process ===" && \
ps aux | grep "python3 app.py" | grep -v grep && \
echo "" && \
echo "=== Port 5000 Test ===" && \
curl -s http://127.0.0.1:5000 | head -3 && \
echo "..." && \
echo "✅ Port 5000 is responding!" && \
echo "" && \
echo "=== Recent Logs ===" && \
tail -10 /tmp/neuroshield_competitive.log
```

---

## 🛠️ **IF PORT 5000 IS NOT RUNNING**

### Start the Flask App:
```bash
cd /workspace/ML_based_detectionn
python3 app.py
```

### Or start in background:
```bash
cd /workspace/ML_based_detectionn
nohup python3 app.py > /tmp/neuroshield.log 2>&1 &
```

### Check it started:
```bash
tail -20 /tmp/neuroshield.log
```

---

## 🎯 **QUICK REFERENCE**

| What to Check | Command | Expected Output |
|---------------|---------|-----------------|
| **Process running?** | `ps aux \| grep "python3 app.py"` | See Python process ✅ |
| **Port open?** | `lsof -i :5000` | See LISTEN on 5000 ✅ |
| **App responding?** | `curl http://127.0.0.1:5000` | See HTML output ✅ |
| **Check logs** | `tail -20 /tmp/neuroshield_competitive.log` | See "Running on..." ✅ |

---

## ✅ **SUMMARY**

**These 3 commands tell you everything:**

1. **Is the process running?**
   ```bash
   ps aux | grep "python3 app.py"
   ```

2. **Is port 5000 responding?**
   ```bash
   curl -s http://127.0.0.1:5000 | head -5
   ```

3. **What do the logs say?**
   ```bash
   tail -20 /tmp/neuroshield_competitive.log
   ```

If all three work → **Port 5000 is running correctly!** ✅

---

**Developed by F.J.G**  
**© 2025 NeuroShield**
