class EntityManager:
    def __init__(self, ents=None, systems=None):
        self.ent_count = 0
        self.ents = ents
        if not self.ents:
            self.ents = []

        self.systems = systems
        if not self.systems:
            self.systems = [] # TODO: Put removal system here?

    def do_step(self):
        for system in self.systems:
            system.step(self.ents)


    def add_ent(self, ent):
        # TODO: Could this live in the entity constructor?
        id = self.ent_count
        ent.id = id
        self.ents[id] = ent


class System:
    ''' Abstract base class for system
    To use, override the "criteria" array of components to look for,
    and override the do_step function to implement the system.'''

    criteria = []

    def step(self, unfiltered_list):
        ''' This is called with a list of every ent, regardless of
        what components they contain. If the system needs this (or
        always affects all ents) override this. '''
        self.do_step_all(for ent in unfiltered_list
                if all( (comp in ent) for comp in criteria)])

    def do_step_all(self, ents):
        ''' This is called with a list of ents that matches the
        criteria. Override it for systems where ents affect each
        other, like gravity or magnetism '''
        for ent in ents:
            self.do_step_individual(ent)

    def do_step_individual(self, ent):
        '''By default this is called for every ent that meets the
        criteria. Use this for systems where every ent moves
        independantly, such as velocity.'''
        pass


class Entity(dict):

    ''' Credit due to this stack overflow question:
    http://stackoverflow.com/a/23689767/1048464
    Essentially an entity is just a dict. What this class
    gives us is a type and .notation access to members
    (so you can write code that uses entities in a pythonic
    way and not care about what members it does or does not
    have.

    Note that beecause this is a dict, you can just pass
    a dict of the components you'd like in and it'll just
    work.'''


    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class DeletionSystem(System):
    def __init__(self, mgr):
        self.mgr = mgr

    criteria = ['del', 'id']

    def do_step_all(self, ents):
        to_delete = []

        for ent in ents:
            to_delete.append(ent.id)

        for id in to_delete:
           del mgr.ents[id] 
