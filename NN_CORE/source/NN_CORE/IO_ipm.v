`include "extern.v"
//输入处理模块，由路由模块控制，发送数据请求，获得响应后发送数据
module ipm(clk,rst_n,
				a_in,nn_start,
				ipm_request,ipm_enable,ipm_finish,
				ipm_base,ipm_offset,ipm_din,ipm_wen);

parameter OVERFLOW_TIME = 32'd2_000_000;
				
input clk,rst_n,ipm_enable;								//时钟，复位，输入请求
input [`I_NUM-1:0] a_in;												//数据输入
input nn_start;												//开始计算
output[`D_LEN-1:0] ipm_din;								//输入处理模块与路由模块数据接口
output ipm_finish,ipm_wen;									//输入完成
output [`DA_AWIDTH-1:0] ipm_base;
output[`OFS_WIDTH-1:0] ipm_offset;
output ipm_request;

reg ipm_finish,ipm_wen;
reg [`OFS_WIDTH-1:0] ipm_offset;
reg[`DA_AWIDTH-1:0] ipm_base;
reg[`IN_AWIDTH-1:0] ipm_cnt;
reg ipm_request;

reg start_nn_pbuf;											//上升沿判断缓冲
wire start_nn_pedge = (~start_nn_pbuf)&nn_start;	//判断上升沿
integer cnt;
reg[4:0] state_c;

wire [`D_LEN-1:0] ipm_din = (a_in[`I_NUM-1-ipm_cnt] == 0)?0:{2'b00,{(`E_bit-1){1'b1}},{(`F_bit){1'b0}}};

always @(posedge clk)begin
	start_nn_pbuf <= nn_start;
end

always @(posedge clk or negedge rst_n)begin
	if(!rst_n)begin
		ipm_finish <= 0;
		ipm_wen <= 0;
		
		ipm_base <= 0;
		ipm_offset <= 0;
		ipm_cnt <= 0;
		
		ipm_request <= 0;
		cnt <= 0;
		state_c <= 0;
	end
	else begin
		case(state_c)
		0:begin
			if(start_nn_pedge)begin				//开始推理计算
				state_c <= 1;
				ipm_finish <= 0;
				ipm_wen <= 0;
				//地址
				ipm_base <= 0;
				ipm_offset <= 0;
				ipm_cnt <= 0;
				
				cnt <= 0;
				ipm_request <= 1;					//发起写RAM请求
			end
			else begin
				state_c <= 0;
			end
		end
		1:begin
			if(ipm_enable)begin					//接收到路由模块使能
				state_c <= 3;
				cnt <= 0;
				
				ipm_base <= 0;
				ipm_offset <= 0;
				ipm_cnt <= 0;
				
				ipm_request <= 0;
			end
			else begin
				if(cnt > OVERFLOW_TIME)begin	//超出溢出时间
					state_c <= 0;
					cnt <= 0;
				end
				else begin
					state_c <= 1;
					cnt <= cnt + 1'b1;
				end
			end
		end
		2:begin										//开始传输
			ipm_wen <= 0;
			if(ipm_cnt < `I_NUM-1)begin
				ipm_cnt <= ipm_cnt+1'b1;
				if(ipm_offset < `CELL_N-1'b1)begin
					ipm_offset <= ipm_offset + 1'b1;
				end
				else begin
					ipm_offset <= 0;
					ipm_base <= ipm_base + 1'b1;
				end
				state_c <= 3;
			end
			else begin
				cnt <= 0;
				ipm_finish <= 1;
				state_c <= 10;
			end
		end
		3:state_c <= 4;
		4:state_c <= 5;
		5:state_c <= 6;
		6:state_c <= 7;
		7:state_c <= 8;
		8:begin
			ipm_wen <= 1;
			state_c <= 9;
		end
		9:begin
			ipm_wen <= 0;
			state_c <= 2;
		end
		10:begin
			ipm_finish <= 0;
			state_c <= 0;
		end
		default:state_c <= 0;
		endcase
	end
end

endmodule
				