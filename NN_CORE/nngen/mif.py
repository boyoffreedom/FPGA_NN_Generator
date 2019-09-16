import ctypes
import math

cf_dll = ctypes.windll.LoadLibrary('./bin/f2cf_dll.dll')

def h2f(s):
    cp = ctypes.pointer(ctypes.c_long(s))
    fp = ctypes.cast(cp, ctypes.POINTER(ctypes.c_float))
    return fp.contents.value

def cf2sf(cf_in,f_bit,e_bit):
    d = cf_dll.cf2f(ctypes.c_long(cf_in),f_bit,e_bit)
    cp = ctypes.pointer(ctypes.c_long(d))
    fp = ctypes.cast(cp, ctypes.POINTER(ctypes.c_float))
    return fp.contents.value

def intTo2Str(X,K):
    """ intTo2Str( X , K )
        将整数 X 转化为 K位2进制字符串
    """
    try:
        X = int(X)
    except:
        X = 0
    try:
        K = int( K)
    except:
        K = 0
    
    if K<1 :
        K = 1 
    if X<0 :
        FH = 1
        X = -X
    else:
       FH = 0
    
    A =[ 0 for J in range( 0, K ) ]
    J = K-1
    while ((J >= 0) and ( X > 0)):
          Y = X % 2
          X = X / 2
          A[J] = Y
          J = J - 1
    if FH==1:
       # 求反
       for J in xrange(0, K):
           if (A[J] == 1):
              A[J] = 0
           else:
              A[J] = 1
       # 末位加1
       J = K - 1
       while (J >= 0):
             A[J] = A[J] +1
             if (A[J] <= 1):
                break
             A[J] = 0
             J = J -1
    return "".join([ chr(int(J)+48) for J in A ])

#mif文件生成器
class Mif(object):
    def __init__(self,path,fname,depth,width,dwidth):           #初始化输入文件名，内存长度，内存位宽
        self.path = path
        self.fname = fname
        self.depth = int(depth)&0xffffffff
        self.width = int(width)&0xffffffff
        self.dwidth = int(dwidth)&0xffffffff
        self.byte_n = math.ceil(int(dwidth)/4)&0xffffffff
        self.bit_n = int(dwidth)&0xffffffff
        if(width%dwidth != 0):
            print("数据位宽错误！目标位宽无法整除单元位宽！")
            self.__del__()
    def load_data(self,data):                       #装载数据
        self.data = data
    def write_file(self,float_format=None,hob=0):    #写文件
        #计算前置参数
        fp = open(str(self.path+self.fname+'.mif'), "w+")
        if float_format!= None:
            f_bit,e_bit = float_format
            if(f_bit+e_bit+1 != self.dwidth):
                print("数据位宽错误！定制浮点格式与数据位宽不符！")
                return 0
            else:
                dtype = 'float'
        else:
            dtype = 'int'

        d_type = '%0'+str(self.byte_n)+'X'     #输出数据格式
        fp.write("DEPTH = %d;\n"%(self.depth)) #数据个数
        fp.write("WIDTH = %d;\n"%(self.width)) #RAM数据位宽
        fp.write("ADDRESS_RADIX=UNS;\n")      #地址线进制
        if(hob == 1):
            fp.write("DATA_RADIX=HEX;\n")         #数据线进制
        else:
            fp.write("DATA_RADIX=BIN;\n")         #数据线进制
        fp.write("CONTENT ")
        fp.write("BEGIN\n")
        s_i = int(self.width/self.dwidth)
        for i in range(0,self.depth):
            fp.write("%d\t:\t"%i)
            for j in range(int(self.width/self.dwidth)-1,-1,-1):              #同一行并置数据
                if(s_i*i+j < len(self.data)):
                    if(dtype == 'float'):
                        if(hob == 1):
                            fp.write(d_type%(((cf_dll.f2cf(ctypes.c_float(self.data[s_i*i+j]),f_bit,e_bit))&0xffffffff)%(2**self.dwidth)))
                        else:
                            fp.write(intTo2Str((cf_dll.f2cf(ctypes.c_float(self.data[s_i*i+j]),f_bit,e_bit))&0xffffffff,self.bit_n))
                    else:
                        if(hob == 1):
                            fp.write(d_type%(int(self.data[s_i*i+j])&0xffffffff))
                        else:
                            fp.write(intTo2Str(self.data[s_i*i+j],self.bit_n))
                else:
                    if(dtype == 'float'):
                        if(hob == 1):
                            fp.write(d_type%0)
                        else:
                            fp.write(intTo2Str(0, self.bit_n))
                    else:
                        if(hop == 1):
                            fp.write(d_type % 0)
                        else:
                            fp.write(intTo2Str(((2**self.dwidth)-1)&0xffffffff,self.bit_n))
            fp.write(";\n")
        fp.write("END;\n")
        fp.close()
        print("内存初始化文件%s数据写入成功！"%self.fname)

    def write_dtb_file(self, float_format=None, hob=0):  # 写分布式存储mif
        dtbn = int(self.width/self.dwidth)
        if float_format != None:
            f_bit,e_bit = float_format
            if (f_bit+e_bit + 1 != self.dwidth):
                print("数据位宽错误！定制浮点格式与数据位宽不符！")
                return 0
            else:
                dtype = 'float'
        else:
            dtype = 'int'
        for j in range(0,dtbn):
            with open(format(self.path+self.fname+'%d.mif'%j), "w+") as fp:
                d_type = '%0' + str(self.byte_n) + 'X'  # 输出数据格式
                fp.write("DEPTH = %d;\n" % (self.depth))  # 数据个数
                fp.write("WIDTH = %d;\n" % (self.dwidth))  # RAM数据位宽
                fp.write("ADDRESS_RADIX=UNS;\n")  # 地址线进制
                if (hob == 1):
                    fp.write("DATA_RADIX=HEX;\n")  # 数据线进制
                else:
                    fp.write("DATA_RADIX=BIN;\n")  # 数据线进制
                fp.write("CONTENT ")
                fp.write("BEGIN\n")
                s_i = int(self.width / self.dwidth)
                for i in range(0, self.depth):
                    fp.write("%d\t:\t" % i)
                    if (s_i * i + j < len(self.data)):
                        if (dtype == 'float'):
                            if (hob == 1):
                                fp.write(d_type % (((cf_dll.f2cf(ctypes.c_float(self.data[s_i * i + j]),f_bit, e_bit)) & 0xffffffff) % (2 ** self.dwidth)))
                            else:
                                fp.write(intTo2Str((cf_dll.f2cf(ctypes.c_float(self.data[s_i * i + j]), f_bit,e_bit)) & 0xffffffff, self.bit_n))
                        else:
                            if (hob == 1):
                                fp.write(d_type % (int(self.data[s_i * i + j]) & 0xffffffff))
                            else:
                                fp.write(intTo2Str(self.data[s_i * i + j], self.bit_n))
                    else:
                        if (dtype == 'float'):
                            if (hob == 1):
                                fp.write(d_type % 0)
                            else:
                                fp.write(intTo2Str(0, self.bit_n))
                        else:
                            if (hop == 1):
                                fp.write(d_type % 0)
                            else:
                                fp.write(intTo2Str(((2 ** self.dwidth) - 1) & 0xffffffff, self.bit_n))
                    fp.write(";\n")
                fp.write("END;\n")
        print("内存初始化文件%s数据写入成功！" % self.fname)
if __name__ == '__main__':
    pass