import tkinter as tk
from tkinter.filedialog import askdirectory
from tkinter import messagebox
import time,sys
sys.path.append('./nntrain')
sys.path.append('./tools')
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from bp_train import *
from hopfield_train import *
from number_recog import *
from sc_test import *

matplotlib.use('TkAgg')
cf_dll = ctypes.windll.LoadLibrary('./bin/f2cf_dll.dll')
cf_dll.s2f.restype = ctypes.c_float

def isuint(type_in):
    try:
        r = int(type_in)
        if r <= 0:
            return False
    except ValueError:
        return False
    return r

class PopupTrain():
    def __init__(self,nntype):
        self.Popupwindow=tk.Tk()
        self.Popupwindow.title(nntype+'网络训练窗口')
        self.Popupwindow.resizable(0, 0)
        self.nntype = nntype
        self.database = Number_Data('./nntrain/number_source.txt')
        if(nntype == 'BP'):
            tk.Label(self.Popupwindow, text=('网络类型为:BP 输入神经元数:'+str(self.database.PxQ))).grid(row=0, column=0,sticky=tk.W)
            tk.Label(self.Popupwindow, text=('设置隐含层神经元数:')).grid(row=1,column=0,sticky=tk.W)
            self.hidn = tk.Entry(self.Popupwindow,width=6)
            self.hidn.grid(row=1,column=1,sticky=tk.W)
            tk.Label(self.Popupwindow, text=('输出神经元数:'+str(self.database.N))).grid(row=2, column=0, sticky=tk.W)
            self.btn_train = tk.Button(self.Popupwindow, text='训练', width=8, height=3, command=self.train_callback)
            self.btn_train.grid(row=0, column=9, rowspan=3, sticky=tk.E)
        elif(nntype == 'Hopfield'):
            tk.Label(self.Popupwindow, text=('网络类型为:Hopfield 计算神经元数:' + str(self.database.PxQ))).grid(row=0, column=0, columnspan=6,sticky = tk.W)
            self.btn_train = tk.Button(self.Popupwindow, text='训练', width=8, height=1, command=self.train_callback)
            self.btn_train.grid(row=0, column=9, sticky=tk.E)
        self.txt = tk.Text(self.Popupwindow, width=60, height=15,font=("仿宋", 12, "normal"))
        self.txt.grid(row=3, column=0, rowspan=10, columnspan=10)
        self.btn_finish = tk.Button(self.Popupwindow, text='完成', width=6, height=1, command=self.Popupwindow.destroy)
        self.btn_finish.grid(row=15, column=9,sticky=tk.E)
        self.btn_finish.config(state='disable')
        self.txt.config(state='disable')
    def disp(self,str):
        self.txt.config(state='normal')
        self.txt.insert(tk.END, str)
        self.Popupwindow.update()
        self.txt.config(state='disable')
    def train_callback(self):
        #训练函数
        self.btn_train.config(state='disable')
        self.btn_finish.config(state='disable')
        self.txt.config(state='normal')
        self.txt.delete('1.0', 'end')
        self.txt.config(state='disable')
        if self.nntype=='BP':
            self.bp_train()

        elif self.nntype=='Hopfield':
            self.hopfield_train()

        self.btn_finish.config(state='normal')
        self.btn_train.config(state='normal')

    def loop(self):
        self.btn_finish.config(state='normal')
        self.Popupwindow.mainloop()

    def bp_train(self):
        self.database.generate_train_set(0.10, 800)
        self.database.generate_test_set(0.10, 200)
        x_train = self.database.train_x
        y_train = self.database.train_y

        x_test = self.database.test_x
        y_test = self.database.test_y

        # 定义神经网络结构

        hidnn = isuint(self.hidn.get())
        if hidnn <= 0 or hidnn == False:
            self.disp('Error:输入隐含层为非正整数！\n')
            return -1
        l1 = Layer(self.database.PxQ, hidnn, 'relu')
        l2 = Layer(hidnn, self.database.N, 'sigmoid')
        layers = [l1,l2]
        for i in range(5001):
            train(x_train, y_train,layers, 0.05)
            if (i % 500 == 0):
                self.disp("epoch "+str(i)+" train_error "+ str(lose(x_train, y_train, layers))+'\n')  # 定期输出误差
        self.disp("test_set error "+ str(lose(x_test, y_test, layers))+'\n')  # 定期输出误差
        output_nn('./nntrain/bp.ninfo', [l1, l2])
        self.disp('BP网络结构文件生成完成！\n')

    def hopfield_train(self):
        self.disp('Hopfield训练中...\n')
        self.database.generate_test_set(0.10, 20)
        h = Hopfield(self.database.stander_set_x)
        h.train()
        self.disp('Hopfield训练完成！\n')
        h.output_nn('./nntrain/hop.ninfo')
        self.disp('Hopfield网络结构文件生成完成！\n')
        for i in range(5):
            noise_data = self.database.test_x[:, i].reshape(72, 1)

            noise_data[0:20] = 0
            show_set = noise_data.reshape([8, 9])
            plt.subplot(3, 5, i + 1), plt.imshow(show_set, 'gray')
            plt.axis('off')

            ep = h.inferrence(noise_data)
            show_set = ep.reshape([8, 9])
            plt.subplot(3, 5, i + 6), plt.imshow(show_set, 'gray')
            plt.axis('off')

            ep = h.inferrence(ep)
            show_set = ep.reshape([8, 9])
            plt.subplot(3, 5, i + 11), plt.imshow(show_set, 'gray')
            plt.axis('off')
            plt.pause(0.01)

