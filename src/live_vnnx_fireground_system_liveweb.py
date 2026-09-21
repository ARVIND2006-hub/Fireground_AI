#!/usr/bin/env python3
"""Fireground AI VNNX simulation with live localhost + Vercel publishing."""

import csv
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from vercel_publisher import publish

PROJECT = "/mnt/c/Users/Asus/Fireground_AI"
DATA_PATH = os.path.join(PROJECT, "dataset/live_sensor_stream.csv")
SIMULATOR = "/home/arvind/VectorBlox-SDK/example/sim-c/sim-run-sensor"
MODEL = os.path.join(PROJECT, "models/fireground_v2_V250_ncomp.vnnx")
OUTPUT_PATH = os.path.join(PROJECT, "results/live_vnnx_fireground_result.json")
WINDOW_SIZE = 10
FEATURES = ["heart_rate","acc_x","acc_y","acc_z","gyro_x","gyro_y","gyro_z","gas","temperature"]
MEAN = [91.1068859,0.266849514,0.268908626,9.66666423,0.0322428436,0.0323018356,0.0324732444,27.0979919,31.1267252]
SCALE = [13.34430666,0.13700957,0.13697954,0.1158999,0.02163363,0.02163962,0.02157665,11.87917055,1.93309766]
Q_SCALE = 0.028781553730368614
Q_ZERO = -5
OUT_SCALE = 0.00390625
OUT_ZERO = -128
ACTIVITY_LABELS = ["crawling","standing","walking"]
PHYSIOLOGICAL_LABELS = ["elevated","high","normal"]
ENVIRONMENT_LABELS = ["normal","risk"]


def quantize_window(window):
    return [[max(-128, min(127, int(round(((v-MEAN[j])/SCALE[j])/Q_SCALE+Q_ZERO)))) for j, v in enumerate(row)] for row in window]


def write_bin(qw, path):
    with open(path, "wb") as f:
        f.write(bytes((v + 256) % 256 for row in qw for v in row))


def prob(q):
    return max(0.0, min(1.0, (q - OUT_ZERO) * OUT_SCALE))


def run_vnnx(path):
    p = subprocess.run([SIMULATOR, MODEL, path], capture_output=True, text=True, check=False)
    if p.returncode != 0:
        raise RuntimeError("VNNX simulator failed.\n" + p.stdout + "\n" + p.stderr)
    text = p.stdout
    specs = {"activity": ("Activity output", 3), "physiological": ("Physiological output", 3), "environment": ("Environment output", 2)}
    out = {}
    for name, (hdr, n) in specs.items():
        s = text.find(hdr)
        if s < 0:
            raise RuntimeError("Missing " + hdr)
        e = len(text)
        for oh, _ in specs.values():
            if oh != hdr:
                pos = text.find(oh, s + len(hdr))
                if pos >= 0:
                    e = min(e, pos)
        vals = [int(x) for x in re.findall(r"Class\s+\d+\s+:\s+(-?\d+)", text[s:e])]
        if len(vals) != n:
            raise RuntimeError(f"{name}: expected {n} values, found {len(vals)}")
        idx = max(range(n), key=lambda i: vals[i])
        out[name] = {"class_index": idx, "raw_int8": vals, "confidence": prob(vals[idx])}
    return out


def risk_score(a, e, p):
    return (2 if e == "risk" else 0) + (1 if a == "crawling" else 0) + (2 if p == "high" else 0)


def status(s):
    return "HIGH" if s >= 4 else ("ELEVATED" if s >= 2 else "NORMAL")


def event(a, e, p):
    if a == "crawling" and e == "risk" and p == "high":
        return "deterioration"
    if e == "risk":
        return "environmental_risk"
    if p == "high":
        return "physiological_alert"
    return "normal"


def sensor_payload(rows):
    return [{k: (r[k] if k == "timestamp" else float(r[k])) for k in ["timestamp"] + FEATURES} for r in rows]


