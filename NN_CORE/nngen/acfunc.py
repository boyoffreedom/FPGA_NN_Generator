import numpy as np
import ctypes,math,pickle,sys
sys.path.append('../nntrain/')
sys.path.append('../nntools/')

cf_dll = ctypes.windll.LoadLibrary('./bin/f2cf_dll.dll')

def h2f(s):                         #hex to float
    cp = ctypes.pointer(ctypes.c_long(s))
    fp = ctypes.cast(cp, ctypes.POINTER(ctypes.c_float))
    return fp.contents.value

def cf2sf(cf_in, f_bit, e_bit):         #configurable float to stander float
    d = cf_dll.cf2f(ctypes.c_long(cf_in), f_bit, e_bit)
    cp = ctypes.pointer(ctypes.c_long(d))
    fp = ctypes.cast(cp, ctypes.POINTER(ctypes.c_float))
    return fp.contents.value

def func_type(f_type, x):               #define of active function type
    if (f_type == 'sigmoid'):
        y = (1 / (np.exp(-x) + 1))
    elif (f_type == 'tanh'):
        y = np.tanh(x)
    else:
        return x.copy
    return y

def piecewise_linear(f_type, seg_n):        #piecewise linear
    t = np.linspace(-10, 10, 2000)
    sig = func_type(f_type, t)
    x_fd = np.zeros(seg_n)
    x_fd[0] = t[0]
    dx = (sig[1] - sig[0]) / (t[1] - t[0])
    s_k = dx
    dx_max = dx
    dx_min = dx
    x0 = t[-1]
    y0 = sig[-1]
    for i in range(0, len(t) - 1):
        dx = (sig[i] - y0) / (t[i] - x0)
        if (dx > dx_max):
            dx_max = dx
        elif (dx < dx_min):
            dx_min = dx
        y0 = sig[i]
        x0 = t[i]
    dx_rand = (dx_max - dx_min) * 2

    # 正向搜索
    x0 = t[0]
    y0 = sig[0]
    j = 0
    for i in range(1, len(t)):
        dx = (sig[i] - y0) / (t[i] - x0)
        if (abs(dx - s_k) > (dx_rand / seg_n)):
            j = j + 1
            x_fd[j] = x0
            s_k = dx
        y0 = sig[i]
        x0 = t[i]
    x_fd[-1] = t[-1]
    # 查找分段点反向搜索
    j = 2
    x0 = t[-1]
    y0 = sig[-1]
    for i in range(len(t) - 2, 0, -1):
        dx = (sig[i] - y0) / (t[i] - x0)
        if (abs(dx - s_k) > (dx_rand / seg_n)):
            x_fd[seg_n - j] = (x_fd[seg_n - j] + x0) / 2
            s_k = dx
            j = j + 1
        y0 = sig[i]
        x0 = t[i]
    y_fd = func_type(f_type, x_fd)
    a = np.zeros(seg_n)
    b = np.zeros(seg_n)
    x_s = x_fd[0]
    y_s = y_fd[0]
    for i in range(0, seg_n - 1):
        a[i] = (y_s - y_fd[i + 1]) / (x_s - x_fd[i + 1])
        b[i] = -a[i] * x_s + y_s
        y_s = y_fd[i + 1]
        x_s = x_fd[i + 1]
    a[seg_n - 1] = round(a[seg_n - 2])
    b[seg_n - 1] = round(b[seg_n - 2])
    a = np.append(round(a[0]), a)
    b = np.append(round(b[0]), b)
    return [x_fd, y_fd, a, b]

def float2hex(fin, f_bit, e_bit):               #configurable float to hex
    dwidth = (f_bit + e_bit + 1)
    d_type = '%0' + str(math.ceil(dwidth / 4)) + 'X'
    return format(d_type % (((cf_dll.f2cf(ctypes.c_float(fin), f_bit, e_bit)) & 0xffffffff) % (2 ** dwidth)))

