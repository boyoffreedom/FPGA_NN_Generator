`include "extern.v"

module nn(clk,rst_n,state,
			nn_start,nn_finish,
			rxd,txd
			);

input clk,rst_n;
output nn_start,nn_finish;
input rxd;
output txd;
output[7:0] state;

wire[`DA_AWIDTH-1:0] opm_base;
wire[`D_LEN-1:0] opm_dout;
wire[`OFS_WIDTH-1:0] opm_offset;
wire [`I_NUM-1:0] a_in;

nn_core u1(clk,rst_n,
			state,
			nn_start,nn_finish,a_in,
			opm_base,opm_offset,opm_dout);

SCI_IO u2(clk,rst_n,
			nn_start,nn_finish,a_in,
			opm_base,opm_offset,opm_dout,
			rxd,txd);
endmodule
