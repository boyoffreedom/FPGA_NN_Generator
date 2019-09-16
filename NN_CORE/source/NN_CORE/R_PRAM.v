`include "extern.v"

module R_PRAM(clk,rst_n,
	da_wen, da_addr, da_sel, da_din, da_dout, da_bout,
	dw_wen, dw_addr, dw_sel, dw_din, dw_dout, dw_bout);

input clk,rst_n;
input[`CELL_N-1:0] da_wen,dw_wen;
input [`DA_AWIDTH-1:0] da_addr;
input [`DW_AWIDTH-1:0] dw_addr;

input [`CELL_N-1:0] da_sel;
input [`CELL_N-1:0] dw_sel;

input [`D_LEN-1:0] da_din,dw_din;
output [`D_LEN-1:0] da_dout,dw_dout;
output [`DWIDTH-1:0] da_bout,dw_bout;

reg [`D_LEN-1:0] da_0,dw_0;
reg [`D_LEN-1:0] da_1,dw_1;
reg [`D_LEN-1:0] da_2,dw_2;
reg [`D_LEN-1:0] da_3,dw_3;
reg [`D_LEN-1:0] da_4,dw_4;
reg [`D_LEN-1:0] da_5,dw_5;
reg [`D_LEN-1:0] da_6,dw_6;
reg [`D_LEN-1:0] da_7,dw_7;
reg [`D_LEN-1:0] da_8,dw_8;
reg [`D_LEN-1:0] da_9,dw_9;

//并置输出
assign da_bout = {da_9, da_8, da_7, da_6, da_5, da_4, da_3, da_2, da_1, da_0};
assign dw_bout = {dw_9, dw_8, dw_7, dw_6, dw_5, dw_4, dw_3, dw_2, dw_1, dw_0};

assign da_dout = ({`D_LEN{da_sel[0]}})&da_0|
				({`D_LEN{da_sel[1]}})&da_1|
				({`D_LEN{da_sel[2]}})&da_2|
				({`D_LEN{da_sel[3]}})&da_3|
				({`D_LEN{da_sel[4]}})&da_4|
				({`D_LEN{da_sel[5]}})&da_5|
				({`D_LEN{da_sel[6]}})&da_6|
				({`D_LEN{da_sel[7]}})&da_7|
				({`D_LEN{da_sel[8]}})&da_8|
				({`D_LEN{da_sel[9]}})&da_9;

assign dw_dout = ({`D_LEN{dw_sel[0]}})&dw_0|
				({`D_LEN{dw_sel[1]}})&dw_1|
				({`D_LEN{dw_sel[2]}})&dw_2|
				({`D_LEN{dw_sel[3]}})&dw_3|
				({`D_LEN{dw_sel[4]}})&dw_4|
				({`D_LEN{dw_sel[5]}})&dw_5|
				({`D_LEN{dw_sel[6]}})&dw_6|
				({`D_LEN{dw_sel[7]}})&dw_7|
				({`D_LEN{dw_sel[8]}})&dw_8|
				({`D_LEN{dw_sel[9]}})&dw_9;

reg [`D_LEN-1:0] DA_RAM_0 [`DA_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_a0.mif" */;
reg [`D_LEN-1:0] DW_RAM_0 [`DW_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_w0.mif" */;

reg [`D_LEN-1:0] DA_RAM_1 [`DA_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_a1.mif" */;
reg [`D_LEN-1:0] DW_RAM_1 [`DW_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_w1.mif" */;

reg [`D_LEN-1:0] DA_RAM_2 [`DA_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_a2.mif" */;
reg [`D_LEN-1:0] DW_RAM_2 [`DW_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_w2.mif" */;

reg [`D_LEN-1:0] DA_RAM_3 [`DA_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_a3.mif" */;
reg [`D_LEN-1:0] DW_RAM_3 [`DW_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_w3.mif" */;

reg [`D_LEN-1:0] DA_RAM_4 [`DA_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_a4.mif" */;
reg [`D_LEN-1:0] DW_RAM_4 [`DW_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_w4.mif" */;

reg [`D_LEN-1:0] DA_RAM_5 [`DA_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_a5.mif" */;
reg [`D_LEN-1:0] DW_RAM_5 [`DW_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_w5.mif" */;

reg [`D_LEN-1:0] DA_RAM_6 [`DA_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_a6.mif" */;
reg [`D_LEN-1:0] DW_RAM_6 [`DW_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_w6.mif" */;

reg [`D_LEN-1:0] DA_RAM_7 [`DA_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_a7.mif" */;
reg [`D_LEN-1:0] DW_RAM_7 [`DW_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_w7.mif" */;

reg [`D_LEN-1:0] DA_RAM_8 [`DA_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_a8.mif" */;
reg [`D_LEN-1:0] DW_RAM_8 [`DW_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_w8.mif" */;

reg [`D_LEN-1:0] DA_RAM_9 [`DA_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_a9.mif" */;
reg [`D_LEN-1:0] DW_RAM_9 [`DW_DEPTH-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/ram_w9.mif" */;

//group0
always @(posedge clk) begin
	da_0 <= DA_RAM_0[da_addr];
	if(da_wen[0]) begin
		DA_RAM_0[da_addr] <= da_din;
	end
end


always @(posedge clk) begin
	dw_0 <= DW_RAM_0[dw_addr];
	if(dw_wen[0]) begin
		DW_RAM_0[dw_addr] <= dw_din;
	end
end

//group1
always @(posedge clk) begin
	da_1 <= DA_RAM_1[da_addr];
	if(da_wen[1]) begin
		DA_RAM_1[da_addr] <= da_din;
	end
end


always @(posedge clk) begin
	dw_1 <= DW_RAM_1[dw_addr];
	if(dw_wen[1]) begin
		DW_RAM_1[dw_addr] <= dw_din;
	end
end

//group2
always @(posedge clk) begin
	da_2 <= DA_RAM_2[da_addr];
	if(da_wen[2]) begin
		DA_RAM_2[da_addr] <= da_din;
	end
end


always @(posedge clk) begin
	dw_2 <= DW_RAM_2[dw_addr];
	if(dw_wen[2]) begin
		DW_RAM_2[dw_addr] <= dw_din;
	end
end

//group3
always @(posedge clk) begin
	da_3 <= DA_RAM_3[da_addr];
	if(da_wen[3]) begin
		DA_RAM_3[da_addr] <= da_din;
	end
end


always @(posedge clk) begin
	dw_3 <= DW_RAM_3[dw_addr];
	if(dw_wen[3]) begin
		DW_RAM_3[dw_addr] <= dw_din;
	end
end

//group4
always @(posedge clk) begin
	da_4 <= DA_RAM_4[da_addr];
	if(da_wen[4]) begin
		DA_RAM_4[da_addr] <= da_din;
	end
end


always @(posedge clk) begin
	dw_4 <= DW_RAM_4[dw_addr];
	if(dw_wen[4]) begin
		DW_RAM_4[dw_addr] <= dw_din;
	end
end

//group5
always @(posedge clk) begin
	da_5 <= DA_RAM_5[da_addr];
	if(da_wen[5]) begin
		DA_RAM_5[da_addr] <= da_din;
	end
end


always @(posedge clk) begin
	dw_5 <= DW_RAM_5[dw_addr];
	if(dw_wen[5]) begin
		DW_RAM_5[dw_addr] <= dw_din;
	end
end

//group6
always @(posedge clk) begin
	da_6 <= DA_RAM_6[da_addr];
	if(da_wen[6]) begin
		DA_RAM_6[da_addr] <= da_din;
	end
end


always @(posedge clk) begin
	dw_6 <= DW_RAM_6[dw_addr];
	if(dw_wen[6]) begin
		DW_RAM_6[dw_addr] <= dw_din;
	end
end

//group7
always @(posedge clk) begin
	da_7 <= DA_RAM_7[da_addr];
	if(da_wen[7]) begin
		DA_RAM_7[da_addr] <= da_din;
	end
end


always @(posedge clk) begin
	dw_7 <= DW_RAM_7[dw_addr];
	if(dw_wen[7]) begin
		DW_RAM_7[dw_addr] <= dw_din;
	end
end

//group8
always @(posedge clk) begin
	da_8 <= DA_RAM_8[da_addr];
	if(da_wen[8]) begin
		DA_RAM_8[da_addr] <= da_din;
	end
end


always @(posedge clk) begin
	dw_8 <= DW_RAM_8[dw_addr];
	if(dw_wen[8]) begin
		DW_RAM_8[dw_addr] <= dw_din;
	end
end

//group9
always @(posedge clk) begin
	da_9 <= DA_RAM_9[da_addr];
	if(da_wen[9]) begin
		DA_RAM_9[da_addr] <= da_din;
	end
end


always @(posedge clk) begin
	dw_9 <= DW_RAM_9[dw_addr];
	if(dw_wen[9]) begin
		DW_RAM_9[dw_addr] <= dw_din;
	end
end

endmodule

