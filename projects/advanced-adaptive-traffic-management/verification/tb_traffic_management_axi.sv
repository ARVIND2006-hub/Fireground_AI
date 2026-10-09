`timescale 1ns/1ps
module tb_traffic_management_axi;
    localparam integer AW=6, DW=32;
    logic aclk=0, aresetn=0;
    logic [AW-1:0] s_axi_awaddr=0;
    logic s_axi_awvalid=0;
    wire s_axi_awready;
    logic [DW-1:0] s_axi_wdata=0;
    logic [DW/8-1:0] s_axi_wstrb=4'hF;
    logic s_axi_wvalid=0;
    wire s_axi_wready;
    wire [1:0] s_axi_bresp;
    wire s_axi_bvalid;
    logic s_axi_bready=0;
    logic [AW-1:0] s_axi_araddr=0;
    logic s_axi_arvalid=0;
    wire s_axi_arready;
    wire [DW-1:0] s_axi_rdata;
    wire [1:0] s_axi_rresp;
    wire s_axi_rvalid;
    logic s_axi_rready=0;

    wire [1:0] ns_light, ew_light;
    wire ped_walk_ns, ped_walk_ew, emergency_active, fault_active;
    wire [3:0] debug_state;
    wire [7:0] debug_timer;

    traffic_management_soc_top #(.AXI_ADDR_WIDTH(AW), .AXI_DATA_WIDTH(DW)) dut (.*);
    always #5 aclk=~aclk;

    task automatic axi_write(input logic [AW-1:0] addr,
                             input logic [DW-1:0] data);
        bit aw_done, w_done;
        begin
            aw_done=0; w_done=0;
            @(negedge aclk);
            s_axi_awaddr=addr; s_axi_awvalid=1;
            s_axi_wdata=data; s_axi_wstrb=4'hF; s_axi_wvalid=1;
            s_axi_bready=0;
            while (!aw_done || !w_done) begin
                @(posedge aclk);
                if (s_axi_awvalid && s_axi_awready) begin
                    aw_done=1;
                end
                if (s_axi_wvalid && s_axi_wready) begin
                    w_done=1;
                end
                @(negedge aclk);
                if (aw_done) s_axi_awvalid=0;
                if (w_done) s_axi_wvalid=0;
            end
            s_axi_bready=1;
            do @(posedge aclk); while (!s_axi_bvalid);
            if (s_axi_bresp !== 2'b00) $fatal(1,"AXI write response not OKAY");
            @(negedge aclk); s_axi_bready=0;
        end
    endtask

    task automatic axi_read(input logic [AW-1:0] addr,
                            output logic [DW-1:0] data);
        begin
            @(negedge aclk);
            s_axi_araddr=addr; s_axi_arvalid=1; s_axi_rready=0;
            do @(posedge aclk); while (!s_axi_arready);
            @(negedge aclk); s_axi_arvalid=0; s_axi_rready=1;
            do @(posedge aclk); while (!s_axi_rvalid);
            if (s_axi_rresp !== 2'b00) $fatal(1,"AXI read response not OKAY");
            data=s_axi_rdata;
            @(negedge aclk); s_axi_rready=0;
        end
    endtask

    logic [DW-1:0] readback;
    initial begin
        $dumpfile("traffic_management_axi.vcd");
        $dumpvars(0,tb_traffic_management_axi);
        repeat (4) @(negedge aclk);
        aresetn=1;

        // Write and read back demand: NS=5, EW=9.
        axi_write(6'h04, 32'h00000095);
        axi_read(6'h04, readback);
        if (readback[7:0] !== 8'h95)
            $fatal(1,"Demand register readback failed: %h",readback);

        // Control register: sensor-valid=1, request bits initially cleared.
        axi_write(6'h00, 32'h00000001);
        axi_read(6'h00, readback);
        if (readback[4:0] !== 5'b00001)
            $fatal(1,"Control register readback failed: %h",readback);

        // Assert NS emergency request and verify control register.
        axi_write(6'h00, 32'h00000003);
        axi_read(6'h00, readback);
        if (readback[1:0] !== 2'b11)
            $fatal(1,"Emergency request control readback failed: %h",readback);

        // Read status/debug to exercise all mapped read addresses.
        axi_read(6'h08, readback);
        axi_read(6'h0C, readback);

        // Clear request, preserve sensor-valid, then request a latched fault.
        axi_write(6'h00, 32'h00000001);
        axi_write(6'h00, 32'h00000000);
        repeat (4) @(negedge aclk);
        if (!fault_active)
            $fatal(1,"Invalid sensor status did not produce fault output");

        $display("PASS: basic AXI register read/write smoke tests completed.");
        $display("Note: this smoke test is not exhaustive AXI protocol verification.");
        $finish;
    end
endmodule