class PopupTest():
    def __init__(self,nntype):
        self.Popupwindow=tk.Tk()
        self.Popupwindow.title(nntype+'网络测试窗口')
        self.Popupwindow.resizable(0, 0)
        self.nntype = nntype

        self.database = Number_Data('./nntrain/number_source.txt')
        tk.Label(self.Popupwindow, text=('网络类型为:'+nntype + '请输入测试串口号: COM')).grid(row=0, column=0,sticky=tk.E)
        self.com = tk.Entry(self.Popupwindow,width=2,justify=tk.RIGHT)
        self.com.grid(row=0,column=1,sticky=tk.W)
        tk.Label(self.Popupwindow, text=('添加噪声比例：')).grid(row=0, column=2, sticky=tk.E)
        self.noise = tk.Entry(self.Popupwindow, width=4, justify=tk.RIGHT)
        self.noise.grid(row=0, column=3, sticky=tk.W)
        self.btn_train = tk.Button(self.Popupwindow, text='测试', width=8, height=1, command=self.test_callback)
        self.btn_train.grid(row=0, column=4, sticky=tk.W)

        if nntype == 'BP':
            self.fig = Figure(figsize=(5,2),dpi=150)
        elif nntype == 'Hopfield':
            self.fig = Figure(figsize=(5, 4), dpi=150)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.Popupwindow)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(row=1,rowspan=10,columnspan=10)
        self.label = tk.Label(self.Popupwindow,text='请选择FPGA连接的串口！')
        self.label.grid(row=11,column=0)

    def test_callback(self):
        comn = isuint(self.com.get())
        self.fig.clear()
        if comn <= 0 or comn == False:
            self.lable.config(text='请输入正确的串口号!')
            messagebox.showerror('串口错误','请输入正确的串口号!')
            return False
        with open('./sctest.info', 'rb') as fp:
            sc_info = pickle.load(fp)
            read_base = int(sc_info['dst_addr'])
            datalen = int(sc_info['out_nn'])
            f_bit, e_bit = sc_info['float_format']
            print('read_base: ',read_base,' data_len: ',datalen,' f_bit: ',f_bit,' e_bit: ',e_bit)
        try:
            comn = format('COM%d'%comn)
            ser = serial.Serial(comn, 115200, timeout=1.0)
        except:
            self.label.config(text=('无法打开'+comn))
            return False
        self.database.generate_train_set(float(self.noise.get()), 5)
        self.label.config(text='打开'+comn+'成功 开始测试')
        if self.nntype == 'BP':
            for i in range(0, 5):
                da = array2uc(self.database.train_x[:, i])
                show_set = self.database.train_x[:, i].reshape([8, 9])
                # 显示原图
                sub = self.fig.add_subplot(2, 5, i + 1)
                sub.imshow(show_set, 'gray')
                sub.set_axis_off()

                sda = ser.read_all()
                send_frame(ser, da, read_base)
                sda = ser.read(4 * datalen).hex()
                str = re.sub(r"(?<=\w)(?=(?:\w\w)+$)", " ", sda)
                fo = []
                for j in range(0, datalen):
                    dc = sda[j * 8:j * 8 + 8]
                    fo.append(cf_dll.s2f(ctypes.c_char_p(bytes(dc, 'utf-8')), f_bit, e_bit))
                    print('%3.2f' % fo[-1], end=' ')
                mindex = fo.index(max(fo))
                #fo = softmax(np.array(fo)).reshape(1, datalen)
                fo = np.array(fo).reshape(1,datalen)
                print('\n序号:%d，最大值:%.3f' % (mindex, fo[0, mindex]))

                sub = self.fig.add_subplot(2, 5, i + 6)
                sub.imshow(fo, 'gray')
                sub.set_axis_off()
                sub.set_title(label=format(' %d : %.2f' % (mindex, fo[0, mindex])),fontdict={'fontsize':8})
                self.canvas.show()

        if self.nntype == 'Hopfield':
            sn = math.ceil(datalen / 8)
            for i in range(0, 5):
                da = self.database.train_x[:, i]
                show_set = da.reshape([8, 9])
                str = ser.read_all()
                # da[0:23] = 0
                da = array2uc(da)
                send_frame(ser, da, read_base)
                sub = self.fig.add_subplot(4, 5, i + 1)
                sub.imshow(show_set, 'gray')
                sub.set_axis_off()
                sub.set_title(label=format('source'), fontdict={'fontsize': 8})
                self.canvas.show()
                # 第J次迭代
                for j in range(1, 4):
                    str = (re.sub(r"(?<=\w)(?=(?:\w\w)+$)", " ", ser.read(sn).hex())).split(' ')
                    a = []
                    print(str)
                    if len(str) >= sn:
                        for d in range(0, sn):
                            a.append(int(str[d], 16))
                        a.reverse()
                        send_frame(ser, a, read_base)
                    else:
                        a = [0xfe for i in range(0, sn)]
                        send_frame(ser, da, read_base)

                    show_set = uc2array(a).reshape([8, 9])

                    sub = self.fig.add_subplot(4, 5, i + j*5 + 1)
                    sub.imshow(show_set, 'gray')
                    sub.set_axis_off()
                    sub.set_title(label=format('epoch %d'%j), fontdict={'fontsize': 8})
                    self.canvas.show()
        ser.close()
    def loop(self):
        self.Popupwindow.mainloop()

