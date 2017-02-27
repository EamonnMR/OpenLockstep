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
            ServerThread(clientsock).start()


class ServerThread(threading.Thread):
    def __init__(self, client_socket):
        threading.Thread.__init__(self)
        self.socket = client_socket

    def run(self):
        last_data = None
        while last_data != b'':
            last_data = self.socket.recv(1)
            length = ord(last_data) 
            last_data = self.socket.recv(length)
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
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--host', type=str, default='localhost')

    args = parser.parse_args()
    if args.client:
        client = Client(args.host, args.port)
        while True:
            text = input("> ")[:255]
            client.send(bytes([len(text)]))
            client.send(text.encode('utf-8'))
    elif args.server:
        Server(args.port, host=args.host).run()
        
