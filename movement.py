import math

from ecs import System
import graphics


class MoveSystem(System):
    def __init__(self):
        self.criteria = ['pos', 'dir', 'move_goal']

    def do_step_individual(self, ent):
        speed = 3
        angle = math.atan2(ent.move_goal[1] - ent.pos[1],
                           ent.move_goal[0] - ent.pos[0])
        ent.dir = graphics.angle_to_frame(angle)
        # FIXME: Using stock float functions is bad, we need fixed point
        dx = (math.cos(angle) * speed)
        dy = math.sin(angle) * speed
        ent.pos = (
            int(ent.pos[0] + dx),
            int(ent.pos[1] + dy)
        )

