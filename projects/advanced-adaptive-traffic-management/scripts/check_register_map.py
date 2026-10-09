#!/usr/bin/env python3
"""Dependency-free consistency checks for the documented traffic register map."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "projects" / "advanced-adaptive-traffic-management"
JSON_MAP = PROJECT / "docs" / "register_map.json"
RTL = PROJECT / "rtl" / "axi4lite_traffic_registers.sv"
HEADER = PROJECT / "software" / "include" / "traffic_regs.h"

def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)

data = json.loads(JSON_MAP.read_text(encoding="utf-8"))
rtl = RTL.read_text(encoding="utf-8")
header = HEADER.read_text(encoding="utf-8")

for item in data.get("registers", []):
    name = item["name"]
    offset = int(item["offset"], 16)
    if name not in {"CONTROL", "DEMAND", "STATUS", "DEBUG"}:
        fail(f"unexpected register name: {name}")
    rtl_name = f"REG_{name}"
    rtl_match = re.search(
        rf"localparam\s+logic\s*\[[^\]]+\]\s+{rtl_name}\s*=\s*'h([0-9A-Fa-f]+)",
        rtl,
    )
    if not rtl_match:
        fail(f"{rtl_name} not found in RTL")
    if int(rtl_match.group(1), 16) != offset:
        fail(f"{name} offset differs between JSON and RTL")
    c_match = re.search(rf"#define\s+TRAFFIC_REG_{name}\s+0x([0-9A-Fa-f]+)u", header)
    if not c_match:
        fail(f"TRAFFIC_REG_{name} not found in C header")
    if int(c_match.group(1), 16) != offset:
        fail(f"{name} offset differs between JSON and C header")

expected_offsets = {"CONTROL": 0x00, "DEMAND": 0x04, "STATUS": 0x08, "DEBUG": 0x0C}
seen = {item["name"]: int(item["offset"], 16) for item in data.get("registers", [])}
if seen != expected_offsets:
    fail(f"register set/offsets unexpected: {seen}")

print("PASS: JSON, RTL, and C-header register offsets are consistent.")
