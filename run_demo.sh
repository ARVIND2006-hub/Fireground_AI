#!/bin/bash
set -e

cd /mnt/c/Users/Asus/Fireground_AI

source /home/arvind/VectorBlox-SDK/setup_vars.sh

echo "=============================================="
echo "        FIREGROUND AI DEMONSTRATION"
echo "=============================================="
echo

python3 src/live_vnnx_fireground_system.py

echo
echo "=============================================="
echo "             DASHBOARD"
echo "=============================================="
echo

python3 dashboard/fireground_dashboard.py
