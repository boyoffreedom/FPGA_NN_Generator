`include "extern.v"

module ACTIVE_FUNC(clk,rst_n,func_type,
						float_in,acfunc_out);
input clk,rst_n;
input [`D_LEN-1:0] float_in;
input[3:0] func_type;
output [`D_LEN-1:0] acfunc_out;

wire [`D_LEN-1:0] relu_out,si_out;

wire [15:0]coder_in;
wire [4:0] coder_out;
reg[`D_LEN-1:0] float_in_[2:0];
always @(posedge clk)begin
	float_in_[2] <= float_in_[1];
	float_in_[1] <= float_in_[0];
	float_in_[0] <= float_in;
end

wire [`D_LEN-1:0] acfunc_out = (func_type == 4'd0)?relu_out:
										 (func_type == 4'd2)?si_out:float_in_[1];

relu u2 (clk,rst_n,float_in_[0],relu_out);

signh u3 (clk,rst_n,float_in_[0],si_out);


endmodule
