`include "extern.v"
module sci_controller(clk,rst_n,
						nn_start,nn_finish,
						rx_data,rx_ready,rx_error,
						tx_data,tx_ready,tx_start,
						opm_base,opm_offset,r_data,a_in);

parameter SOF_1 = 8'h55, SOF_2 = 8'hab, SOF_3 = 8'haa;			//3 bytes : start of frame 

input clk,rst_n;
input nn_finish;
output nn_start;

input [7:0] rx_data;
output [7:0] tx_data;
input rx_ready,rx_error,tx_ready;
output tx_start;

output [`I_NUM-1:0] a_in;

input [`D_LEN-1:0] r_data;
output [`OFS_WIDTH-1:0] opm_offset;
output [`DA_AWIDTH-1:0] opm_base;

//串口控制启动计算
reg nn_start;

//写RAM相关控制
reg [`OFS_WIDTH-1:0] opm_offset;
reg[`OUT_AWIDTH-1:0] opm_cnt;
reg[`DA_AWIDTH-1:0] opm_base;

reg[7:0] rx_len,rx_lcnt;
reg [`DA_AWIDTH-1:0] base_addr;
reg [`I_NUM-1:0] a_in;								//神经元输入数据

//发送串口相关
reg tx_start;
reg [`O_NUM-1:0] tx_buf;				//字节长度（8的整数倍）

assign tx_data = tx_buf>>(tx_byte_cnt*8);

//转换控制
reg [`O_NUM-1:0] a_out,a_out_;
reg send_cmd;					//发送指令
reg hop_as;

//状态机控制
reg[3:0] frame_p;
reg[7:0] state_r,state_t,state_m;

//发送计数器
reg[7:0] tx_byte_cnt;

//赋值数据
reg nn_finish_;
wire nn_f = (~nn_finish_)&nn_finish;

always @(posedge clk)begin
	nn_finish_ <= nn_finish;
end

//接收帧解码
//1: SOF_1
//2: SOF_2
//3: SOF_3
//4: BASE_ADDR 
//5: DLEN
always @(posedge rx_ready or negedge rst_n)begin
	if(!rst_n)begin
		frame_p <= 0;
		base_addr <= 0;
	end
	else begin
		case(frame_p)
		0:begin
			if(rx_data == SOF_1)	frame_p <= 1;
			else frame_p <= 0;
		end
		1:begin
			if(rx_data == SOF_2) frame_p <= 2;
			else frame_p <= 0;
		end
		2:begin
			if(rx_data == SOF_3)	frame_p <= 3; 
			else frame_p <= 0;
		end
		3:begin
			base_addr <= rx_data;
			frame_p <= 4;
		end
		4:begin
			rx_len <= rx_data;
			a_in <= 0;
			rx_lcnt <= 0;
			frame_p <= 5;
		end
		5:begin
			if(rx_lcnt < rx_len)begin			//接收一定长度的数据
				a_in <= {a_in[`I_NUM-9:0],rx_data};
				rx_lcnt <= rx_lcnt + 1'b1;
				frame_p <= 5;
			end
			else begin
				a_in <= {a_in[`I_NUM-9:0],rx_data};
				frame_p <= 0;
			end
		end
		endcase
	end
end

//接收缓存处理
always @(posedge clk or negedge rst_n)begin
	if(!rst_n)begin
		state_r <= 0;
		nn_start <= 0;
	end
	else begin
		case(state_r)
		0:begin
			nn_start <= 0;
			if(frame_p < 3)begin				//未接受到帧头
				state_r <= 0;
			end
			else begin
				state_r <= 1;
			end
		end
		
		1:begin												//接收数据中
			if(frame_p == 0)begin		//开始写数据
				state_r <= 2;
			end
			else begin
				state_r <= 1;								//数据接收完成
			end
		end
		
		2:begin									//将数据转换并写入
			nn_start <= 1;
			state_r <= 3;
		end
		3:begin									//8bit 全部写入，数据未写满
			state_r <= 0;
		end
		default : state_r <= 0;
		endcase
	end
end

//内存读取转换状态机 state of memery read
always @(posedge clk or negedge rst_n)begin
	if(!rst_n)begin
		state_m <= 0;
		
		opm_base <= 0;
		opm_offset <= 0;
		opm_cnt <= 0;
		
		a_out <= 0;											//hopfield单次迭代输出
		send_cmd <= 0;										//触发发送指令
	end
	else begin
		case(state_m)
		0:begin			
			if(nn_f == 1)	begin							//神经网络运算完成
				hop_as <= 1;
				a_out <= 0;
				opm_base <= base_addr;
				opm_offset <= 0;
				opm_cnt <= 0;
				
				state_m <= 1;
			end
			else begin
				send_cmd <= 0;
				state_m <= 0;
			end
		end
		
		1:state_m <= 2;
		2:state_m <= 3;
		3:state_m <= 4;
		4:state_m <= 5;
		
		5:begin																	//读取内存，转换数据
			if(r_data != {(`F_bit+`E_bit+1){1'b0}})begin				//如果等于浮点1，则并置1，否则并置0
				a_out <= {a_out[`O_NUM-2:0],1'b1};						//左移并位
			end
			else begin
				a_out <= {a_out[`O_NUM-2:0],1'b0};
			end
			
			if(opm_cnt < `O_NUM-1)begin									//更新地址
				opm_cnt <= opm_cnt + 1'b1;
				if(opm_offset < `CELL_N-1)begin
					opm_offset <= opm_offset + 1'b1;
				end
				else begin
					opm_offset <= 0;
					opm_base <= opm_base + 1'b1;
				end
				state_m <= 1;
			end
			else begin															//读取结束
				state_m <= 6;
			end
		end
		
		6:begin
			tx_buf <= a_out;
			state_m <= 7;
		end
		7:begin								//等待发送状态机闲置
			if(state_t != 0)begin
				send_cmd <= 0;
				state_m <= 7;
			end
			else begin
				send_cmd <= 1;				//启动transmition
				state_m <= 0;
			end
		end
		default: state_m <= 0;
		endcase
	end
end

//串口发送状态机 state of sci transmite
always @(posedge clk or negedge rst_n)begin
	if(!rst_n)begin
		state_t <= 0;
		tx_start <= 0;
		tx_byte_cnt <= 0;
	end
	else begin
		case(state_t)
		0:begin
			if(send_cmd == 1)	begin							//神经网络运算完成
				state_t <= 1;
				tx_byte_cnt <= 0;
			end
			else begin
				tx_start <= 0;
				state_t <= 0;
			end
		end
		
		1:state_t <= 4;		
		3:begin
			if(tx_byte_cnt < (`O_NUM>>3)-1)begin					//发送N字节数据
				tx_byte_cnt <= tx_byte_cnt + 1'b1;
				state_t <= 4;								//发送状态
			end
			else begin										//发送完一个字节
				state_t <= 0;
			end
		end
		
		4:begin							//等待发送响应
			if(tx_ready == 1) state_t <= 5;
			else state_t <= 4;
		end
		
		5:begin							//启动发送，等待串口发送模块响应
			tx_start <= 1;
			if(tx_ready == 0)begin
				tx_start <= 0;
				state_t <= 3;
			end
			else state_t <= 5;
		end
		default:state_t <= 0;
		endcase
	end
end

endmodule

