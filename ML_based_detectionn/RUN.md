PowerShell instructions to run the ML-based detection app (Windows PowerShell):

1. From the repository root, run:

```powershell
# Activate your virtualenv if you use one
# Example: .\venv\Scripts\Activate.ps1

# Install requirements if not already installed
pip install -r ML_based_detectionn\requirements.txt

# Start the ML web app explicitly
python .\run_ml_app.py
```

2. The app will start on http://127.0.0.1:5000 by default. Set FLASK_HOST and FLASK_PORT environment variables to change.

Note: This launcher imports `ML_based_detectionn/app.py` directly to avoid starting other apps in the workspace.
