`timescale 1ns/1ps
// Integrated low-voltage tabletop demonstration top.
// This is a separate sensor-driven top; it does not replace the AXI SoC top.
// Watchdog faults invalidate sensor_data_valid, which drives the controller
// into its latched all-red fault state. Recovery therefore requires reset.
module traffic_management_physical_top #(
    parameter integer DEBOUNCE_CYCLES = 4,
    parameter integer DEMAND_DECAY_CYCLES = 1000,
    parameter integer WATCHDOG_TIMEOUT_CYCLES = 100000
) (
    input logic clk,
    input logic rst_n,
    input logic vehicle_ns_async,
    input logic vehicle_ew_async,
    input logic emergency_ns_async,
    input logic emergency_ew_async,
    input logic ped_ns_async,
    input logic ped_ew_async,
    input logic heartbeat,
    input logic external_sensor_valid,
    input logic clear_watchdog_fault,
    output logic [1:0] ns_light,
    output logic [1:0] ew_light,
    output logic ped_walk_ns,
    output logic ped_walk_ew,
    output logic emergency_active,
    output logic fault_active,
    output logic watchdog_fault,
    output logic [31:0] heartbeat_age,
    output logic [3:0] ns_demand,
    output logic [3:0] ew_demand,
    output logic [3:0] debug_state,
    output logic [7:0] debug_timer
);
    logic emergency_ns_clean, emergency_ew_clean;
    logic pedestrian_ns_clean, pedestrian_ew_clean;
    logic sensor_frontend_healthy;
    logic controller_sensor_valid;

    traffic_sensor_frontend #(
        .DEBOUNCE_CYCLES(DEBOUNCE_CYCLES),
        .DEMAND_DECAY_CYCLES(DEMAND_DECAY_CYCLES)
    ) u_sensor_frontend (
        .clk(clk), .rst_n(rst_n),
        .vehicle_ns_async(vehicle_ns_async),
        .vehicle_ew_async(vehicle_ew_async),
        .emergency_ns_async(emergency_ns_async),
        .emergency_ew_async(emergency_ew_async),
        .ped_ns_async(ped_ns_async),
        .ped_ew_async(ped_ew_async),
        .ns_demand(ns_demand), .ew_demand(ew_demand),
        .emergency_ns(emergency_ns_clean),
        .emergency_ew(emergency_ew_clean),
        .pedestrian_ns(pedestrian_ns_clean),
        .pedestrian_ew(pedestrian_ew_clean),
        .sensor_frontend_healthy(sensor_frontend_healthy)
    );

    traffic_watchdog #(
        .TIMEOUT_CYCLES(WATCHDOG_TIMEOUT_CYCLES)
    ) u_watchdog (
        .clk(clk), .rst_n(rst_n),
        .heartbeat(heartbeat),
        .sensor_data_valid(external_sensor_valid && sensor_frontend_healthy),
        .clear_fault(clear_watchdog_fault),
        .watchdog_fault(watchdog_fault),
        .heartbeat_age(heartbeat_age)
    );

    assign controller_sensor_valid =
        external_sensor_valid && sensor_frontend_healthy && !watchdog_fault;

    advanced_traffic_management_controller u_controller (
        .clk(clk), .rst_n(rst_n),
        .ns_demand(ns_demand), .ew_demand(ew_demand),
        .sensor_data_valid(controller_sensor_valid),
        .ns_emergency_async(emergency_ns_clean),
        .ew_emergency_async(emergency_ew_clean),
        .ped_ns_async(pedestrian_ns_clean),
        .ped_ew_async(pedestrian_ew_clean),
        .ns_light(ns_light), .ew_light(ew_light),
        .ped_walk_ns(ped_walk_ns), .ped_walk_ew(ped_walk_ew),
        .emergency_active(emergency_active), .fault_active(fault_active),
        .debug_state(debug_state), .debug_timer(debug_timer)
    );
endmodule
