# 🚀 NeuroShield - Quick Start Guide

**Virus Removal & Quarantine System**  
**Developer:** F.J.G  
**© 2025 NeuroShield. All Rights Reserved.**

---

## ⚡ **5-Minute Quick Start**

### **1. Access NeuroShield** (Already Running!)
```
http://127.0.0.1:5000
```

### **2. Upload a File**
- Click "Choose File"
- Select: `.exe`, `.dll`, `.txt`, or `.pdf`
- Click "Analyze"

### **3. If Malware Detected - Choose Action:**

**🔒 QUARANTINE** (Recommended for executables)
- Encrypts and isolates the file
- Prevents accidental execution
- Can be restored later
- Safe and reversible

**🧹 CLEAN FILE** (For PDFs and text files)
- Removes malicious content
- Creates safe version
- Download cleaned file
- Original deleted

**🗑️ DELETE** (Permanent)
- Immediate deletion
- Cannot recover
- Use for confirmed malware

### **4. Manage Quarantine**
- Click "Quarantine Manager" button
- View all quarantined files
- Restore or permanently delete
- See statistics

---

## 📋 **What Each Feature Does**

### **QUARANTINE** 🔒
**What it does:**
- Encrypts file with XOR cipher
- Stores in isolated folder
- Cannot be executed
- Tracks all metadata (SHA256, threat type, date, etc.)

**When to use:**
- Detected malware in .exe/.dll files
- Want to keep file for analysis
- Unsure if false positive
- Want reversible action

**How to restore:**
1. Go to Quarantine Manager
2. Find your file
3. Click "Restore"
4. File decrypted and restored

---

### **CLEAN FILE** 🧹
**What it removes:**
- **From PDFs:**
  - JavaScript code
  - Auto-action triggers
  - Launch commands
  - Embedded files
  - Malicious URLs

- **From Text Files:**
  - Malicious keywords
  - Suspicious URLs
  - Script tags

**When to use:**
- Suspicious PDF or text file
- Want to keep the document
- Want to remove only malicious parts
- Need safe version

**What you get:**
- Cleaned file (download link)
- Cleaning report (before/after)
- List of removed items
- Original deleted

---

### **DELETE** 🗑️
**What it does:**
- Immediately deletes file
- No recovery possible
- Permanent removal

**When to use:**
- Confirmed malware
- Don't need the file
- Want immediate removal
- No plans to restore

---

## 🎯 **Example Scenarios**

### **Scenario 1: Suspicious Email PDF**
```
Problem: Received PDF from unknown sender

Steps:
1. Don't open it!
2. Upload to NeuroShield
3. Analysis shows: "Suspicious - Contains JavaScript"
4. Click "Clean File"
5. Download cleaned version
6. Original malicious PDF deleted

Result: Safe PDF without malicious code ✅
```

---

### **Scenario 2: Downloaded .exe File**
```
Problem: Downloaded program, antivirus flagged it

Steps:
1. Upload to NeuroShield
2. Analysis shows: "Malware - 100% confidence"
3. Click "Quarantine"
4. File encrypted and isolated

Result: Malware safely quarantined ✅

Later:
- If false positive → Restore from quarantine
- If confirmed malware → Permanently delete
```

---

### **Scenario 3: Suspicious Text File**
```
Problem: Found .txt with suspicious keywords

Steps:
1. Upload to NeuroShield
2. Analysis shows: "Suspicious content detected"
3. Click "Clean File"
4. Review cleaning report
5. Download sanitized version

Result: Clean text file ✅
```

---

## 📊 **Quarantine Manager**

**Access:** `http://127.0.0.1:5000/quarantine_manager`

### **Dashboard Shows:**
- **Total Files:** All quarantined items
- **Quarantined:** Currently in quarantine
- **Restored:** Previously restored files
- **Total Size:** Storage used

### **For Each File:**
- Original name
- Threat type
- Confidence level
- Quarantine date
- File size
- Status (quarantined/restored)
- Actions (Restore/Delete/Details)

### **Actions Available:**
- **Restore:** Decrypt and restore file
- **Delete:** Permanently remove
- **Details:** View full information
  - File hash (SHA256)
  - Quarantine ID
  - Threat details
  - Complete timeline

---

## 🔐 **Security Features**

### **Encryption**
- XOR cipher prevents execution
- Files stored as `.quar`
- Decryption only on restore
- Key: `NeuroShield_Quarantine_Key_2025`

### **Isolation**
- Separate quarantine folder
- Cannot execute from quarantine
- Metadata in JSON format
- SHA256 integrity check

### **Audit Trail**
- All actions logged
- Timestamps recorded
- Original paths saved
- Threat details preserved

