# Adaptive Traffic Signal Controller — SystemVerilog RTL

An educational RTL project exploring demand-adaptive traffic lights, emergency priority, pedestrian crossing requests, asynchronous input synchronization, and fail-safe handling.

## Recommended version: Advanced
The expanded version is in the `advanced/` folder and adds:
- Green timing adjusted by encoded vehicle demand.
- Emergency requests with safe yellow/all-red transitions.
- Latched pedestrian crossing requests and dedicated walk phases.
- Two-flop synchronizers for asynchronous emergency and pedestrian controls.
- A latched all-red fault state when sensor data is marked invalid.
- Testbench checks for conflicting green lights, pedestrian safety, and fault-state outputs.

**Start here:** [Advanced project documentation](advanced/README.md)

### Advanced source files
- [Advanced RTL module](advanced/rtl/adaptive_traffic_controller_advanced.sv)
- [Advanced verification testbench](advanced/tb/tb_adaptive_traffic_controller_advanced.sv)

## Original baseline version
The original implementation remains in place:
- `rtl/adaptive_traffic_controller.sv`
- `tb/tb_adaptive_traffic_controller.sv`

It demonstrates a simpler FSM with demand-based green duration and emergency-request inputs.

## Run the advanced simulation with Cadence Xcelium
From the repository root:
```bash
xrun -sv projects/adaptive-traffic-signal-controller/advanced/rtl/adaptive_traffic_controller_advanced.sv projects/adaptive-traffic-signal-controller/advanced/tb/tb_adaptive_traffic_controller_advanced.sv -access +rwc
```

## Run with Icarus Verilog
If installed with SystemVerilog support:
```bash
iverilog -g2012 -o traffic_advanced_sim projects/adaptive-traffic-signal-controller/advanced/rtl/adaptive_traffic_controller_advanced.sv projects/adaptive-traffic-signal-controller/advanced/tb/tb_adaptive_traffic_controller_advanced.sv
vvp traffic_advanced_sim
```
A `traffic_controller_advanced.vcd` waveform should be generated for GTKWave or another VCD viewer.

## Engineering limitations
This is an educational RTL prototype, not a certified traffic-control product. Demand inputs are abstract digital values rather than actual detector interfaces. Real hardware needs validated sensor interfaces, synchronizers and filters as appropriate, fault analysis, independently validated safety interlocks, and applicable standards compliance. Emergency tie-breaking and pulse-capture behavior need further design review for production use.

The files have been published to GitHub, but do not claim simulation or FPGA validation until you have actually run the tools and inspected the results.
