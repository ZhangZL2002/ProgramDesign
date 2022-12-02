# 2022/11/30
import socket
import time
from threading import Thread
import sys

BS = 2022
usernames = {}
clients = {}


def get_time():
    return str(time.strftime("%Y-%m-%d %H:%M:%S"))


class Manager:
    def __init__(self, conn, addr, username=''):  # 实质是建立了一个客户端对象，addr从accept中获取
        self.socket = conn
        self.ip = addr[0]
        self.port = addr[1]
        self.identify = '{}-{}'.format(self.ip, self.port)
        self.username = username

    def _recv(self, conn):  # 接收消息
        while True:
            data = conn.recv(BS).decode("utf-8")
            if not data or data == '再见！':
                break
            else:
                return data

    def _broadcast(self, message, sender):  # 发送广播
        for identify in clients.keys():
            if sender != usernames[identify]:
                clients[identify].socket.send(('%s %s:%s' % (get_time(), sender, message)).encode("utf-8"))

    def _private_chat(self, message, sender, receiver):  # 发送私信
        for identify in clients.keys():
            if usernames[identify] == receiver:
                clients[identify].socket.send(('%s %s[私信]:%s' % (get_time(), sender, message)).encode("utf-8"))
                break

    def chat(self):  # 与客户端交互：收发消息
        log = open('server_log.txt', 'a')
        log.write('\n#### 服务器数据 ####\n')
        print('{}尝试连接'.format(self.identify))
        log.write('{}尝试连接\n'.format(self.identify))
        name = self._recv(self.socket)
        if not name:
            return
        self.username = name
        clients[self.identify] = self  # 客户列表中加入客户 { identify:client }
        usernames[self.identify] = self.username
        # 处理连接成功信息
        print('用户 %s 已连接！' % self.username)
        log.write('用户 %s 已连接！\n' % self.username)
        self.socket.send("您已连接".encode("utf-8"))
        user_connect_message = ('我已进入聊天室')
        self._broadcast(user_connect_message, self.username)
        # 开始聊天
        while True:
            message = self._recv(self.socket)
            if not message:
                break
            elif message.split(' ')[0] == '@':  # 私信
                receiver = message.split(' ')[1]
                self._private_chat(message, self.username, receiver)
                print("%s (%s) %s private chat with %s: %s" %
                      (get_time(), self.identify, self.username, receiver, message))
                log.write("%s (%s) %s private chat with %s: %s\n" %
                          (get_time(), self.identify, self.username, receiver, message))
            else:  # 广播
                print("%s (%s) %s: %s" % (get_time(), self.identify, self.username, message))
                log.write("%s (%s) %s: %s\n" % (get_time(), self.identify, self.username, message))
                self._broadcast(message, self.username)
        # 断开连接：信息发送、用户删除、连接终止
        print("%s(%s) 断开连接" % (self.ip, self.port))
        log.write("%s(%s) 断开连接\n" % (self.ip, self.port))
        user_exit_message = ('再见！\n%s已退出聊天室' % self.username)
        self._broadcast(user_exit_message, self.username)
        clients.pop(self.identify)
        usernames.pop(self.identify)
        log.close()
        self.socket.close()


def main():
    if len(sys.argv) != 3:
        print('usage: python my_server.py ip port')
    else:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((ip, port))  # 设置绑定监听的ip和port
        server.listen(10)
        print("服务器已开启，正在监听{}".format(server.getsockname()))

        while True:
            conn, addr = server.accept()  # 接受客户端连接，获取其地址
            client = Manager(conn, addr)  # 创建客户
            t = Thread(target=client.chat, args=())
            t.start()


if __name__ == '__main__':
    main()
