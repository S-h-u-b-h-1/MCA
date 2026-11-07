`timescale 1ns/1ps
`default_nettype none
// Synthesizable integration of the author-owned direction, BTB and control RTL.
// This wrapper is NOT a complete CPU or a pipeline register implementation.
module branch_prediction_unit #(
    parameter integer INDEX_BITS = 4
)(
    input wire clk,
    input wire reset,
    input wire [31:0] fetch_pc,
    output wire predicted_taken,
    output wire [1:0] prediction_state,
    output wire btb_hit,
    output wire [31:0] predicted_target,
    output wire [31:0] predicted_next_pc,
    input wire resolve_valid,
    input wire [31:0] resolve_pc,
    input wire resolve_predicted_taken,
    input wire resolve_btb_hit,
    input wire [31:0] resolve_predicted_target,
    input wire resolve_actual_taken,
    input wire [31:0] resolve_actual_target,
    output wire mispredict,
    output wire flush,
    output wire redirect,
    output wire [31:0] redirect_pc,
    output wire [31:0] selected_next_pc
);
    // The caller must save fetch-time prediction metadata until resolution.
    // A squashed/invalid branch cannot train either table.
    wire train_valid = resolve_valid & ~reset;

    predictor_2bit #(.INDEX_BITS(INDEX_BITS)) direction (
        .clk(clk), .reset(reset), .lookup_pc(fetch_pc),
        .predict_taken(predicted_taken), .prediction_state(prediction_state),
        .update_valid(train_valid), .update_pc(resolve_pc),
        .actual_taken(resolve_actual_taken)
    );

    // Only actually taken branches train target storage.
    branch_target_buffer #(.INDEX_BITS(INDEX_BITS)) targets (
        .clk(clk), .reset(reset), .lookup_pc(fetch_pc),
        .update_valid(train_valid & resolve_actual_taken),
        .update_pc(resolve_pc), .update_target(resolve_actual_target),
        .hit(btb_hit), .target(predicted_target)
    );

    next_pc_mux speculate (
        .pc(fetch_pc), .predicted_taken(predicted_taken),
        .btb_hit(btb_hit), .predicted_target(predicted_target),
        .predicted_next_pc(predicted_next_pc)
    );

    // Resolve against SAVED fetch-time values, not the current lookup outputs.
    branch_resolution recovery (
        .valid(resolve_valid), .branch_pc(resolve_pc),
        .predicted_taken(resolve_predicted_taken),
        .btb_hit(resolve_btb_hit),
        .predicted_target(resolve_predicted_target),
        .actual_taken(resolve_actual_taken),
        .actual_target(resolve_actual_target),
        .mispredict(mispredict), .flush(flush), .redirect(redirect),
        .redirect_pc(redirect_pc)
    );

    // Execute-stage recovery wins over an unrelated speculative fetch.
    assign selected_next_pc = redirect ? redirect_pc : predicted_next_pc;
endmodule
`default_nettype wire
