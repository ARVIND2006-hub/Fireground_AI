`timescale 1ns/1ps

module tb_adaptive_traffic_controller_advanced;
    logic clk = 0, rst_n = 0;
    logic [3:0] north_south_demand = 0, east_west_demand = 0;
    logic ns_emergency_async = 0, ew_emergency_async = 0;
    logic ped_cross_ns_async = 0, ped_cross_ew_async = 0;
    logic sensor_data_valid = 1;
    logic [1:0] ns_light, ew_light;
    logic ped_walk_ns, ped_walk_ew, emergency_active, fault_active;

    localparam logic [1:0] RED=2'b00, YELLOW=2'b01, GREEN=2'b10;

    adaptive_traffic_controller_advanced #(
        .GREEN_MIN_CYCLES(4), .GREEN_MAX_CYCLES(20),
        .GREEN_SCALE(2), .YELLOW_CYCLES(3),
        .ALL_RED_CYCLES(2), .PED_WALK_CYCLES(8)
    ) dut (
        .clk(clk), .rst_n(rst_n),
        .north_south_demand(north_south_demand),
        .east_west_demand(east_west_demand),
        .ns_emergency_async(ns_emergency_async),
        .ew_emergency_async(ew_emergency_async),
        .ped_cross_ns_async(ped_cross_ns_async),
        .ped_cross_ew_async(ped_cross_ew_async),
        .sensor_data_valid(sensor_data_valid),
        .ns_light(ns_light), .ew_light(ew_light),
        .ped_walk_ns(ped_walk_ns), .ped_walk_ew(ped_walk_ew),
        .emergency_active(emergency_active), .fault_active(fault_active)
    );

    always #5 clk = ~clk;

    // Continuously check important output safety invariants.
    always @(negedge clk) begin
        if (rst_n) begin
            if (ns_light == GREEN && ew_light == GREEN) begin
                $error("FAIL: conflicting green lights at %0t", $time);
                $fatal(1);
            end
            if ((ped_walk_ns || ped_walk_ew) &&
                (ns_light != RED || ew_light != RED)) begin
                $error("FAIL: pedestrian walk active while a road is not red at %0t", $time);
                $fatal(1);
            end
            if (ped_walk_ns && ped_walk_ew) begin
                $error("FAIL: both pedestrian crossings active together at %0t", $time);
                $fatal(1);
            end
            if (fault_active && (ns_light != RED || ew_light != RED ||
                                 ped_walk_ns || ped_walk_ew)) begin
                $error("FAIL: unsafe output during fault state at %0t", $time);
                $fatal(1);
            end
        end
    end

    initial begin
        $dumpfile("traffic_controller_advanced.vcd");
        $dumpvars(0, tb_adaptive_traffic_controller_advanced);
        $display("Starting advanced traffic controller test.");

        repeat (3) @(negedge clk);
        rst_n = 1;

        // Demand-adaptive normal operation.
        north_south_demand = 2;
        east_west_demand = 7;
        repeat (30) @(negedge clk);

        // Pedestrian crossing requests; pulse long enough for synchronization.
        ped_cross_ns_async = 1;
        repeat (4) @(negedge clk);
        ped_cross_ns_async = 0;
        ped_cross_ew_async = 1;
        repeat (4) @(negedge clk);
        ped_cross_ew_async = 0;
        repeat (35) @(negedge clk);

        // Emergency request should be synchronized and prioritized at a safe transition.
        ew_emergency_async = 1;
        repeat (12) @(negedge clk);
        ew_emergency_async = 0;
        repeat (20) @(negedge clk);

        // Invalid sensor status should force a latched all-red fault state.
        sensor_data_valid = 0;
        repeat (4) @(negedge clk);
        if (!fault_active) begin
            $error("FAIL: invalid sensor data did not enter fault state");
            $fatal(1);
        end
        sensor_data_valid = 1;
        repeat (4) @(negedge clk);
        if (!fault_active) begin
            $error("FAIL: fault state should remain latched until reset");
            $fatal(1);
        end

        $display("PASS: safety invariants held in the exercised scenarios.");
        $display("Note: this testbench is not formal verification or hardware certification.");
        $finish;
    end
endmodule
