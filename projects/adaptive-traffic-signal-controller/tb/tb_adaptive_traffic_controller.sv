`timescale 1ns/1ps

module tb_adaptive_traffic_controller;
    logic clk = 0, rst_n = 0;
    logic [3:0] north_south_count = 0, east_west_count = 0;
    logic ns_emergency = 0, ew_emergency = 0;
    logic [1:0] ns_light, ew_light;
    logic emergency_mode;
    localparam logic [1:0] RED=2'b00, YELLOW=2'b01, GREEN=2'b10;

    adaptive_traffic_controller #(
        .GREEN_MIN_CYCLES(4), .GREEN_MAX_CYCLES(12),
        .YELLOW_CYCLES(2), .ALL_RED_CYCLES(1)
    ) dut (
        .clk(clk), .rst_n(rst_n),
        .north_south_count(north_south_count),
        .east_west_count(east_west_count),
        .ns_emergency(ns_emergency), .ew_emergency(ew_emergency),
        .ns_light(ns_light), .ew_light(ew_light),
        .emergency_mode(emergency_mode)
    );

    always #5 clk = ~clk;

    always @(negedge clk) begin
        if (rst_n && ns_light == GREEN && ew_light == GREEN) begin
            $error("FAIL: both roads are green at %0t", $time);
            $fatal(1);
        end
    end

    initial begin
        $dumpfile("traffic_controller.vcd");
        $dumpvars(0, tb_adaptive_traffic_controller);
        $display("Starting adaptive traffic controller test.");
        repeat (2) @(negedge clk);
        rst_n = 1;

        north_south_count = 1;
        east_west_count = 7;
        repeat (18) @(negedge clk);

        $display("Requesting EW emergency");
        ew_emergency = 1;
        repeat (8) @(negedge clk);
        ew_emergency = 0;

        $display("Requesting NS emergency");
        ns_emergency = 1;
        repeat (8) @(negedge clk);
        ns_emergency = 0;

        north_south_count = 8;
        east_west_count = 2;
        repeat (24) @(negedge clk);

        $display("PASS: no conflicting green lights observed.");
        $display("Inspect traffic_controller.vcd for timing waveforms.");
        $finish;
    end
endmodule
