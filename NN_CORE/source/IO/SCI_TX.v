module SCI_TX (baud_clk,rst_n,txd,tx_data,tx_start,tx_ready);

input baud_clk,rst_n,tx_start;
input [7:0] tx_data;
output tx_ready,txd;

reg  tx_ready,txd;

reg[3:0] state_tx;
reg[3:0] cnt;
reg[7:0] txd_buf;		//txd bit send buf
reg[3:0] send_bit;

reg tx_start_;

wire txd_s = (~tx_start_)&tx_start;

always @(posedge baud_clk)begin
	tx_start_ <= tx_start;
end

//serial communication byte level
always@(posedge baud_clk or negedge rst_n) begin
	if(!rst_n) begin
		tx_ready <= 1;
		send_bit <= 0;
		txd_buf <= 0;
		state_tx <= 0;
	end
	else begin
	case(state_tx)
		0:begin					//等待信号发生
			if(txd_s == 1) begin
				tx_ready <= 0;			//进入忙碌状态
				txd_buf <= tx_data;		//数据缓存
				send_bit <= 1;
				state_tx <= 1;
				cnt <= 0;
			end
			else begin
				send_bit <= 0;
				tx_ready <= 1;
				state_tx <= 0;
			end
		end
		1:begin
			if(cnt < 4'd6)begin
				cnt <= cnt + 1'b1;
			end
			else begin
				cnt <= 0;
				if(send_bit < 10) begin
					send_bit <= send_bit + 1'b1;
				end
				else begin
					send_bit <= 0;							//重置发送位计数器
					state_tx <= 2;
				end
			end
		end
		2:begin		//end of send;
			tx_ready <= 1;
			state_tx <= 0;
		end
		default:state_tx <= 0;
		endcase
	end
end

//serial communication bit level
always @(send_bit or txd_buf)begin
	case(send_bit)
		4'd0 : txd <= 1'b1;			//start_bit_pre
		4'd1 : txd <= 1'b0;			//start_bit
		4'd2 : txd <= txd_buf[0];	//data_bit
		4'd3 : txd <= txd_buf[1];
		4'd4 : txd <= txd_buf[2];
		4'd5 : txd <= txd_buf[3];
		4'd6 : txd <= txd_buf[4];
		4'd7 : txd <= txd_buf[5];
		4'd8 : txd <= txd_buf[6];
		4'd9 : txd <= txd_buf[7];
		4'd10: txd <= 1'b1;
		default:txd<= 1'b1;			//default
	endcase
end
endmodule