def write_payload(results, rows, total):
    stats = {k: sum(1 for r in results if r["risk"]["local_status"] == k.upper()) for k in ("normal","elevated","high")}
    overall = "HIGH" if stats["high"] else ("ELEVATED" if stats["elevated"] else "NORMAL")
    return {
        "system": "Fireground AI",
        "inference_engine": "Microchip VectorBlox VNNX simulator",
        "generated_at": datetime.now().isoformat(),
        "sensor_samples": len(rows),
        "window_size": WINDOW_SIZE,
        "ai_windows_processed": len(results),
        "window_statistics": stats,
        "overall_status": overall,
        "firefighter": "FF01",
        "results": results,
        "sensor_stream": sensor_payload(rows),
        "sensor_channels": [
            {"key":"heart_rate","name":"Heart Rate","unit":"bpm"},
            {"key":"acc_x","name":"Accelerometer X","unit":"g"},
            {"key":"acc_y","name":"Accelerometer Y","unit":"g"},
            {"key":"acc_z","name":"Accelerometer Z","unit":"g"},
            {"key":"gyro_x","name":"Gyroscope X","unit":"°/s"},
            {"key":"gyro_y","name":"Gyroscope Y","unit":"°/s"},
            {"key":"gyro_z","name":"Gyroscope Z","unit":"°/s"},
            {"key":"gas","name":"Gas","unit":"ppm"},
            {"key":"temperature","name":"Temperature","unit":"°C"},
        ],
    }


def main():
    for path in (DATA_PATH, MODEL, SIMULATOR):
        if not os.path.exists(path):
            raise FileNotFoundError(path)
    with open(DATA_PATH, newline="") as f:
        rows = list(csv.DictReader(f))
    total = len(rows) - WINDOW_SIZE + 1
    results = []
    remote_warned = False

    print("================================================")
    print(" FIREGROUND AI - VNNX LIVE SOFTWARE + WEB SYSTEM")
    print("================================================")
    print(f"Samples: {len(rows)} | Windows: {total}")

    for start in range(total):
        wr = rows[start:start+WINDOW_SIZE]
        window = [[float(r[k]) for k in FEATURES] for r in wr]
        fd, bp = tempfile.mkstemp(suffix=".bin")
        os.close(fd)
        try:
            write_bin(quantize_window(window), bp)
            pred = run_vnnx(bp)
        finally:
            try:
                os.remove(bp)
            except OSError:
                pass

        a = ACTIVITY_LABELS[pred["activity"]["class_index"]]
        p = PHYSIOLOGICAL_LABELS[pred["physiological"]["class_index"]]
        e = ENVIRONMENT_LABELS[pred["environment"]["class_index"]]
        score = risk_score(a, e, p)
        st = status(score)
        ev = event(a, e, p)
        zone_status = "HIGH" if st == "HIGH" else ("ELEVATED" if e == "risk" or st == "ELEVATED" else "NORMAL")
        priority = "HIGH" if st == "HIGH" else ("MEDIUM" if st == "ELEVATED" else "LOW")
        wn = start + 1
        ts = wr[-1]["timestamp"]
        results.append({
            "window": wn,
            "timestamp": ts,
            "firefighter": {"node_id":"FF01","x":10,"y":20,"zone":"A"},
            "ai_prediction": {
                "activity": a,
                "activity_confidence": pred["activity"]["confidence"],
                "physiological_state": p,
                "physiological_confidence": pred["physiological"]["confidence"],
                "environment": e,
                "environment_confidence": pred["environment"]["confidence"],
            },
            "risk": {"risk_score": score, "local_status": st, "event_type": ev},
            "zone": {"zone_id":"A","zone_status":zone_status},
            "command_center": {"alert_priority":priority},
        })

        print(f"Window {wn:02d}/{total} | {ts} | Activity={a} | Physiology={p} | Environment={e} | Score={score} | {st}")

        payload = write_payload(results, rows, total)
        Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
        Path(OUTPUT_PATH).write_text(json.dumps(payload, indent=4), encoding="utf-8")
        ok, msg = publish(payload)
        if ok:
            print(f"           WEB UPDATE: {msg}")
        elif not remote_warned:
            print(f"           WEB UPDATE: skipped ({msg})")
            remote_warned = True

    final = write_payload(results, rows, total)
    Path(OUTPUT_PATH).write_text(json.dumps(final, indent=4), encoding="utf-8")
    print("================================================")
    print(f"NORMAL: {final['window_statistics']['normal']} | ELEVATED: {final['window_statistics']['elevated']} | HIGH: {final['window_statistics']['high']}")
    print("OVERALL STATUS:", final["overall_status"])
    print("Result saved to:", OUTPUT_PATH)


if __name__ == "__main__":
    main()
