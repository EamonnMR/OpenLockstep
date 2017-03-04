#!/usr/bin/python3
import socket
import argparse
import threading
import queue # Use Async io Queue?

import commands


def get_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class Step:
    '''Just a list of commands and an ID.
    '''
    def __init__(self, uid, command_list=[]):
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
    def send_step(self, step):
        # First message: Unique ID of the frame (as a string because
        # it will be a very large number. Might need to use bignum.
        self.send_bytes(str(step.uid).encode('utf-8'))

        # Second message (int): number of commands
        self.send_int(len(step.commands))

        # Remaining messages: send serialized commands
        for command in step.commands:
            self.send_bytes(command.serialize())

    def get_step(self):
        # This mirrors the sending code closely, p
        return Step(int(self.get_bytes().decode('utf-8')), [
            commands.deserialize(self.get_bytes())
            for counter in range(self.get_int())])


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

    def send_int(self, integer): # TODO: Make this a bigger int (uglier code)
        self.socket.send(bytes([integer]))

    def get_int(self):
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
        self.steps = {}

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

    def add_msg(self, step, con_id):
        # Tuple here tracks the actual step (which we build in this call)
        # and a hash that decides if every client has checked in to the server

        server_step, check_in = self.steps.setdefault(step.uid, 
                (Step(step.uid), 
                    {k: False for k, v in self.client_cons.items()}
                )
        )

        server_step.commands += step.commands

        check_in[con_id] = True

        # Kicked off here because it can only change after the above line
        if all(check_in.values()):
            print('frame finished: ' + str(step.uid))
            for id, client_con in self.client_cons.items():
                client_con.message_que.put(server_step)

        # Delete the step on the server because otherwise it'll blow up
        # the memory.

        del self.steps[step.uid]

        # TODO: Put it on a queue to write to disc, broadcast to obs, etc.


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
                self.messenger.send_step(self.message_que.get())


    def run(self):
        # start worker thread to send messages off the queue

        threading.Thread(target=self.queue_consumer).start()

        # Run loop to recieve data
        while True:
            self.parent.add_msg(self.messenger.get_step(), self.con_id)


class Client():
    def __init__(self, host, port):
        socket = get_socket()
        socket.connect((host, port))
        self.messenger = Messenger(socket)
        self.thread = Client.ClientThread(self.messenger)
        self.thread.start()

    def send(self, step):
        self.messenger.send_step(step)
    
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
                self.queue.put(self.messenger.get_step())


