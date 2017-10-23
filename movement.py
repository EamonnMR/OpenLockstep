import math
import heapq

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
    ent.pos = [
        int(ent.pos[0] + dx),
        int(ent.pos[1] + dy)
    ]

def distance(lpos, rpos):
    dx = rpos[0] - lpos[0]
    dy = rpos[1] - lpos[1]
    return math.sqrt(dx ** 2 + dy ** 2)

def basic_move(ent):
    # Moves an ent inexorably towards its move goal
    angle = get_angle(ent.move_goal, ent.pos)
    ent.dir = graphics.angle_to_frame(angle)
    
    if ent.speed >= distance(ent.pos, ent.move_goal) :
        ent.pos = list(ent.move_goal)
        commands.clear_ai(ent)
    else:
        move_ent(ent, angle, ent.speed)


class FlySystem(System):
    ''' Simple move system which just turns towards the move
    goal and goes straight towards it, ignoring any obstacles.'''
    def __init__(self):
        self.criteria = ['pos', 'dir', 'move_goal', 'movetype_fly']

    def do_step_individual(self, ent):
        basic_move(ent)


class PathFollowSystem(System):
    ''' Moves a unit along a prescribed path across the map. '''
    def __init__(self):
        self.criteria = ['pos', 'dir', 'speed', 'move_goal']
        self.pathmap = None
        self.tile_offset = None
        
    def setup_post_handshake(self, pathmap):
        self.pathmap = pathmap
        self.tile_offset = (pathmap.width / 2, pathmap.height / 2)

    def do_step_individual(self, ent):
        if 'path_complete' in ent:
            basic_move(ent)
            return

        elif 'path' not in ent:
            self.find_path(ent)
        
        if 'path' in ent:
            self.follow_path(ent)

    def find_path(self, ent):
        path = self.pathmap.get_path_from_pos(ent.pos, ent.move_goal)
        if path:
            ent.path = path
        else: # No path found
            print("no path found")
            commands.clear_ai(ent)

    def follow_path(self, ent):
        # I noticed while looking over the old Scandium_rts code that
        # there where a lot of baked in assumptions that the units would
        # always be fixed to the grid. I think that though writing it
        # without that assumption will make for less efficient code,
        # more readable code is more important to this project, and it
        # will be more useful when ultimately the assumption is broken
        # by flocking / no overlapping unit behavour
        speed_pool = ent.speed
        while speed_pool > 0:
            if len(ent.path) <= 0:
                del ent.path
                ent.path_complete = True
                return speed_pool

            next_node = ent.path[-1]
            next_node_pos = self.pathmap.get_node_pos(next_node)

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
                ent.pos = list(next_node_pos)
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
        self.tileheight = tiledmap.tileheight
        self.tilewidth = tiledmap.tilewidth
        self.diagonal = distance((0,0),(self.tilewidth, self.tileheight))
        print(self.diagonal)
 
    def get_neighbors(self, node):
        x, y = node
        if self.path_grid[y][x]:
            return set([((nx, ny), cost) for nx, ny, cost in [
                # This table represents each surrounding tile and
                # the cost associated with it.
                    (x + 1, y    , self.tilewidth),
                    (x + 1, y + 1, self.diagonal),
                    (x + 1, y - 1, self.diagonal),
                    (x    , y + 1, self.tileheight),
                    (x    , y - 1, self.tileheight),
                    (x - 1, y    , self.tilewidth),
                    (x - 1, y + 1, self.diagonal),
                    (x - 1, y - 1, self.diagonal),
                ]
                if self.on_map((nx, ny)) and self.path_grid[ny][nx]
            ])
        else:
            return set()
    
    def on_map(self, node):
        x, y = node
        return 0 <= x < self.width and 0 <= y < self.height

    def closest_node(self, pos):
        # TODO: Do better
        node = (
                int((pos[0] ) / self.tilewidth),
                int((pos[1] ) / self.tileheight)
        )
        if self.on_map(node):
            return node
        else:
            return None

    def get_node_pos(self, node):
        return (
                int((node[0] + .5) * self.tilewidth),
                int((node[1] + .5) * self.tileheight)
        )
        

    def get_path_from_pos(self, position, destination):

        # From Red Blob's tut
        first_node = self.closest_node(position)
        goal_node = self.closest_node(destination)

        return self.get_path(first_node, goal_node)

    def get_path(self, first_node, goal_node):
        # TODO: A*
        # TODO: Cache chunks
        # TODO: Find large rectangular areas and draw straight paths
        # through them as additional nodes to make it look more natural
        #frontier = []
        #heapq.heappush(frontier, (first_node, 0))
        frontier = PriorityQueue()
        frontier.put(first_node, 0)
        came_from = {first_node: None}
        cost = {first_node: 0}

        while not frontier.empty():
            #current = heapq.heappop(frontier)[0]
            current = frontier.get()
            if current == goal_node:
                return unwind_came_from(goal_node, came_from)
            for next, next_additional_cost in self.get_neighbors(current):
                total_next_cost = cost[current] + next_additional_cost 
                if next not in cost or cost[next] > total_next_cost:
                    #heapq.heappush(frontier, (next, total_next_cost))
                    frontier.put(next, total_next_cost)
                    came_from[next] = current
                    cost[next] = total_next_cost
        return None # No path exists


def unwind_came_from(final_node, came_from):
    current = final_node
    path = []
    while current:
        path.append(current)
        current = came_from[current]
    return path


# Redblob's wrapper around heapq
class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def empty(self):
        return len(self.elements) == 0
    
    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self):
        return heapq.heappop(self.elements)[1]

