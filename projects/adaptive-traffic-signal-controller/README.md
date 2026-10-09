# Adaptive Traffic Signal Controller Using SystemVerilog

An educational RTL project for a two-road traffic controller. Green-light time adapts to encoded vehicle-demand inputs, and emergency request inputs can prioritize a road at the next safe transition.

## Features
- Finite-state machine (FSM) for north-south and east-west traffic lights.
- Demand-based green duration bounded by configurable minimum and maximum values.
- Emergency-request inputs for either road.
- Yellow and all-red transition intervals.
- Testbench check that fails if both roads are green simultaneously.
- VCD waveform generation for visual inspection.

## Folder structure
```text
projects/adaptive-traffic-signal-controller/
├── rtl/adaptive_traffic_controller.sv
├── tb/tb_adaptive_traffic_controller.sv
└── README.md
```

## Light encoding
- `00`: RED
- `01`: YELLOW
- `10`: GREEN

## Main signals
| Signal | Direction | Purpose |
|---|---|---|
| `clk` | Input | Clock |
| `rst_n` | Input | Active-low asynchronous reset |
| `north_south_count[3:0]` | Input | Encoded demand for north-south road |
| `east_west_count[3:0]` | Input | Encoded demand for east-west road |
| `ns_emergency` | Input | Emergency request for north-south road |
| `ew_emergency` | Input | Emergency request for east-west road |
| `ns_light[1:0]` | Output | North-south signal code |
| `ew_light[1:0]` | Output | East-west signal code |
| `emergency_mode` | Output | High while either emergency request is asserted |

## Green timing
The design calculates the green duration as `GREEN_MIN_CYCLES + demand`, capped at `GREEN_MAX_CYCLES`. These are clock cycles, not real-world seconds. To use actual timing, derive suitable cycle counts from the chosen FPGA clock frequency.

## Simulate with Cadence Xcelium
From the repository root:
```bash
xrun -sv projects/adaptive-traffic-signal-controller/rtl/adaptive_traffic_controller.sv projects/adaptive-traffic-signal-controller/tb/tb_adaptive_traffic_controller.sv -access +rwc
```

## Simulate with Icarus Verilog (if installed)
```bash
iverilog -g2012 -o traffic_sim projects/adaptive-traffic-signal-controller/rtl/adaptive_traffic_controller.sv projects/adaptive-traffic-signal-controller/tb/tb_adaptive_traffic_controller.sv
vvp traffic_sim
```
A `traffic_controller.vcd` waveform should be generated. View it with GTKWave or another VCD viewer.

## Suggested verification
1. Confirm reset starts with north-south green.
2. Confirm the two roads are never green simultaneously.
3. Observe yellow and all-red phases between green phases.
4. Try different demand inputs and compare green durations.
5. Assert each emergency request and observe the controller transition toward that road.
6. Test the case where both emergency inputs are asserted and document the chosen policy.

## Limitations and safety
This is a learning prototype, not a certified traffic-control system. The vehicle-demand inputs are abstract digital values, not physical sensor measurements. Real hardware requires input synchronization, sensor validation, fault handling, independent safety interlocks, timing analysis, and compliance with applicable standards. The included simulation testbench is not a substitute for formal verification or hardware testing.

## Resume bullet (only after running and verifying)
**Adaptive Traffic Signal Controller Using SystemVerilog**
- Designed an FSM-based traffic controller with demand-adjusted green timing and emergency-request handling.
- Developed a SystemVerilog testbench to exercise traffic scenarios and check for conflicting green signals.
- Simulated with [actual simulator] and inspected timing waveforms using [actual viewer].
