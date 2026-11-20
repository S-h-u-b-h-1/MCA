// Timing-only FPGA I/O wrapper for the existing synthesizable BPU.
// IMPORTANT: This wrapper DOES NOT implement a CPU or new prediction algorithm.
// It registers every data input and the observed outputs so that nextpnr
// measures synchronous register-to-register paths rather than untimed
// primary-input/primary-output combinational paths.
//
// Target for the reproducible study: Lattice iCE40HX8K-CT256.
// No external board pinout or input/output delay constraints are assumed;
// therefore the resulting post-route Fmax is a software ESTIMATE for this
// registered harness, not a physical FPGA measurement or a CPU speedup.
`timescale 1ns/1ps
`default_nettype none

module bpu_fpga_timing_top (
    input wire clk,
    input wire reset,
    input wire [31:0] fetch_pc,
    input wire resolve_valid,
    input wire [31:0] resolve_pc,
    input wire resolve_predicted_taken,
    input wire resolve_btb_hit,
    input wire [31:0] resolve_predicted_target,
    input wire resolve_actual_taken,
    input wire [31:0] resolve_actual_target,

    output reg [31:0] observed_selected_next_pc,
    output reg [1:0] observed_prediction_state,
    output reg observed_predicted_taken,
    output reg observed_btb_hit,
    output reg observed_mispredict,
    output reg observed_flush,
    output reg observed_redirect
);

    // Explicit registered boundary: all BPU data inputs arrive from
    // launching registers, and all relevant outputs end at capture registers.
    // External stimulus must provide correctly aligned/saved metadata, as
    // required by the original BPU integration contract.
    reg [31:0] fetch_pc_q;
    reg resolve_valid_q;
    reg [31:0] resolve_pc_q;
    reg resolve_predicted_taken_q;
    reg resolve_btb_hit_q;
    reg [31:0] resolve_predicted_target_q;
    reg resolve_actual_taken_q;
    reg [31:0] resolve_actual_target_q;

    always @(posedge clk) begin
        if (reset) begin
            fetch_pc_q <= 32'd0;
            resolve_valid_q <= 1'b0;
            resolve_pc_q <= 32'd0;
            resolve_predicted_taken_q <= 1'b0;
            resolve_btb_hit_q <= 1'b0;
            resolve_predicted_target_q <= 32'd0;
            resolve_actual_taken_q <= 1'b0;
            resolve_actual_target_q <= 32'd0;
        end else begin
            fetch_pc_q <= fetch_pc;
            resolve_valid_q <= resolve_valid;
            resolve_pc_q <= resolve_pc;
            resolve_predicted_taken_q <= resolve_predicted_taken;
            resolve_btb_hit_q <= resolve_btb_hit;
            resolve_predicted_target_q <= resolve_predicted_target;
            resolve_actual_taken_q <= resolve_actual_taken;
            resolve_actual_target_q <= resolve_actual_target;
        end
    end

    wire predicted_taken_w;
    wire [1:0] prediction_state_w;
    wire btb_hit_w;
    wire [31:0] predicted_target_w;
    wire [31:0] predicted_next_pc_w;
    wire mispredict_w, flush_w, redirect_w;
    wire [31:0] redirect_pc_w, selected_next_pc_w;

    branch_prediction_unit #(.INDEX_BITS(4)) dut (
        .clk(clk),
        .reset(reset),
        .fetch_pc(fetch_pc_q),
        .predicted_taken(predicted_taken_w),
        .prediction_state(prediction_state_w),
        .btb_hit(btb_hit_w),
        .predicted_target(predicted_target_w),
        .predicted_next_pc(predicted_next_pc_w),
        .resolve_valid(resolve_valid_q),
        .resolve_pc(resolve_pc_q),
        .resolve_predicted_taken(resolve_predicted_taken_q),
        .resolve_btb_hit(resolve_btb_hit_q),
        .resolve_predicted_target(resolve_predicted_target_q),
        .resolve_actual_taken(resolve_actual_taken_q),
        .resolve_actual_target(resolve_actual_target_q),
        .mispredict(mispredict_w),
        .flush(flush_w),
        .redirect(redirect_w),
        .redirect_pc(redirect_pc_w),
        .selected_next_pc(selected_next_pc_w)
    );

    // All observed outputs are captured on the same clock domain.
    // selected_next_pc includes prediction, BTB address, target comparison
    // and correction/redirect logic, so none of the essential BPU paths
    // can be erased as unused by the technology mapper.
    always @(posedge clk) begin
        if (reset) begin
            observed_selected_next_pc <= 32'd0;
            observed_prediction_state <= 2'b00;
            observed_predicted_taken <= 1'b0;
            observed_btb_hit <= 1'b0;
            observed_mispredict <= 1'b0;
            observed_flush <= 1'b0;
            observed_redirect <= 1'b0;
        end else begin
            observed_selected_next_pc <= selected_next_pc_w;
            observed_prediction_state <= prediction_state_w;
            observed_predicted_taken <= predicted_taken_w;
            observed_btb_hit <= btb_hit_w;
            observed_mispredict <= mispredict_w;
            observed_flush <= flush_w;
            observed_redirect <= redirect_w;
        end
    end
endmodule

`default_nettype wire
