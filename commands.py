import json


class UnknownCommand(Exception):
    ''' Indicates that a command type or ID cannot be mapped '''
    pass

def deserialize(data):
    if data:
        command_type = data[0]
        if command_type in INDEX_TO_COMMAND:
            return INDEX_TO_COMMAND[command_type].deserialize(data[1:])
        else:
            raise UnknownCommand()
    else:
        return None

def serialize(command):
   return COMMAND_TO_INDEX[type(command).__name__] + command.serialize()

def get_mapped(command_str):
    return STR_COMMANDS[command_str]

class Command:
    ''' Command: An instruction for units to be sent over the network

    The default serialization methods encode and decode everything inside
    net_members into a json string. If you end up with a bottleneck here,
    you can override serialize and deserialize in your classes and send the
    data in whatever custom binary format you desire. In that case, you can
    ignore net_members.
    
    If you're going to use the default deserialize command, you need to
    ensure that your constructor works when called with no arguments - just
    make all of the arguments optional.
    '''

    net_members = []

    def serialize(self):
        cls = type(self)
        return json.dumps(
            {k: self.__dict__[k] for k in cls.net_members}
        ).encode('utf-8')
    
    @classmethod
    def deserialize(cls, byte_string):
        new_instance = cls()
        new_instance.__dict__.update(
            {k:  v for k, v in json.loads(
                byte_string.decode('utf-8')).items()
                if k in cls.net_members})
        return new_instance


class Ping(Command):
    net_members = ['position']
    
    def __init__(self, position=[0,0]):
        self.position = position

class Handshake(Command):
    net_members = ['start_building', 'your_id']

    def __init__(self, start_building=[0,0], your_id=0):
        self.start_building = start_building
        self.your_id = your_id

class Move(Command):
    net_members = ['ids', 'to']

    def __init__(self, ids=[], to=[0,0]):
        self.ids = ids
        self.to = to

class Make(Command):
    net_members = ['ids', 'type']

    def __init__(self, ids=[], type=''):
        self.ids = ids
        self.type = type

class Stop(Command):
    net_members = ['ids']

    def __init__(self, ids=[]):
        self.ids = ids

STR_COMMANDS = {
    'make': Make,
    'move': Move,
    'stop': Stop,
}

INDEX_TO_COMMAND = {
    1: Ping,
    2: Handshake,
    3: Move,
    4: Make,
    5: Stop
}

COMMAND_TO_INDEX = dict((item[1].__name__, bytes([item[0]])) for item in INDEX_TO_COMMAND.items())
