`include "../extern.v"
module greater_than(clk,rst_n,float_a,float_b,gt);
//float_a > float_b => gt = 1
//float_a < float_b => gt = 0

input clk,rst_n;
input [`D_LEN-1:0] float_a,float_b;			//浮点比较输入
output gt;												//
reg g_t;

assign gt = g_t;

wire a_s = float_a[`F_bit+`E_bit];			//符号位
wire b_s = float_b[`F_bit+`E_bit];			
/*
wire[`E_bit-1:0] a_e = float_a[`F_bit+`E_bit-1:`F_bit];		//指数位
wire[`E_bit-1:0] b_e = float_b[`F_bit+`E_bit-1:`F_bit];		
wire[`F_bit-1:0] a_f = float_a[`F_bit-1:0];			//尾数位
wire[`F_bit-1:0] b_f = float_b[`F_bit-1:0];



always@(posedge clk or negedge rst_n) begin
	if(!rst_n)begin
		g_t <= 1'b0;
	end
	else begin
		g_t <= 0;
		if(a_s == b_s) begin								//同符号时
			if(a_e > b_e) g_t <= 1'b1^a_s; 			//a指数大于b
			else if(a_e < b_e) g_t <= 1'b0^a_s;		//a指数小于b
			else begin										//尾数相同时
				if(a_f > b_f) g_t <= 1'b1^a_s;		//a尾数大于b
				else g_t <= 1'b0^a_s;					//a尾数小于等于b
			end
		end
		else			 										//符号相异，a为正
			g_t <= 1'b1^a_s;
	end
end*/

always @(posedge clk or negedge rst_n)begin
	if(!rst_n)begin
		g_t <= 1'b0;
	end
	else begin
		g_t <= 0;
		if(a_s == b_s)begin
			if(float_a[`D_LEN-2:0] > float_b[`D_LEN-2:0])begin
				g_t <= 1'b1^a_s;
			end
			else begin
				g_t <= 1'b0^a_s;
			end
		end
		else begin
			g_t <= 1'b1^a_s;
		end
	end
end

endmodule
