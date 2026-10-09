# Next-Stage Engineering Plan

This document separates current repository contents from unimplemented work.

## Processor subsystem
- Integrate a real RISC-V soft CPU, on-chip memory, boot ROM, and bus interconnect.
- Connect the traffic register bank through a documented memory map.
- Add a startup program, linker script, peripheral driver, and interrupt handling.
- Test the firmware in simulation before trying it on a board.

## RTL verification
- Run the current smoke-test script and preserve all logs.
- Add independent timing for AXI write address and write data.
- Add response backpressure, byte-strobe, reset-during-transaction, and invalid-address cases.
- Run assertion-based checks and a supported formal tool.
- Review parameter corner cases and clock-domain crossings.

## FPGA implementation
- Select a specific FPGA board and exact device.
- Replace the constraint template with board-verified clock and pin constraints.
- Run synthesis, place-and-route, timing analysis, and CDC review.
- Record tool versions, utilization, worst slack, and the bitstream hash.

## Better traffic modeling
- Add platoon arrivals, turning movements, multiple lanes, spillback, detector noise, and pedestrian demand.
- Compare across multiple seeds and preserve all scenario outputs.
- Validate model assumptions against an established traffic simulator before drawing real-world conclusions.

## Release checklist
A credible release includes the exact source revision, reproducible commands, passing logs, reviewed warnings, benchmark JSON, synthesis and timing reports, and a tabletop demo record. A workflow definition alone is not evidence of a passing run.
