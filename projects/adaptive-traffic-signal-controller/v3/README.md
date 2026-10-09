# Traffic Management Controller V3 — Hardened RTL + Verification

V3 is a more advanced educational SystemVerilog design study for an adaptive two-road intersection controller. It adds startup all-red sequencing, bounded-width timing, edge-captured request queues, explicit emergency tie-breaking, fault latching, debug visibility, simulation monitors, and assertion properties.

> **Safety disclaimer:** This is an educational prototype. It is not certified, validated for public-road deployment, or safety-rated. Do not connect it to real traffic signals.

## V3 feature set
1. **Startup all-red phase** before normal operation.
2. **Demand-adaptive green timing**, computed as `GREEN_MIN_CYCLES + demand × GREEN_SCALE` and capped at `GREEN_MAX_CYCLES`.
3. **Emergency request capture**: synchronized request rising edges are stored as pending flags and considered at a safe all-red decision.
4. **Defined simultaneous-emergency policy**: when both emergency requests are pending, the next direction alternates relative to the previous green phase.
5. **Pedestrian request queues**: synchronized rising edges remain pending until their corresponding pedestrian phase is serviced.
6. **Fault-latched all-red state**: invalid sensor status drives the controller into a fault state, which stays latched until reset.
7. **Bounded timer width**: counter width is derived from the configured longest phase.
8. **Debug ports**: expose the current FSM state and timer for waveform inspection.
9. **Directed/stress scenarios**: demand changes, emergency requests, pedestrian requests, simultaneous emergencies, and invalid sensor status.
10. **Assertion module**: properties for mutually exclusive green signals, yellow interlocks, pedestrian safety, and fault outputs.

## Files
- `rtl/traffic_management_controller_v3.sv` — V3 synthesizable RTL candidate.
- `verification/tb_traffic_management_controller_v3.sv` — directed/randomized testbench with simulation monitors.
- `verification/traffic_management_v3_sva.sv` — SystemVerilog Assertion (SVA) checker.

## Run using Cadence Xcelium
From the repository root:
```bash
xrun -sv projects/adaptive-traffic-signal-controller/v3/rtl/traffic_management_controller_v3.sv projects/adaptive-traffic-signal-controller/v3/verification/tb_traffic_management_controller_v3.sv -access +rwc
```
The testbench writes `traffic_management_v3.vcd` if VCD support is enabled by the simulator.

## Run using Icarus Verilog
If installed:
```bash
iverilog -g2012 -o traffic_v3_sim projects/adaptive-traffic-signal-controller/v3/rtl/traffic_management_controller_v3.sv projects/adaptive-traffic-signal-controller/v3/verification/tb_traffic_management_controller_v3.sv
vvp traffic_v3_sim
```
Support for some SystemVerilog features varies by Icarus version. The separate SVA checker generally requires an SVA-capable simulator and should be added to the run only after checking tool support.

## Example timing calculation
With defaults, `GREEN_MIN_CYCLES=8`, `GREEN_SCALE=4`, and `GREEN_MAX_CYCLES=64`:
- Demand 0 gives 8 clock cycles.
- Demand 5 gives 28 clock cycles.
- Demand 15 gives 68 before clipping, so it is capped at 64 cycles.

These are **clock cycles**, not seconds. Convert them to real time using the target clock frequency and appropriate engineering requirements.

## Verification plan
- Check startup outputs remain all-red during startup phase.
- Sweep demand values 0 through 15 and measure green duration.
- Verify no conflicting greens and no yellow overlap.
- Exercise each emergency input and both inputs together.
- Exercise each pedestrian input and simultaneous requests.
- Force sensor invalid and check all-red fault latch.
- Run SVA in a compatible simulator.
- Record simulator version, command, exit status, waveform, and assertion log.
- Synthesize the RTL and inspect warnings, resource reports, timing constraints, and critical paths before FPGA experimentation.

## Known limitations / required engineering work
- Demand inputs are assumed to be synchronous and conditioned; actual sensors require front-end filtering, debounce, synchronization and plausibility checking.
- Two-flop synchronizers reduce metastability propagation risk but cannot guarantee capture of arbitrarily short pulses. Use a handshake, event toggle, or pulse stretcher sized for the actual clock and input source.
- Emergency pending flags and service/clear ordering should undergo corner-case review; this RTL has not been formally proven.
- Reset is asynchronous assertion and deassertion is not synchronized internally. Real FPGA/ASIC integration should use a reset strategy appropriate to the platform.
- The design does not implement a full pedestrian clearance/flashing interval, vehicle detector diagnostics, watchdog, redundant safety controller, or standards-compliant phase plan.
- Random simulation is not formal proof. SVA is not proof unless run in a proper verification flow with assumptions and coverage.
- Do not claim synthesis, timing closure, formal verification, or FPGA success until those activities have actually been performed.

## Resume entry (use only after actual validation)
**Traffic Management Controller V3 — SystemVerilog RTL and Verification**
- Designed an FSM-based adaptive traffic controller with bounded demand-based timing, queued emergency/pedestrian requests, and latched all-red fault response.
- Created simulation checks and SVA properties for conflicting greens, yellow interlocks, pedestrian output safety, and fault-state behavior.
- Verified using [simulator/version], with [actual test count/results], and evaluated synthesis/timing using [actual tool/results].

Replace bracketed fields only with results you have personally obtained.
