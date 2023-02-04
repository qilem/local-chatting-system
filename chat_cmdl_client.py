import tkinter.filedialog
import tkinter.messagebox
import tkinter as tk
from tkinter import ttk
from chat_client_class import *
import datetime
from time import strftime
from simpleGame import SimpleGame

#登陆界面
class Login_win:

    def show(self):
        self.win.mainloop()

    def destroy(self):
        self.win.destroy()

    def __init__(self):
        self.win = tk.Tk()
        self.user = tk.StringVar()
        self.pwd = tk.StringVar()

        self.win.geometry("320x240")
        self.win.title("loginUI")
        self.win.resizable(width=False, height=False)

        self.label1 = tk.Label(self.win)
        self.label1.place(relx=0.055, rely=0.1, height=31, width=89)
        self.label1.configure(text='Account')

        self.entry_user = tk.Entry(self.win)
        self.entry_user.place(relx=0.28, rely=0.11, height=26, relwidth=0.554)
        self.entry_user.configure(textvariable=self.user)

        self.label2 = tk.Label(self.win)
        self.label2.place(relx=0.055, rely=0.27, height=31, width=89)
        self.label2.configure(text='psw')

        self.entry_pwd = tk.Entry(self.win)
        self.entry_pwd.place(relx=0.28, rely=0.28, height=26, relwidth=0.554)
        self.entry_pwd.configure(show="*")
        self.entry_pwd.configure(textvariable=self.pwd)

        self.btn_login = tk.Button(self.win)
        self.btn_login.place(relx=0.13, rely=0.6, height=32, width=88)
        self.btn_login.configure(text='login')

        self.btn_reg = tk.Button(self.win)
        self.btn_reg.place(relx=0.6, rely=0.6, height=32, width=88)
        self.btn_reg.configure(text='register')


class Main_win:
    
    closed_fun = None

    def show(self):
        self.win.mainloop()

    def destroy(self):
        try:
            self.closed_fun()
        except:
            pass
        self.win.destroy()

    def __init__(self):
        self.win = tk.Tk()
        self.win.protocol('WM_DELETE_WINDOW', self.destroy)
        self.win.geometry("640x640")  # 480x320
        self.win.title("ICS")
        self.win.resizable(width=False, height=False)

        self.msg = tk.StringVar()
        self.name = tk.StringVar()
        self.searchOrPoem = tk.StringVar()
        self.nickName = ''

        
        self.history = tk.Text(self.win)
        self.history.tag_config("tag_00", backgroun="white", foreground="black", justify="left")
        self.history.tag_config("tag_01", backgroun="white", foreground="black", justify="right")
        self.history.tag_config("tag_10", backgroun="white", foreground="red", justify="left")
        self.history.tag_config("tag_11", backgroun="white", foreground="red", justify="right")
        self.history.tag_config("tag_20", backgroun="white", foreground="black", justify="left")
        self.history.tag_config("tag_21", backgroun="green", foreground="black", justify="right")
        self.history.tag_config("tag_30", backgroun="white", foreground="blue", justify="left")
        self.history.tag_config("tag_31", backgroun="white", foreground="blue", justify="right")
        self.history.place(relx=0.02, rely=0.17, relheight=0.63, relwidth=0.696)  # 0.696
        self.history.configure(state='disabled')

        self.entry_msg = tk.Entry(self.win)
        self.entry_msg.place(relx=0.02, rely=0.9, height=24, relwidth=0.49)
        self.entry_msg.configure(textvariable=self.msg)

        self.btn_send = tk.Button(self.win)
        self.btn_send.place(relx=0.52, rely=0.9, height=28, width=45)
        self.btn_send.configure(text='send')

        self.btn_clear = tk.Button(self.win)
        self.btn_clear.place(relx=0.62, rely=0.9, height=28, width=45)
        self.btn_clear.configure(text='clear')

        self.btn_bot = tk.Button(self.win)
        self.btn_bot.place(relx=0.716, rely=0.9, height=28, width=50)
        self.btn_bot.configure(text='chatbot')

        # 用户列表
        self.user_list = tk.Listbox(self.win)
        self.user_list.place(relx=0.75, rely=0.15, relheight=0.25, relwidth=0.23)  # 0.23

        self.label1 = tk.Label(self.win)
        self.label1.place(relx=0.72, rely=0.08, height=21, width=100)
        self.label1.configure(text='user_list')
        self.btn_refresh = tk.Button(self.win)
        self.btn_refresh.place(relx=0.85, rely=0.08, height=28, width=80)
        self.btn_refresh.configure(text='refresh')

        # 搜索或诗歌
        self.label4 = tk.Label(self.win)
        self.label4.place(relx=0.80, rely=0.42, height=21, width=100)
        self.label4.configure(text='record&poem')
        self.searchResult = tk.Text(self.win)
        self.searchResult.place(relx=0.75, rely=0.45, relheight=0.35, relwidth=0.23)
        self.forSearch = tk.Entry(self.win)
        self.forSearch.place(relx=0.75, rely=0.82, height=24, relwidth=0.23)
        self.forSearch.configure(textvariable=self.searchOrPoem)
        self.btn_search = tk.Button(self.win)
        self.btn_search.place(relx=0.82, rely=0.9, height=28, width=45)
        self.btn_search.configure(text='search')
        self.btn_poem = tk.Button(self.win)
        self.btn_poem.place(relx=0.92, rely=0.9, height=28, width=45)
        self.btn_poem.configure(text='poem')

        # self.btn_file = tk.Button(self.win)
        # self.btn_file.place(relx=0.752, rely=0.89, height=28, width=108)
        # self.btn_file.configure(text='发送文件')
        # self.btn_file.configure(state='disabled')
        # username
        self.label2 = tk.Label(self.win)
        self.label2.place(relx=0.24, rely=0.0, height=57, width=140)
        self.label2.configure(textvariable=self.name)

        # 聊天字体颜色，默认绿色背景
        self.comvalue = tk.StringVar()  # 窗体自带的文本，新建一个值
        self.comboxlist = ttk.Combobox(self.win, textvariable=self.comvalue)  # 初始化
        self.comboxlist["values"] = ("black", "red", "green", "blue")
        self.comboxlist.current(2)  # 选择第3个
        self.comboxlist.bind("<<ComboboxSelected>>", comboboxSelected)  # 绑定事件,(下拉列表框被选中时，绑定comboboxSelected()函数)
        self.label3 = tk.Label(self.win)
        self.label3.place(relx=0, rely=0.1, height=21, width=60)
        self.label3.configure(text='msgColor')
        self.comboxlist.place(relx=0.1, rely=0.1, height=21, width=60)
        self.tag_color = '2'

        # game

        self.game_value = tk.StringVar()  # 窗体自带的文本，新建一个值
        self.game_list = ttk.Combobox(self.win, textvariable=self.game_value)  # 初始化
        self.game_list["values"] = ("simple")
        # self.comboxlist.current(2)  # 选择第3个
        self.game_list.bind("<<ComboboxSelected>>", gameSelected)  # 绑定事件,(下拉列表框被选中时，绑定comboboxSelected()函数)
        self.label5 = tk.Label(self.win)
        self.label5.place(relx=0.4, rely=0.1, height=21, width=60)
        self.label5.configure(text='game')
        self.game_list.place(relx=0.5, rely=0.1, height=21, width=60)



    def fromChild(self, data):
        print("from child")


