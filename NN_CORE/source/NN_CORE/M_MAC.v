`include "extern.v"
module N_MAC(clk,rst_n,
				HMB_AS,HMB_CTRL,
				HMB_D0,HMB_D1,HMB_DMUL,HMB_DADD,HMB_DMAC,HMB_SMF,
				HMB_ARD,
				HMB_ST);
//乘累加模块

input clk,rst_n;
input HMB_AS;										//模块选择，挂载到
input [`AWIDTH:0] HMB_CTRL;					//control控制位
input [`DWIDTH-1:0] HMB_D0,HMB_D1;								//浮点数输入
output [`DWIDTH-1:0] HMB_DMUL,HMB_DADD;								//输出单次乘加结果
output [`D_LEN-1:0] HMB_DMAC;
output [`AWIDTH-1:0]HMB_ARD;  							//外接ram（存取乘法器与加法器直接输出值）地址
output [7:0]HMB_ST;
output HMB_SMF;												//mac_finish

//用于标明乘累加器矩阵工作状态
//    6            5           4         3          2          1        0 
//{edb_busy,require_error,space_error,bus_crash,mult_busy,adder_busy,mac_finish};
//挂载总线
assign HMB_DMUL = (HMB_AS == 1)?mult_out:{(`DWIDTH){1'bz}};
assign HMB_DADD = (HMB_AS == 1)?adder_out:{(`DWIDTH){1'bz}};
assign HMB_DMAC = (HMB_AS == 1)?mac_out:{(`D_LEN){1'bz}};
assign HMB_ARD = (HMB_AS == 1)?addr_rd:{(`AWIDTH){1'bz}};
assign HMB_ST = (HMB_AS == 1)?state:8'bzzzz_zzzz;
assign HMB_SMF = state[0];
//内部连线
wire [`DWIDTH-1:0] mult_out;
wire [`DWIDTH-1:0] adder_out;
wire mult_clk,adder_clk;
wire [`AWIDTH-1:0] addr_rd;
wire [7:0] state;
wire acc_finish;
wire mult_rst,adder_rst;
wire d_valid,acc_enable,acc_mux;
wire [`D_LEN-1:0]mac_out;

reg[`DWIDTH-1:0] fin_a,fin_b;
always @(posedge clk or negedge rst_n)begin
	if(!rst_n)begin
		fin_a <= 0;
		fin_b <= 0;
	end
	else begin
		fin_a <= HMB_D0;
		fin_b <= HMB_D1;
	end
end

	n_mult u0(mult_clk,rst_n,fin_a,fin_b,mult_out);
	
	n_adder u1(adder_clk,adder_rst,
				d_valid,acc_enable,acc_mux,
				mult_out,adder_out,mac_out);
					
	n_mac_controller u2(clk,rst_n,HMB_CTRL,				//clock,reset,inner ram data mux,adder data mux  时钟、复位、内部RAM数据选择、加法器数据选择
							addr_rd,mult_clk,d_valid,
							adder_rst,adder_clk,
							acc_mux,acc_enable,
							state);	
endmodule 

