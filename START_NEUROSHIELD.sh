#!/bin/bash

# NeuroShield Startup Script
# Developed by F.J.G

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║              🛡️  STARTING NEUROSHIELD 🛡️                     ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Change to app directory
cd /workspace/ML_based_detectionn

# Check if already running
if ps aux | grep -v grep | grep "python3 app.py" > /dev/null; then
    echo "⚠️  NeuroShield is already running!"
    echo ""
    echo "To restart, first stop it with:"
    echo "  pkill -f 'python3 app.py'"
    echo ""
    echo "Or run this script with: bash $0 restart"
    exit 1
fi

# Start the app in background
echo "🚀 Starting NeuroShield..."
nohup python3 app.py > /tmp/neuroshield.log 2>&1 &
PID=$!

# Wait a moment for app to start
sleep 2

# Check if it started successfully
if ps -p $PID > /dev/null; then
    echo "✅ NeuroShield started successfully!"
    echo ""
    echo "📊 Details:"
    echo "  Process ID: $PID"
    echo "  URL: http://127.0.0.1:5000"
    echo "  Logs: /tmp/neuroshield.log"
    echo ""
    echo "🌐 Access NeuroShield:"
    echo "  1. Open your browser"
    echo "  2. Go to: http://127.0.0.1:5000"
    echo ""
    echo "📋 Useful commands:"
    echo "  View logs:    tail -f /tmp/neuroshield.log"
    echo "  Check status: ps aux | grep 'python3 app.py'"
    echo "  Stop app:     pkill -f 'python3 app.py'"
else
    echo "❌ Failed to start NeuroShield"
    echo "Check logs: tail /tmp/neuroshield.log"
    exit 1
fi