def comboboxSelected(event):
    global client, main_win
    main_win.tag_color = str(main_win.comboxlist.current())
    print(main_win.comboxlist.get())


def gameSelected(event):
    global client, main_win, mygame
    index = main_win.game_list.current()
    if index == 0 and client.isChatting():  # 只有处于聊天状态才可以玩网络版游戏
        client.setShowGame(True)
        client.send2('#', act='requestGame')  # 让对方也玩游戏
        startGame()
    else:
        tkinter.messagebox.showerror('error', 'You are chatting with no one!')
        # client.send2('0&0&0')

    # main_win.tag_color = str(main_win.comboxlist.current())
    # print(main_win.comboxlist.get())


def itemSelected(event):
    obj = event.widget
    index = obj.curselection()
    if len(index) != 0:
        print(obj.get(index))
        msg = client.send2('c ' + obj.get(index))
        if len(msg) > 0:
            append_history(msg)
            client.clearMsg()


def on_btn_send_clicked():
    global client, main_win
    msg2 = main_win.msg.get()
    if msg2 != '':
        msg = client.send2(msg2)
        append_history(msg2, '1')
        if len(msg) > 0:
            append_history(msg)
            client.clearMsg()
        main_win.msg.set('')
    else:
        tkinter.messagebox.showinfo('error', 'msg is None！')

def chat_with_bot():
    global client, main_win
    msg2 = main_win.msg.get()
    if msg2 != '':
        msg = client.send2(msg2, act='chatwithbot')
        append_history(msg2, '1')
        if len(msg) > 0:
            append_history(msg)
            client.clearMsg()
        main_win.msg.set('')
    else:
        tkinter.messagebox.showinfo('error', 'msg is None！')



def on_btn_clear_clicked():
    global client, main_win
    main_win.msg.set('')


def on_btn_search():
    global client, main_win
    msg2 = main_win.searchOrPoem.get()
    if msg2 != '':
        msg = client.send2('? ' + msg2)
        if len(msg) > 0:
            append_search_or_poem(msg)
            client.clearMsg()
        main_win.searchOrPoem.set('')
    else:
        tkinter.messagebox.showinfo('error', 'msg is None！')


def on_btn_poem():
    global client, main_win
    msg2 = main_win.searchOrPoem.get()
    if msg2 != '':
        msg = client.send2('p ' + msg2)
        if len(msg) > 0:
            append_search_or_poem(msg)
            client.clearMsg()
        main_win.searchOrPoem.set('')
    else:
        tkinter.messagebox.showinfo('error', 'msg is None！')





def startGame():  # 开启游戏
    global mygame, main_win, client
    client.setShowGame(True)
    # mygame = FiveGame(main_win, client, main_win.nickName)
    mygame = SimpleGame(client, main_win.nickName)
    # mygame.show()


