import number_recog as nr
import numpy as np
import pickle,cv2
from scipy import linalg
from matplotlib import pyplot as plt

class Hopfield:
    def __init__(self,t=None):
        self.t = t
        self.w = None
        self.b = None

    def load_data(self,t):
        self.t = t

    def train(self):
        if self.t.any() == None:
            return 1
        [S,Q] = self.t.shape
        Y = self.t[:, 0:Q-1] - np.dot(self.t[:,Q-1].reshape(S,1),np.ones((1,Q-1)))
        [U,SS,V] = np.linalg.svd(Y) #对线性子空间进行奇异值分解
        K = SS.shape[0]
        TP = np.zeros((S,S))
        for k in range(0,K):
            u = U[:,k].reshape(S,1)
            TP = TP + np.dot(u,u.T)

        TM = np.zeros((S,S))
        for k in range(K,S):
            u = U[:,k].reshape(S,1)
            TM = TM + np.dot(u,u.T)

        tau = 10            #权值调整参数
        Ttau = TP - tau*TM
        Itau = self.t[:,Q-1].reshape(S,1) - np.dot(Ttau,self.t[:,Q-1].reshape(S,1))
        w = Ttau
        b = Itau

        h = 0.15
        C1 = np.exp(h)-1
        C2 = -(np.exp(-tau*h)-1)/tau

        w = linalg.expm(h*Ttau)

        A0 = C1 * np.eye(K)
        A1 = np.zeros((K,S-K))
        A2 = np.zeros((S-K,K))
        A3 = C2*np.eye(S-K)

        h0 = np.hstack([A0,A1])
        h1 = np.hstack([A2,A3])
        b0 = np.vstack([h0,h1])

        b = np.dot(U, b0)
        b = np.dot(b,U.T)
        b = np.dot(b,Itau)

        self.w = w
        self.b = b

    def infer_epoch(self,din):
        Q = din.shape[0]
        do = din.reshape(Q,1)
        for i in range(0, Q):
            a = np.dot(self.w[:,i].T, do) + self.b[i, 0]
            if (a > 0.5):
                a = 1
            else:
                a = 0
            do[i,0] = a
        return do

    def infer(self,din):
        do = np.dot(self.w.T, din) + self.b
        do[do >= 0.5] = 1  # 阶跃激活函数
        do[do < 0.5] = 0
        return do

    def inferrence(self,din):
        Q = din.shape[0]
        di = din.reshape(Q,1)
        do = di
        i = 0
        while di.all() != do.all() or i < 1:
            di = do
            do = self.infer(di.reshape(Q,1))
            i += 1
        do[do < 0] = 0
        return do

    def output_nn(self,file_name):
        if self.w.any() == None or self.b.any() == None:
            print('参数错误!')
            return 1
        #self.w = np.eye(72)
        #self.b = np.zeros([72,1])
        nn_num = self.w.shape[0]
        p_data = {'scale':[nn_num,nn_num]}
        self.wlist = []
        for i in range(0,nn_num):                            #写各网络的权值阈值
            wl = []
            for j in range(0,nn_num):
                wl.append(self.w[j,i])
            wl.append(self.b[i,0])
            self.wlist.append(wl)
        p_data['l1_info'] = {'wlist':self.wlist,'active_function':'sign'}           #记录权值阈值
        with open(file_name,'wb+') as f:               #将数据写入文件
            pickle.dump(p_data,f)
            print("HOPFIELD网络参数泡菜装坛完成！")

if __name__ == '__main__':
    d = nr.Number_Data()
    t = d.stander_set_x
    d.generate_test_set(0.00,20)
    h = Hopfield(t)
    h.train()
    h.output_nn('hop.ninfo')
    for i in range(5):
        noise_data = d.test_x[:, i].reshape(72,1)

        noise_data[0:20] = 0
        show_set = noise_data.reshape([8, 9])
        #tmp_image = cv2.resize(show_set, (show_set.shape[1] * 20, show_set.shape[0] * 20), cv2.INTER_NEAREST)
        plt.subplot(3, 5, i+1), plt.imshow(show_set, 'gray')
        plt.xticks([])
        plt.yticks([])
        plt.axis('off')

        ep = h.inferrence(noise_data)
        show_set = ep.reshape([8, 9])
        #tmp_image = cv2.resize(show_set, (show_set.shape[1] * 20, show_set.shape[0] * 20), cv2.INTER_NEAREST)
        plt.subplot(3, 5, i + 6), plt.imshow(show_set, 'gray')
        plt.xticks([])
        plt.yticks([])
        plt.axis('off')

        ep = h.inferrence(ep)
        show_set = ep.reshape([8, 9])
        #tmp_image = cv2.resize(show_set, (show_set.shape[1] * 20, show_set.shape[0] * 20), cv2.INTER_NEAREST)
        plt.subplot(3, 5, i + 11), plt.imshow(show_set, 'gray')
        plt.xticks([])
        plt.yticks([])
        plt.axis('off')
    plt.show()
