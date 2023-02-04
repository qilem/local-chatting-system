"""
Created on Tue Jul 22 00:47:05 2014

@author: alina, zzhang
"""

import time
import socket
import select
import sys
import string
import indexer
import json
import pickle as pkl
from chat_utils import *
import chat_group as grp
from chatbot import Chatter


class JudgeGame:
    def __init__(self):
        self.round = 0
        self.res = {}
        self.record = {}  # 记录第几轮的结果，每一轮只有收到两个人的选择才会比较输赢，并重置

    def reset(self):
        self.round = 0
        self.res = {}
        self.record = {}  # 记录第几轮的结果


class Server:
    def __init__(self):
        self.new_clients = []  # list of new sockets of which the user id is not known
        self.logged_name2sock = {}  # dictionary mapping username to socket
        self.logged_sock2name = {}  # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        # start server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        # initialize past chat indices
        self.indices = {}
        # sonnet
        self.sonnet = indexer.PIndex("AllSonnets.txt")
        self.judgeGame = JudgeGame()

    def new_client(self, sock):
        # add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def isExist(self, name):
        file = open('user.txt', 'r')
        data = file.readlines()
        file.close()
        for row in data:
            tmp_list = row.split(':')
            if tmp_list[0] == name:
                return True, tmp_list[1]
        return False, ''

    def writeToTxt(self, name, psw):
        file = open('user.txt', 'a+')
        file.write(name + ":" + psw + "\n")
        file.close()

    def login(self, sock):
        # read the msg that should have login code plus username
        try:
            msg = json.loads(myrecv(sock))
            if len(msg) > 0:

                if msg["action"] == "login":
                    name = msg["name"]
                    psw = msg["psw"]
                    flag, pw = self.isExist(name)
                    pw = pw.strip("\n")
                    if flag:
                        if pw!=psw:
                            mysend(sock, json.dumps(
                                {"action": "login", "status": "psw is wrong"}))
                        else:
                            if self.group.is_member(name) != True:
                                # move socket from new clients list to logged clients
                                self.new_clients.remove(sock)
                                # add into the name to sock mapping
                                self.logged_name2sock[name] = sock
                                self.logged_sock2name[sock] = name
                                # load chat history of that user
                                if name not in self.indices.keys():
                                    try:
                                        self.indices[name] = pkl.load(
                                            open(name + '.idx', 'rb'))
                                    except IOError:  # chat index does not exist, then create one
                                        self.indices[name] = indexer.Index(name)
                                print(name + ' logged in')
                                self.group.join(name)
                                mysend(sock, json.dumps(
                                    {"action": "login", "status": "ok"}))
                            else:  # a client under this name has already logged in
                                mysend(sock, json.dumps(
                                    {"action": "login", "status": "duplicate"}))
                                print(name + ' duplicate login attempt')
                    else:
                        mysend(sock, json.dumps({"action": "login", "status": "user is not exist"}))
                elif msg['action'] =='register':
                    self.register(sock,msg)
                else:
                    print('wrong code received')
            else:  # client died unexpectedly
                self.logout(sock)
        except:
            self.all_sockets.remove(sock)

    def register(self, sock,msg):
        try:
            # msg = json.loads(myrecv(sock))
            if len(msg) > 0:
                if msg["action"] == "register":
                    name = msg["name"]
                    psw = msg["psw"]
                    flag, pw = self.isExist(name)
                    if flag:
                        mysend(sock, json.dumps(
                            {"action": "register", "status": "user is exist"}))
                    else:
                        self.writeToTxt(name, psw)
                        if self.group.is_member(name) != True:
                            # move socket from new clients list to logged clients
                            self.new_clients.remove(sock)
                            # add into the name to sock mapping
                            self.logged_name2sock[name] = sock
                            self.logged_sock2name[sock] = name
                            # load chat history of that user
                            if name not in self.indices.keys():
                                try:
                                    self.indices[name] = pkl.load(
                                        open(name + '.idx', 'rb'))
                                except IOError:  # chat index does not exist, then create one
                                    self.indices[name] = indexer.Index(name)
                            print(name + ' register in')
                            self.group.join(name)
                            mysend(sock, json.dumps(
                                {"action": "register", "status": "ok"}))
                else:
                    print('wrong code received')
            else:  # client died unexpectedly
                self.logout(sock)
        except:
            self.all_sockets.remove(sock)

    def logout(self, sock):
        # remove sock from all lists
        name = self.logged_sock2name[sock]
        pkl.dump(self.indices[name], open(name + '.idx', 'wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()

    # ==============================================================================
    # main command switchboard
    # ==============================================================================
    def handle_msg(self, from_sock,liaotian):
        # read msg code
        msg = myrecv(from_sock)
        if len(msg) > 0:
            # ==============================================================================
            # handle connect request this is implemented for you
            # ==============================================================================
            msg = json.loads(msg)
            if msg["action"] == "connect":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action": "connect", "status": "self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = json.dumps(
                        {"action": "connect", "status": "success"})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps(
                            {"action": "connect", "status": "request", "from": from_name}))
                else:
                    msg = json.dumps(
                        {"action": "connect", "status": "no-user"})
                mysend(from_sock, msg)
            # ==============================================================================
            # handle messeage exchange: IMPLEMENT THIS
            # ==============================================================================
            elif msg["action"] == "exchange":
                from_name = self.logged_sock2name[from_sock]
                """
                Finding the list of people to send to and index message
                """
                # IMPLEMENTATION
                # ---- start your code ---- #
                # massage = text_proc(msg["message"], from_name)
                massage = msg["message"]
                # mysend(self.s, json.dumps({"action": "exchange", "from": "[" + from_name + "]", "message": massage}))
                self.indices[from_name].add_msg_and_index(massage)
                # ---- end of your code --- #
                the_guys = self.group.list_me(from_name)[1:]
                for g in the_guys:
                    to_sock = self.logged_name2sock[g]
                    # IMPLEMENTATION
                    # ---- start your code ---- #
                    self.indices[g].add_msg_and_index(massage)
                    # mysend(
                    #     to_sock, "...Remember to index the messages before sending, or search won't work")
                    mysend(
                        to_sock, json.dumps({"action": "exchange", "from": "[" + from_name + "]", "message": massage}))

                    # ---- end of your code --- #
            elif msg["action"] == "requestGame":  # 有人发起游戏请求
                from_name = self.logged_sock2name[from_sock]
                """
                Finding the list of people to send to and index message
                """
                self.judgeGame.reset()
                massage = msg["message"]
                self.indices[from_name].add_msg_and_index(massage)
                the_guys = self.group.list_me(from_name)[1:2]
                for g in the_guys:
                    to_sock = self.logged_name2sock[g]
                    self.indices[g].add_msg_and_index(massage)
                    mysend(
                        to_sock, json.dumps({"action": "requestGame", "message": massage}))
            # ==============================================================================
            # the "from" guy has had enough (talking to "to")!
            # ==============================================================================
            elif msg["action"] == "recordPlay":  # 计算游戏结果
                num = int(msg['message'])
                msgToFrom = ''
                msgToGuy = ''
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)[1]
                to_sock = self.logged_name2sock[the_guys]
                if num == 5:  # 继续新的游戏
                    self.judgeGame.reset()
                    mysend(
                        to_sock, json.dumps({"action": "gameRes", "message": '5'}))
                else:
                    self.judgeGame.record[from_name] = num
                    if from_name not in self.judgeGame.res:
                        self.judgeGame.res[from_name] = 0
                    if the_guys not in self.judgeGame.res:
                        self.judgeGame.res[the_guys] = 0
                    if the_guys in self.judgeGame.record:  # 两个人的选择都收到了，开始判断
                        self.judgeGame.round += 1
                        num2 = self.judgeGame.record[the_guys]
                        msgToFrom += str(num2) + '&'  # 把对方的发过来
                        msgToGuy += str(num) + '&'  # 把一方的发给另对方
                        if num == num2:  # 0是剪刀，1石头，2布  打平不算分
                            self.judgeGame.res[from_name] += 0
                            self.judgeGame.res[the_guys] += 0
                        elif num == 0:
                            if num2 == 1:
                                self.judgeGame.res[the_guys] += 1
                            elif num2 == 2:
                                self.judgeGame.res[from_name] += 1
                        elif num == 1:
                            if num2 == 2:
                                self.judgeGame.res[the_guys] += 1
                            elif num2 == 0:
                                self.judgeGame.res[from_name] += 1
                        elif num == 2:
                            if num2 == 0:
                                self.judgeGame.res[the_guys] += 1
                            elif num2 == 1:
                                self.judgeGame.res[from_name] += 1
                        # 判断游戏结果
                        if self.judgeGame.round == 3:
                            if self.judgeGame.res[from_name] == self.judgeGame.res[the_guys]:  # 打和
                                msgToFrom += str(0)
                                msgToGuy += str(0)
                            elif self.judgeGame.res[from_name] > self.judgeGame.res[the_guys]:
                                msgToFrom += str(1)  # 赢
                                msgToGuy += str(2)  # 输
                            else:
                                msgToFrom += str(2)  # 输
                                msgToGuy += str(1)  # 赢
                        elif self.judgeGame.round == 2 and self.judgeGame.res[from_name] == 2:  # 2:0
                            msgToFrom += str(1)  # 赢
                            msgToGuy += str(2)  # 输
                        elif self.judgeGame.round == 2 and self.judgeGame.res[the_guys] == 2:  # 2:0
                            msgToFrom += str(2)  # 输
                            msgToGuy += str(1)  # 赢
                        # if (self.judgeGame.res[from_name] == 3 and self.judgeGame.res[the_guys] == 3) \
                        #         or (self.judgeGame.res[from_name] == 2 and self.judgeGame.res[the_guys] == 2):  # 打和
                        #     msgToFrom += str(0)
                        #     msgToGuy += str(0)
                        #     self.judgeGame.reset()
                        # elif self.judgeGame.res[from_name] == 2:  # 3:2 or 2:0
                        #     msgToFrom += str(1)
                        #     msgToGuy += str(2)
                        #     self.judgeGame.reset()
                        # elif self.judgeGame.res[the_guys] == 3 or (
                        #         self.judgeGame.res[from_name] == 0 and self.judgeGame.res[the_guys] == 2) \
                        #         or (self.judgeGame.res[from_name] == 1 and self.judgeGame.res[the_guys] == 2):
                        #     msgToFrom += str(2)
                        #     msgToGuy += str(1)
                        #     self.judgeGame.reset()
                        else:  # 游戏继续
                            msgToFrom += str(-1)
                            msgToGuy += str(-1)
                        mysend(
                            to_sock, json.dumps({"action": "gameRes", "message": msgToGuy}))
                        mysend(
                            from_sock, json.dumps({"action": "gameRes", "message": msgToFrom}))
                        self.judgeGame.record = {}  # 重置
                    else:  # 用于提示另一方做选择
                        mysend(
                            to_sock, json.dumps({"action": "gameRes", "message": '6'}))

            elif msg["action"] == "chatwithbot":
                from_name = self.logged_sock2name[from_sock]
                massage = msg["message"]
                self.indices[from_name].add_msg_and_index(massage)
                to_sock = self.logged_name2sock[from_name]
                mysend(to_sock, json.dumps({"action": "chatwithbot", "from": 'chatbot', "message": liaotian.r(massage)}))


            elif msg["action"] == "disconnect":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps(
                        {"action": "disconnect", "msg": "everyone left, you are alone"}))
            # ==============================================================================
            #                 listing available peers: IMPLEMENT THIS
            # ==============================================================================
            elif msg["action"] == "list":

                # IMPLEMENTATION
                # ---- start your code ----
                # msg = self.group.list_all()
                msg = self.group.list_name()
                # ---- end of your code --- #
                mysend(from_sock, json.dumps(
                    {"action": "list", "results": msg}))
            # ==============================================================================
            #             retrieve a sonnet : IMPLEMENT THIS
            # ==============================================================================
            elif msg["action"] == "poem":

                # IMPLEMENTATION
                # ---- start your code ---- #
                from_name = self.logged_sock2name[from_sock]
                poem = '\n'.join(self.sonnet.get_poem(int(msg['target']))).strip()
                print(from_name + ' asked for ' + msg['target'] + '\n' + 'here:\n', poem)
                # ---- end of your code --- #
                mysend(from_sock, json.dumps(
                    {"action": "poem", "results": poem}))
            # ==============================================================================
            #                 time
            # ==============================================================================
            elif msg["action"] == "time":
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, json.dumps(
                    {"action": "time", "results": ctime}))
            # ==============================================================================
            #                 search: : IMPLEMENT THIS
            # ==============================================================================
            elif msg["action"] == "search":

                # IMPLEMENTATION
                # ---- start your code ---- #
                term = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                print('search for ' + from_name + ' for ' + term)
                # search_rslt = (self.indices[from_name].search(term))
                search_rslt = '\n'.join([x[-1] for x in self.indices[from_name].search(term)])
                print('server side search: ' + search_rslt)

                # ---- end of your code --- #
                mysend(from_sock, json.dumps(
                    {"action": "search", "results": search_rslt}))

        # ==============================================================================
        #                 the "from" guy really, really has had enough
        # ==============================================================================

        else:
            # client died unexpectedly
            self.logout(from_sock)

    # ==============================================================================
    # main loop, loops *forever*
    # ==============================================================================
    def run(self):
        print('starting server...')
        cha=Chatter()
        while (1):
            read, write, error = select.select(self.all_sockets, [], [])
            print('checking logged clients..')
            for logc in list(self.logged_name2sock.values()):
                if logc in read:
                    self.handle_msg(logc,cha)
            print('checking new clients..')
            for newc in self.new_clients[:]:
                if newc in read:
                    self.login(newc)
            print('checking for new connections..')
            if self.server in read:
                # new client request
                sock, address = self.server.accept()
                self.new_client(sock)


def main():
    server = Server()
    server.run()


if __name__ == '__main__':
    main()