def recv_async():
    global client, mygame
    while True and client.onLine():
        msg = client.proc()
        if len(msg) > 0:
            if msg[0] == '#':  # 收到邀请玩游戏，启动游戏
                startGame()
            elif msg[0] == '*':  # 更新游戏状态
                mygame.update(msg[1:])
            else:
                append_history(msg)
            client.clearMsg()
        time.sleep(CHAT_WAIT)


def on_closed():
    client.close()


def append_history(msg, flag='0'):
    now = datetime.datetime.now()
    theTime = now.strftime("%Y-%m-%d %H:%M:%S")
    main_win.history['state'] = 'normal'
    main_win.history.insert('end', theTime + '\n' + msg + '\n\n', 'tag_' + main_win.tag_color + flag)  # text
    main_win.history.see('end')
    main_win.history['state'] = 'disabled'
    # main_win.user_list.selection_set(0)


def append_search_or_poem(msg):
    main_win.searchResult['state'] = 'normal'
    main_win.searchResult.insert('end', msg + '\n', 'text')  # text
    main_win.searchResult.see('end')
    main_win.searchResult['state'] = 'disabled'


args = None
login_win = Login_win()
main_win = None
client = None
mygame = None

def get_who():
    global client, main_win
    #设置用户列表内名字和用户名字一致，从socket里面找在线用户
    names = client.send2('who')
    name_list = names.split('&')
    theSize = main_win.user_list.size()
    main_win.user_list.delete(0, theSize)
    for i in range(len(name_list)):
        if name_list[i] != '' and name_list[i] != main_win.nickName:
            main_win.user_list.insert('end', name_list[i])
    client.clearMsg()




def on_btn_login_clicked():
    global login_win, args, main_win, client
    name = login_win.user.get()
    psw = login_win.pwd.get()
    #账户密码不为空时
    if name != '' and login_win.pwd != '':
        #client继承自己的所有属性，详见client class
        client = Client(args)
        res, info = client.login2(name,psw)
        if res:
            #登录验证通过时，在客户端的终端print success
            print('success')
            #关闭登陆界面
            login_win.destroy()
            #打开聊天主界面
            main_win = Main_win()
            #看起来像是关闭按钮
            main_win.closed_fun = on_closed
            #这是user name
            main_win.nickName = name
            #欢迎词
            main_win.name.set('Welcome back!\n%s' % name)
            #按下对应的按钮以后调用的函数
            main_win.btn_send.configure(command=on_btn_send_clicked)
            main_win.btn_clear.configure(command=on_btn_clear_clicked)
            main_win.btn_search.configure(command=on_btn_search)
            main_win.btn_poem.configure(command=on_btn_poem)
            main_win.btn_refresh.configure(command=get_who)
            main_win.btn_bot.configure(command=chat_with_bot)

            #点击user list里面的用户以后进行连接
            main_win.user_list.bind("<<ListboxSelect>>", itemSelected)
            #将欢迎词加入历史检索
            append_history('Welcome back, ' + name + '!')

            get_who()
            #在这个过程之中一直保持信息的接收
            t = threading.Thread(target=recv_async, args=())
            t.setDaemon(True)
            t.start()
            main_win.show()

        else:
            tkinter.messagebox.showerror('error', 'fail：' + info)

    else:
        tkinter.messagebox.showerror('tips', 'account or psw is None')

def on_btn_reg_clicked():
    global login_win, args, main_win, client
    if login_win.user.get() != '' and login_win.pwd.get() != '':
        client = Client(args)
        name = login_win.user.get()
        res, info = client.register(login_win.user.get(),login_win.pwd.get())
        #和login的过程是一样的
        if res:
            login_win.destroy()
            main_win = Main_win()
            main_win.closed_fun = on_closed
            main_win.nickName = name
            #和login是不一样的欢迎词
            main_win.name.set('Welcome for new friend.\n%s' % name)
            main_win.btn_send.configure(command=on_btn_send_clicked)
            main_win.btn_clear.configure(command=on_btn_clear_clicked)
            main_win.btn_search.configure(command=on_btn_search)
            main_win.btn_poem.configure(command=on_btn_poem)
            main_win.btn_refresh.configure(command=get_who)
            main_win.user_list.bind("<<ListboxSelect>>", itemSelected)
            append_history('Welcome new friend. ' + name + '!')
            get_who()
            t = threading.Thread(target=recv_async, args=())
            t.setDaemon(True)
            t.start()
            main_win.show()
        else:
            tkinter.messagebox.showerror('error', info)
    else:
        tkinter.messagebox.showerror('error', 'Account and psw is None！')



def main():
    global args
    import argparse
    parser = argparse.ArgumentParser(description='chat client argument')
    parser.add_argument('-d', type=str, default=None, help='server IP addr')
    args = parser.parse_args()

    login_win.btn_login.configure(command=on_btn_login_clicked)
    login_win.btn_reg.configure(command=on_btn_reg_clicked)
    login_win.show()


if __name__ == "__main__":
    main()
