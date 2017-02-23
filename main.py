#!/usr/bin/python3

import argparse
import threading
import socket

def get_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class Server():
    def __init__(self, port, listen=5, host=None):
        self.socket = get_socket()
        self.listen = listen
        self.socket.bind((socket.gethostname() if not host else host, port))

    def run(self):
        self.socket.listen(self.listen)
        
        while True:
            (clientsock, address) = self.socket.accept()
            print(address)
            ServerThread(clientsock).run()


class ServerThread(threading.Thread):
    def __init__(self, client_socket):
        self.socket = client_socket

    def run(self):
        last_data = None
        while last_data != b'':
            last_data = self.socket.recv(1)
            print(last_data)

class Client():
    def __init__(self, host, port):
        self.socket = get_socket()
        self.socket.connect((host, port))

    def send(self, string):
        self.socket.send(string)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs OpenLockstep')
    parser.add_argument('--server', action='store_true')
    parser.add_argument('--client', action='store_true')
    args = parser.parse_args()
    port = 8000
    host = 'localhost'
    if args.client:
        client = Client(host, port)
        while True:
            text = input("> ")
            client.send(text.encode('utf-8'))
    elif args.server:
        Server(port, host=host).run()
        
