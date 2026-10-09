`timescale 1ns/1ps

module tb_water_pressure_monitor;
    logic clk = 0;
    logic rst_n = 0;
    logic sensor_valid = 0;
    logic [11:0] pressure_adc = 0;
    logic pressure_low_alarm, pressure_high_alarm;
    logic pressure_sensor_fault, pressure_normal;

    water_pressure_monitor #(
        .LOW_PRESSURE_THRESHOLD(12'd900),
        .HIGH_PRESSURE_THRESHOLD(12'd2800)
    ) dut (
        .clk(clk), .rst_n(rst_n),
        .sensor_valid(sensor_valid), .pressure_adc(pressure_adc),
        .pressure_low_alarm(pressure_low_alarm),
        .pressure_high_alarm(pressure_high_alarm),
        .pressure_sensor_fault(pressure_sensor_fault),
        .pressure_normal(pressure_normal)
    );

    always #5 clk = ~clk;

    task automatic check(input logic condition, input string message);
        if (!condition) begin
            $error("FAIL: %s at time %0t", message, $time);
            $fatal(1);
        end
    endtask

    initial begin
        $dumpfile("water_pressure_monitor.vcd");
        $dumpvars(0, tb_water_pressure_monitor);

        repeat (2) @(negedge clk);
        rst_n = 1;

        // Sensor invalid: fault is asserted and normal status is cleared.
        sensor_valid = 0;
        @(negedge clk);
        check(pressure_sensor_fault && !pressure_normal,
              "invalid sensor must raise fault and not report normal");

        // Low pressure.
        sensor_valid = 1;
        pressure_adc = 12'd700;
        @(negedge clk);
        check(pressure_low_alarm && !pressure_high_alarm && !pressure_normal,
              "low-pressure classification");

        // Normal range.
        pressure_adc = 12'd1500;
        @(negedge clk);
        check(!pressure_low_alarm && !pressure_high_alarm && pressure_normal,
              "normal-pressure classification");

        // High pressure.
        pressure_adc = 12'd3200;
        @(negedge clk);
        check(!pressure_low_alarm && pressure_high_alarm && !pressure_normal,
              "high-pressure classification");

        $display("PASS: pressure thresholds and sensor-fault cases checked.");
        $display("Inspect water_pressure_monitor.vcd for waveforms.");
        $finish;
    end
endmodule
