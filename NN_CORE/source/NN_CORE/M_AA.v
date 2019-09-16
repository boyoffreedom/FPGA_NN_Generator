//加法器阵列
`include "extern.v"
module n_adder(clk,rst_n,
				d_valid,acc_enable,acc_mux,
				mult_out,adder_out,mac_out);


input clk,rst_n;
input acc_enable,acc_mux,acc_mux,d_valid;

input [`DWIDTH-1:0] mult_out;
output [`DWIDTH-1:0] adder_out;
output [`D_LEN-1:0] mac_out;
wire [`DWIDTH-1:0] mult_din = (d_valid==0)?0:mult_out;
wire [2*`DWIDTH-1:0] din = (acc_mux == 0)?{mult_din,adder_out}:{{(2*`DWIDTH-2*`D_LEN){1'b0}},mac_ram,adder_out[`D_LEN-1:0]};

reg [`D_LEN-1:0] mac_ram;
assign mac_out = mac_ram;

always @(posedge clk or negedge rst_n)begin				//DFF数据缓存
	if(!rst_n)begin
		mac_ram <= 0;
	end
	else begin
		if(acc_enable)begin
			mac_ram <= adder_out[`D_LEN-1:0];
		end
		else begin
			mac_ram <= mac_ram;
		end
	end
end

//生成多个加法器
genvar gv_i;
generate
	for(gv_i = 0; gv_i < `CELL_N;gv_i = gv_i + 1)
	begin: float_adder
		float_adder u_fm(clk,rst_n,
							din[gv_i*2*`D_LEN+`D_LEN-1:gv_i*2*`D_LEN],
							din[gv_i*2*`D_LEN+2*`D_LEN-1:gv_i*2*`D_LEN+`D_LEN],
							adder_out[gv_i*`D_LEN+`D_LEN-1:gv_i*`D_LEN]);
	end
endgenerate
endmodule
