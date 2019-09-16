`include "extern.v"

module ROUTER_BUS(clk,rst_n,
						nn_start,nn_finish, 
						ipm_request,ipm_finish,ipm_enable,ipm_din,ipm_base,ipm_offset,ipm_wen,							//ipm接口
						opm_request,opm_finish,opm_enable,opm_dout,opm_base,opm_offset,						//opm接口
						mac0_din,mac0_ctrl,mac0_finish,mac0_da,mac0_dw,mac0_addr,mac0_acftype,
						);

input clk,rst_n,nn_start;
output nn_finish;

//输入处理模块数据、握手信号
input [`OFS_WIDTH-1:0]ipm_offset;
input [`D_LEN-1:0]ipm_din;
input ipm_request,ipm_wen,ipm_finish;
output ipm_enable;

//输出处理模块
input opm_request,opm_finish;
output opm_enable;
input [`DA_AWIDTH-1:0]opm_base,ipm_base;
input [`OFS_WIDTH-1:0]opm_offset;
output [`D_LEN-1:0] opm_dout;

//矩阵乘法单元接口定义
input[`D_LEN-1:0] mac0_din;
output[`AWIDTH:0] mac0_ctrl;
input mac0_finish;
output [`DWIDTH-1:0] mac0_da,mac0_dw;
input [`LL-1:0] mac0_addr;
output[3:0]mac0_acftype;

wire [`DA_AWIDTH-1:0]ipm_addr_wr;
wire [`D_LEN-1:0] ipm_din;
wire ipm_request,ipm_enable,ipm_wen,ipm_finish;
wire opm_request,opm_finish;
wire [`OFS_WIDTH-1:0]opm_offset;
wire [`D_LEN-1:0] opm_dout;

wire [`D_LEN-1:0] da_din,dw_din,da_dout,dw_dout;
wire [`DA_AWIDTH-1:0] da_addr;
wire [`DW_AWIDTH-1:0] dw_addr;
wire [`CELL_N-1:0] da_sel,dw_sel;
wire [`DWIDTH-1:0] da_bout,dw_bout;
wire [`CELL_N-1:0] da_wen,dw_wen;

wire [`DWIDTH-1:0] mac0_da,mac0_dw;

assign mac0_da = da_bout;
assign mac0_dw = dw_bout;

router_controller u0(clk,rst_n,nn_start,nn_finish,
							ipm_request,ipm_finish,ipm_enable,ipm_din,ipm_base,ipm_offset,ipm_wen,							//ipm接口
							opm_request,opm_finish,opm_enable,opm_dout,opm_base,opm_offset,						//opm接口
							mac0_din,mac0_ctrl,mac0_finish,mac0_addr,mac0_acftype,									//mac0接口
							da_din,da_wen,da_addr,da_sel,da_dout,														//PRAM接口
							dw_din,dw_wen,dw_addr,dw_sel,dw_dout
							);

R_PRAM u1(clk,rst_n,
	da_wen, da_addr, da_sel, da_din, da_dout, da_bout,
	dw_wen, dw_addr, dw_sel, dw_din, dw_dout, dw_bout);

endmodule
