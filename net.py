#!/usr/bin/python3
import socket
import argparse
import threading
import queue # Use Async io Queue?

def send_with_length(socket, msg):
    socket.send(bytes([len(msg)]))
    socket.send(msg)

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
        
        # Create connection objects as connections appear
        while len(self.client_cons) < self.client_count:
            (clientsock, address) = self.socket.accept()
            print(address)
            con_id = len(self.client_cons)
            client_con = ServerThread(self, clientsock, con_id)
            self.client_cons[con_id] = client_con
            client_con.start()
            print('Connected: ' + str(address) + ' id: ' + str(con_id))

    def send(self, message):
        print('send')
        for id, client_con in self.client_cons.items():
            client_con.message_que.put(message)


class ServerThread(threading.Thread):
    def __init__(self, parent, client_socket, uid):
        threading.Thread.__init__(self)
        self.socket = client_socket
        self.parent = parent
        self.message_que = queue.Queue()

    def queue_consumer(self):
        print('started queue consumer')
        while True:
            if not self.message_que.empty():
                print('Sending message')
                send_with_length(self.socket, self.message_que.get())


    def run(self):
        # start worker thread to send messages off the queue

        threading.Thread(target=self.queue_consumer).start()

        # Run loop to recieve data
        last_data = None
        while True:
            print('in server loop')
            msg_len_byte = self.socket.recv(1)
            if msg_len_byte:
                length = ord(msg_len_byte) 
                last_data = self.socket.recv(length)
                print(last_data)
                self.parent.send(last_data)
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
        self.thread = Client.ClientThread(self.socket)
        self.thread.start()

    def send(self, bytestr):
        print('client.send')
        send_with_length(self.socket, bytestr)

    def recieve(self):
        if self.thread.queue.empty():
            return None
        else:
            return self.thread.queue.get()

    class ClientThread(threading.Thread):
        def __init__(self, socket):
            threading.Thread.__init__(self)
            self.queue = queue.Queue()
            self.socket = socket

        def run(self):
            print('running client thread')
            while True:    
                print('cli pre rcv')
                msg_len_byte = self.socket.recv(1)
                print('cli post rcv')
                if msg_len_byte:
                    print('got message with length')
                    length = ord(msg_len_byte)
                    self.queue.put(self.socket.recv(length))


