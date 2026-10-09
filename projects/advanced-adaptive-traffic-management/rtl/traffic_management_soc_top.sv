`timescale 1ns/1ps
// Processor-facing top-level integration for the educational traffic SoC.
// An external AXI4-Lite master (e.g. a soft CPU) configures the controller.
module traffic_management_soc_top #(
    parameter integer AXI_ADDR_WIDTH = 6,
    parameter integer AXI_DATA_WIDTH = 32
) (
    input logic aclk,
    input logic aresetn,

    input logic [AXI_ADDR_WIDTH-1:0] s_axi_awaddr,
    input logic s_axi_awvalid,
    output logic s_axi_awready,
    input logic [AXI_DATA_WIDTH-1:0] s_axi_wdata,
    input logic [AXI_DATA_WIDTH/8-1:0] s_axi_wstrb,
    input logic s_axi_wvalid,
    output logic s_axi_wready,
    output logic [1:0] s_axi_bresp,
    output logic s_axi_bvalid,
    input logic s_axi_bready,

    input logic [AXI_ADDR_WIDTH-1:0] s_axi_araddr,
    input logic s_axi_arvalid,
    output logic s_axi_arready,
    output logic [AXI_DATA_WIDTH-1:0] s_axi_rdata,
    output logic [1:0] s_axi_rresp,
    output logic s_axi_rvalid,
    input logic s_axi_rready,

    output logic [1:0] ns_light,
    output logic [1:0] ew_light,
    output logic ped_walk_ns,
    output logic ped_walk_ew,
    output logic emergency_active,
    output logic fault_active,
    output logic [3:0] debug_state,
    output logic [7:0] debug_timer
);
    logic sensor_data_valid;
    logic [3:0] ns_demand, ew_demand;
    logic ns_emergency_request, ew_emergency_request;
    logic ped_ns_request, ped_ew_request;

    axi4lite_traffic_registers #(
        .ADDR_WIDTH(AXI_ADDR_WIDTH),
        .DATA_WIDTH(AXI_DATA_WIDTH)
    ) u_registers (
        .aclk(aclk), .aresetn(aresetn),
        .s_axi_awaddr(s_axi_awaddr), .s_axi_awvalid(s_axi_awvalid),
        .s_axi_awready(s_axi_awready),
        .s_axi_wdata(s_axi_wdata), .s_axi_wstrb(s_axi_wstrb),
        .s_axi_wvalid(s_axi_wvalid), .s_axi_wready(s_axi_wready),
        .s_axi_bresp(s_axi_bresp), .s_axi_bvalid(s_axi_bvalid),
        .s_axi_bready(s_axi_bready),
        .s_axi_araddr(s_axi_araddr), .s_axi_arvalid(s_axi_arvalid),
        .s_axi_arready(s_axi_arready),
        .s_axi_rdata(s_axi_rdata), .s_axi_rresp(s_axi_rresp),
        .s_axi_rvalid(s_axi_rvalid), .s_axi_rready(s_axi_rready),
        .sensor_data_valid(sensor_data_valid),
        .ns_demand(ns_demand), .ew_demand(ew_demand),
        .ns_emergency_request(ns_emergency_request),
        .ew_emergency_request(ew_emergency_request),
        .ped_ns_request(ped_ns_request), .ped_ew_request(ped_ew_request),
        .ns_light(ns_light), .ew_light(ew_light),
        .ped_walk_ns(ped_walk_ns), .ped_walk_ew(ped_walk_ew),
        .emergency_active(emergency_active), .fault_active(fault_active),
        .debug_state(debug_state), .debug_timer(debug_timer)
    );

    advanced_traffic_management_controller u_controller (
        .clk(aclk), .rst_n(aresetn),
        .ns_demand(ns_demand), .ew_demand(ew_demand),
        .sensor_data_valid(sensor_data_valid),
        .ns_emergency_async(ns_emergency_request),
        .ew_emergency_async(ew_emergency_request),
        .ped_ns_async(ped_ns_request), .ped_ew_async(ped_ew_request),
        .ns_light(ns_light), .ew_light(ew_light),
        .ped_walk_ns(ped_walk_ns), .ped_walk_ew(ped_walk_ew),
        .emergency_active(emergency_active), .fault_active(fault_active),
        .debug_state(debug_state), .debug_timer(debug_timer)
    );
endmodule
