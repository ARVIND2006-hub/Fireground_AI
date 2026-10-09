# Advanced Adaptive Traffic Signal Controller

An educational SystemVerilog RTL prototype exploring demand-adaptive traffic lights, emergency requests, pedestrian phases, asynchronous input synchronization, and fail-safe behavior. This repository now includes directed simulation, a pseudo-random stress testbench, and reusable assertion properties.

## Architecture and features
- **Demand-adaptive green time:** `GREEN_MIN_CYCLES + demand × GREEN_SCALE`, capped at `GREEN_MAX_CYCLES`.
- **Emergency preemption:** emergency requests influence road selection after safe yellow and all-red transitions.
- **Pedestrian service:** crossing requests are latched until a dedicated walk phase; both vehicle approaches stay red during the walk phase.
- **Clock-domain crossing basics:** two-flop synchronizers are used for asynchronous emergency and pedestrian inputs.
- **Fail-safe behavior:** invalid sensor status enters a latched all-red fault state; reset is required to recover.
- **Directed tests:** representative demand, emergency, pedestrian, and fault scenarios.
- **Stress testing:** pseudo-random demand and request activity over 600 test cycles.
- **Assertion properties:** reusable checks for no conflicting green, pedestrian safety, mutually exclusive pedestrian phases, and safe fault outputs.

## Repository files
- `rtl/adaptive_traffic_controller_advanced.sv` — advanced controller RTL.
- `tb/tb_adaptive_traffic_controller_advanced.sv` — directed testbench.
- `verification/tb_traffic_controller_stress.sv` — pseudo-random stress testbench.
- `verification/traffic_controller_assertions.sv` — reusable SystemVerilog assertion checker module.

## Run directed simulation with Cadence Xcelium
From the repository root:
```bash
xrun -sv projects/adaptive-traffic-signal-controller/advanced/rtl/adaptive_traffic_controller_advanced.sv projects/adaptive-traffic-signal-controller/advanced/tb/tb_adaptive_traffic_controller_advanced.sv -access +rwc
```

## Run stress simulation with Cadence Xcelium
```bash
xrun -sv projects/adaptive-traffic-signal-controller/advanced/rtl/adaptive_traffic_controller_advanced.sv projects/adaptive-traffic-signal-controller/advanced/verification/tb_traffic_controller_stress.sv -access +rwc
```
The stress test writes `traffic_controller_stress.vcd`.

## Run with Icarus Verilog
If installed with SystemVerilog support:
```bash
iverilog -g2012 -o traffic_advanced_sim projects/adaptive-traffic-signal-controller/advanced/rtl/adaptive_traffic_controller_advanced.sv projects/adaptive-traffic-signal-controller/advanced/tb/tb_adaptive_traffic_controller_advanced.sv
vvp traffic_advanced_sim
```
Some Icarus versions do not support every SystemVerilog assertion feature. The reusable assertion checker is intended for a simulator with SVA support and may need to be instantiated or bound according to that simulator's syntax.

## Suggested verification campaign
1. Check reset behavior and normal state transitions.
2. Vary demand inputs from 0 to 15 and observe green-time changes.
3. Test each emergency input independently and test both asserted together.
4. Exercise each pedestrian request, including simultaneous requests.
5. Drive `sensor_data_valid` low and confirm the controller enters and remains in fault state.
6. Run the stress test and save the transcript and VCD waveform.
7. Run assertion-based checks in a simulator with SVA support.
8. For FPGA use, synthesize the design, inspect timing/resource reports, and test only on a low-voltage educational demo board.

## Known limitations and next engineering steps
- Demand inputs are assumed stable and synchronous to `clk`; real detector interfaces need filtering, validity checks, and suitable synchronization.
- Two-flop synchronizers reduce metastability propagation risk but do not guarantee capture of arbitrarily short pulses. Use a request/acknowledge handshake or pulse stretcher for a real interface.
- Simultaneous emergency requests do not yet have a dedicated tie-break policy.
- Pedestrian request inputs are level-sampled; real pushbuttons need debouncing and a defined request interface.
- The stress test is simulation-based, not formal proof. Assertions must be run in a compatible simulator.
- A real traffic installation requires independent safety engineering, hazard analysis, validated timing, redundant interlocks, and compliance with applicable standards. This learning project is not a deployable traffic controller.

## Resume description (only after you have run the tools)
**Advanced Adaptive Traffic Signal Controller with Emergency, Pedestrian, and Fail-Safe Logic**
- Developed a SystemVerilog FSM with demand-adjusted green timing, emergency requests, and pedestrian crossing phases.
- Added asynchronous-input synchronizers and a latched all-red fault response for invalid sensor status.
- Built directed and pseudo-random testbenches plus assertion properties for key output-safety invariants.
- Simulated with [actual simulator] and recorded [actual verified results]; inspected waveforms using [actual viewer].

Do not claim simulation, assertion, synthesis, timing, or FPGA results until you have actually run the relevant tools.
