`include "extern.v"

module float_adder(clk,rst_n,f_a,f_b,adder_out);

parameter E_ref = {(`E_bit-1){1'b1}};
parameter E_max = {(`E_bit){1'b1}};

input wire[`E_bit+`F_bit:0] f_a,f_b;
output wire[`E_bit+`F_bit:0] adder_out;
input rst_n,clk;

assign adder_out = {add_s2,add_e2,add_f2};

wire [`E_bit-1:0] a_e = add_a[`E_bit+`F_bit-1:`F_bit];
wire [`E_bit-1:0] b_e = add_b[`E_bit+`F_bit-1:`F_bit];
wire [2*`F_bit:0] a_f = {1'b1,add_a[`F_bit-1:0],{`F_bit{1'b0}}};
wire [2*`F_bit:0] b_f = {1'b1,add_b[`F_bit-1:0],{`F_bit{1'b0}}};
wire 				  a_s = add_a[`E_bit+`F_bit];
wire 				  b_s = add_b[`E_bit+`F_bit];
 
reg a_s0,b_s0,add_s1,add_s2;
reg sub_eq1;

reg[`E_bit-1:0] add_e0;
reg[`E_bit-1:0] add_e1;
reg[`E_bit-1:0] add_e2;

reg[2*`F_bit+1:0] a_f0,b_f0;
reg[2*`F_bit+1:0] add_f1;									
reg[`F_bit-1:0] add_f2;

reg[`D_LEN-1:0] add_a,add_b;

always @(posedge clk or negedge rst_n)begin
	if(!rst_n)begin
		add_a <= 0;
		add_b <= 0;
	end
	else begin
		add_a <= f_a;
		add_b <= f_b;
	end
end

always @(posedge clk or negedge rst_n) begin
	if(!rst_n) begin
		a_s0 <= 0;
		b_s0 <= 0;
		add_e0 <= `F_bit;
		a_f0 <= 0;
		b_f0 <= 0;
	end
	else begin
		if(add_a == 0 && add_b == 0)begin
			a_s0 <= 0;
			b_s0 <= 0;
			add_e0 <= `F_bit;
			a_f0 <= 0;
			b_f0 <= 0;
		end
		else begin
			if((a_e < b_e)|| (a_e == b_e && a_f < b_f)) begin			
				a_s0 <= b_s;
				b_s0 <= a_s;
				add_e0 <= b_e;
				a_f0 <= b_f;
				b_f0 <= a_f>>(b_e-a_e);
			end
			else begin
				a_s0 <= a_s;
				b_s0 <= b_s;
				add_e0 <= a_e;
				a_f0 <= a_f;
				b_f0 <= b_f>>(a_e-b_e);
			end
		end
	end
end


always @(posedge clk or negedge rst_n) begin
	if(!rst_n) begin
		add_e1 <= `F_bit;
		add_f1 <= 0;
		add_s1 <= 0;
		sub_eq1 <= 0;
	end
	else begin
		sub_eq1 <= 0;
		if(a_s0 == b_s0) begin
			add_f1 <= a_f0 + b_f0;
		end
		else begin
			add_f1 <= a_f0 - b_f0;
			if(a_f0 == b_f0) begin
				sub_eq1 <= 1;
			end
		end
		add_s1 <= a_s0;
		add_e1 <= add_e0;
	end
end

reg[`E_bit-1:0] sub_shift;
wire[2*`F_bit+1:0] sub_shift_f1 = (add_f1 << (sub_shift-1'b1));
wire[`F_bit+1:0] add_f1_mix = (add_f1[2*`F_bit+1])?add_f1[2*`F_bit+1:`F_bit]:sub_shift_f1[2*`F_bit:`F_bit-1];
wire[`F_bit+1:0] add_f1_round = add_f1_mix[`F_bit+1:1]+add_f1_mix[0];

always @(posedge clk or negedge rst_n) begin
	if(!rst_n) begin
		add_e2 <= 0;
		add_f2 <= 0;
		add_s2 <= 0;
	end
	else begin
		add_s2 <= add_s1;
		if(add_e1 == E_max) begin
				add_f2 <= 1;
				add_e2 <= {`E_bit{1'b1}};
		end
		else begin	
			if(sub_eq1 == 1) begin
				add_s2 <= 0;
				add_e2 <= 0;
				add_f2 <= 0;
			end
			else begin
				if(add_f1_round[`F_bit+1]) begin
					add_f2 <= add_f1_round[`F_bit:1];
					if(add_f1[2*`F_bit+1])add_e2 <= add_e1 + 2'd2;
					else add_e2 <= add_e1 - (sub_shift-1'b1) + 1'b1;
				end
				else begin
					add_f2 <= add_f1_round[`F_bit-1:0];
					if(add_f1[2*`F_bit+1]) add_e2 <= add_e1 + 2'd1;
					else add_e2 <= add_e1 - (sub_shift-1'b1);
				end
			end
		end
	end
end



always @(add_f1) begin
	casex(add_f1[2*`F_bit+1:`F_bit+1])
		9'b1xxxxxxxx: sub_shift=5'd0;
		9'b01xxxxxxx: sub_shift=5'd1;
		9'b001xxxxxx: sub_shift=5'd2;
		9'b0001xxxxx: sub_shift=5'd3;
		9'b00001xxxx: sub_shift=5'd4;
		9'b000001xxx: sub_shift=5'd5;
		9'b0000001xx: sub_shift=5'd6;
		9'b00000001x: sub_shift=5'd7;
		9'b000000001: sub_shift=5'd8;
		default: sub_shift = 5'd9;
	endcase
end
endmodule