class PopupShowSet():
    def __init__(self,nntype):
        self.Popupwindow=tk.Tk()
        self.Popupwindow.title(nntype+'网络测试窗口')
        self.nntype = nntype
        self.noise = tk.StringVar()
        self.noise.set('0.05')
        self.com = tk.StringVar()
        self.com.set('17')
        self.database = Number_Data('./nntrain/number_source.txt')
        tk.Label(self.Popupwindow, text=('网络类型为:'+nntype + '请输入测试串口号: COM')).grid(row=0, column=0,sticky=tk.E)
        tk.Entry(self.Popupwindow,textvariable=self.com,width=2,justify=tk.RIGHT).grid(row=0,column=1,sticky=tk.W)
        tk.Label(self.Popupwindow, text=('添加噪声比例：')).grid(row=0, column=2, sticky=tk.E)
        tk.Entry(self.Popupwindow, width=4,textvariable=self.noise, justify=tk.RIGHT).grid(row=0, column=3, sticky=tk.W)
        self.btn_train = tk.Button(self.Popupwindow, text='测试', width=8, height=1, command=self.test_callback)
        self.btn_train.grid(row=0, column=4, sticky=tk.W)

if __name__ == '__main__':
    #win_train = PopupTrain('BP')
    #win_train.loop()
    win_test = PopupTest('BP')
    win_test.loop()

