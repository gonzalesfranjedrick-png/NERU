# ⚠️ Port 5500 vs 5000 - Fix Instructions

## Problem
You're seeing port **5500** but NeuroShield runs on port **5000**.

---

## Cause
**VS Code Live Server** is running on port 5500 (for static HTML files).  
**Flask (NeuroShield)** is running on port 5000 (the real app).

---

## ✅ Solution

### Step 1: Stop Live Server
In VS Code:
- Look at bottom status bar
- If you see "Port: 5500" or "Go Live" → **Click to stop**
- Or: `Ctrl+Shift+P` → "Live Server: Stop"

### Step 2: Access Correct Port
**Open browser and type:**
```
http://127.0.0.1:5000
```

**NOT:** `http://127.0.0.1:5500` ❌

---

## Why Port 5000?

**Port 5500 (Live Server):**
- Shows static HTML files only
- Cannot handle file uploads
- Cannot run Python/Flask code
- Will give "405 Method Not Allowed" errors

**Port 5000 (Flask App):**
- Full NeuroShield application
- Handles file uploads ✅
- Runs malware detection ✅
- Quarantine/clean features work ✅

---

## How to Avoid This

### ❌ DON'T:
- Right-click HTML files → "Open with Live Server"
- Click "Go Live" in VS Code
- Run HTML files from VS Code file explorer

### ✅ DO:
1. Open your browser
2. Type: `http://127.0.0.1:5000`
3. Press Enter

---

## Verify Flask is Running

Check if Flask responds on port 5000:
```bash
curl http://127.0.0.1:5000
```

You should see HTML starting with:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>NeuroShield - AI-Powered Malware Detection</title>
```

If you see this → Flask is working! ✅

---

## Still Not Working?

1. **Check Flask is running:**
   ```bash
   ps aux | grep "python3 app.py"
   ```

2. **Restart Flask if needed:**
   ```bash
   cd /workspace/ML_based_detectionn
   python3 app.py
   ```

3. **Use incognito/private browser window** (clears cache)

4. **Hard refresh browser:** `Ctrl+Shift+R` or `Ctrl+F5`

---

## Summary

✅ Flask is running on port 5000  
✅ Just access: `http://127.0.0.1:5000`  
✅ Don't use Live Server (port 5500)

**Developed by F.J.G**  
**© 2025 NeuroShield**
