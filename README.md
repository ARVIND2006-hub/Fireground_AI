# FIREGROUND AI

## Project Overview

Fireground AI is a software prototype for monitoring firefighter conditions using sensor data and a multitask AI model.

The system analyzes:
- Activity
- Physiological state
- Environmental condition

The AI outputs are passed to a risk decision engine that produces:
- NORMAL
- ELEVATED
- HIGH

## Target Platform

Microchip PolarFire SoC Icicle Kit

## Current Implementation

Software-only implementation using:
- Python
- TensorFlow/Keras
- NumPy
- INT8 quantization
- Microchip VectorBlox SDK
- VNNX model
- VectorBlox C simulator

No physical hardware is currently available.

## AI Pipeline

Sensor data
    ↓
10-sample sliding window
    ↓
Preprocessing
    ↓
INT8 quantization
    ↓
VNNX AI inference
    ↓
Activity + Physiology + Environment
    ↓
Risk Decision Engine
    ↓
NORMAL / ELEVATED / HIGH

## Model Outputs

### Activity
- 0 = crawling
- 1 = standing
- 2 = walking

### Physiological State
- 0 = elevated
- 1 = high
- 2 = normal

### Environment
- 0 = normal
- 1 = risk

## Live Simulation

Input:
- 60 sensor samples
- 51 sliding windows

Current result:
- 37 NORMAL windows
- 14 ELEVATED windows
- 0 HIGH windows
- Overall status: ELEVATED

## Important Files

- VNNX model: models/fireground_v2_V250_ncomp.vnnx
- Live result: results/live_vnnx_fireground_result.json
- Dashboard: dashboard/fireground_dashboard.py
- Risk graph: results/fireground_risk_progression.png
- Architecture diagram: assets/rtosf.png

## Run the Dashboard

python3 dashboard/fireground_dashboard.py

## Run the Complete VNNX Simulation

source /home/arvind/VectorBlox-SDK/setup_vars.sh
python3 src/live_vnnx_fireground_system.py

## Additional ECE / VLSI Project

### Advanced Adaptive Traffic Management SoC
An educational SystemVerilog traffic-control subsystem with adaptive timing, AXI4-Lite memory-mapped registers, a processor-facing top-level wrapper, C firmware helpers, register-map documentation, testbenches, and a GitHub Actions smoke-test workflow.

- [Project documentation](projects/advanced-adaptive-traffic-management/README.md)
- [Controller RTL](projects/advanced-adaptive-traffic-management/rtl/advanced_traffic_management_controller.sv)
- [AXI4-Lite register bank](projects/advanced-adaptive-traffic-management/rtl/axi4lite_traffic_registers.sv)
- [SoC top-level wrapper](projects/advanced-adaptive-traffic-management/rtl/traffic_management_soc_top.sv)
- [Controller testbench](projects/advanced-adaptive-traffic-management/verification/tb_advanced_traffic_management_controller.sv)
- [AXI smoke testbench](projects/advanced-adaptive-traffic-management/verification/tb_traffic_management_axi.sv)
- [Embedded C register helpers](projects/advanced-adaptive-traffic-management/software/include/traffic_regs.h)
- [Architecture and integration guide](projects/advanced-adaptive-traffic-management/docs/system_architecture.md)
- [Automated smoke-test runner](projects/advanced-adaptive-traffic-management/scripts/run_smoke_tests.sh)
- [Register-map consistency checker](projects/advanced-adaptive-traffic-management/scripts/check_register_map.py)
- [Verification matrix](projects/advanced-adaptive-traffic-management/docs/verification_matrix.md)
- [Sensor front-end RTL](projects/advanced-adaptive-traffic-management/rtl/traffic_sensor_frontend.sv)
- [Watchdog RTL](projects/advanced-adaptive-traffic-management/rtl/traffic_watchdog.sv)
- [Digital twin simulator](projects/advanced-adaptive-traffic-management/software/sim/traffic_digital_twin.py)
- [Digital twin unit tests](projects/advanced-adaptive-traffic-management/software/sim/test_traffic_digital_twin.py)
- [FPGA bring-up checklist](projects/advanced-adaptive-traffic-management/docs/fpga_bringup_checklist.md)
- [Digital-twin metric definitions](projects/advanced-adaptive-traffic-management/docs/performance_metrics.md)
- [FPGA constraint template](projects/advanced-adaptive-traffic-management/constraints/traffic_management_template.xdc)

This is an educational prototype. The repository does not yet include a RISC-V CPU core or FPGA bitstream, and the test suite has not been independently run by the assistant. Review actual CI results before claiming passing verification. Do not connect this design to public-road signals.