---

## ⚠️ **Important Notes**

### **Executable Files (.exe, .dll)**
- ❌ **Cannot be cleaned** - too risky!
- ✅ **Can be quarantined** - safe option
- ✅ **Can be deleted** - permanent
- Cleaning executables could corrupt them
- Quarantine is the recommended action

### **PDF & Text Files**
- ✅ **Can be cleaned** - safe to sanitize
- ✅ **Can be quarantined** - also an option
- ✅ **Can be deleted** - if preferred
- Cleaning removes malicious parts only
- Legitimate content preserved

### **Restoration**
- Only restore files you trust!
- Scan restored files again if unsure
- Check threat details first
- Review file hash

### **Cleaning Limitations**
- Basic pattern matching (not deep parsing)
- May affect functionality
- Manual review recommended
- Not 100% guaranteed

---

## 💡 **Best Practices**

### **For Executables:**
1. Upload to NeuroShield
2. If malware detected → **Quarantine**
3. Check quarantine details
4. If false positive → Restore & scan again
5. If confirmed → Permanently delete

### **For PDFs:**
1. Upload to NeuroShield
2. If suspicious → **Clean File**
3. Download cleaned version
4. Test cleaned PDF works
5. Use cleaned version

### **For Text Files:**
1. Upload to NeuroShield
2. If suspicious → **Clean File**
3. Review cleaning report
4. Verify content acceptable
5. Download if OK

### **Quarantine Management:**
- Review quarantine weekly
- Delete confirmed malware
- Keep false positives temporarily
- Document decisions

---

## 🎨 **User Interface Tips**

### **Dark Mode**
- Click moon/sun icon
- Preference saved
- Works on all pages

### **Navigation**
- "Home" button on quarantine page
- "Quarantine Manager" on main page
- "Analyze Another File" on results

### **Alerts**
- Green = Safe/Success
- Yellow = Suspicious/Warning
- Red = Malware/Error
- Auto-dismiss after 5 seconds

---

## 🆘 **Troubleshooting**

### **Issue: File won't upload**
- Check file size (max 10MB)
- Check file type (.exe, .dll, .txt, .pdf)
- Try different file

### **Issue: Cleaning failed**
- File may be corrupted
- Try quarantine instead
- Check error message

### **Issue: Restore failed**
- Quarantine file may be missing
- Check quarantine ID
- Try permanent delete instead

### **Issue: Can't download cleaned file**
- Check browser downloads folder
- Try different browser
- Check file permissions

---

## 📈 **Feature Matrix**

| Action | .exe/.dll | .pdf | .txt |
|--------|-----------|------|------|
| **Detect** | ✅ 100% | ✅ Yes | ✅ Yes |
| **Quarantine** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Clean** | ❌ No | ✅ Yes | ✅ Yes |
| **Delete** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Restore** | ✅ Yes | ✅ Yes | ✅ Yes |

---

## 🎯 **Quick Reference**

### **Main Page**
```
http://127.0.0.1:5000
```
- Upload files
- Analyze files
- Get results
- Choose action

### **Quarantine Manager**
```
http://127.0.0.1:5000/quarantine_manager
```
- View quarantined files
- See statistics
- Restore files
- Delete permanently
- View details

---

## ✅ **Checklist**

**Before Uploading:**
- [ ] File is from untrusted source
- [ ] Suspicious behavior noticed
- [ ] Want second opinion
- [ ] Ready to take action

**After Detection:**
- [ ] Read threat details
- [ ] Choose appropriate action
- [ ] Follow through with decision
- [ ] Document if needed

**Quarantine Management:**
- [ ] Review quarantined files
- [ ] Check threat details
- [ ] Decide: restore or delete
- [ ] Execute decision
- [ ] Verify outcome

---

## 🌟 **Remember**

**NeuroShield now:**
- ✅ Detects malware (100% for executables)
- ✅ Removes viruses (PDFs & text)
- ✅ Quarantines threats (encrypted)
- ✅ Cleans files (sanitization)
- ✅ Manages quarantine (web interface)

**Not just a scanner - a complete security suite!**

---

## 📞 **Need Help?**

**Check:**
- `VIRUS_REMOVAL_COMPLETE.md` - Full documentation
- `PDF_SUPPORT.md` - PDF feature details
- `HIGH_ACCURACY_MODEL.md` - ML model details

**Developer:** F.J.G  
**Project:** NeuroShield - Malware Detection with Machine Learning  
**© 2025 NeuroShield. All Rights Reserved.**

---

**Start protecting your system now:** `http://127.0.0.1:5000` 🚀
