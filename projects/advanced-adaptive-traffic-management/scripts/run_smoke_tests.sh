#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"

BUILD_DIR="${BUILD_DIR:-build/traffic-management}"
mkdir -p "$BUILD_DIR"

RTL_DIR="projects/advanced-adaptive-traffic-management/rtl"
VERIFY_DIR="projects/advanced-adaptive-traffic-management/verification"

if ! command -v iverilog >/dev/null 2>&1 || ! command -v vvp >/dev/null 2>&1; then
  echo "ERROR: Icarus Verilog (iverilog and vvp) is required." >&2
  exit 2
fi

echo "[1/2] Compile and run controller testbench"
iverilog -g2012 -s tb_advanced_traffic_management_controller \
  -o "$BUILD_DIR/controller_tb" \
  "$RTL_DIR/advanced_traffic_management_controller.sv" \
  "$VERIFY_DIR/tb_advanced_traffic_management_controller.sv"
(
  cd "$BUILD_DIR"
  vvp ./controller_tb
)

echo "[2/2] Compile and run AXI/SoC smoke testbench"
iverilog -g2012 -s tb_traffic_management_axi \
  -o "$BUILD_DIR/axi_tb" \
  "$RTL_DIR/advanced_traffic_management_controller.sv" \
  "$RTL_DIR/axi4lite_traffic_registers.sv" \
  "$RTL_DIR/traffic_management_soc_top.sv" \
  "$VERIFY_DIR/tb_traffic_management_axi.sv"
(
  cd "$BUILD_DIR"
  vvp ./axi_tb
)

echo "Smoke-test commands completed. Review both logs and waveforms; this script does not perform formal verification or synthesis."
