import pickle,os
from nn_core_mif import *
from acfunc import *
from pram import *

#生成可配置加法器
def adder_gen(path,src,float_format):
    [F_bit,E_bit] = float_format
    with open(path+'/NN_CORE/M_float_adder.v', 'w') as f:
        f.write("always @(add_f1) begin\n\tcasex(add_f1[2*`F_bit+1:`F_bit+1])\n")
        for i in range(0, F_bit + 1):
            f.write("\t\t%d\'b" % (F_bit + 1))
            a = ""
            for j in range(0, i):
                a += "0"
            a += "1"
            for j in range(i, F_bit):
                a += "x"
            f.write(a)
            f.write(": sub_shift=%d'd%d" % (E_bit, i))
            f.write(";\n")
        f.write("\t\tdefault: sub_shift = %d'd%d;\n" % (E_bit, F_bit + 1))
        f.write("\tendcase\nend\nendmodule\n\n")

    with open(path+'/NN_CORE/M_float_adder.v','rb') as f:
        d = f.read()
    with open(path+'/NN_CORE/M_float_adder.v','wb+') as f:
        f.write(src)
        f.write(d)

#生成网络核心部件
def NN_CORE(path,cell_n,float_format):
    if(len(float_format) < 2):
        print('float format error!')
        return 1

    with open('./bin/nn_core.srcpack', 'rb') as f:
        nn_source = pickle.load(f)

    isExists = os.path.exists(path+'/NN_CORE')
    if not isExists:
        os.makedirs(path+'/NN_CORE')

    #A_encoder、A_sigmoid、A_sigmoid_lut由ACTIVE FUNC库生成

    #MAC Module
    with open(path+'/NN_CORE/M_MAC.v','wb') as f:
        f.write(nn_source['M_MAC'])

    with open(path+'/NN_CORE/M_AA.v','wb') as f:
        f.write(nn_source['M_AA'])

    with open(path+'/NN_CORE/M_MA.v','wb') as f:
        f.write(nn_source['M_MA'])

    with open(path+'/NN_CORE/M_controller.v','wb') as f:
        f.write(nn_source['M_controller'])

    with open(path+'/NN_CORE/M_float_mul.v','wb') as f:
        f.write(nn_source['M_float_mul'])

    adder_gen(path, nn_source['M_float_adder'],float_format)

    #roater
    with open(path+'/NN_CORE/R_ROUTER_BUS.v','wb') as f:
        f.write(nn_source['R_ROUTER_BUS'])

    with open(path+'/NN_CORE/R_router_controller.v','wb') as f:
        f.write(nn_source['R_router_controller'])

    #main
    with open(path+'/NN_CORE/nn_core.v','wb') as f:
        f.write(nn_source['nn_core'])
    with open(path+'/nn_core/IO_ipm.v', 'wb') as f:  # 将数据写入文件
        f.write(nn_source['IO_ipm'])
    with open(path+'/nn.v','wb') as f:
        f.write(nn_source['nn'])

    acfunc_gen(path, nn_source,float_format)
    PRAM_gen(path, cell_n)
    print('网络内核架构生成完成!')

#生成串口IO文件
def SCI_IO_GEN(path,mode=0):
    with open('./bin/sci_io.srcpack', 'rb') as pkl_file:
        io_source = pickle.load(pkl_file)

    isExists = os.path.exists(path+'/IO')
    if not isExists:
        os.makedirs(path+'/IO')

    with open(path+'./IO/clk_mg.v','wb') as f:
        f.write(io_source['clk_mg'])
    with open(path+'/IO/sci_controller.v','wb') as f:
        if mode == 0:
            f.write(io_source['sci_controller'])
        else:
            f.write(io_source['sci_img'])

    with open(path+'/IO/SCI_IO.v','wb') as f:
        f.write(io_source['SCI_IO'])

    with open(path+'/IO/SCI_RX.v','wb') as f:
        f.write(io_source['SCI_RX'])

    with open(path+'/IO/SCI_TX.v','wb') as f:
        f.write(io_source['SCI_TX'])

    print('串口源文件生成完成！')

if __name__ == '__main__':
    cvm_n = 20
    fm = [8, 5]                #定义运算浮点数格式
    path = '../source'
    #ninfo_f = '../nntrain/hop.ninfo'
    ninfo_f = '../nntrain/bp.ninfo'
    NN_CORE(path,cvm_n, fm)
    SCI_IO_GEN(path,1)
    nn_mif_gen(path, cvm_n, fm, ninfo_f)
    #hop_mif_gen(path, cvm_n, fm, './nnstruct/hop.ninfo')