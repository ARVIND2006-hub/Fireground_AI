`timescale 1ns/1ps
module tb_traffic_management_physical_top;
    logic clk=0, rst_n=0;
    logic vehicle_ns_async=0, vehicle_ew_async=0;
    logic emergency_ns_async=0, emergency_ew_async=0;
    logic ped_ns_async=0, ped_ew_async=0;
    logic heartbeat=0, external_sensor_valid=1, clear_watchdog_fault=0;
    wire [1:0] ns_light, ew_light;
    wire ped_walk_ns, ped_walk_ew, emergency_active, fault_active, watchdog_fault;
    wire [31:0] heartbeat_age;
    wire [3:0] ns_demand, ew_demand, debug_state;
    wire [7:0] debug_timer;

    traffic_management_physical_top #(
        .DEBOUNCE_CYCLES(2),
        .DEMAND_DECAY_CYCLES(100),
        .WATCHDOG_TIMEOUT_CYCLES(20)
    ) dut (.*);
    always #5 clk=~clk;

    task automatic beat;
      begin
        @(negedge clk); heartbeat=1;
        repeat(3) @(negedge clk);
        heartbeat=0;
        repeat(3) @(negedge clk);
      end
    endtask

    initial begin
        repeat(3) @(negedge clk); rst_n=1;
        // Keep the watchdog alive while startup completes.
        repeat(4) beat();
        if (fault_active) $fatal(1,"unexpected fault while heartbeat is active");
        // Invalid external sensor status must latch controller fault/all-red.
        external_sensor_valid=0;
        repeat(5) @(negedge clk);
        if (!fault_active) $fatal(1,"controller did not latch invalid-sensor fault");
        if (ns_light !== 2'b00 || ew_light !== 2'b00)
            $fatal(1,"fault state must show both vehicle approaches red");
        if (ped_walk_ns || ped_walk_ew)
            $fatal(1,"pedestrian walk output must be off in fault state");
        $display("PASS: physical-top sensor fault path and all-red output smoke test.");
        $finish;
    end
endmodule
