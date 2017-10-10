import math

from ecs import System, DrawSystem
import graphics
import commands


def get_angle(goal, pos):
    return math.atan2(goal[1] - pos[1], goal[0] - pos[0])

def move_ent(ent, angle, distance):
    # FIXME: Using stock float functions is bad, we need fixed point
    # TODO: I fear sync issues
    dx = math.cos(angle) * ent.speed
    dy = math.sin(angle) * ent.speed
    ent.pos = (
        int(ent.pos[0] + dx),
        int(ent.pos[1] + dy)
    )

def distance(lpos, rpos):
    dx = rpos[0] - lpos[0]
    dy = rpos[1] - lpos[1]
    return math.sqrt(dx ** 2 + dy ** 2)

class FlySystem(System):
    ''' Simple move system which just turns towards the move
    goal and goes straight towards it, ignoring any obstacles.'''
    def __init__(self):
        self.criteria = ['pos', 'dir', 'move_goal', 'movetype_fly']

    def do_step_individual(self, ent):
        angle = get_angle(goal, pos)
        ent.dir = graphics.angle_to_frame(angle)
        
        move_ent(ent, angle, ent.speed)

        if -2 < (ent.pos[0] - ent.move_goal[0]) < 2 and \
           -2 < (ent.pos[1] - ent.move_goal[1]) < 2:
            commands.clear_ai(ent)

class PathFollowSystem(System):
    ''' Moves a unit along a prescribed path across the map. '''
    def __init__(self):
        self.criteria = ['pos', 'dir', 'path', 'speed']
        self.pathmap = None
        self.tile_offset = None
        
    def setup_post_handshake(self, pathmap):
        self.pathmap = pathmap
        self.tile_offset = (pathmap.width / 2, pathmap.height / 2)

    def do_step_individual(self, ent):
        # I noticed while looking over the old Scandium_rts code that
        # there where a lot of baked in assumptions that the units would
        # always be fixed to the grid. I think that though writing it
        # without that assumption will make for less efficient code,
        # more readable code is more important to this project, and it
        # will be more useful when ultimately the assumption is broken
        # by flocking / no overlapping unit behavour
        print("Pathing: ")
        print(ent)
        speed_pool = ent.speed
        while speed_pool > 0 and ent.path:

            next_node = ent.path[-1]
            next_node_pos = (
                (next_node[0] * self.pathmap.width) + self.tile_offset[0],
                (next_node[1] * self.pathmap.height) + self.tile_offset[1]
            )

            dist = distance(ent.pos, next_node_pos)
            angle = get_angle(next_node_pos, ent.pos)
            ent.dir = graphics.angle_to_frame(angle)
            
            if dist > speed_pool:
                # We're not going to reach the node this step - go closer
                move_ent(ent, angle, speed_pool)
                break;
            else:
                # Enough speed is left to reach the next node.
                # Subtract out the speed needed to travel the
                # distance to the next node, and loop.
                ent.pos = next_node_pos
                ent.path.pop()
                # TODO: Possible source of sync issues right here
                speed_pool -= dist
                continue
        
        

class PathabilityDrawSystem(DrawSystem):
    ''' A debugging tool to show what the pathing system
    sees on a map. Useful for making maps as well as debugging
    the pathing system. '''
    def __init__(self, pathmap, tile_height, tile_width, sprite, screen):
        self.pathing_data = pathmap.path_grid 
        self.tile_height = tile_height
        self.tile_width = tile_width
        self.tile_offset = (tile_width / 2, tile_height / 2)
        self.sprite = sprite
        self.screen = screen

    def draw(self, unfiltered_list, offset):
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


def is_pathable(tiled_map, x, y):
    ''' Gets the pathability status of a given tile based on
    magic strings. '''
    gid = tiled_map.get_tile_gid(x, y, 0)
    if gid in tiled_map.tile_properties:
        props = tiled_map.tile_properties[gid]
        return 'p' in props and props['p'] == 't'
    else:
        return False

class Pathmap:
    ''' Creates a pathfinding map from a tiled map.
    Tiled related cruft could probably be pulled down into a subclass
    '''
    def __init__(self, tiledmap):
        self.width = tiledmap.width
        self.height = tiledmap.height
        self.path_grid = [
                [ is_pathable(tiledmap, i, j)
                    for i in range(tiledmap.width)]
                for j in range(tiledmap.height)

        ]

            
    def get_neighbors(x, y):
        if self.path_grid[y][x]:
            return set([(nx, ny) for nx, ny in [
                    # TODO: Add costs; diagonal is 2(sqrt(2)) iirc
                    (x + 1, y, 1),
                    # (x + 1, y + 1),
                    # (x + 1, y - 1),
                    (x, y + 1),
                    (x, y - 1),
                    (x - 1, y),
                    #(x - 1, y + 1),
                    #(x - 1, y - 1),
                ] if 0 >= nx >= self.width and 
                0 >= ny >= self.height and
                self.path_grid[ny][nx]
            ])
        else:
            return set()


