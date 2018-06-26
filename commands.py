import ujson


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

    Execute defines how the game state is affected by the Command. Be careful
    when using anything else to influence the gamestate (for example, see how
    Handshake is used)
    '''

    net_members = []
    
    def execute(self, ecs, data):
        pass

    def serialize(self):
        cls = type(self)
        return ujson.dumps(
            {k: self.__dict__[k] for k in cls.net_members}
        ).encode('utf-8')
    
    @classmethod
    def deserialize(cls, byte_string):
        new_instance = cls()
        new_instance.__dict__.update(
            {k:  v for k, v in ujson.loads(
                byte_string.decode('utf-8')).items()
                if k in cls.net_members})
        return new_instance


class Ping(Command):
    net_members = ['position']
    
    def __init__(self, position=[0,0]):
        self.position = position

class Handshake(Command):
    net_members = ['startlocs', 'your_id', 'map']

    def __init__(self, your_id=0, startlocs={}, map=''):
        self.startlocs = startlocs
        self.your_id = your_id
        self.map = map


class Move(Command):
    net_members = ['ids', 'to']

    def __init__(self, ids=[], to=[0,0]):
        self.ids = ids
        self.to = to

    def execute(self, ecs, data):
        for id in self.ids:
            clear_ai(ecs[id])
            ecs[id].move_goal = self.to


class Attack(Move):
    net_members = ['ids', 'at']

    def __init__(self, ids=[], at=None):
        self.ids = ids
        self.at = at

    def execute(self, ecs, data):
        for id in self.ids:
            clear_ai(ecs[id])
            ecs[id].attack_target = self.at


class AttackMove(Move):
    pass


class Make(Command):
    net_members = ['ids', 'type']

    def __init__(self, ids=[], type=''):
        self.ids = ids
        self.type = type

    def execute(self, ecs, data):
      for id in self.ids:
          spawner = ecs[id]
          ecs.add_ent(
                  data.spawn(utype=self.type,
                  # TODO: Reasonable start locations (how?)
                  pos=[spawner.pos[0], spawner.pos[1] + 10],
                  dir=0,
                  owner=spawner.owner,
              )
          )


class Stop(Command):
    net_members = ['ids']

    def __init__(self, ids=[]):
        self.ids = ids

    def execute(self, ecs, data):
        for unit in [ecs[id] for id in self.ids]:
            clear_ai(unit)

def clear_ai(ent):
    ''' Removes AI state from an entity. If this isn't
    working, it's possible that someone has added new
    AI components and not added them to this list!'''
    active_members = [
            'move_goal',
            'attack_target',
            'path',
            'path_complete',
    ]
    for member in active_members:
        if member in ent:
            del ent[member]
# Corresponds to commands in unit descriptions
# TODO:  Obviate this with some sort of reflection
# scheme?
STR_COMMANDS = {
    'make': Make,
    'move': Move,
    'stop': Stop,
    'attack': Attack,
    'attackmove': AttackMove,
}

# What index this command is encoded as over the net.
# TODO: Would it be possible to assign these automatically?
INDEX_TO_COMMAND = {
    1: Ping,
    2: Handshake,
    3: Move,
    4: Make,
    5: Stop,
    6: Attack,
    7: AttackMove,
}

# An inverted list dict, so if 1: Ping, "Ping": 1
# Thanks stackoverflow
COMMAND_TO_INDEX = dict((item[1].__name__, bytes([item[0]])) for item in INDEX_TO_COMMAND.items())
