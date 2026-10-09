`timescale 1ns/1ps
// Minimal AXI4-Lite register bank for the educational traffic-management SoC.
// Register map (word aligned):
// 0x00 CONTROL: bit0 sensor_valid, bit1 NS emergency request,
//               bit2 EW emergency request, bit3 NS pedestrian request,
//               bit4 EW pedestrian request. Requests remain asserted until
//               software clears them, allowing edge capture in the controller.
// 0x04 DEMAND:  bits[3:0] NS demand, bits[7:4] EW demand.
// 0x08 STATUS: read-only: lights, pedestrian outputs, emergency and fault.
// 0x0C DEBUG:  read-only: debug_state[3:0], debug_timer[7:0].
// This is a learning implementation; validate AXI corner cases before reuse.
module axi4lite_traffic_registers #(
    parameter integer ADDR_WIDTH = 6,
    parameter integer DATA_WIDTH = 32
) (
    input logic aclk,
    input logic aresetn,
    input logic [ADDR_WIDTH-1:0] s_axi_awaddr,
    input logic s_axi_awvalid,
    output logic s_axi_awready,
    input logic [DATA_WIDTH-1:0] s_axi_wdata,
    input logic [DATA_WIDTH/8-1:0] s_axi_wstrb,
    input logic s_axi_wvalid,
    output logic s_axi_wready,
    output logic [1:0] s_axi_bresp,
    output logic s_axi_bvalid,
    input logic s_axi_bready,
    input logic [ADDR_WIDTH-1:0] s_axi_araddr,
    input logic s_axi_arvalid,
    output logic s_axi_arready,
    output logic [DATA_WIDTH-1:0] s_axi_rdata,
    output logic [1:0] s_axi_rresp,
    output logic s_axi_rvalid,
    input logic s_axi_rready,

    output logic sensor_data_valid,
    output logic [3:0] ns_demand,
    output logic [3:0] ew_demand,
    output logic ns_emergency_request,
    output logic ew_emergency_request,
    output logic ped_ns_request,
    output logic ped_ew_request,
    input logic [1:0] ns_light,
    input logic [1:0] ew_light,
    input logic ped_walk_ns,
    input logic ped_walk_ew,
    input logic emergency_active,
    input logic fault_active,
    input logic [3:0] debug_state,
    input logic [7:0] debug_timer
);
    localparam logic [ADDR_WIDTH-1:0] REG_CONTROL = 'h00;
    localparam logic [ADDR_WIDTH-1:0] REG_DEMAND  = 'h04;
    localparam logic [ADDR_WIDTH-1:0] REG_STATUS  = 'h08;
    localparam logic [ADDR_WIDTH-1:0] REG_DEBUG   = 'h0C;

    logic aw_held, w_held;
    logic [ADDR_WIDTH-1:0] awaddr_hold;
    logic [DATA_WIDTH-1:0] wdata_hold;
    logic [DATA_WIDTH/8-1:0] wstrb_hold;
    logic [ADDR_WIDTH-1:0] write_addr;
    logic [DATA_WIDTH-1:0] write_data;
    logic [DATA_WIDTH/8-1:0] write_strb;
    logic write_commit;
    integer byte_index;

    assign s_axi_awready = !aw_held && !s_axi_bvalid;
    assign s_axi_wready  = !w_held  && !s_axi_bvalid;
    assign s_axi_arready = !s_axi_rvalid;
    assign s_axi_bresp = 2'b00; // OKAY
    assign s_axi_rresp = 2'b00; // OKAY

    always_comb begin
        write_addr = aw_held ? awaddr_hold : s_axi_awaddr;
        write_data = w_held ? wdata_hold : s_axi_wdata;
        write_strb = w_held ? wstrb_hold : s_axi_wstrb;
        write_commit = (aw_held || (s_axi_awvalid && s_axi_awready)) &&
                       (w_held  || (s_axi_wvalid  && s_axi_wready)) &&
                       !s_axi_bvalid;
    end

    always_ff @(posedge aclk or negedge aresetn) begin
        if (!aresetn) begin
            aw_held <= 1'b0;
            w_held <= 1'b0;
            awaddr_hold <= '0;
            wdata_hold <= '0;
            wstrb_hold <= '0;
            s_axi_bvalid <= 1'b0;
            s_axi_rvalid <= 1'b0;
            s_axi_rdata <= '0;
            sensor_data_valid <= 1'b1;
            ns_demand <= 4'd0;
            ew_demand <= 4'd0;
            ns_emergency_request <= 1'b0;
            ew_emergency_request <= 1'b0;
            ped_ns_request <= 1'b0;
            ped_ew_request <= 1'b0;
        end else begin
            if (s_axi_awvalid && s_axi_awready) begin
                awaddr_hold <= s_axi_awaddr;
                aw_held <= 1'b1;
            end
            if (s_axi_wvalid && s_axi_wready) begin
                wdata_hold <= s_axi_wdata;
                wstrb_hold <= s_axi_wstrb;
                w_held <= 1'b1;
            end

            if (write_commit) begin
                aw_held <= 1'b0;
                w_held <= 1'b0;
                s_axi_bvalid <= 1'b1;
                case (write_addr)
                    REG_CONTROL: begin
                        for (byte_index = 0; byte_index < DATA_WIDTH/8; byte_index = byte_index + 1) begin
                            if (write_strb[byte_index]) begin
                                case (byte_index)
                                    0: begin
                                        sensor_data_valid <= write_data[0];
                                        ns_emergency_request <= write_data[1];
                                        ew_emergency_request <= write_data[2];
                                        ped_ns_request <= write_data[3];
                                        ped_ew_request <= write_data[4];
                                    end
                                    default: begin end
                                endcase
                            end
                        end
                    end
                    REG_DEMAND: begin
                        if (write_strb[0]) begin
                            ns_demand <= write_data[3:0];
                            ew_demand <= write_data[7:4];
                        end
                    end
                    default: begin end // unmapped writes are ignored, response OKAY
                endcase
            end else begin
                if (s_axi_bvalid && s_axi_bready)
                    s_axi_bvalid <= 1'b0;
            end

            if (s_axi_arvalid && s_axi_arready) begin
                s_axi_rvalid <= 1'b1;
                case (s_axi_araddr)
                    REG_CONTROL: s_axi_rdata <= {{(DATA_WIDTH-5){1'b0}},
                        ped_ew_request, ped_ns_request, ew_emergency_request,
                        ns_emergency_request, sensor_data_valid};
                    REG_DEMAND: s_axi_rdata <= {{(DATA_WIDTH-8){1'b0}},
                        ew_demand, ns_demand};
                    REG_STATUS: s_axi_rdata <= {{(DATA_WIDTH-10){1'b0}},
                        fault_active, emergency_active, ped_walk_ew, ped_walk_ns,
                        ew_light, ns_light};
                    REG_DEBUG: s_axi_rdata <= {{(DATA_WIDTH-12){1'b0}},
                        debug_timer, debug_state};
                    default: s_axi_rdata <= '0;
                endcase
            end else if (s_axi_rvalid && s_axi_rready) begin
                s_axi_rvalid <= 1'b0;
            end
        end
    end
endmodule
