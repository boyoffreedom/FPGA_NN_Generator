import number_recog as nr
import numpy as np
import pickle
from matplotlib import pyplot as plt

def array2uc(ar):
    a = []
    d = 0
    i = 0
    for l in range(ar.shape[0]):
        if(ar[l] == 1):
            d = (d << 1) | 1
        else:
            d = (d << 1) | 0
        i += 1
        if(i >= 8):
            a.append(d)
            i = 0
            d = 0
    if d != 0:                  #无法被8整除
        a.append(d)
    for i in a:
        print("%02X"%i,end = ' ')
    print("\n")
    return a

def uc2array(ar):
    a = np.zeros([len(ar)*8])
    j = 0
    for l in ar:
        for i in range(0,8):
            if (l & (1<<(7-i))) != 0:
                a[j] = 1
            else:
                a[j] = 0
            j += 1
    return a

def relu(Z):
    data = Z.copy()
    data = np.max(data, 0)
    return data

def bp_struct_test(fname,ucd):                #不定参数,该网络各层的神经元数
    with open(fname, 'rb') as pkl_file:
        nn_data = pickle.load(pkl_file)
    w1 = nn_data['l1_info']['wlist']
    w2 = nn_data['l2_info']['wlist']
    dimg =  uc2array(ucd).reshape(8,9)
    plt.subplot(111), plt.imshow(dimg, 'gray')

    dimg = np.vstack((dimg.reshape(72,1),np.array([1]))).reshape(73,1)
    #print(dimg)
    P = len(dimg)
    a1 = np.ones([len(w1)+1,1])
    a2 = []
    i = 0
    for w in w1:
        a1[i] = relu(np.dot(np.array(w).reshape(1,P),dimg))
        i += 1
    i = 0
    P = len(w1)+1
    a2 = np.ones([len(w2),1])
    for w in w2:
        a2[i] = np.dot(np.array(w).reshape(1,P),a1).astype('float')
        i += 1
    print(a2)
    plt.show()


if __name__ == '__main__':
    img_data = [0x3E,0x01,0x00,0x80,0x80,0x80,0x40,0x20,0x10]
    bp_struct_test('./bp.ninfo',img_data)
