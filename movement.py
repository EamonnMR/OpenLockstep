import math

from ecs import System
import graphics
import commands


class MoveSystem(System):
    def __init__(self):
        self.criteria = ['pos', 'dir', 'move_goal']

    def do_step_individual(self, ent):
        angle = math.atan2(ent.move_goal[1] - ent.pos[1],
                           ent.move_goal[0] - ent.pos[0])
        ent.dir = graphics.angle_to_frame(angle)
        # FIXME: Using stock float functions is bad, we need fixed point
        # TODO: I fear sync issues
        dx = (math.cos(angle) * ent.speed)
        dy = math.sin(angle) * ent.speed
        ent.pos = (
            int(ent.pos[0] + dx),
            int(ent.pos[1] + dy)
        )

        if ent.pos[0] == ent.move_goal[0] and \
                ent.pos[1] == ent.move_goal[1]:
            commands.clear_ai(ent)

