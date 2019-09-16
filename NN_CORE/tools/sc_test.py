#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: K_liu
'STM32 操作函数模块'

import serial,math,re,time,pickle
import sys
sys.path.append("../nntrain")
import number_recog as nr
import numpy as np
from matplotlib import pyplot as plt
import ctypes

def send_frame(s,d,base_addr):
    sof = [0x55,0xab,0xaa]          #start of frame
    fl = [len(d)-1]                 #length of frame
    frame = sof + [base_addr] + fl + d  #combine frame
    s.write(frame)

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

def softmax(X):
    exps = np.exp(X)
    return exps/np.sum(exps)

def serial_test(com,noise=0.0,mode=0,epoch_n=0,read_bas=None,datal=None):
    if read_bas == None or datal == None:
        with open('./sctest.info', 'rb') as fp:
            sc_info = pickle.load(fp)
            read_base = int(sc_info['dst_addr'])
            datalen = int(sc_info['out_nn'])
    else:
        read_base = read_bas
        datalen = datal

    with open('./sctest.info', 'rb') as fp:
        sc_info = pickle.load(fp)
        f_bit, e_bit = sc_info['float_format']

    ser = serial.Serial(com, 115200, timeout=1.0)
    ds = nr.Number_Data('../nntrain/number_source.txt')
    ds.generate_train_set(noise, 20)
    #原始数据模式
    if mode == 0:
        for i in range(0, epoch_n):
            da = array2uc(ds.train_x[:, i])
            show_set = ds.train_x[:, i].reshape([8, 9])
            sda = ser.read_all()
            send_frame(ser, da, read_base)
            sda = ser.read(4*datalen).hex()
            str = re.sub(r"(?<=\w)(?=(?:\w\w)+$)", " ", sda)
            fo = []
            for j in range(0,datalen):
                dc = sda[j*8:j*8+8]
                fo.append(cf_dll.s2f(ctypes.c_char_p(bytes(dc,'utf-8')),f_bit,e_bit))
                print('%3.2f'%fo[-1],end=' ')
            mindex  =fo.index(max(fo))
            fo = softmax(np.array(fo)).reshape(1,datalen)
            #print('\n',fo)
            print('\n序号:%d，最大值:%.3f'%(mindex,fo[0,mindex]))

            plt.subplot(1, epoch_n, i + 1), plt.imshow(show_set, 'gray')
            plt.xticks([])
            plt.yticks([])
            plt.xlabel(format(' %d : %.2f'%(mindex,fo[0,mindex])))
            plt.pause(0.01)
        ser.close()
        plt.show()
    #接收纯数据
    elif mode == 1:
        for i in range(0, epoch_n):
            da = array2uc(ds.train_x[:, i])
            show_set = ds.train_x[:, i].reshape([8, 9])
            sda = ser.read_all()
            send_frame(ser, da, read_base)
            sda = ser.read(4 * datalen).hex()
            str = re.sub(r"(?<=\w)(?=(?:\w\w)+$)", " ", sda)

            plt.subplot(1, epoch_n, i + 1), plt.imshow(show_set, 'gray')
            plt.xticks([])
            plt.yticks([])
            plt.pause(0.01)
        ser.close()
        plt.show()
    #图显模式
    else:
        epoch_t = 4
        sn = math.ceil(datalen / 8)
        for i in range(0, epoch_n):
            da = ds.train_x[:, i]
            show_set = da.reshape([8, 9])
            str = ser.read_all()
            #da[0:23] = 0
            da = array2uc(da)
            send_frame(ser, da, read_base)
            plt.subplot(epoch_t, epoch_n, i + 1), plt.imshow(show_set, 'gray')
            # 第J次迭代
            for j in range(1, epoch_t):
                str = (re.sub(r"(?<=\w)(?=(?:\w\w)+$)", " ", ser.read(sn).hex())).split(' ')
                a = []
                print(str)
                if len(str) >= sn:
                    for d in range(0, sn):
                        a.append(int(str[d], 16))
                    a.reverse()
                    send_frame(ser, a, read_base)
                else:
                    a = [0xfe for i in range(0,sn)]
                    send_frame(ser,da, read_base)

                show_set = uc2array(a).reshape([8, 9])
                plt.subplot(epoch_t, epoch_n, i + j * epoch_n + 1), plt.imshow(show_set, 'gray')
                plt.pause(0.001)
        ser.close()
        plt.show()

def show_s2h(dc):
    hex_c = re.sub(r"(?<=\w)(?=(?:\w\w)+$)", " ", dc).split(' ')
    hex_h = []
    for i in hex_c:
        hex_h.append(int(i, 16))
    show_set = uc2array(hex_h).reshape(8, 9)
    plt.subplot(111), plt.imshow(show_set, 'gray')
    plt.show()

if __name__ == '__main__':
    cf_dll = ctypes.windll.LoadLibrary('../bin/f2cf_dll.dll')
    cf_dll.s2f.restype = ctypes.c_float
    noise = 0.10
    img_n = 5
    mode = 2            #0：接收浮点数据 2：接收二值图像
    serial_test('COM17',noise,mode,img_n)


