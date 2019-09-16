`include "extern.v"

module float_mult(clk,rst_n,f_a,f_b,out_a);

//运算参数，根据定义生成，一般不需要更改。
parameter E_ref = {(`E_bit-1){1'b1}};			//指数零偏
parameter E_add_max = {(`E_bit){1'b1}}+E_ref-1;

input wire[`E_bit+`F_bit:0] f_a,f_b;			//符号位1 指数位 `E_bit 尾数位`F_bit
output [`E_bit+`F_bit:0] out_a;
input rst_n,clk;

//reg [`E_bit+`F_bit:0] out_a;
assign out_a = {S[2],e2,f2};

wire[`E_bit:0] mul_a_e,mul_b_e;		//浮点数分解
wire[`F_bit:0] mul_a_f,mul_b_f;
wire S0;

//输入规范化解码
assign S0 = mul_a[`E_bit+`F_bit]^mul_b[`E_bit+`F_bit];			//乘法符号位流水线
assign mul_a_e = {1'b0, mul_a[`E_bit+`F_bit-1:`F_bit]};		//指数位高位扩充0
assign mul_b_e = {1'b0, mul_b[`E_bit+`F_bit-1:`F_bit]};		//指数位高位扩充0
assign mul_a_f = {1'b1, mul_a[`F_bit-1:0]};						//规范化转非规范化，尾数高位扩充为1
assign mul_b_f = {1'b1, mul_b[`F_bit-1:0]};						//规范化转非规范化，尾数高位扩充为1

reg[`F_bit*2+1:0] f0;								//各级流水线尾数暂存
reg[`F_bit+1:0] f1;
reg[`F_bit-1:0] f2;

reg[`E_bit:0] e0,e1;							//各级流水线指数暂存
reg[`E_bit-1:0]e2;

reg[2:0] S;											//各级流水线符号暂存

reg [`D_LEN-1:0] mul_a,mul_b;

//LEVEL 0: INPUT BUF
always @(posedge clk or negedge rst_n)begin
	if(!rst_n)begin
		mul_a <= 0;
		mul_b <= 0;
	end
	else begin
		mul_a <= f_a;
		mul_b <= f_b;
	end
end

//LEVEL1:尾数求积，阶码求和
always @(posedge clk or negedge rst_n) begin
	if(!rst_n) begin					//复位流水线级各参数
		f0 <= 0;
		e0 <= 0;
		S[0] <= 0;
	end
	else begin
		S[0] <= S0;			//流水线移位
		f0 <= mul_a_f * mul_b_f;
		if(mul_a_e == {1'b0,{(`E_bit){1'b1}}} || mul_b_e == {1'b0,{(`E_bit){1'b1}}})begin		//Nan|无穷数判断
			e0 <= E_add_max;
			S[0] <= 1;
		end
		else if(mul_a_e == 0 || mul_b_e == 0)begin															//0判断
			e0 <= 0;
		end
		else begin
			e0 <= mul_a_e + mul_b_e;
		end
	end
end

//LEVEL2:指数减偏置并判溢
always @(posedge clk or negedge rst_n)begin
	if(!rst_n) begin					//复位流水线级各参数
		f1 <= 0;
		e1 <= 0;
		S[1] <= 0;
	end
	else begin
		S[1] <= S[0];
		if(e0 > E_ref) begin
			if(e0 >= E_add_max) begin		//指数上溢，Nan
				e1 <= {(`E_bit+1){1'b1}};	//指数全赋值1
				f1[`F_bit-1] <= 1;			//尾数!=0
			end
			else begin				//没有溢出
				if(f0[2*`F_bit+1]) begin	//如果最高位为1，尾数进位
					f1 <= f0[`F_bit*2+1:`F_bit+1]+f0[`F_bit];
					e1 <= e0 - E_ref+1'b1;
				end
				else begin
					f1 <= f0[`F_bit*2:`F_bit]+f0[`F_bit-1];			//保留`F_bit*2+1-`F_bit+1 用于规范化输出，同时进位
					e1 <= (e0 - E_ref);
				end
			end
		end
		else begin					//指数下溢，无穷小
			e1 <= 0;			//每位赋0
			f1 <= 0;			//每位赋0
		end
	end
end

//LEVEL3:尾数进位判断
always @(posedge clk or negedge rst_n)begin
	if(!rst_n) begin					//复位流水线级各参数
		f2 <= 0;
		e2 <= 0;
		S[2] <= 0;
	end
	else begin
		S[2] = S[1];
		if(f1[`F_bit+1]) begin	//如果最高位为1，尾数进位
			f2 <= f1[`F_bit:1];
			e2 <= e1[`E_bit-1:0]+1'b1;
		end
		else begin
			f2 <= f1[`F_bit-1:0];
			e2 <= e1[`E_bit-1:0];
		end
	end
end

endmodule
