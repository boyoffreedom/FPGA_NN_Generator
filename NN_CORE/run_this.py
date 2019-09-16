import tkinter as tk
from tkinter.filedialog import askdirectory
from tkinter import ttk
from tkinter import messagebox
from Popup import *
import time,sys
sys.path.append('./nngen')
sys.path.append('./nntrain')

from nn_core_gen import *
from number_recog import *

def selectPath():
    path_ = askdirectory()
    path.set(path_)

def cmb_nn(event):
    #l0.config(text = NNChosen.get())
    l_nng.config(text=('选择网络为:'+NNChosen.get()+'  请选择训练或生成.v文件'))
    pass

def load_config():
    pass

def show_dataset():
    s = Number_Data('./nntrain/number_source.txt')
    s.generate_test_set(0.02, 200)
    for i in range(s.N):
        show_set = s.stander_set_x[:, i].reshape([8, 9])
        plt.subplot(2,5,i+1),plt.imshow(show_set,'gray')

        plt.xticks([])
        plt.yticks([])
        plt.axis('off')
    plt.show()
def save_config():

    pass

#菜单回调函数
def setfp32():
    ent_fb.set('23')
    ent_eb.set('8')

def setfp16():
    ent_fb.set('10')
    ent_eb.set('5')

def setfp14():
    ent_fb.set('8')
    ent_eb.set('5')

def nn_gen():
    cell_n = isuint(ent_cn.get())
    #t.delete('1.0', 'end')          #清空text内容
    if cell_n == False:
        l_nng.config(text='网络生成失败!请检查运算器数量!')
        messagebox.showinfo(title='ERROR!', message='运算器数量非正整数')
        ent_cn.set('10')
        return False
    f_bit = isuint(ent_fb.get())
    if f_bit == False:
        l_nng.config(text='网络生成失败!请检查配置浮点格式的尾数位数!')
        messagebox.showinfo(title='ERROR!', message='配置尾数非正整数')
        ent_fb.set('23')
        return False
    e_bit = isuint(ent_eb.get())
    if e_bit == False:
        l_nng.config(text='网络生成失败!请检查配置浮点格式的指数位数!')
        messagebox.showinfo(title='ERROR!', message='配置指数非正整数')
        ent_eb.set('8')
        return False

    NN_CORE(path.get(), cell_n, [f_bit,e_bit])
    if NNChosen.get() == 'BP':
        ninfo_f = './nntrain/bp.ninfo'
        SCI_IO_GEN(path.get(), 0)
    elif NNChosen.get() == 'Hopfield':
        ninfo_f = './nntrain/hop.ninfo'
        SCI_IO_GEN(path.get(), 1)
    else:
        ninfo_f = None
    nn_mif_gen(path.get(), cell_n, [f_bit,e_bit], ninfo_f)

    tx = NNChosen.get()+'网络文件生成成功，请进入FPGA软件进行编译！'
    l_nng.config(text=tx)
    messagebox.showinfo(title='Success', message=tx)


def nn_train():
    win_train = PopupTrain(NNChosen.get())
    win_train.loop()

def nn_test():
    win_test = PopupTest(NNChosen.get())
    win_test.loop()

window = tk.Tk()
window.title('FPGA神经网络生成器')
window.resizable(0,0)
path = tk.StringVar()

#菜单
menubar = tk.Menu(window)
##定义一个空菜单单元
filemenu = tk.Menu(menubar)
cfgmenu = tk.Menu(menubar)

##将上面定义的空菜单命名为`File`，放在菜单栏中，就是装入那个容器中
menubar.add_cascade(label='文件', menu=filemenu)
menubar.add_cascade(label='配置', menu=cfgmenu)

##在`File`中加入`New`的小菜单，即我们平时看到的下拉菜单，每一个小菜单对应命令操作。
##如果点击这些单元, 就会触发`do_job`的功能
filemenu.add_command(label='数据集', command=show_dataset)##同样的在`File`中加入`Open`小菜单
filemenu.add_command(label='加载配置', command=load_config)
filemenu.add_command(label='保存配置', command=save_config)##同样的在`File`中加入`Open`小菜单
filemenu.add_separator()##这里就是一条分割线
##同样的在`File`中加入`Exit`小菜单,此处对应命令为`window.quit`
filemenu.add_command(label='退出', command=window.quit)

cfgmenu.add_command(label='配置FP32',command=setfp32)
cfgmenu.add_command(label='配置FP16',command=setfp16)
cfgmenu.add_command(label='配置FP14',command=setfp14)

#第0行，选择路径
tk.Label(window,text ='项目路径:',width=12).grid(row = 0, column = 0,sticky=tk.E)
tk.Entry(window, textvariable = path,width = 60).grid(row = 0, column=1, columnspan=7, sticky=tk.W)
tk.Button(window, text = '浏览...', command = selectPath).grid(row = 0, column=5,sticky=tk.E)
path.set('./source')
#第一行，选择网络
l0 = tk.Label(window,text='网络类型:', width=12,height=2)
l0.grid(row = 1, column = 0,sticky=tk.E)

nn_type = tk.StringVar()
NNChosen = ttk.Combobox(window, width=12, textvariable=nn_type)
NNChosen['values'] = ('BP','Hopfield')  # 设置下拉列表的值
NNChosen.grid(row=1,column=1,sticky=tk.W,columnspan=2)  # 设置其在界面中出现的位置  column代表列   row 代表行
NNChosen.current(0)  # 设置下拉列表默认显示的值，0为 numberChosen['values'] 的下标值
NNChosen.bind("<<ComboboxSelected>>",cmb_nn)

ent_cn = tk.StringVar()
ent_cn.set('10')
tk.Label(window,text='运算器数量:',width=12).grid(row=1,column=3)
tk.Entry(window,textvariable = ent_cn,width = 8,justify=tk.RIGHT).grid(row=1,column=4)

btn_train = tk.Button(window,text='训练网络',width=15,height=1,command=nn_train)
btn_train.grid(row=1,column=5)

ent_fb = tk.StringVar()
ent_fb.set('23')
ent_eb = tk.StringVar()
ent_eb.set('8')
#第三行：配置浮点数格式
tk.Label(window,text='配置浮点格式:',width=12,height=2).grid(row=2,column=0,sticky=tk.E)
tk.Label(window,text='指数位数:',width=8).grid(row=2,column=1)
tk.Entry(window,textvariable = ent_eb,width = 8,justify=tk.RIGHT).grid(row=2,column=2)
tk.Label(window,text='尾数位数:',width=8).grid(row=2,column=3)
tk.Entry(window,textvariable = ent_fb,width = 8,justify=tk.RIGHT).grid(row=2,column=4)


btn_nng = tk.Button(window,text='生成.v源文件',width=15,height=1,command=nn_gen)
btn_nng.grid(row=2,column=5)

l_nng = tk.Label(window,text='请选择路径，点击生成按钮生成网络文件！', width=50)
l_nng.grid(row=3,column=1,columnspan=4)
btn_test = tk.Button(window,text='测试',width=15,height=1,command=nn_test)
btn_test.grid(row=3,column=5)
window['menu']=menubar
window.mainloop()
