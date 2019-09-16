`include "../extern.v"

module router_controller(clk,rst_n,nn_start,nn_finish,
								ipm_request,ipm_finish,ipm_enable,ipm_din,ipm_base,ipm_offset,ipm_wen,							//ipm接口
								opm_request,opm_finish,opm_enable,opm_dout,opm_base,opm_offset,						//opm接口
								mac0_din,mac0_ctrl,mac0_finish,mac0_addr,mac0_acftype,									//mac0接口
								da_din,da_wen,da_addr,da_sel,da_dout,														//PRAM接口
								dw_din,dw_wen,dw_addr,dw_sel,dw_dout
								);

input clk,rst_n,nn_start;
output nn_finish;

//IO处理模块接口定义
input ipm_request,ipm_finish,ipm_wen;
input opm_request,opm_finish;
output ipm_enable,opm_enable;
input [`D_LEN-1:0] ipm_din;
input [`OFS_WIDTH-1:0] ipm_offset;			//相对地址的偏移量
input [`OFS_WIDTH-1:0] opm_offset;
input [`DA_AWIDTH-1:0] ipm_base,opm_base;
output[`D_LEN-1:0] opm_dout;

//mac0接口定义
input[`D_LEN-1:0] mac0_din;
output[`AWIDTH:0] mac0_ctrl;
input mac0_finish;
input[`LL-1:0] mac0_addr;
output[3:0] mac0_acftype;

//路由模块数据交互接口定义
	//da
output [`D_LEN-1:0]da_din;				//PRAM单个数据输入
input [`D_LEN-1:0] da_dout;			//PRAM单个数据输出
output [`DA_AWIDTH-1:0] da_addr;
output [`CELL_N-1:0] da_wen;
output [`CELL_N-1:0] da_sel;
	//dw
output [`D_LEN-1:0] dw_din;			//PRAM单个数据输入
input [`D_LEN-1:0] dw_dout;			//PRAM单个数据输出
output [`DW_AWIDTH-1:0] dw_addr;
output [`CELL_N-1:0] dw_wen;
output [`CELL_N-1:0] dw_sel;

//神经元信息表
//神经元信息表：状态值基地址，权值基地址，连接神经元长度比，计算结果目的地址，激活函数类型
reg[`DA_AWIDTH-1:0] ROM_BAA[`NP_NUM-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/rom_baa.mif" */;			//BASS ADDTRESS OF A
reg[`DW_AWIDTH-1:0] ROM_BAW[`NP_NUM-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/rom_baw.mif" */;			//BASS ADDTRESS OF W
reg[`LL-1:0] 		  ROM_LNL[`NP_NUM-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/rom_lnl.mif" */;			//link neuron length
reg[`DA_AWIDTH-1:0] ROM_BAD[`NP_NUM-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/rom_bad.mif" */;			//dest base address
reg[`OFS_WIDTH-1:0] ROM_OFS[`NP_NUM-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/rom_ofs.mif" */;			//dest offset address
reg[3:0] 			  ROM_ACF[`NP_NUM-1:0]/* synthesis ram_init_file = "./NN_CORE/MIF/rom_acf.mif" */;			//active function

reg [`NP_W-1:0] mac0_np;

//mac0 运算信息寄存器
reg mac0_start;
reg [`DA_AWIDTH-1:0] mac0_base_a;		//source address
reg [`DW_AWIDTH-1:0] mac0_base_w;		//source address
reg[`LL-1:0] mac0_lnl;					//connection neuron data length
reg [`DA_AWIDTH-1:0] mac0_dstbase;		//destnation address
reg [`OFS_WIDTH-1:0] mac0_offset;		//destnation address
reg[3:0] mac0_acftype;
wire [`AWIDTH-1:0] mac0_loop = mac0_lnl;
assign mac0_ctrl = {mac0_loop,mac0_start};

//IO处理模块信息
reg ipm_enable,nn_finish;
reg opm_enable;

assign opm_dout = (opm_enable==1'b1)?da_dout:0;

//PRAM读取单个数据接口
reg[`D_LEN-1:0] da_din,dw_din;
reg[`CELL_N-1:0] da_wen,dw_wen;
reg[`CELL_N-1:0] da_sel,dw_sel;
reg[`DA_AWIDTH-1:0] da_addr;
reg[`DW_AWIDTH-1:0] dw_addr;

//状态机变量
reg[4:0] state_a,state_w,state_c;

//MAC0运算结束上升沿判断
reg mac0_finish_;
wire mac0_f = (~mac0_finish_)&mac0_finish;
always @(posedge clk)begin
	mac0_finish_ <= mac0_finish;
end

