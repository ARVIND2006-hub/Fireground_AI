# Advanced Adaptive Traffic Signal Controller

This is an expanded SystemVerilog RTL prototype that adds pedestrian request handling, synchronized asynchronous control inputs, emergency priority, demand-adaptive green timing, and a latched fail-safe state for invalid sensor data.

## Advanced features
- **Demand-adaptive green time:** green duration is `GREEN_MIN_CYCLES + demand × GREEN_SCALE`, capped at `GREEN_MAX_CYCLES`.
- **Emergency preemption:** an emergency request can trigger a safe transition through yellow and all-red before serving the requested road.
- **Pedestrian requests:** synchronized crossing requests are latched until a dedicated pedestrian phase; vehicle lights remain red during the walk interval.
- **Input synchronization:** two-flop synchronizers are used for asynchronous emergency and pedestrian inputs.
- **Fail-safe sensor status:** when `sensor_data_valid` becomes low, the controller enters a latched all-red fault state. Reset is required to recover after sensor validity returns.
- **Safety-oriented testbench:** checks that both roads are never green simultaneously, pedestrian walk outputs only occur when both roads are red, both pedestrian phases are not active together, and the fault state keeps all outputs safe.

## Files
- `rtl/adaptive_traffic_controller_advanced.sv` — advanced controller RTL.
- `tb/tb_adaptive_traffic_controller_advanced.sv` — testbench.

## Simulate with Cadence Xcelium
Run from the repository root:
```bash
xrun -sv projects/adaptive-traffic-signal-controller/advanced/rtl/adaptive_traffic_controller_advanced.sv projects/adaptive-traffic-signal-controller/advanced/tb/tb_adaptive_traffic_controller_advanced.sv -access +rwc
```

## Simulate with Icarus Verilog
If installed with SystemVerilog support:
```bash
iverilog -g2012 -o traffic_advanced_sim projects/adaptive-traffic-signal-controller/advanced/rtl/adaptive_traffic_controller_advanced.sv projects/adaptive-traffic-signal-controller/advanced/tb/tb_adaptive_traffic_controller_advanced.sv
vvp traffic_advanced_sim
```
The simulation writes `traffic_controller_advanced.vcd`. Open the waveform with GTKWave or another VCD viewer.

## Important limitations
- Demand inputs are assumed to be stable and synchronous to `clk`; real sensor interfaces need appropriate synchronization, filtering, and validation.
- Emergency requests are synchronized but pulse capture depends on the input pulse lasting long enough to be sampled. A production design should use a handshake or pulse-stretching circuit.
- If both emergency inputs are active together, the controller follows its normal demand/pedestrian selection logic; a deployment must define and verify an explicit tie-break policy.
- The design is an educational prototype, not a certified road traffic controller. It has not been represented as simulated or hardware-tested until you run the testbench and verify its outputs.

## Resume description (only after simulation)
**Advanced Adaptive Traffic Signal Controller with Pedestrian and Emergency Handling**
- Developed SystemVerilog FSM logic for demand-adaptive signal timing, emergency requests, and pedestrian crossing phases.
- Added synchronizers for asynchronous control inputs and a fail-safe all-red state for invalid sensor status.
- Created a testbench to check traffic-light conflict, pedestrian-phase, and fault-state invariants.
- Verified using [simulator] and inspected waveforms using [viewer].