#生成分段线性后的函数
def pieces_linear_gen(path,func_type, float_format, seg_n):
    f_bit = float_format[0]
    e_bit = float_format[1]
    [x_fd, y_fd, a, b] = piecewise_linear(func_type, seg_n)
    cin_bit_n = (seg_n - 1)
    cout_bit_n = math.log(seg_n, 2)
    if cout_bit_n - math.floor(cout_bit_n) == 0:
        cout_bit_n = math.ceil(cout_bit_n)
    else:
        cout_bit_n = (math.ceil(cout_bit_n) - 1)

    with open(path+'/NN_CORE/A_'+func_type + '.v', 'w+') as f:
        f.write('`include "extern.v"\n\n')
        f.write('module sigmoid(clk,rst_n,f_in,coder_in,coder_out,x_out,a_out,b_out);\n\n')
        f.write('input clk,rst_n;\ninput[`D_LEN-1:0] f_in;\noutput[`D_LEN-1:0] x_out,a_out,b_out;\n\n')
        f.write('output[%d:0] coder_in;\noutput [%d:0] coder_out;\n\n' % (cin_bit_n, cout_bit_n))
        f.write('wire [%d:0] coder_in;\n' % cin_bit_n)
        f.write('wire [%d:0] coder_out;\n' % cout_bit_n)
        f.write('wire[`D_LEN-1:0] comp_f[%d:0];\n' % cin_bit_n)
        f.write('reg[`D_LEN-1:0] x_out;\n')
        f.write('wire[`E_bit - 1:0] f_e = f_in[`F_bit + `E_bit - 1:`F_bit];\n\n')
        f.write('//正负无穷特殊处理\n')
        f.write('always @(posedge clk)begin\n')
        f.write('\tif(clk == 1)begin\n')
        f.write('\t\tif(f_e == {(`E_bit){1\'b1}})begin\n')
        f.write('\t\t\tx_out <= 0;\n\t\tend\n')
        f.write('\t\telse begin\n\t\t\tx_out <= f_in;\n')
        f.write('\t\tend\n\tend\nend\n')
        for i in range(0, seg_n):
            f.write('assign comp_f[%d] = %d\'h' % (i, f_bit + e_bit + 1))
            f.write(float2hex(x_fd[i], f_bit, e_bit))
            f.write(';\n')
        f.write('\n')
        for i in range(0, seg_n):
            f.write('greater_than u%d(clk,rst_n,f_in,comp_f[%2d],coder_in[%2d]);\n' % (i, i, i))
        f.write('encoder u%d (coder_in,coder_out);\n' % (i + 1))
        f.write('sigmoid_lut u%d (coder_out,a_out,b_out);\n' % (i + 2))
        f.write('\n\nendmodule\n')

    with open(path+'/NN_CORE/A_encoder.v', 'w+') as f:
        f.write('`include "extern.v"\n')
        f.write('module encoder(d_in,d_out);\n\n')
        f.write('input[%d:0] d_in;\noutput[%d:0] d_out;\nreg[%d:0]d_out;\n\n' % (cin_bit_n, cout_bit_n, cout_bit_n))
        f.write('always @(*) begin\n\tcase(d_in)\n')
        for i in range(0, seg_n + 1):
            f.write('\t\t%d\'b' % seg_n)
            for j in range(i, seg_n):
                f.write('0')
            for j in range(0, i):
                f.write('1')
            f.write(': d_out <= %d\'d%d;\n' % (cout_bit_n + 1, i))
        f.write('\t\tdefault:d_out <= %d\'d0;\n' % (cout_bit_n + 1))
        f.write('\tendcase\nend\nendmodule\n')

    with open(path+'/NN_CORE/A_'+func_type + '_lut.v', 'w+') as f:
        f.write('`include "extern.v"\n\n')
        f.write('module %s_lut(coder_out,a_out,b_out);\n\n' % (func_type))
        f.write('input [%d:0] coder_out;\n' % (cout_bit_n))
        f.write('output [`D_LEN-1:0] a_out,b_out;\n\nreg [`D_LEN-1:0] a_out,b_out;\n\n')
        f.write('always @(*)begin\n\tcase(coder_out)\n')
        for i in range(0, seg_n + 1):
            f.write('\t\t%2d:begin a_out = %d\'h' % (i, (f_bit + e_bit + 1)))
            f.write(float2hex(a[i], f_bit, e_bit))
            f.write('; b_out = %d\'h' % (f_bit + e_bit + 1))
            f.write(float2hex(b[i], f_bit, e_bit))
            f.write('; end\n')
        f.write('\t\tdefault:begin a_out = %d\'h' % (f_bit + e_bit + 1))
        f.write(float2hex(0, f_bit, e_bit))
        f.write('; b_out = %d\'h' % (f_bit + e_bit + 1))
        f.write(float2hex(0, f_bit, e_bit))
        f.write('; end\n')
        f.write('\tendcase\nend\n\nendmodule\n')
#ACTIVE FUNCTION
def active_func_v(path,acfunc_list):                 #生成active_func顶层文件
    with open('./source/NN_CORE/A_ACTIVE_FUNC.v','w') as f:
        f.write('`include \"extern.v\"\n\nmodule ACTIVE_FUNC(clk,rst_n,func_type,\n\t\t\tfloat_in,acfunc_out);\n')
        f.write('input clk,rst_n;\ninput [`D_LEN-1:0] float_in;\ninput[3:0] func_type;\noutput [`D_LEN-1:0] acfunc_out;\n\n')
        for al in acfunc_list:
            f.write('wire [`D_LEN-1:0] relu_out,pl_out,si_out;\n')
        f.write()
        f.write()
        f.write()
        f.write()
        f.write()



def acfunc_gen(path,modul,float_format):
    with open(path+'/NN_CORE/A_relu.v', 'wb') as f:
        f.write(modul['A_relu'])
    with open(path+'/NN_CORE/A_sign.v', 'wb') as f:
        f.write(modul['A_sign'])

    with open(path+'/NN_CORE/A_greater_than.v', 'wb') as f:
        f.write(modul['A_greater_than'])
    with open(path+'/NN_CORE/A_float_mac.v', 'wb') as f:
        f.write(modul['A_float_mac'])
    with open(path+'/NN_CORE/A_ACTIVE_FUNC.v', 'wb') as f:
        f.write(modul['A_ACTIVE_FUNC'])

    #pieces_linear_gen(path,'sigmoid', float_format, 16)

if __name__ == '__main__':
    func_list = ['relu','sigmoid','sign','linear']
    with open('./bin/nn_core.srcpack', 'rb') as pkl_file:
        nn_source = pickle.load(pkl_file)
    acfunc_gen('./source/',n_source,[23,8])