`timescale 1ns/1ps

// Educational pressure-monitoring logic for a fire-truck / hose telemetry node.
// pressure_adc is the calibrated digital value from an external pressure sensor
// and ADC. Thresholds are board/application-specific and must be calibrated.
module water_pressure_monitor #(
    parameter logic [11:0] LOW_PRESSURE_THRESHOLD  = 12'd900,
    parameter logic [11:0] HIGH_PRESSURE_THRESHOLD = 12'd2800
) (
    input  logic        clk,
    input  logic        rst_n,
    input  logic        sensor_valid,
    input  logic [11:0] pressure_adc,
    output logic        pressure_low_alarm,
    output logic        pressure_high_alarm,
    output logic        pressure_sensor_fault,
    output logic        pressure_normal
);

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pressure_low_alarm  <= 1'b0;
            pressure_high_alarm <= 1'b0;
            pressure_sensor_fault <= 1'b1;
            pressure_normal     <= 1'b0;
        end else begin
            pressure_sensor_fault <= !sensor_valid;

            // Invalid sensor data must not be reported as normal.
            if (!sensor_valid) begin
                pressure_low_alarm  <= 1'b0;
                pressure_high_alarm <= 1'b0;
                pressure_normal     <= 1'b0;
            end else begin
                pressure_low_alarm  <= (pressure_adc < LOW_PRESSURE_THRESHOLD);
                pressure_high_alarm <= (pressure_adc > HIGH_PRESSURE_THRESHOLD);
                pressure_normal     <= (pressure_adc >= LOW_PRESSURE_THRESHOLD) &&
                                       (pressure_adc <= HIGH_PRESSURE_THRESHOLD);
            end
        end
    end
endmodule
