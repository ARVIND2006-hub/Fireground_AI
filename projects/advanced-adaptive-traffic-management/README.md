# Advanced Adaptive Traffic Management Controller

An educational SystemVerilog RTL project for a two-road intersection controller. It combines demand-adaptive timing, emergency and pedestrian request capture, startup all-red sequencing, fault latching, debug outputs, simulation monitors, and assertion properties.

> **Safety disclaimer:** This is an educational prototype, not a certified traffic controller. Do not connect it to public-road traffic signals.

## Key features
1. Startup all-red phase before normal operation.
2. Demand-adaptive green timing, calculated as `GREEN_MIN_CYCLES + demand × GREEN_SCALE`, capped at `GREEN_MAX_CYCLES`.
3. Synchronized emergency request inputs with pending-request flags.
4. A defined policy for simultaneous emergency requests.
5. Pedestrian requests retained until their crossing phase is served.
6. Latched all-red fault state when sensor status becomes invalid.
7. Timer width derived from the longest configured phase.
8. Debug outputs for state and timer waveform inspection.
9. Directed and randomized simulation scenarios.
10. SystemVerilog assertions for key output-safety properties.

## Files
- `rtl/advanced_traffic_management_controller.sv` — controller RTL.
- `verification/tb_advanced_traffic_management_controller.sv` — simulation testbench and safety monitors.
- `verification/advanced_traffic_management_sva.sv` — assertion checker for an SVA-capable simulator.

## Run with Cadence Xcelium
From the repository root:
```bash
xrun -sv projects/advanced-adaptive-traffic-management/rtl/advanced_traffic_management_controller.sv projects/advanced-adaptive-traffic-management/verification/tb_advanced_traffic_management_controller.sv -access +rwc
```

## Run with Icarus Verilog
If installed with SystemVerilog support:
```bash
iverilog -g2012 -o traffic_management_sim projects/advanced-adaptive-traffic-management/rtl/advanced_traffic_management_controller.sv projects/advanced-adaptive-traffic-management/verification/tb_advanced_traffic_management_controller.sv
vvp traffic_management_sim
```
The testbench requests a waveform file named `advanced_traffic_management.vcd`. Check the simulator output to confirm whether it was generated. SVA support varies by simulator; use a compatible tool for the separate assertion checker.

## Example timing calculation
With the default settings, minimum green time is 8 cycles and each demand unit adds 4 cycles, capped at 64 cycles. Demand 5 therefore gives 28 clock cycles. These are clock cycles, not seconds; actual time depends on the clock frequency.

## Verification checklist
- Confirm startup all-red behavior.
- Sweep demand inputs from 0 to 15 and measure green duration.
- Check that conflicting green signals and yellow overlap never occur.
- Exercise each emergency request and simultaneous emergency requests.
- Exercise pedestrian requests, including back-to-back requests.
- Force sensor invalid and confirm the fault remains latched until reset.
- Run assertion properties in an SVA-capable simulator.
- Record simulator version, commands, exit status, waveform, and assertion log.
- Synthesize the RTL and inspect warnings, resource use, timing constraints, and critical paths before FPGA testing.

## Limitations and next work
- Demand inputs are assumed synchronous and conditioned. Real sensor interfaces need filtering, validation, and suitable synchronization.
- Two-flop synchronizers reduce metastability propagation risk but cannot capture arbitrarily short pulses reliably. A handshake, event-toggle, or pulse-stretching scheme may be required.
- Request priority and clear ordering need additional corner-case review and formal analysis.
- Reset deassertion is not synchronized internally; platform-specific reset design is required for real hardware.
- The design lacks a complete pedestrian clearance interval, detector diagnostics, watchdog integration, redundant safety logic, and standards-compliant signal plans.
- Simulation monitors and assertions are not proof until run with a suitable verification flow.
- Do not claim simulation, formal verification, synthesis, timing closure, or FPGA validation until you have run the tools and reviewed the results.

## Résumé description (after validation only)
**Advanced Adaptive Traffic Management Controller — SystemVerilog RTL and Verification**
- Developed an FSM-based traffic controller with demand-adaptive timing, queued emergency and pedestrian requests, and a latched all-red fault response.
- Added debug visibility, simulation monitors, and assertion properties for traffic-signal safety invariants.
- Verified using [actual simulator/version] with [actual results]; evaluated synthesis and timing using [actual tool/results].

Replace bracketed fields only with results you have personally obtained.
