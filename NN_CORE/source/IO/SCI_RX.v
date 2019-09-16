module SCI_RX(baud_clk,rst_n,rxd,rx_data,rx_ready,rx_error);

input baud_clk,rst_n;
input rxd;
output [7:0] rx_data;
output rx_ready,rx_error;

reg [3:0] cnt;						//接收数据计数器
reg [2:0] rxp;
reg [7:0] rx_data;				//接收数据缓存
reg [7:0] rx_buf;
reg [3:0] state_rx;				//接收数据状态
reg rx_ready,rx_error;

//下降沿采样
wire rxd_nedge = rxd_&(~rxd); //rxd下降沿，表示串口通信开始
reg rxd_;
always @(posedge baud_clk)begin
	rxd_ <= rxd;
end

//接收串口
always @(posedge baud_clk or negedge rst_n)begin
	if(!rst_n)begin
		rx_ready <= 1;
		rx_error <= 0;
		rx_data <= 0;
		rx_buf <= 0;
		cnt <= 0;
		rxp <= 0;
		state_rx <= 0;
	end
	else begin
		case(state_rx)
		0:begin											//等待下降沿开始串口数据接收
			if(rxd_nedge)begin						//下降沿开始接收
				cnt <= 0;								//初始化计数器
				rx_ready <= 0;							//进入忙碌模式
				rx_error <= 0;							//清空错误
				state_rx <= 1;
			end
			else begin
				rx_ready <= 1;
				state_rx <= 0;
			end
		end
		
		1:begin
			if(cnt < 4'd2)begin				   	//采样时钟为baudrate的1/7，时钟对齐采样中心
				state_rx <= 1;
				cnt <= cnt + 1'b1;
			end
			else begin
				if(rxd == 0)begin						//采样为下降沿
					state_rx <= 2;						//开始接收数据
					cnt <= 0;
					rxp <= 0;
				end
				else begin
					state_rx <= 0;
				end
			end
		end
		
		2:begin											//接收八组串口数据
			if(cnt < 4'd6)begin
				cnt <= cnt + 1'b1;
				state_rx <= 2;
			end
			else begin
				cnt <= 0;
				rx_buf[7] <= rxd;
				rx_buf[6:0] <= rx_buf[7:1];			//右移一位
				if(rxp < 3'd7) begin
					rxp <= rxp + 1'b1;
					state_rx <= 2;
				end
				else begin
					cnt <= 0;
					state_rx <= 3;
				end
			end
		end
		
		3:begin											//结束位判断
			if(rxd == 0)begin
				if(cnt >= 4'd10)begin				//结束位过长，接收到数据错误
					rx_error <= 1;
					rx_data <= 8'd0;
					state_rx <= 0;
					cnt <= 0;
				end
				else begin
					cnt <= cnt + 1'b1;
				end
			end
			else begin
				rx_data <= rx_buf;
				state_rx <= 4;
			end
		end
		
		4:begin
			rx_ready <= 1;
			state_rx <= 0;
		end
		
		default:state_rx <= 0;
		endcase
	end
end

endmodule

