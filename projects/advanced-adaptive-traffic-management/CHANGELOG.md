# Changelog

## Repository enhancement set

### Architecture and RTL
- Added a demand-adaptive two-road controller with startup all-red, emergency/pedestrian requests, fault latching, and debug visibility.
- Added an AXI4-Lite memory-mapped register bank.
- Added a processor-facing top-level wrapper.
- Added C register helpers and a firmware example skeleton. A RISC-V CPU core itself is not included.

### Verification and automation
- Added a controller simulation testbench and basic AXI/SoC smoke testbench.
- Added an SVA checker source file for a compatible simulator.
- Added a shell runner for Icarus Verilog.
- Added a static register-offset consistency checker.
- Added a GitHub Actions workflow to run the checks on relevant pushes and pull requests.
- Added an optional generic Yosys synthesis/structural-check script.

### Documentation
- Added register-map JSON, architecture guide, verification matrix, and release-readiness checklist.
- Updated the root repository README with links to this project.

## Validation status
These files were committed to GitHub, but no HDL simulation, SVA/formal verification, Yosys synthesis, FPGA implementation, or hardware test has been executed by the assistant. Check actual CI results and run the appropriate tools before reporting validation.


### Additional advanced extensions
- Added standalone sensor front-end RTL with synchronized vehicle events, debounced human inputs, saturating demand estimates, and slow decay.
- Added standalone heartbeat/sensor-valid watchdog diagnostic RTL.
- Added unit-test benches for both new RTL modules and extended the smoke-test runner.
- Added a seeded Python queueing digital twin comparing fixed and adaptive signal policies, with unit tests and JSON metrics output.
- Added CI steps for Python tests and a sample digital-twin run.
- Added FPGA constraint template, bring-up checklist, and performance-metric definitions.
- Added a local browser dashboard for loading and comparing JSON simulation reports.

Validation remains pending: the assistant has not executed HDL simulation, Python tests, synthesis, place-and-route, or physical hardware tests. CI results must be checked before claiming a pass.


### Integrated physical demonstration and benchmark matrix
- Added a separate sensor-driven top that connects vehicle sensing, button conditioning, watchdog diagnostics, and the traffic controller.
- Added an integrated-top testbench for invalid-sensor fault behavior and all-red vehicle outputs.
- Expanded the smoke-test runner to compile and invoke five HDL testbenches.
- Added multi-scenario, multi-seed software benchmark generation and unit tests.
- Configured CI to produce and upload JSON benchmark reports when the workflow succeeds.
- Added integration, benchmark protocol, and next-stage engineering documentation.

No local HDL simulator was available in the execution environment, so the newly added HDL tests have not been run here. Check the GitHub Actions run for actual results.
