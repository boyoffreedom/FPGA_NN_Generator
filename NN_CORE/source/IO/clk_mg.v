module CLK_MNG (clk,rst_n,baud_clk);

parameter BAUD_CNT = 62;//50M/Baudrate/7

input clk,rst_n;
output baud_clk;

reg baud_clk;
reg[16:0] fdiv_cnt;

always @(posedge clk or negedge rst_n)begin
	if(!rst_n)begin
		fdiv_cnt <= 0;
	end
	else begin
		if(fdiv_cnt <= BAUD_CNT)begin
			fdiv_cnt <= fdiv_cnt + 1'b1;
			baud_clk <= 0;
		end
		else begin
			fdiv_cnt <= 0;
			baud_clk <= 1;
		end
	end
end
endmodule 

