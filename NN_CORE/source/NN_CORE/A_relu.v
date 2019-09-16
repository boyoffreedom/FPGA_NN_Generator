`include "../extern.v"

module relu(clk,rst_n,float_in,float_out);

input clk,rst_n;
input [`D_LEN-1:0] float_in;
output[`D_LEN-1:0] float_out;

wire f_in_s = float_in[`E_bit+`F_bit];
reg[`D_LEN-1:0] out_fifo[6:0];
reg [`D_LEN-1:0] float_out;

always @(posedge clk)begin
	if(f_in_s == 0)begin
		float_out <= float_in;
	end
	else begin
		float_out <= 0;
	end
end

endmodule
