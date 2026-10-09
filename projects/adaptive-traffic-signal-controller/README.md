# Adaptive Traffic Signal Controller

The latest working direction for this project is documented under **Advanced Adaptive Traffic Management Controller**.

**Start here:** [Advanced Adaptive Traffic Management project](../advanced-adaptive-traffic-management/README.md)

## Earlier controller implementations
This folder contains earlier RTL experiments:
- `rtl/adaptive_traffic_controller.sv` — baseline controller.
- `tb/tb_adaptive_traffic_controller.sv` — baseline testbench.
- `advanced/` — expanded controller with pedestrian and emergency handling.

The advanced project folder provides a cleaner project entry point with controller RTL, a simulation testbench, assertion properties, run commands, and a verification checklist.

## Status
Code and documentation have been published to GitHub. Simulation, formal verification, synthesis, timing analysis, and FPGA testing must be run separately before claiming verified results.

This is an educational design, not a certified traffic controller. Do not connect it to public-road traffic signals.
