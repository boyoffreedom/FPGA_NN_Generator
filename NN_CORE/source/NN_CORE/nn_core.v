`include "extern.v"

module nn_core(clk,rst_n,
			state,
			nn_start,nn_finish,a_in,
			opm_base,opm_offset,opm_dout,
			);

input clk,rst_n;
input nn_start;
input [`I_NUM-1:0] a_in;
output nn_finish;
output[7:0] state;
input [`DA_AWIDTH-1:0] opm_base;
input [`OFS_WIDTH-1:0] opm_offset;
output [`D_LEN-1:0] opm_dout;

//乘累加模块引脚
wire [`DWIDTH-1:0] mult_out,adder_out;
wire [`D_LEN-1:0] da_din,dw_din;
wire [`NP_W-1:0] mac0_np;
wire[`D_LEN-1:0] mac0_din;
wire[`AWIDTH:0] mac0_ctrl;
wire [`DA_AWIDTH-1:0] mac0_addr;
wire[`DWIDTH-1:0] mac0_da,mac0_dw;

//输入输出处理模块引脚
wire ipm_request,ipm_finish,ipm_wen;
wire ipm_enable;
wire [`D_LEN-1:0] ipm_din,opm_dout;
wire [`OFS_WIDTH-1:0] ipm_offset;
wire [`DA_AWIDTH-1:0] ipm_base;
wire nn_start,nn_finish;

//激活函数模块引脚定义
wire[3:0] mac0_acftype;					//激活函数种类
wire [`D_LEN-1:0] acfunc_out;	//激活函数输出

wire mac0_cs = 1;
wire mac0_f;

ROUTER_BUS u0(clk,rst_n,
					nn_start,nn_finish, 
					ipm_request,ipm_finish,ipm_enable,ipm_din,ipm_base,ipm_offset,ipm_wen,							//ipm接口
					opm_request,opm_finish,opm_enable,opm_dout,opm_base,opm_offset,						//opm接口
					acfunc_out,mac0_ctrl,mac0_f,mac0_da,mac0_dw,mac0_addr,mac0_acftype,
					);

N_MAC 	u1(clk,rst_n,
				mac0_cs,mac0_ctrl,																			//乘累加器模块
				mac0_da,mac0_dw,mult_out,adder_out,mac0_din,mac0_f,
				mac0_addr,
				state);

ACTIVE_FUNC u2 (clk,rst_n,mac0_acftype,																	//激活函数模块
						mac0_din,acfunc_out);
	
ipm	u3 (clk,rst_n,
			a_in,nn_start,
			ipm_request,ipm_enable,ipm_finish,
			ipm_base,ipm_offset,ipm_din,ipm_wen);
			 
endmodule
