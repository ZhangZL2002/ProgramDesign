import socket
import sys
import threading
from threading import Thread

BS = 2022

class Chatter:
    def __init__(self, conn):
        self.socket = conn

    def send(self):
        username = input('用户名：')
        self.socket.send(username.encode('utf-8'))
        log.write('\n##### 用户 %s 聊天记录#####\n'%username)
        while not exit_event.is_set():
            message = input('')
            log.write(message+'\n')
            self.socket.send(message.encode('utf-8'))
            if message == '再见！':
                exit_event.set()


    def recv(self):

        while not exit_event.is_set():
            message = self.socket.recv(BS).decode('utf-8')
            print(message)
            log.write(message+'\n')


def main():
    if len(sys.argv) != 3:
        print('usage: python my_client.py ip port')
    else:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((ip, port))
            chat1 = Chatter(client)
            chat2 = Chatter(client)

            send_thread = Thread(target=chat1.send, args=())
            recv_thread = Thread(target=chat2.recv, args=())
            send_thread.start()
            recv_thread.start()
            send_thread.join()
            recv_thread.join()
        finally:
            print("连接已被关闭")
            client.close()
if __name__ == '__main__':
    log = open('client_log.txt', 'a')
    exit_event = threading.Event()
    main()
    log.close()