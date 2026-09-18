#!/usr/bin/env python3
import json
from pathlib import Path

RESULT_FILE = Path("/mnt/c/Users/Asus/Fireground_AI/results/live_vnnx_fireground_result.json")

with RESULT_FILE.open("r", encoding="utf-8") as f:
    data = json.load(f)

stats = data["window_statistics"]

print()
print("=" * 60)
print("             FIREGROUND AI DASHBOARD")
print("=" * 60)
print("Firefighter       :", data["firefighter"])
print("Sensor samples    :", data["sensor_samples"])
print("Windows processed :", data["ai_windows_processed"])
print()

print("WINDOW STATISTICS")
print("-" * 60)
print("NORMAL            :", stats["normal"])
print("ELEVATED          :", stats["elevated"])
print("HIGH              :", stats["high"])
print()

print("OVERALL STATUS    :", data["overall_status"])
print("-" * 60)

if data["overall_status"] == "HIGH":
    print("ALERT             : HIGH")
elif data["overall_status"] == "ELEVATED":
    print("ALERT             : MEDIUM")
else:
    print("ALERT             : LOW")

print()
print("LATEST 10 AI WINDOWS")
print("-" * 60)
print(f"{'Win':>3}  {'Time':>8}  {'Activity':<10} {'Physiology':<12} {'Env':<8} {'Score':>5}  Status")
print("-" * 60)

for r in data["results"][-10:]:
    ai = r["ai_prediction"]
    risk = r["risk"]

    print(
        f"{r['window']:3d}  "
        f"{r['timestamp']:>8}  "
        f"{ai['activity']:<10} "
        f"{ai['physiological_state']:<12} "
        f"{ai['environment']:<8} "
        f"{risk['risk_score']:5d}  "
        f"{risk['local_status']}"
    )

print("=" * 60)
