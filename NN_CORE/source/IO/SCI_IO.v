`include "extern.v"

module SCI_IO(clk,rst_n,
			 nn_start,nn_finish,a_in,
			 opm_base,opm_offset,opm_dout,
			 rxd,txd);

input clk,rst_n;
input nn_finish;
output nn_start;
input rxd;
output txd;
output[`I_NUM-1:0] a_in;

//RAM装载wire
output [`DA_AWIDTH-1:0] opm_base;
output [`OFS_WIDTH-1:0] opm_offset;
input [`D_LEN-1:0] opm_dout;


//串口收发wire
wire baud_clk;
wire [7:0] rx_data,tx_data;
wire rx_ready,tx_ready;
wire rx_error,tx_start;



wire [`I_NUM-1:0] a_in;

CLK_MNG u0(clk,rst_n,baud_clk);

SCI_RX u1(baud_clk,rst_n,rxd,rx_data,rx_ready,rx_error);

SCI_TX u2(baud_clk,rst_n,txd,tx_data,tx_start,tx_ready);

sci_controller u3(clk,rst_n,
						nn_start,nn_finish,
						rx_data,rx_ready,rx_error,
						tx_data,tx_ready,tx_start,
						opm_base,opm_offset,opm_dout,a_in);

		
endmodule
