from tkinter import *
from PIL import Image, ImageTk
import tkinter.messagebox


class SimpleGame:
    def __init__(self, client, name):

        self.root = Toplevel()
        self.client = client
        self.name = name
        self.root['bg'] = 'green'
        self.root.geometry('640x640')
        self.root.title('SimpleGame user: ' + name)
        self.result = StringVar()
        self.round = StringVar()
        self.score_me = 0
        self.score_peer = 0
        self.round.set(0)
        self.pics = ['jian.jpg', 'shi.jpg', 'bu.jpg', 'wen.jpg']
        self.num = 0
        self.userChoice = None  # 自己出的
        self.peerChoice = None  # 对方出的
        self.photo1 = None
        self.photo2 = None
        self.photo3 = None
        self.photo4 = None
        self.photo5 = None
        self.count = 0  # 统计结果
        self.step = 0  # 第几个回合
        self.nextRound = True  # 是否可以下一个回合
        self.end = False  # 是否结束
        self.layout()
        # self.root.mainloop()

    def layout(self):
        #图标
        Label(self.root, text='result:', font=('黑体', 20), fg='white', bg='green') \
            .place(relx=0.35, rely=0.05)
        Label(self.root, textvariable=self.result, font=('黑体', 20), fg='white', bg='green').place(relx=0.5, rely=0.05)
        self.result.set('')

        Label(self.root, text='round:', font=('黑体', 20), fg='white', bg='green') \
            .place(relx=0.35, rely=0.1)
        Label(self.root, textvariable=self.round, font=('黑体', 20), fg='white', bg='green').place(relx=0.5, rely=0.1)

        Label(self.root, text='me', font=('黑体', 20), fg='white', bg='green') \
            .place(relx=0.3, rely=0.25)
        Label(self.root, text='peer', font=('黑体', 20), fg='white', bg='green') \
            .place(relx=0.68, rely=0.25)

        image1 = Image.open(self.pics[0])
        self.photo1 = ImageTk.PhotoImage(image1)  # 转为与tkinter兼容的图像对象
        image2 = Image.open(self.pics[1])
        self.photo2 = ImageTk.PhotoImage(image2)
        image3 = Image.open(self.pics[2])
        self.photo3 = ImageTk.PhotoImage(image3)
        image4 = Image.open(self.pics[3])
        self.photo4 = ImageTk.PhotoImage(image4)
        image5 = Image.open(self.pics[3])
        self.photo5 = ImageTk.PhotoImage(image5)
        #石头，剪刀，布
        Button(self.root, image=self.photo1,
               command=lambda: self.choose(0)).place(relx=0.05, rely=0.65, height=150, width=150)
        Button(self.root, image=self.photo2,
               command=lambda: self.choose(1)).place(relx=0.38, rely=0.65, height=150, width=150)
        Button(self.root, image=self.photo3,
               command=lambda: self.choose(2)).place(relx=0.7, rely=0.65, height=150, width=150)

        self.userChoice = Button(self.root, image=self.photo4)
        self.userChoice.place(relx=0.2, rely=0.3, height=150, width=150)
        
        Label(self.root, text='VS', font=('黑体', 20), fg='white', bg='green') \
            .place(relx=0.5, rely=0.4)

        self.peerChoice = Button(self.root, image=self.photo5)
        self.peerChoice.place(relx=0.6, rely=0.3, height=150, width=150)
        
        Button(self.root, text='Again',
               command=lambda: self.reset()).place(relx=0.4, rely=0.92, height=45, width=100)

    def choose(self, n):
        if self.end:
            tkinter.messagebox.showinfo('tip', 'Game is over!\n Please Play Again!')
            return
        if self.nextRound:
            self.num = n
            chooseImage = Image.open(self.pics[n])
            self.photo4 = ImageTk.PhotoImage(chooseImage)
            self.userChoice.configure(image=self.photo4)
            retImage = Image.open(self.pics[3])
            self.photo5 = ImageTk.PhotoImage(retImage)
            self.peerChoice.configure(image=self.photo5)
            self.step += 1
            # if self.step == 3:  # 3局2胜
            #     self.end = True
            self.round.set(str(self.step))
            self.nextRound = False  # 等待对方出
            self.client.send2(str(n), act='recordPlay')

    def resetTwoChoice(self):
        retImage = Image.open(self.pics[3])
        self.photo4 = ImageTk.PhotoImage(retImage)
        self.userChoice.configure(image=self.photo4)
        self.photo5 = ImageTk.PhotoImage(retImage)
        self.peerChoice.configure(image=self.photo5)

    def clearState(self):
        self.resetTwoChoice()
        self.result.set('')
        self.round.set('0')
        self.count = 0
        self.step = 0
        self.nextRound = True
        self.end = False

    def reset(self):
        if self.end:
            self.clearState()
            self.client.send2(str(5), act='recordPlay')  # 重置服务器的变量
        else:
            tkinter.messagebox.showinfo('tip', 'Game is playing!')

    def update(self, msg):
        data = msg.split('&')  # 第一位是对方的选择，第二个是结果，-1代表还没结束，0代表和，1代表赢，2代表对方赢
        print('update==', data)
        peerNum = int(data[0])
        if peerNum == 5:  # 对方请求玩新的游戏
            self.clearState()
            return
        elif peerNum == 6:
            self.resetTwoChoice()  # 下一轮已经开始，对方已出拳
            return
        res = int(data[1])
        chooseImage = Image.open(self.pics[peerNum])
        self.photo5 = ImageTk.PhotoImage(chooseImage)
        self.peerChoice.configure(image=self.photo5)
        self.nextRound = True
        if res == 0:
            self.result.set('Draw')
            self.end = True
        elif res == 1:
            self.result.set('Win')
            self.end = True
        elif res == 2:
            self.result.set('Loss')
            self.end = True

# SimpleGame( 1, '1')
