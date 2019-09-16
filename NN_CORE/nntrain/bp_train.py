import numpy as np
import pickle
from number_recog import *


class Layer(object):
    def __init__(self,input_nodes,output_nodes,active_function = 'relu'):        #生成一层BP神经网络
        self.in_n = input_nodes
        self.out_n = output_nodes
        self.wlist = []
        self.w = np.random.normal(0,1,(input_nodes,output_nodes))
        self.b = 0.01*np.ones((output_nodes,1))
        self.active_function = active_function

    def acfunc(self,Z):
        if(self.active_function == 'sigmoid'):      #激活函数为sigmoid
            return (1/(1 + np.exp(-Z)))
        elif(self.active_function == 'relu'):       #激活函数为relu
            return np.maximum(Z,0)
        else:                                       #否则当线性处理
            return Z
    
    def forward(self, x):                            #计算前向传播 Z=W*X+B
        self.Z = np.dot(self.w.T, x)+self.b
        self.A = self.acfunc(self.Z)
    
    def backward(self,inputs_list,dZ,learning_rate):    #计算反向传播
        m = inputs_list.shape[1]                        #样本个数
        dw = np.dot(dZ,inputs_list.T)/m                 #计算dw
        db = np.sum(dZ,axis=1,keepdims=True)/m          #计算db
        self.w -= learning_rate * dw.T                    #更新权值
        self.b -= learning_rate*db

    def acfunc_prime(self,Z):                           #定义激活函数导数
        if(self.active_function == 'relu'):             #relu导数
            data = Z.copy()
            data[data>0] = 1
            data[data<0] = 0
            return data 
        elif(self.active_function == 'sigmoid'):        #sigmoid导数
            return self.acfunc(Z)
        else:
            return 1

    def gen_wlist(self):                              #以列表的方式输出权值与阈值
        self.wlist = []
        for i in range (0,self.out_n):
            wl = []
            for j in range(0,self.in_n):
                wl.append(self.w[j,i])
            wl.append(self.b[i,0])
            self.wlist.append(wl)
        return self.wlist

def output_nn(file_name,layers):
    p_data = {'scale':[]}
    for la in layers:
        la.gen_wlist()
    if isinstance(layers[0],Layer):
        scale = [layers[0].in_n]
    else:
        print("参数传递错误!")
        return 0
    l = 1
    for la in layers:                            #写各网络的权值阈值
        if isinstance(la,Layer):
            p_data[str('l%d_info'%l)] = {'wlist':la.wlist,'active_function':la.active_function}           #记录权值阈值
            l += 1
            if la.in_n != scale[-1]:           #查看传输各层是否可以相互衔接
                print("层间节点不对应!")
                return 0
            else:
                scale += [la.out_n]             #记录当前网络层的输出节点，用于与下一层对比
        else:
            print("参数传递错误!")
            return 0
    p_data['scale'] = scale
    with open(file_name,'wb+') as f:               #将数据写入文件
        pickle.dump(p_data,f)
        print("泡菜装坛完成！")

def train(x_,y_,layers,alpha):
    layers[0].forward(x_)  # l1前向传播
    layers[1].forward(layers[0].A)  # l2前向传播

    dZ2 = layers[1].A - y_  # 计算dZ2
    layers[1].backward(layers[0].A, dZ2, alpha)  # l2反向传播
    dZ1 = np.multiply(np.dot(layers[1].w, dZ2), layers[0].acfunc_prime(layers[0].Z))  # 计算dZ1
    layers[0].backward(x_, dZ1, 0.05)  # l1反向传播

def lose(x_,y_,layers):
    layers[0].forward(x_)  # l1前向传播
    layers[1].forward(layers[0].A)  # l2前向传播

    dZ2 = layers[1].A - y_  # 计算dZ2
    return np.sum(abs(dZ2))/dZ2.shape[1]

def predict(x_,layers):
    layers[0].forward(x_)  # l1前向传播
    layers[1].forward(layers[0].A)  # l2前向传播
    prd = layers[1].A
    return prd

if __name__ == '__main__':
    # 生成训练样本
    ds = Number_Data('./number_source.txt')
    ds.generate_train_set(0.10, 800)
    ds.generate_test_set(0.10, 200)
    x_train = ds.train_x
    y_train = ds.train_y

    x_test = ds.test_x
    y_test = ds.test_y

    # 定义神经网络结构
    l1 = Layer(72, 36, 'relu')
    l2 = Layer(36, 10, 'sigmoid')
    layers = [l1,l2]

    # 训练神经网络
    for i in range(5001):
        train(x_train, y_train,layers, 0.05)
        if (i % 1000 == 0):
            print("train_error ", lose(x_train, y_train,layers))  # 定期输出误差

    print("test_set error ", lose(x_test, y_test,layers))  # 定期输出误差

    output_nn('bp.ninfo', [l1, l2])
    # loss = -np.dot(np.log(A2),y.T) + np.dot(np.log(1-A2),(1-y).T)；0