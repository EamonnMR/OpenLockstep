import math

from ecs import System, DrawSystem
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

        if -2 < (ent.pos[0] - ent.move_goal[0]) < 2 and \
           -2 < (ent.pos[1] - ent.move_goal[1]) < 2:
            commands.clear_ai(ent)

class PathabilityDrawSystem(DrawSystem):
    def __init__(self, pathing_data, tile_height, tile_width, sprite, screen):
        self.pathing_data = pathing_data
        self.tile_height = tile_height
        self.tile_width = tile_width
        self.tile_offset = (tile_width / 2, tile_height / 2)
        self.sprite = sprite
        self.screen = screen

    def draw(self, untiltered_list, offset):
        x = 0
        y = 0
        for row in self.pathing_data:
            for column in row:
                self.sprite.draw(x + self.tile_offset[0] - offset[0],
                                 y + self.tile_offset[1] - offset[1],
                                 0 if column else 1, self.screen)
                x += self.tile_width

            y += self.tile_height
            x = 0

