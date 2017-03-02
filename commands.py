import json



def deserialize(data):
    return Ping.deserialize(data)


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

    net_members = ['step']

    def __init__(self, step=None):
        self.step = step

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
    net_members = ['position', 'step']
    
    def __init__(self, step=None, position=[0,0]):
        self.position = position
        self.step = step

