`include "extern.v"

module signh(clk,rst_n,float_in,float_out);

input clk,rst_n;
input [`D_LEN-1:0] float_in;
output[`D_LEN-1:0] float_out;

wire f_in_s = float_in[`E_bit+`F_bit];
wire [`E_bit+`F_bit-1:0] f_in_abs = float_in[`E_bit+`F_bit-1:0];
reg[`D_LEN-1:0] float_out;

always @(posedge clk)begin
	if(f_in_s == 0 && f_in_abs >= {2'b0,{(`E_bit-2){1'b1}},{(`F_bit+1){1'b0}}})begin
		float_out <= {2'b00,{(`E_bit-1){1'b1}},{(`F_bit){1'b0}}};
	end
	else begin
		float_out <= 0;
	end
end

endmodule
