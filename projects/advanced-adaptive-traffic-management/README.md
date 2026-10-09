# Advanced Adaptive Traffic Management SoC

An educational SystemVerilog subsystem for a two-road model intersection. The repository now contains a demand-adaptive controller, an AXI4-Lite memory-mapped register bank, a processor-facing integration wrapper, basic testbenches, an example C firmware interface, a machine-readable register map, and a GitHub Actions smoke-test workflow.

> **Safety disclaimer:** This is an educational prototype, not a certified traffic controller. Never connect it to public-road traffic signals.

## Architecture

```text
External AXI4-Lite master / future RISC-V soft CPU
                     |
            AXI4-Lite register bank
             | config       ^ status
             v              |
       Adaptive traffic controller FSM
             |
       model signal outputs
```

The repository provides the processor-facing peripheral and example firmware, but does **not** yet include or instantiate a RISC-V CPU core. The top-level expects an external AXI4-Lite master.

## Features

1. Startup all-red phase.
2. Demand-adaptive green timing: `GREEN_MIN_CYCLES + demand * GREEN_SCALE`, capped at `GREEN_MAX_CYCLES`.
3. Synchronized emergency and pedestrian request inputs with pending flags.
4. Defined simultaneous-emergency arbitration policy.
5. Latched all-red fault state when sensor status is invalid.
6. AXI4-Lite control, demand, status, and debug registers.
7. Processor-facing SoC wrapper.
8. Controller testbench with directed/randomized stimuli and output safety monitors.
9. Basic AXI register smoke testbench.
10. C header and firmware example for a future soft processor.
11. JSON register-map description.
12. GitHub Actions workflow to attempt smoke tests on pushes and pull requests.
13. Sensor front-end module with synchronizers, button debouncing, saturating demand scores, and slow decay.
14. Separate watchdog module for heartbeat timeout and invalid-sensor diagnostics.
15. Dedicated unit-test benches for the sensor front end and watchdog.
16. Python digital twin to compare a fixed-time baseline against a queue-aware adaptive policy.
17. Unit tests for deterministic digital-twin behavior and accounting sanity.

## Source layout

- `rtl/advanced_traffic_management_controller.sv` — controller FSM.
- `rtl/axi4lite_traffic_registers.sv` — memory-mapped peripheral registers.
- `rtl/traffic_management_soc_top.sv` — integrated top-level wrapper.
- `rtl/traffic_sensor_frontend.sv` — standalone button-conditioning and demand-estimation module.
- `rtl/traffic_watchdog.sv` — standalone heartbeat/sensor-health watchdog.
- `CHANGELOG.md` — summary of repository enhancements and validation status.
- `verification/tb_advanced_traffic_management_controller.sv` — controller testbench.
- `verification/tb_traffic_management_axi.sv` — basic AXI and top-level smoke test.
- `verification/tb_traffic_sensor_frontend.sv` — sensor debounce and demand smoke test.
- `verification/tb_traffic_watchdog.sv` — heartbeat timeout smoke test.
- `verification/advanced_traffic_management_sva.sv` — assertion checker for an SVA-capable simulator.
- `software/include/traffic_regs.h` — C register definitions and helper functions.
- `software/examples/traffic_demo.c` — illustrative firmware skeleton.
- `software/sim/traffic_digital_twin.py` — configurable queueing simulation and JSON report generator.
- `software/sim/test_traffic_digital_twin.py` — unit tests for the simulation.
- `docs/register_map.json` — machine-readable register map.
- `docs/system_architecture.md` — architecture, integration steps, and limitations.
- `docs/verification_matrix.md` — evidence matrix and release readiness gates.
- `docs/fpga_bringup_checklist.md` — board bring-up checklist and evidence requirements.
- `docs/performance_metrics.md` — definitions and limitations of digital-twin metrics.
- `constraints/traffic_management_template.xdc` — placeholder-only FPGA timing constraint template.
- `scripts/run_smoke_tests.sh` — local Icarus Verilog smoke-test runner.
- `scripts/check_register_map.py` — dependency-free JSON/RTL/C register-offset consistency check.
- `scripts/synth_yosys.ys` — optional Yosys generic synthesis/structural-check script.
- `.gitignore` — ignores local build and waveform outputs.
- `.github/workflows/traffic-management-smoke.yml` — CI smoke-test workflow.

## AXI4-Lite register map

Offsets are byte offsets from the peripheral base address assigned by the system integrator.

| Offset | Name | Access | Meaning |
|---|---|---|---|
| `0x00` | CONTROL | R/W | bit 0 sensor status valid; bit 1 NS emergency; bit 2 EW emergency; bit 3 NS pedestrian; bit 4 EW pedestrian |
| `0x04` | DEMAND | R/W | bits [3:0] NS demand; bits [7:4] EW demand |
| `0x08` | STATUS | R | bits [1:0] NS light; [3:2] EW light; bit 4 NS walk; bit 5 EW walk; bit 6 emergency active; bit 7 fault active |
| `0x0C` | DEBUG | R | bits [3:0] state; bits [11:4] timer |

