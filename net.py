#!/usr/bin/python3
import socket
import argparse
import threading
import queue # Use Async io Queue?

import commands


def get_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class Step:
    def __init__(self, uid, command_list):
        self.uid = uid
        self.commands = command_list


class Messenger:
    ''' This sends and recieves ints and byte arrays as discrete groups.
    The purpose of this is to ensure that all of the bytes are transmitted -
    for example, we need to make sure that when we send an encoded message
    we send the length and the other end can expect.
    
    This wrapper should also help if you need to rewrite everything as UDP - 
    this is where you'd implement the reliability.

    TODO: Make send and recieve ints use more bits, it'll make life easier.
    '''

    class Disconnect(Exception):
        ''' Indicates that the connection is closed '''
        pass

    def __init__(self, open_socket):
        print(self)
        print(open_socket)
        self.socket = open_socket

    def send_bytes(self, msg):
        self.send_int(len(msg))
        self.socket.send(msg)

    def send_int(self, integer):
        self.socket.send(bytes([integer]))

    def get_int(self):
        print(self.socket)
        byte = self.socket.recv(1)
        if byte:
            return ord(byte)
        else:
            raise Messenger.Disconnect()


    def get_bytes(self):
        length = self.get_int()
        if length:
             msg = self.socket.recv(length)
             if len(msg) != length:
                 raise Messenger.Disconnect()
             else:
                 return msg
        else:
            return b''


class Server:
    def __init__(self, port, listen=5, host=None, client_count=1):
        self.socket = get_socket()
        self.listen = listen
        self.socket.bind((socket.gethostname() if not host else host, port))
        self.client_count = client_count
        self.client_cons = {}
        self.frames = {}

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

    def add_msg(self, message, con_id):
        print('send')
        print(message, con_id) 
        self.frames.setdefault(message.step, {})[con_id] = message

        if self.frames[message.step].keys() == self.client_cons.keys():
            print('frame finished')
            print(self.frames[message.step])
            for id, client_con in self.client_cons.items():
                for send_message in self.frames[message.step].values():
                    sent_nothing = True
                    if send_message is not None:
                        sent_nothing = False
                        print('Sending ', send_message)
                        client_con.message_que.put(send_message)


class ServerThread(threading.Thread):
    def __init__(self, parent, client_socket, con_id):
        threading.Thread.__init__(self)
        self.messenger = Messenger(client_socket)
        self.parent = parent
        self.message_que = queue.Queue()
        self.con_id = con_id

    def queue_consumer(self):
        print('started queue consumer')
        while True:
            if not self.message_que.empty():
                print('Sending message')
                msg =  self.message_que.get().serialize()
                print(msg)
                self.messenger.send_bytes(msg)


    def run(self):
        # start worker thread to send messages off the queue

        threading.Thread(target=self.queue_consumer).start()

        # Run loop to recieve data
        last_data = None
        while True:
            print('in server loop')
            self.parent.add_msg(
                    commands.deserialize(self.messenger.get_bytes()),
                    self.con_id)


class Client():
    def __init__(self, host, port):
        socket = get_socket()
        socket.connect((host, port))
        self.messenger = Messenger(socket)
        self.thread = Client.ClientThread(self.messenger)
        self.thread.start()

    def send(self, msg):
        print('client.send')
        self.messenger.send_bytes(msg)
    
    def recieve(self):
        if self.thread.queue.empty():
            return None
        else:
            return self.thread.queue.get()

    class ClientThread(threading.Thread):
        def __init__(self, messenger):
            threading.Thread.__init__(self)
            self.queue = queue.Queue()
            self.messenger = messenger

        def run(self):
            print('running client thread')
            while True:    
                print('cli pre rcv')
                msg = self.messenger.get_bytes()
                print('cli post rcv')
                if msg:
                    print('got message with length')
                    self.queue.put(msg)


