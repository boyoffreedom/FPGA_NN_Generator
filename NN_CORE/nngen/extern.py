import math,codecs

def extern_gen(path,cell_n,float_format,depth_info):
    [f_bit,e_bit] = float_format
    [np_num, da_depth, dw_depth, l_depth, in_n, on_n, ofs_width, iw, ow] = depth_info

    np_width = math.floor(math.log(np_num, 2) + 1)  # 神经元位宽
    dw_width = math.floor(math.log(dw_depth, 2) + 1)
    da_width = math.floor(math.log(da_depth, 2) + 1)
    ll = math.floor(math.log(l_depth, 2) + 1)

    with codecs.open(path+'/extern.v', 'w', encoding='utf-8') as fe:
        fe.write(u'//超参数定义\n\t//浮点位数定义，加法器需重新定制编码器\n')
        fe.write(u'`define E_bit %d\n`define F_bit %d\n`define D_LEN (`E_bit+`F_bit+1)\n' % (e_bit, f_bit))
        fe.write(u'\t//单次运算数据长度、运算单元数量、运算单元输出地址位数定义\n')
        fe.write(u'`define CELL_N %d \t\t\t//运算单元的数量\n' % cell_n)
        fe.write(u'`define AWIDTH %d\t\t\t//输入地址位宽，数据总个数除以运算单元的位数\n' % ll)
        fe.write(u'`define ADDR_L (2**`AWIDTH-1) \t\t//单次触发最大循环调用运算单元次数\n')
        fe.write(u'\n//t//内部RAM参数定义\n')
        fe.write(u'`define DWIDTH (`CELL_N*(`E_bit+`F_bit+1)) \t//内部RAM数据总线宽度\n\n')
        # 神经网络数据路由接口位宽定义
        fe.write(u'\t//神经网络数据路由接口位宽定义\n')
        fe.write(u'`define NP_W %d \t\t\t\t//NEURON POINTER NUMBER 神经元个数，与网络规模有关，每个神经元对应一个地址\n' % np_width)

        fe.write(u'`define LL %d \t\t\t\t//Link Width 连接长度，决定了与该神经元连接的神经元数的最大值，8位单个神经元最大相关神经元为256个\n\n' % ll)
        fe.write(u'`define DA_AWIDTH %d \t\t\t//特征值存储器地址宽度\n' % da_width)
        fe.write(u'`define DW_AWIDTH %d \t\t\t//权值存储器地址宽度\n\n' % dw_width)
        # 神经网络结构与数据RAM DEPTH定义
        fe.write(u'\t//神经网络结构与数据RAM DEPTH定义\n')
        fe.write(u'`define NP_NUM %d \t\t//神经元个数\n' % np_num)
        #fe.write(u'`define L_DEPTH %d \t\t\t\t//连接长度DEPTH\n\n' % l_depth)
        fe.write(u'`define DA_DEPTH %d \t\t\t//特征值存储器DEPTH\n' % da_depth)
        fe.write(u'`define DW_DEPTH %d \t\t\t//权值存储器DEPTH\n\n' % dw_depth)

        fe.write(u'//输入输出\n`define IN_AWIDTH %d\n' % iw)
        fe.write(u'`define OUT_AWIDTH %d\n' % ow)
        fe.write(u'`define OFS_WIDTH %d\n' % ofs_width)
        fe.write(u'`define I_NUM %d\n' % in_n)
        fe.write(u'`define O_NUM %d\n' % on_n)
        print('extern.v文件生成完成！')

if __name__ == '__main__':
    extern_gen('./',10,[23,8],[46,120,3000,13,72,10])