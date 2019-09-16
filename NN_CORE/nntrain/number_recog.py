import numpy as np
import cv2
from matplotlib import pyplot as plt

class Number_Data:
    def __init__(self,src_fname):             #构建标准库
        fp = open(src_fname,'r')
        array_info = fp.readline().split(' ')
        self.P = int(array_info[0])
        self.Q = int(array_info[1])
        self.N = int(array_info[2])
        self.PxQ = self.P*self.Q
        self.stander_set_x = np.zeros([self.PxQ,self.N])
        self.stander_set_y = np.zeros([self.N,self.N])
        print('数据集信息 P:',self.P,'Q:',self.Q,'N:',self.N)
        for i in range(0,self.N):
            l = fp.readline().split(':')
            x_ = l[0].split(' ')
            y_ = l[1]
            for j in range(0,self.PxQ):
                self.stander_set_x[j,i] = int(x_[j])
            self.stander_set_y[i,int(y_)] = 1
        fp.close()
        self.train_x = np.copy(self.stander_set_x)
        self.train_y = np.copy(self.stander_set_y)

    def add_noise(self,index,percetage):
        G_Noise = np.copy(self.stander_set_x[:,index]).reshape(72,1)
        G_NoiseNum = int(percetage * 72)
        for i in range(G_NoiseNum):
            g_index = np.random.randint(0, 71)
            G_Noise[g_index][0] = 1 - G_Noise[g_index][0]
        return G_Noise

    def generate_train_set(self,noise_percent,size=80):
        self.train_x = np.zeros([72, size])
        self.train_y = np.zeros([10, size])
        for i in range(size):
            _index = np.random.randint(0,10)
            _x = self.add_noise(_index,noise_percent).reshape(72)
            _y = np.zeros([10])
            _y[_index] = 1.

            self.train_x[:,i] = np.copy(_x)
            self.train_y[:,i] = np.copy(_y)

    def generate_test_set(self,noise_percent,size=20):
        self.test_x = np.zeros([72, size])
        self.test_y = np.zeros([10, size])
        for i in range(size):
            _index = np.random.randint(0, 10)
            _x = self.add_noise(_index, noise_percent).reshape(72)
            _y = np.zeros([10])
            _y[_index] = 1.

            self.test_x[:,i] = np.copy(_x)
            self.test_y[:,i] = np.copy(_y)

if __name__ == '__main__':
    s = Number_Data('./number_source.txt')

    s.generate_test_set(0.02,200)
    print('test for image')

    for i in range(s.N):
        show_set = s.stander_set_x[:, i].reshape([8, 9])
        plt.subplot(1,s.N,i+1),plt.imshow(show_set,'gray')

        plt.xticks([])
        plt.yticks([])
        plt.axis('off')
    plt.show()

