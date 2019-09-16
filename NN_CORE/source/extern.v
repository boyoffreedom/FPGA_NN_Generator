//超参数定义
	//浮点位数定义，加法器需重新定制编码器
`define E_bit 5
`define F_bit 8
`define D_LEN (`E_bit+`F_bit+1)
	//单次运算数据长度、运算单元数量、运算单元输出地址位数定义
`define CELL_N 10 			//运算单元的数量
`define AWIDTH 4			//输入地址位宽，数据总个数除以运算单元的位数
`define ADDR_L (2**`AWIDTH-1) 		//单次触发最大循环调用运算单元次数

//t//内部RAM参数定义
`define DWIDTH (`CELL_N*(`E_bit+`F_bit+1)) 	//内部RAM数据总线宽度

	//神经网络数据路由接口位宽定义
`define NP_W 7 				//NEURON POINTER NUMBER 神经元个数，与网络规模有关，每个神经元对应一个地址
`define LL 4 				//Link Width 连接长度，决定了与该神经元连接的神经元数的最大值，8位单个神经元最大相关神经元为256个

`define DA_AWIDTH 5 			//特征值存储器地址宽度
`define DW_AWIDTH 10 			//权值存储器地址宽度

	//神经网络结构与数据RAM DEPTH定义
`define NP_NUM 72 		//神经元个数
`define DA_DEPTH 16 			//特征值存储器DEPTH
`define DW_DEPTH 576 			//权值存储器DEPTH

//输入输出
`define IN_AWIDTH 7
`define OUT_AWIDTH 7
`define OFS_WIDTH 4
`define I_NUM 72
`define O_NUM 72
