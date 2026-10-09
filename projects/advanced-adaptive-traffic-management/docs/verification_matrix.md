# Verification Matrix and Release Readiness

| Area | Existing artifact | What it currently checks | Not yet established |
|---|---|---|---|
| Controller behavior | Controller testbench | Directed and randomized inputs; output interlock monitors | Full state/transition coverage, formal proof, all corner cases |
| AXI register access | AXI smoke testbench | Basic reads/writes of demand/control/status/debug registers | Full AXI4-Lite protocol compliance and backpressure coverage |
| Register documentation | Static Python checker | JSON, RTL, and C header register offsets agree | All bitfields and access semantics match automatically |
| Continuous integration | GitHub Actions workflow | Attempts to run smoke tests on relevant pushes/PRs | A passing run until a run result is available |
| SVA | Assertion checker source | Properties are written for an SVA-capable simulator | Assertions compiled and proven by a compatible tool |
| Synthesis | No validated report committed | None | Area, timing, inferred latches, critical paths |
| FPGA hardware | No board validation recorded | None | Pin constraints, clock constraints, timing closure, physical I/O testing |

## Release gate

Do not label a release as verified until the relevant evidence is attached:
- simulator and version;
- exact compile/run commands and exit status;
- test output and waveform;
- assertion/formal logs where applicable;
- synthesis reports and timing constraints;
- board model, pin map, clock source, and hardware test record if FPGA tested.

## Safe demonstration scope

Use only a low-voltage tabletop model with appropriate drivers and isolation. This educational design is not certified for road infrastructure or any safety-critical deployment.
