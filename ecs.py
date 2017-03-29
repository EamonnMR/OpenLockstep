'''
Entity/Component system. See:
    Game Engine Architecture, Second Edition
    By Jason Gregory
    Page 885 

For a discussion of entity/component.

'''

import hashlib

class EntityManager:
    def __init__(self, ents=None, systems=None):
        self.ent_count = 0
        self.ents = ents
        if not self.ents:
            self.ents = {}

        self.systems = systems
        if not self.systems:
            self.systems = [] # TODO: Put removal system here?

    def do_step(self):
        for system in self.systems:
            system.step(self.ents)

        #state_str = ''
        print(self.ents)

        state_str = ''

        for ent in self.ents.values():
            state_str += str(ent)
        
        # Return an md5 of the state to ensure that all is well

        state_hash = hashlib.md5()
        state_hash.update(state_str.encode('utf-8'))
        state_hash_bin = state_hash.hexdigest()

        print(state_hash_bin)
        return state_hash_bin # hashlib.md5(state_str.encode()).hexdigest()
        

    def add_ent(self, ent):
        # TODO: Could this live in the entity constructor?
        id = self.ent_count
        ent.id = id
        self.ents[id] = ent
        self.ent_count += 1


class System:
    ''' Abstract base class for system
    To use, override the "criteria" array of components to look for (in
    your constructor) and override the do_step function to.'''
    def __init__(self):
        self.criteria = []

    def step(self, unfiltered_list):
        ''' This is called with a list of every ent, regardless of
        what components they contain. If the system needs this (or
        always affects all ents) override this. '''
        self.do_step_all([ent for ent in unfiltered_list.values()
                if all([True for comp in self.criteria if comp in ent])])

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
    work.
    
    Ensure that components all implement a to_string function,
    otherwise there will be issues because the plan is to use
    stringified components as the basis for the hashes that will
    determine if the states are locked in.

    '''



    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class DeletionSystem(System):
    def __init__(self, mgr):
        self.mgr = mgr
        self.criteria = ['del', 'id']

    def do_step_all(self, ents):
        to_delete = []

        for ent in ents:
            to_delete.append(ent.id)

        for id in to_delete:
           del mgr.ents[id] 