//MAC0运算信息读取
always @(posedge clk or negedge rst_n)begin
	if(!rst_n)begin
		mac0_base_a <= 0;
		mac0_base_w <= 0;
		mac0_lnl <= 0;
		mac0_dstbase <= 0;
		mac0_offset <= 0;
		mac0_acftype <= 0;
	end
	else begin
		mac0_base_a <= ROM_BAA[mac0_np];
		mac0_base_w <= ROM_BAW[mac0_np];
		mac0_lnl <= ROM_LNL[mac0_np]-1'b1;
		mac0_dstbase <= ROM_BAD[mac0_np];
		mac0_offset <= ROM_OFS[mac0_np];
		mac0_acftype <= ROM_ACF[mac0_np];
	end
end

//状态值读写管理控制
always @(posedge clk or negedge rst_n)begin
	if(!rst_n)begin
		state_a <= 0;
		ipm_enable <= 0;
		opm_enable <= 1;
		
		da_wen <= 0;
		da_addr <= 0;
		da_sel <= 0;
		da_din <= 0;
	end
	else begin
		case(state_a)
			0:begin
				opm_enable <= 1;
				ipm_enable <= 0;
				state_a <= 1;
			end
			
			1:begin
				if(ipm_request)begin					//等待IPM请求信号
					ipm_enable <= 1;
					opm_enable <= 0;
					
					da_addr <= ipm_base;
					da_wen <= (1'b1 << ipm_offset)&ipm_wen;
					da_din <= ipm_din;
					
					state_a <= 2;
				end
				else begin
					ipm_enable <= 0;
					opm_enable <= 1;
					
					da_sel <= (1'b1 << opm_offset);
					da_wen <= 0;
					da_addr <= opm_base;
					
					state_a <= 1;
				end
			end
			2:begin										//开始写入输入数据
				ipm_enable <= 0;
				da_addr <= ipm_base;
				da_wen <= (1'b1 << ipm_offset);
				da_din <= ipm_din;
				da_sel <= 0;
				if(ipm_finish == 0)begin			//写入输入数据
					state_a <= 2;
				end
				else begin
					state_a <= 3;
				end
			end
			
			3:begin
			
				da_wen <= 0;					//RAM写入权转给MAC
				da_din <= 0;
				da_addr <= 0;
				
				state_a <= 4;
			end
			
			4:begin														//读写判断
				da_wen <= 0;
				if(nn_finish)begin									//神经网络计算完成，跳转到等待输入
					state_a <= 0;
				end
				else begin 
					if(mac0_f)begin				//写入
						da_addr <= mac0_dstbase;
						state_a <= 5;
					end
					else begin
						da_addr <= mac0_base_a + mac0_addr;
						state_a <= 4;
					end
				end
			end
			5:state_a <= 6;
			6:state_a <= 7;
			7:state_a <= 8;
			8:state_a <= 9;
			9:state_a <= 10;
			10:state_a <= 11;
			11:state_a <= 12;
			12:begin
				da_din <= mac0_din;
				state_a <= 20;
			end
			20:state_a <= 21;
			21:begin
				da_wen <= (1'b1 << mac0_offset);
				state_a <= 22;
			end
			22:state_a <= 4;
			default state_a <= 0;
		endcase
	end
end

//权值阈值读写管理控制
always @(posedge clk or negedge rst_n)begin
	if(!rst_n)begin
		state_w <= 0;
		dw_addr <= 0;
		dw_din <= 0;
		dw_wen <= 0;
		dw_sel <= 0;
	end
	else begin
		dw_addr <= mac0_base_w + mac0_addr;
		dw_din <= 0;
		dw_wen <= 0;
		dw_sel <= 0;
		state_w <= 0;
	end
end

//各神经元指针控制
always @(posedge clk or negedge rst_n)begin
	if(!rst_n)begin
		state_c <= 0;
		nn_finish <= 1;
	end
	else begin
		case(state_c)
			0:begin
				if(nn_start == 1)begin						//等待开始信号
					mac0_np <= 0;
					nn_finish <= 0;
					mac0_start <= 0;
					state_c <= 1;
				end
				else begin
					state_c <= 0;
				end
			end
			1:begin												//等待IPM数据写入
				if(state_a != 4)begin
					state_c <= 1;
				end
				else begin
					mac0_start <= 1'b1;
					state_c <= 9;
				end
			end
			2:begin								//等待运算
				mac0_start <= 0;
				if(mac0_f) state_c <= 3;
				else state_c <= 2;
			end
			3:state_c <= 4;
			4:begin								//等待结果写入
				if(state_a != 4) state_c <= 4;
				else state_c <= 5;
			end
			5:state_c <= 6;
			6:begin								//神经元运算更新
				if(mac0_np < `NP_NUM-1)begin
					mac0_np <= mac0_np+1'b1;
					state_c <= 7;
				end
				else begin						//完成计算
					nn_finish <= 1;
					state_c <= 0;
				end
			end	
			7:state_c <= 8;
			8:begin
				mac0_start <= 1'b1;
				state_c <= 9;
			end
			9:state_c <= 10;
			10:state_c <= 2;
			default state_c <= 0;
		endcase
	end
end

endmodule
