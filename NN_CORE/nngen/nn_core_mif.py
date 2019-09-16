import pickle,random,math,os,shutil
from extern import *
from mif import *

def nn_mif_gen(path, cell_n,float_format,fname):                #不定参数,该网络各层的神经元数
    with open(fname, 'rb') as pkl_file:
        nn_data = pickle.load(pkl_file)

    cell_n = int(cell_n)&0xffffffff
    layers = nn_data['scale']
    [f_bit,e_bit] = float_format

    n_n = sum(layers)                  #神经元数个数，神经元信息表的长度
    l_n = len(layers)                  #层数

    np_baa = []           #base address of A
    np_baw = []           #base address of W
    np_lnl = []           #link neuro length
    np_bad = []           #base address of dest
    np_ofs = []           #offset of dest
    np_acf = []           #active function

    da = []
    dw = []

    in_n = layers[0]                    #输入神经元个数
    on_n = layers[-1]
    iw = math.floor(math.log(in_n, 2) + 1)
    ow = math.floor(math.log(on_n, 2) + 1)

    last_layer_neuro_n = layers[0]                  # 上一层神经元个数
    for i in range(1,len(layers)):                  #遍历需要计算的节点神经元
        index_l = str('l%d_info' % i)
        w_data = nn_data[index_l]['wlist']
        acf = nn_data[index_l]['active_function']
        if acf == 'relu':
            acfunc = 0
        elif acf == 'sigmoid':
            acfunc = 1
        elif acf == 'sign':
            acfunc = 2
        else:
            acfunc = 3


        neuro_n_el = layers[i]
        layer_in_atl = math.ceil((last_layer_neuro_n+1)/cell_n )        #当前节点需要循环计算的次数
        da_base = len(da)/cell_n
        #print(len(da),da_base)
        #状态值写入
        da += [random.random() for j in range(0,last_layer_neuro_n)]            #前一层神经元占位
        da += [1.0]                                                             #前一层阈值
        if (last_layer_neuro_n + 1) % cell_n:
            da += [0.0 for j in range(0,cell_n - ((last_layer_neuro_n + 1) % cell_n))]        #用0填充多余的运算器
        dst_base = (len(da)/cell_n)
        for each_neuro in range(0,neuro_n_el):                          #遍历该层所有神经元
            dw_base = int(len(dw) / cell_n)
            wl = w_data[each_neuro]
            dw += wl
            if (last_layer_neuro_n + 1) % cell_n:
                dw += [0.0 for j in range(0, cell_n - ((last_layer_neuro_n + 1) % cell_n))]    #用0填充多余的地址

            np_baa += [da_base]                       #神经元运算状态值起始地址
            np_baw += [dw_base]                       #神经元运算权值起始地址
            np_lnl += [layer_in_atl]                  #连接的神经元数量/运算器数量取整（需要运算循环次数）
            np_bad += [dst_base+math.floor(each_neuro/cell_n)]                      #神经元输出基地址
            np_ofs += [each_neuro%cell_n]                    #神经元输出偏移地址
            np_acf += [acfunc]                        #神经元激活函数
        last_layer_neuro_n = neuro_n_el
    da += [random.random() for j in range(0, last_layer_neuro_n)]       #添加输出层神经元

    np_num = sum(layers[1:])                          #运算神经元位宽
    dw_depth = math.ceil(len(dw)/cell_n)              #权值阈值RAM DEPTH
    da_depth = math.ceil(len(da)/cell_n)              #状态值RAM_DEPTH
    l_depth = math.ceil((max(layers)+1)/cell_n)       #神经元的最大连接数

    np_width = math.floor(math.log(np_num,2)+1)       #神经元位宽
    dw_width = math.floor(math.log(dw_depth,2)+1)     #权值阈值RAM位宽
    da_width = math.floor(math.log(da_depth,2)+1)     #状态值RAM位宽
    ofs_width = math.floor(math.log(cell_n,2)+1) #偏置位宽
    ll = math.floor(math.log(l_depth,2)+1)            #循环计算最大位宽
    print("网络层数",l_n,"输入神经元数量",in_n,"权值数量",len(dw),"状态值数量",len(da))
    print("神经元个数", np_num, '占位地址深度', l_depth, '权值深度', dw_depth, '状态值深度', da_depth)
    print("神经元位宽",np_width,'占位地址位宽',ll,'权值位宽',dw_width,'状态值位宽',da_width)

    #生成内存初始化文件
    isExists = os.path.exists(path + '/NN_CORE/MIF')
    if isExists:
        shutil.rmtree(path + '/NN_CORE/MIF')
        os.makedirs(path + '/NN_CORE/MIF')
    else:
        os.makedirs(path + '/NN_CORE/MIF')
    rom_baa = Mif(path+'/NN_CORE/MIF/', 'rom_baa', np_num, da_width, da_width)         #状态值起始地址
    rom_baw = Mif(path+'/NN_CORE/MIF/', 'rom_baw', np_num, dw_width, dw_width)         #权值起始地址
    rom_lnl = Mif(path+'/NN_CORE/MIF/', 'rom_lnl', np_num, ll, ll)                     #运算周期
    rom_bad = Mif(path+'/NN_CORE/MIF/', 'rom_bad', np_num, da_width, da_width)         #运算神经元状态值基地址
    rom_ofs = Mif(path+'/NN_CORE/MIF/', 'rom_ofs', np_num, ofs_width, ofs_width)           #运算神经元状态值偏移地址
    rom_acf = Mif(path+'/NN_CORE/MIF/', 'rom_acf', np_num,4,4)                           #激活函数
    
    ram_w = Mif(path+'/NN_CORE/MIF/', 'ram_w',dw_depth,cell_n*(f_bit+e_bit+1),(f_bit+e_bit+1))
    ram_a = Mif(path+'/NN_CORE/MIF/', 'ram_a',da_depth,cell_n*(f_bit+e_bit+1),(f_bit+e_bit+1))        #隐层神经元数+输出层神经元数+2

    with open('./sctest.info', 'wb') as f:
        sctest = {}
        sctest['dst_addr'] = dst_base
        sctest['out_nn'] = on_n
        sctest['float_format'] = float_format
        pickle.dump(sctest,f)
        print('串口测试信息写入！')

    ram_w.load_data(dw)
    ram_w.write_dtb_file([f_bit,e_bit],1)
    
    ram_a.load_data(da)
    ram_a.write_dtb_file([f_bit,e_bit],1)

    rom_baa.load_data(np_baa)
    rom_baa.write_file()

    rom_baw.load_data(np_baw)
    rom_baw.write_file()

    rom_lnl.load_data(np_lnl)
    rom_lnl.write_file()

    rom_bad.load_data(np_bad)
    rom_bad.write_file()

    rom_ofs.load_data(np_ofs)
    rom_ofs.write_file()

    rom_acf.load_data(np_acf)
    rom_acf.write_file()

    del(rom_baa)
    del(rom_baw)
    del(rom_lnl)
    del(rom_bad)
    del(rom_ofs)
    del(rom_acf)
    
    del(ram_w)
    del(ram_a)

    depth_info = [np_num, da_depth, dw_depth, l_depth, in_n, on_n, ofs_width, iw, ow]
    extern_gen(path,cell_n,float_format,depth_info)

if __name__ == '__main__':
    nn_mif_gen('./',10,[23,8],'../nntrain/bp.ninfo')
