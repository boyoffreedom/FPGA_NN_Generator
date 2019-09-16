`include "extern.v"

module float_mac(clk,rst_n,mul_a,mul_b,add_a,mac_out);

input clk,rst_n;
input [`D_LEN-1:0] mul_a,mul_b,add_a;
output [`D_LEN-1:0] mac_out;

reg[`D_LEN-1:0] add_a_fifo[3:0];
wire[`D_LEN-1:0] add_b;

always @(posedge clk)begin
	add_a_fifo[0] <= add_a;
	add_a_fifo[1] <= add_a_fifo[0];
	add_a_fifo[2] <= add_a_fifo[1];
	add_a_fifo[3] <= add_a_fifo[2];
end

float_mult u0(clk,rst_n,mul_a,mul_b,add_b);
float_adder u1(clk,rst_n,add_a_fifo[3],add_b,mac_out);

endmodule
