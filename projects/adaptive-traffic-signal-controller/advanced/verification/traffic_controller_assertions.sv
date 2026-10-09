// Bind/include these assertions in a SystemVerilog-capable simulator.
// The checker assumes the DUT signals are visible in the enclosing scope or
// that the properties are adapted to the selected simulator's bind syntax.

module traffic_controller_assertions (
    input logic clk,
    input logic rst_n,
    input logic [1:0] ns_light,
    input logic [1:0] ew_light,
    input logic ped_walk_ns,
    input logic ped_walk_ew,
    input logic fault_active
);
    localparam logic [1:0] RED = 2'b00, GREEN = 2'b10;

    // Safety property 1: opposing vehicle approaches are never green together.
    ap_no_conflicting_green:
        assert property (@(posedge clk) disable iff (!rst_n)
            !(ns_light == GREEN && ew_light == GREEN))
        else $error("Opposing roads green simultaneously");

    // Safety property 2: pedestrian walk requires both approaches to be red.
    ap_pedestrian_only_when_vehicle_red:
        assert property (@(posedge clk) disable iff (!rst_n)
            (ped_walk_ns || ped_walk_ew) |->
            (ns_light == RED && ew_light == RED))
        else $error("Pedestrian walk while vehicle signal is not red");

    // Safety property 3: the two crossing directions cannot be enabled together.
    ap_one_pedestrian_crossing:
        assert property (@(posedge clk) disable iff (!rst_n)
            !(ped_walk_ns && ped_walk_ew))
        else $error("Both pedestrian crossings enabled");

    // Safety property 4: fault mode must remain all-red with pedestrian outputs off.
    ap_fault_outputs_safe:
        assert property (@(posedge clk) disable iff (!rst_n)
            fault_active |->
            (ns_light == RED && ew_light == RED &&
             !ped_walk_ns && !ped_walk_ew))
        else $error("Unsafe output while fault is active");

endmodule
