# System Architecture and Integration Roadmap

## Data path

```text
External sensors / emergency buttons / pedestrian buttons
                         |
              input conditioning layer
                         |
       AXI4-Lite register bank <---- soft CPU / bus master
                         |
              traffic controller FSM
                         |
       isolated signal-driver interface (future)
                         |
              lamps / model intersection

Status and debug registers flow back to the processor for telemetry.
```

## RTL modules

- `advanced_traffic_management_controller.sv`: finite-state-machine traffic controller.
- `axi4lite_traffic_registers.sv`: control, demand, status, and debug registers.
- `traffic_management_soc_top.sv`: connects the register bank and controller.
- `traffic_sensor_frontend.sv`: standalone synchronizers, button debouncers, and saturating demand score estimator.
- `traffic_watchdog.sv`: standalone heartbeat timeout and sensor-valid diagnostic latch.
- `tb_advanced_traffic_management_controller.sv`: controller-level stimulus and output monitors.
- `tb_traffic_management_axi.sv`: basic register access smoke test.

## Integration sequence

1. Compile and elaborate all RTL with the selected simulator.
2. Run the controller testbench and inspect all failures and waveforms.
3. Run the AXI smoke test; then add protocol tests for independent AW/W timing, backpressure, byte strobes, reset, and repeated transactions.
4. Run the assertion checker in a simulator that supports the required SystemVerilog Assertions syntax.
5. Synthesize the top module and inspect latches, inferred memories, resource usage, timing constraints, and critical paths.
6. Connect a soft processor or external AXI4-Lite master and assign a peripheral base address in the platform address map.
7. The repository now has a standalone sensor front end and watchdog example; integrate them only after defining the intended sensor and fault semantics. Add pulse capture/handshakes for narrow asynchronous events.
8. Drive a low-voltage tabletop model through suitable isolated driver circuitry. Do not connect this educational RTL to public-road signal equipment.

## Important design gaps

This repository is an educational prototype. It is not safety-certified. The current register bank is a lightweight learning implementation and needs protocol review and more exhaustive verification. The sensor front end and watchdog are currently separate examples, not wired into the SoC top. The current controller does not implement full pedestrian clearance intervals, watchdog recovery integration, redundant safety channels, or a standards-compliant signal plan. Asynchronous request pulses may be missed unless stretched or captured by a handshake/toggle scheme. Reset release and clock-domain boundaries must be designed for the target platform.
