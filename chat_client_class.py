import time
import socket
import select
import sys
import json
from chat_utils import *
import client_state_machine as csm

import threading

    
class Client:
    def __init__(self, args):
        self.name = None
        self.peer = ''
        self.console_input = []
        self.state = S_OFFLINE
        self.system_msg = ''
        self.local_msg = ''
        self.peer_msg = ''
        self.args = args
        self.showGame = False #是否已经开启游戏

    def quit(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def get_name(self):
        return self.name


        #
    def init_chat(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        svr = SERVER if self.args.d == None else (self.args.d, CHAT_PORT)
        self.socket.connect(svr)
        self.sm = csm.ClientSM(self.socket)
        # reading_thread = threading.Thread(target=self.read_input)
        # reading_thread.daemon = True
        # reading_thread.start()

    def shutdown_chat(self):
        return

    def send(self, msg):
        mysend(self.socket, msg)

    def recv(self):
        return myrecv(self.socket)

    def get_msgs(self):
        read, write, error = select.select([self.socket], [], [], 0)
        my_msg = ''
        peer_msg = []
        # peer_code = M_UNDEF    for json data, peer_code is redundant
        if len(self.console_input) > 0:
            my_msg = self.console_input.pop(0)
        if self.socket in read:
            peer_msg = self.recv()
        return my_msg, peer_msg
    def get_msgs2(self):
        read, write, error = select.select([self.socket], [], [], 0)
        peer_msg = []
        # peer_code = M_UNDEF    for json data, peer_code is redundant
        if self.socket in read:
            peer_msg = self.recv()
        return peer_msg

    def output(self):
        if len(self.system_msg) > 0:
            print(self.system_msg)
            self.system_msg = ''

    def login(self):
        my_msg, peer_msg = self.get_msgs()
        if len(my_msg) > 0:
            self.name = my_msg
            msg = json.dumps({"action": "login", "name": self.name})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                self.state = S_LOGGEDIN
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(self.name)
                self.print_instructions()
                return (True)
            elif response["status"] == 'duplicate':
                self.system_msg += 'Duplicate username, try again'
                return False
        else:  # fix: dup is only one of the reasons
            return (False)

    def login2(self, name, psw):
        self.init_chat()
        my_msg, peer_msg = self.get_msgs()
        self.system_msg += 'Welcome, ' + name + '!'
        self.name = name
        msg = json.dumps({"action": "login", "name": self.name,'psw':psw})
        self.send(msg)
        response = json.loads(self.recv())
        if response["status"] == 'ok':
            self.state = S_LOGGEDIN
            self.sm.set_state(S_LOGGEDIN)
            self.sm.set_myname(self.name)
            self.print_instructions()
            return True, "success"
        elif response["status"] == 'duplicate':
            self.system_msg += 'Duplicate username, try again'
            return False, self.system_msg
        else:  # fix: dup is only one of the reasons
            return False, response["status"]

    def register(self, name, psw):
        self.init_chat()
        self.system_msg += 'Register success, ' + name + '!'
        self.name = name
        msg = json.dumps({"action": "register", "name": self.name, "psw": psw})
        self.send(msg)
        response = json.loads(self.recv())
        if response["status"] == 'ok':
            self.state = S_LOGGEDIN
            self.sm.set_state(S_LOGGEDIN)
            self.sm.set_myname(self.name)
            self.print_instructions()
            return True, "success"
        else :
            self.system_msg = response["status"]
            return False, self.system_msg

    def read_input(self):
        while True:
            text = sys.stdin.readline()[:-1]
            self.console_input.append(text)  # no need for lock, append is thread safe

    def print_instructions(self):
        self.system_msg += menu

    def run_chat(self):
        self.init_chat()
        self.system_msg += 'Welcome to ICS chat\n'
        self.system_msg += 'Please enter your name: '
        self.output()
        while self.login() != True:
            self.output()
        self.system_msg += 'Welcome, ' + self.get_name() + '!'
        self.output()
        while self.sm.get_state() != S_OFFLINE:
            self.proc()
            self.output()
            time.sleep(CHAT_WAIT)
        self.quit()

    def onLine(self):
        return self.sm.get_state() != S_OFFLINE
    def close(self):
        self.quit()
    # ==============================================================================
    # main processing loop
    # ==============================================================================
    def proc(self):
        my_msg, peer_msg = self.get_msgs()
        self.system_msg += self.sm.proc(my_msg, peer_msg)
        return self.system_msg

    def send2(self,my_msg,act=None):
        self.system_msg = ''
        self.system_msg += self.sm.proc(my_msg, '', act)
        return self.system_msg

    def clearMsg(self):
        self.system_msg = ''
    def isChatting(self):
        return self.sm.get_state()  == S_CHATTING
    def isPlaying(self):
        return self.sm.playing
    def isShowGame(self):
        return self.showGame
    def setShowGame(self,flag):
        self.showGame=flag
        self.sm.playing=flag