Writing a request bit high causes a level to be presented to the controller's synchronizer. Software should clear it before raising that request again. The controller captures rising edges, not an unlimited queue of repeated software writes.

## Run smoke tests

From the repository root on a system with Icarus Verilog installed:

```bash
bash projects/advanced-adaptive-traffic-management/scripts/run_smoke_tests.sh
```

Or compile the controller testbench alone:

```bash
iverilog -g2012 -s tb_advanced_traffic_management_controller -o controller_tb projects/advanced-adaptive-traffic-management/rtl/advanced_traffic_management_controller.sv projects/advanced-adaptive-traffic-management/verification/tb_advanced_traffic_management_controller.sv
vvp controller_tb
```

Compile/elaborate the SoC RTL:

```bash
iverilog -g2012 -s traffic_management_soc_top -o soc_elab projects/advanced-adaptive-traffic-management/rtl/advanced_traffic_management_controller.sv projects/advanced-adaptive-traffic-management/rtl/axi4lite_traffic_registers.sv projects/advanced-adaptive-traffic-management/rtl/traffic_management_soc_top.sv
```

The CI workflow is configured to run the register-map consistency check and attempt the smoke-test script on relevant pushes and pull requests. A committed workflow file is not proof that a run passed; inspect the Actions result for the actual outcome.

## Digital twin experiment

Run the queueing model from the repository root:

```bash
python3 projects/advanced-adaptive-traffic-management/software/sim/traffic_digital_twin.py --steps 2000 --seed 2026 --arrival-ns 0.65 --arrival-ew 0.25 --output traffic_digital_twin_report.json
python3 -m unittest discover -s projects/advanced-adaptive-traffic-management/software/sim -p "test_*.py"
```

The model compares a fixed-time baseline with a queue-aware adaptive policy under the same seeded arrivals and emits a JSON report with arrivals, vehicles served, residual queue, an approximate queue-delay metric, maximum queue, and signal-switch count. This is a **toy queueing model**, not a calibrated traffic simulator; benchmark results are not evidence of real-world improvements. Metric definitions and experiment guidance are in `docs/performance_metrics.md`. It is software-only and does not yet exchange live signals with the RTL.

## Optional generic synthesis check

If Yosys is installed, run from the repository root:

```bash
yosys -s projects/advanced-adaptive-traffic-management/scripts/synth_yosys.ys
```

This script performs hierarchy, process lowering, optimization, structural checks, and statistics, then writes a generic netlist under `build/traffic-management/`. It is **not** FPGA-specific synthesis, place-and-route, timing closure, or proof of correct behavior. Review all warnings and the generated report.

## FPGA constraints template\n\n`constraints/traffic_management_template.xdc` is a placeholder only. Pin assignments, I/O standards, clock period, and external delays must be filled using the exact board documentation before FPGA implementation. It is not a ready-to-run board constraint file.\n\n## Firmware example

The C example uses a placeholder peripheral base address. Replace it with the actual address from the target platform's memory map before running it on a processor. The repository does not currently provide a complete RISC-V CPU subsystem, linker script, board support package, or FPGA bitstream.

## Timing example

With default parameters, demand 5 gives `8 + 5*4 = 28` green clock cycles, capped at 64. These are clock cycles, not seconds; real duration depends on clock frequency.

## Verification status and limitations

No simulator, formal verification tool, synthesis tool, timing analysis, or FPGA hardware has been run by this assistant. The CI workflow may run after GitHub processes the commit, but its result must be checked separately. The AXI testbench is a basic smoke test, not exhaustive AXI4-Lite compliance verification.

Before considering hardware use:
- Review the RTL with a qualified engineer and fix all compile/simulation warnings and failures.
- Add AXI protocol tests for independently timed address/data channels, backpressure, byte strobes, reset, and repeated transactions.
- Run assertion-based or formal verification with a compatible tool.
- Synthesize and inspect resource use, latches, clock constraints, and critical paths.
- Add input filtering/debouncing, pulse capture/handshakes, reset-release strategy, watchdogs, and complete pedestrian clearance logic.
- Test only on a low-voltage tabletop model with appropriate drivers and isolation.

This project is **not safety-certified** and must not control real public-road signals.

## Résumé description (only after running and reviewing tools)

**Adaptive Traffic Management SoC Peripheral — SystemVerilog, AXI4-Lite, Embedded C**
- Designed an educational FSM-based controller with demand-dependent timing, emergency/pedestrian request handling, and fault-latched outputs.
- Integrated memory-mapped control/status registers, a processor-facing AXI4-Lite wrapper, and C firmware helpers.
- Verification results: add the actual simulator/tool versions, commands, and outcomes after independently running them. Do not claim passing tests, synthesis, timing closure, or FPGA validation without evidence.
