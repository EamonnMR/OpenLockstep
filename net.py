#!/usr/bin/python3
import socket
import argparse
import threading

def get_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class Server():
    def __init__(self, port, listen=5, host=None, client_count=1):
        self.socket = get_socket()
        self.listen = listen
        self.socket.bind((socket.gethostname() if not host else host, port))
        self.client_count = client_count
        self.client_cons = {}

    def run(self):
        self.socket.listen(self.listen)
        
        while len(self.client_cons) < self.client_count:
            (clientsock, address) = self.socket.accept()
            print(address)
            con_id = len(self.client_cons)
            client_con = ServerThread(self, clientsock, con_id)
            self.client_cons[con_id] = client_con
            client_con.start()
            print('Connected: ' + str(address) + ' id: ' + str(con_id))


class ServerThread(threading.Thread):
    def __init__(self, parent, client_socket, uid):
        threading.Thread.__init__(self)
        self.socket = client_socket
        self.parent = parent

    def run(self):

        last_data = None
        while True:
            msg_len_byte = self.socket.recv(1)
            if msg_len_byte:
                length = ord(msg_len_byte) 
                last_data = self.socket.recv(length)
                print(last_data)
                if len(last_data) != length:
                    print("Bad MSG length - Connection closed")
                    break
            else:
                print("Connection closed")
                break


class Client():
    def __init__(self, host, port):
        self.socket = get_socket()
        self.socket.connect((host, port))

    def send(self, string):
        self.socket.send(string)

