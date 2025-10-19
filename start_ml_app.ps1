# PowerShell script to start the ML-based detection app
# Run this from the repository root in PowerShell

param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 5000
)

# Activate virtualenv if present (optional)
# .\venv\Scripts\Activate.ps1

set-item -path env:FLASK_HOST -value $Host
set-item -path env:FLASK_PORT -value $Port

python .\run_ml_app.py
