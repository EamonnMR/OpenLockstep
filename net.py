import socket
import argparse
import threading
import queue # Use Async io Queue?
import math

import commands

STEP_AHEAD = 3  # Latentcy compensation
INITIAL_STEP = STEP_AHEAD
HANDSHAKE_STEP = 0
EMPTY_HASH = b"".zfill(32) # 32 zeroes

def get_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class Step:
    '''Just a list of commands and an ID.
    '''
    def __init__(self, uid, command_list, state_hash):
        self.uid = uid
        self.state_hash = state_hash
        if command_list:  # This is most definitely not the same as
            # command_list=[] in the arguments
            self.commands = command_list
        else:
            self.commands = []

    def __str__(self):
        return str(self.uid) + ": " + str(self.commands)


class Messenger:
    ''' This sends and recieves ints and byte arrays as discrete groups.
    The purpose of this is to ensure that all of the bytes are transmitted -
    for example, we need to make sure that when we send an encoded message
    we send the length and the other end can expect.
    
    This wrapper should also help if you need to rewrite everything as UDP - 
    this is where you'd implement the reliability.

    TODO: Make send and recieve ints use more bits, it'll make life easier.
    UPDATE: This is a major pain to do
    '''
    def send_step(self, step):
        # First message: Unique ID of the step (as a string because
        # it will be a very large number. Might need to use bignum.
        self.send_bytes(str(step.uid).encode('utf-8'))

        # Second message (int): number of commands
        self.send_int(len(step.commands))

        # Remaining messages: send serialized commands
        for command in step.commands:
            self.send_bytes(commands.serialize(command))
        
        # Send state hash
        self.send_bytes(step.state_hash)

    def get_step(self):
        # This mirrors the sending code closely
        return Step(
            int(self.get_bytes().decode('utf-8')), # Get step ID
            [
                commands.deserialize(self.get_bytes()) # Get count then each
                for counter in range(self.get_int())   # sent command
            ], 
            self.get_bytes()                           # get state hash
        )

    class Disconnect(Exception):
        ''' Indicates that the connection is closed '''
        pass

    def __init__(self, open_socket):
        self.socket = open_socket
        self.inbox = queue.Queue() # Will these work for async?
        self.outbox = queue.Queue()
        self.sender = Messenger.Sender(self)
        self.reciever = Messenger.Reciever(self)
        self.sender.start()
        self.reciever.start()

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

    class SubThread(threading.Thread):
        def __init__(self, parent):
            threading.Thread.__init__(self)
            self.parent = parent
            self.daemon = True # This kills child threads when main thread exits
            
    class Reciever(SubThread):
        def run(self):
            print('Run Reciever')
            while True:
                self.parent.inbox.put(self.parent.get_step())

    class Sender(SubThread):
        def run(self):
            print('Run Sender')
            while True:
                if not self.parent.outbox.empty():
                    self.parent.send_step(self.parent.outbox.get())
    
    def push_step(self, step):
        self.outbox.put(step)

    def pull_step(self):
        if not self.inbox.empty():
            return self.inbox.get()
        else:
            return None

class Server:
    def __init__(self, settings, port, listen=5, host=None,
            client_count=1, ent_manager=None, ):
        self.socket = get_socket()
        self.listen = listen
        self.socket.bind((socket.gethostname() if not host else host, port))
        self.client_count = client_count
        self.client_cons = {}
        self.steps = {}
        self.ents = ent_manager
        self.settings = settings

    def run(self):
        self.socket.listen(self.listen)
        
        # Create connection objects as connections appear
        while len(self.client_cons) < self.client_count:
            clientsock, address = self.socket.accept()
            print(address)
            con_id = len(self.client_cons)
            client_con = Messenger(clientsock)
            self.client_cons[con_id] = client_con
            print('Connected: ' + str(address) + ' id: ' + str(con_id))
        print("All " + str(self.client_count) + " clients connected. Sending Handshakes")  
        
        # Fun hack: always set up the players on opposing sides
        
        start_locations = self._get_start_locations()

        for con_id, client_con in self.client_cons.items():
            client_con.push_step(
                    Step(0, [
                        commands.Handshake(con_id, start_locations, self.settings['map'])], 
                    EMPTY_HASH)
            )

        # Tuple here tracks the actual step (which we build in this call)
        # and a hash that decides if every client has checked in to the server
        print("Starting game")
        while True:
            for con_id, con in self.client_cons.items():
                step = con.pull_step()
                if step:
                    server_step, check_in = self.steps.setdefault(step.uid, 
                        (Step(step.uid, [], None), 
                            {k: False for k, v in self.client_cons.items()}
                        )
                    )

                    server_step.commands += step.commands

                    if not server_step.state_hash:
                        server_step.state_hash = step.state_hash
                    elif server_step.state_hash != step.state_hash:
                        print("Out of sync!!!!")
                        # TODO: Raise "out of sync exception!

                    check_in[con_id] = True
                    

                    # This could be the last one - check to see if we're done
                    if all(check_in.values()):
                        for con_id, con in self.client_cons.items():
                            con.push_step(server_step)

                        # Delete the step on the server to save memory
                        
                        del self.steps[step.uid]

                        # TODO: Put it on a queue to write to disc, etc.
    def _get_start_locations(self):
        center = [self.settings['screen_size'][0] / 2, self.settings['screen_size'][1] / 2]

        angle = (math.pi * 2) / len(self.client_cons)
        radius = 200
        
        current_angle = 0

        faction = {True: 'tan_faction', False: 'purple_faction'}
        faction_toggle = True

        start_locations = {}

        for con_id in self.client_cons:
            start_locations[con_id] = {
                    'fac': faction[faction_toggle],
                    'start': [
                        (math.cos(current_angle) * radius) + center[0],
                        (math.sin(current_angle) * radius) + center[1]
                    ]
            }

            faction_toggle = not faction_toggle
            current_angle = current_angle + angle
        return start_locations



class Client():
    def __init__(self, host, port):
        socket = get_socket()
        socket.connect((host, port))
        self.messenger = Messenger(socket)
        # Fill buffer with empty initial steps
        # Becuase these will never be sent in by any client
        self.steps = {k: Step(k, [], EMPTY_HASH)
                      for k in range(INITIAL_STEP,
                                     INITIAL_STEP + 1 + STEP_AHEAD)
                     }

    def send(self, step_uid, commands, state_hash):
        self.messenger.push_step(
                Step(step_uid + STEP_AHEAD, commands, state_hash)
        )
        
    def block_until_get_step(self, uid):
        while True:
            if uid in self.steps:
                step = self.steps[uid]
                del self.steps[uid]
                return step
            else:
                step = self.messenger.pull_step()
                if step:
                    self.steps[step.uid] = step
