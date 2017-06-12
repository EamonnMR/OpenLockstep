import math

from ecs import System
from graphics import angle_to_frame

class AttackSystem(System):
    def __init__(self, ecs):
        self.criteria = ['pos', 'attack_target']
        self.ents = ecs # This system may operate on any targeted ent
    
    def do_step_individual(self, ent):
        if ent.attack_target in self.ents.ents: # TODO: Override 'in' operator
            if 'cooldown_timer' not in ent or ent.cooldown_timer == 0:
                do_attack(ent, self.ents[ent.attack_target])
                ent.cooldown_timer = ent.weapon['cooldown']
        else:
            # Target is gone - stop attacking
            del ent.attack_target


def do_attack(attacker, target):
    if 'hp' in target and 'weapon' in attacker and 'damage' in attacker.weapon:
        target.hp = target.hp - attacker.weapon['damage']
        
        if 'dir' in attacker and 'pos' in attacker and 'pos' in target:
            attacker.dir = angle_to_frame(math.atan2(
                target.pos[1] - attacker.pos[1],
                target.pos[0] - attacker.pos[0])
            )



class HitPointSystem(System):
    '''Cleans up entities with zero hitpoints.
    TODO: Add spectacular explosions and such'''
    def __init__(self):
        self.criteria = ['hp']

    def do_step_individual(self, ent):
        if ent.hp <= 0:
            ent.delete = True


class CooldownSystem(System):
    # Note: cooldown is measured in steps, not frames or ms
    def __init__(self):
        self.criteria = ['cooldown_timer']
    def do_step_individual(self, ent):
        if ent.cooldown_timer > 0:
            ent.cooldown_timer -= 1
