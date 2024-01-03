from chat_utils import *
import json

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.playing = False

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg, act=None):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:
                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    # self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg = ''
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p':
                    num = my_msg[1:].strip()
                    if num.isdigit():
                        poem_idx = my_msg[1:].strip()
                        mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                        poem = json.loads(myrecv(self.s))["results"]
                        if (len(poem) > 0):
                            self.out_msg += poem + '\n\n'
                        else:
                            self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'

                elif act == 'chatwithbot':

                    if len(my_msg) > 0:
                        print('hh')
                        mysend(self.s,
                               json.dumps({"action": "chatwithbot", "from": "[" + self.me + "]", "message": my_msg}))
                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                try:
                    peer_msg = json.loads(peer_msg)
                except Exception as err :
                    self.out_msg += " json.loads failed " + str(err)
                    return self.out_msg
            
                if peer_msg["action"] == "connect":

                    # ----------your code here------#
                    try:
                        self.peer = peer_msg["from"]
                        self.out_msg += 'You are connected with ' + self.peer + '\n' + '. Chat away!\n\n'
                    except Exception as err:
                        self.out_msg += ' Chat away!\n\n'
                    self.state = S_CHATTING
                elif peer_msg["action"] == "chatwithbot":
                    print(peer_msg['from'], peer_msg['message'])
                    self.out_msg += peer_msg['from'] + ': ' + peer_msg['message']
                    if self.state == S_LOGGEDIN:
                        self.out_msg += menu
                    # ----------end of your code----#
                    
#===========================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif act == 'recordPlay':
            mysend(self.s, json.dumps({"action": "recordPlay", "message": my_msg}))
        elif act == 'requestGame':  # 请求对方玩游戏
            mysend(self.s, json.dumps({"action": "requestGame", "message": my_msg}))

        elif len(peer_msg)>0 and json.loads(peer_msg)['action'] == 'gameRes': # 玩游戏时服务器传过来的消息
            peer_msg = json.loads(peer_msg)
            self.out_msg = '*' # 作为标记 ，正在玩游戏
            self.out_msg += peer_msg['message']
            print('out_msg',self.out_msg)
        elif len(peer_msg)>0 and json.loads(peer_msg)['action'] == 'requestGame':
            self.out_msg = '#'  # 作为标记，游戏没有启动则启动游戏
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                # if self.playing: # play game
                #     mysend(self.s, json.dumps({"action": "play", "message": my_msg}))
                # else:
                if act == 'chatwithbot':
                    if len(my_msg) > 0:
                        print('hh')
                        mysend(self.s,
                               json.dumps({"action": "chatwithbot", "from": "[" + self.me + "]", "message": my_msg}))
                else:
                    mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                    if my_msg == 'bye':
                        self.disconnect()
                        self.state = S_LOGGEDIN
                        self.peer = ''
            if len(peer_msg) > 0:    # peer's stuff, coming in
                # ----------your code here------#
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "chatwithbot":
                    print(peer_msg['from'], peer_msg['message'])
                    self.out_msg += peer_msg['from'] + ': ' + peer_msg['message']
                else:
                    if peer_msg["action"] == "connect":
                        self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                    elif peer_msg["action"] == "disconnect":
                        self.state = S_LOGGEDIN
                    elif peer_msg["action"]=="exchange":
                        print(peer_msg['from'], peer_msg['message'])
                        self.out_msg +=peer_msg['from']+peer_msg['message']
                    elif peer_msg['action'] == "play":
                        self.playing = True  # 开启游戏
                        self.out_msg = ''
                        self.out_msg += peer_msg['message']
                # else:
                #     self.out_msg += peer_msg["from"] + peer_msg["message"]

                # ----------end of your code----#

            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu

#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
