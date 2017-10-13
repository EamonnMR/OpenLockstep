import math

import pygame

import ecs
import commands
import util 

SCROLL_SPEED = 10
SCROLL_MARGIN = 15
class GUI:
    def __init__(self, ecs, mouse_spr, screen, data, player_id, parent, max_scroll):
        self.mouse_spr = mouse_spr
        self.mouse = NormalMouse(mouse_spr, self)
        self.screen = screen
        self.selected_units = []
        self.ecs = ecs
        self.buttons = []
        self.active_hotkeys = {}
        self.data = data
        self.player_id = player_id
        self.parent = parent # TODO: Clean up abstraction
        # Scrolling stuff:

        self.global_keys = [pygame.K_DOWN, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT]
        self.left, self.right, self.up, self.down = (False, False, False, False)
        self.max_scroll = (1400, 1530)

    def update_selection(self, new_selection):
        self.selected_units = new_selection
        units = self.get_units()
        if len(self.selected_units) and all(
                [unit.owner == self.player_id for unit in units]):
        
            orders = [self.data['orders'][order] for order in 
                    set.intersection(
                        *[set(unit.orders) for unit in self.get_units()]
                    )
            ]

            self.active_hotkeys = {order['key']: order for order in orders}

            # TODO: Also populate buttons
        else:
            self.active_hotkeys = {}

    def get_units(self):
        return [self.ecs[id] for id in self.selected_units]

    def handle_event(self, event):
        ''' Returns commands if any, new offset'''
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                return self.mouse.left_up()
            elif event.button == 3:
                return self.mouse.right_up()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                return self.mouse.left_down()
            elif event.button == 3:
                return self.mouse.right_down()
            else:
                return None

        elif event.type == pygame.KEYUP:
            return self.global_key_up(event.key)

        elif event.type == pygame.KEYDOWN:
            if event.key in self.global_keys:
                return self.global_key_down(event.key)
            else:
                hotkey = chr(event.key)
                if hotkey in self.active_hotkeys:
                    order = self.active_hotkeys[hotkey]
                    if "selector" in order:
                        self.mouse = SELECTORS[order['selector']](
                                self.mouse_spr, self, order)
                        return None
                    else:
                        return commands.get_mapped(order['cmd'])(
                                ids=self.selected_units,
                                **(order['args'] if 'args' in order else {})
                        )
                else:
                    return None
        else:
            return None

    def draw(self):
        # TODO: Draw gui stuff here
        self.mouse.draw()

    def get_mouse_world_pos(self):
        ''' Get the world-space coordinates for the mouse's current position '''
        screen_pos = pygame.mouse.get_pos()
        return screen_pos[0] + self.parent.offset[0], screen_pos[1] + self.parent.offset[1]

    def get_screen_pos(self, pos):
        ''' Transform a worldspace coordinate into a screen space coordinate '''
        return self.pos[0] - self.parent.offset[0], self.pos[1] - self.parent.offset[1]

    def global_key_down(self, key):
        if key == pygame.K_DOWN:
            self.down = True
        elif key == pygame.K_UP:
            self.up = True
        elif key == pygame.K_LEFT:
            self.left = True
        elif key == pygame.K_RIGHT:
            self.right = True

        return None

    def global_key_up(self, key):
        if key == pygame.K_DOWN:
            self.down = False
        elif key == pygame.K_UP:
            self.up = False
        elif key == pygame.K_LEFT:
            self.left = False
        elif key == pygame.K_RIGHT:
            self.right = False
        
        return None

    def get_offset(self):
        # TODO: Check for diagonals, in that case do SCROLL_SPEED * SRQ 2 in each dir
        m_right, m_left, m_up, m_down = self.mouse.scroll_update()

        left = self.left or m_left
        right = self.right or m_right
        up = self.up or m_up
        down = self.down or m_down

        x, y = self.parent.offset
        if left and not right:
            x -= SCROLL_SPEED
        elif right and not left:
            x += SCROLL_SPEED

        if up and not down:
            y -= SCROLL_SPEED
        elif down and not up:
            y += SCROLL_SPEED

        max_x, max_y = self.max_scroll

        if x < 0:
            x = 0
        elif x > max_x:
            x = max_x

        if y < 0:
            y = 0
        elif y > max_y:
            y = max_y

        return int(x), int(y)


class MouseMode:
    ''' Implementations should have a 'parent' member which points to a gui '''
    def draw(self):
        pass

    def set_pos(self):
        pass

    def right_up(self):
        pass

    def right_down(self):
        pass

    def left_up(self):
        pass

    def left_down(self):
        pass

    def scroll_update(self):
        x, y = pygame.mouse.get_pos()
        return self.get_dir(x, y)

    def get_dir(self, x, y):
        right, left, up, down = (False, False, False, False)
        if x - SCROLL_MARGIN <= 0:
            left = True
        elif x + SCROLL_MARGIN >= self.parent.parent.screen_size[0]:
            right = True
        if y - SCROLL_MARGIN <= 0:
            up = True
        elif y + SCROLL_MARGIN >= self.parent.parent.screen_size[1]:
            down = True

        return right, left, up, down

class ScrollerMouse(MouseMode):
    def __init__(self, sprite, parent, previous_mouse):
        self.sprite = sprite
        self.parent = parent
        self.sprite_frame = 9
    
    def draw(self):
        x, y = pygame.mouse.get_pos()
        dir = self.get_dir(x, y)
        frame = self.sprite_frame
        if any(dir):
            frame = {
                util.RIGHT: 0,
                util.BOTTOM_RIGHT: 1,
                util.DOWN: 2,
                util.BOTTOM_LEFT: 3,
                util.LEFT: 4,
                util.TOP_LEFT: 5,
                util.UP: 6,
                util.TOP_RIGHT: 7,
            }.get(dir, self.sprite_frame)

            # Clamp to sides of screen
            right, left, up, down = dir
            if right:
                x = self.parent.parent.screen_size[0] - self.sprite.width
            elif left:
                x = 0
            if down:
                y = self.parent.parent.screen_size[1] - self.sprite.height
            elif up:
                y = 0

        self.sprite.draw(x, y, frame, self.parent.screen)


class CrosshairsMouse(ScrollerMouse):
    def __init__(self, sprite, parent, order):
        pygame.mouse.set_visible(False)
        self.parent = parent
        self.sprite = sprite
        self.order = order
        self.sprite_frame = 13
    
    def set_normal_mouse(self):
        self.parent.mouse = NormalMouse(self.parent.mouse_spr, self.parent)

    def left_down(self):
        self.set_normal_mouse()

        # See if we've clicked on a unit
        location = self.parent.get_mouse_world_pos()

        clicked = self.parent.ecs.filter('SpriteClickedFilter',
                point=location)
        if len(clicked) == 1:
            return self.picked_unit(clicked[0])
        else:
            # Returns the appropriate command if any
            return self.picked_location(location)

    def right_down(self):
        self.set_normal_mouse()
    
    def picked_location(self, location):
        return self.construct_command(
                self.order['cmd'], to=location)

    def picked_unit(self, unit):
        command = self.order['cmd']
        if 'cmd_with_target' in self.order:
            comand = self.order['cmd_with_target']

        return self.construct_command(command,
                to=self.parent.ecs[unit].pos)

    def construct_command(self, command_type, **kwargs):
        return commands.get_mapped(command_type)(
            ids=self.parent.selected_units,
            **(self.order['args'] if 'args' in self.order else {}),
            **kwargs)

class CrosshairsUnitPicker(CrosshairsMouse):
    def picked_unit(self, unit):
        command = self.order['cmd']
        if 'cmd_with_target' in self.order:
            command = self.order['cmd_with_target']

        return self.construct_command(command, at=unit)


class NormalMouse(ScrollerMouse):
    def __init__(self, sprite, parent):
        pygame.mouse.set_visible(False)
        self.parent = parent
        self.sprite = sprite
        self.dragging = False
        self.initial_drag_pos = None
        self.selection_box = None
        self.sprite_frame = 11

    def draw(self):
        x, y = pygame.mouse.get_pos()


        if self.dragging:
            self._update_selection_box()
            pygame.draw.rect(self.parent.screen,
                             (200, 200, 250),
                             self.selection_box, 
                             1)
        self.sprite_frame = 11 if self.dragging else 12

        super(NormalMouse, self).draw()

    
    def left_up(self):
        if self.dragging:
            self.dragging = False
            # Logic to determine what ends up being selected
            
            units_in_rect_ids = self.parent.ecs.filter('RectFilter',
                    rect=self.selection_box.move(self.parent.parent.offset[0], self.parent.parent.offset[1]))
            
            units_in_rect = [self.parent.ecs[id] for id in units_in_rect_ids]
            if len(units_in_rect) == 1 or all(
                    ['owner' in unit and unit.owner == self.parent.player_id 
                    for unit in units_in_rect]):
                # User has selected exactly one unit or only units they own
                self.parent.update_selection(units_in_rect_ids)
            else:
                self.parent.update_selection([
                    unit.id for unit in units_in_rect
                    if 'owner' in unit and unit.owner == self.parent.player_id
                    ])
            self.selection_box = None

    def left_down(self):
        self.dragging = True
        self.initial_drag_pos = pygame.mouse.get_pos()
        self._update_selection_box()

    def right_down(self):
        if self.parent.selected_units:
            units = [unit for unit in self.parent.get_units()
                    if unit.owner == self.parent.player_id]
            # TODO: Filter-chaining should fix this
            # TODO: Implement 'unit_set' type - iterable but also features a 'filter' option?
            return commands.Move(ids=[
                unit.id for unit in units if 'orders' in unit and 'move' in unit.orders],
                    to=self.parent.get_mouse_world_pos())

    def _update_selection_box(self):
        ix, iy = self.initial_drag_pos
        nx, ny = pygame.mouse.get_pos()
        # For some reason, selection boxes with negative heights
        # and widths won't collide with any points.
        if nx >= ix:
            x = ix
            w = nx - ix
        else:
            x = nx
            w = ix - nx

        if ny >= iy:
            y = iy
            h = ny - iy
        else:
            y = ny
            h = iy - ny

        self.selection_box = pygame.Rect(x, y, w, h)

# TODO: Right now 'unit' is just what is selectable / targetable
# This needs a saner setup, but that probably requires filter chaining / 
# a major upgrade of how we handle filtering.

class RectFilter(ecs.Filter):
    def apply_individual(self, ent, criteria):
        ''' criteria: {'rect': pygame.Rect}
        Checks to see if the entity is within the selected rect.'''
        # TODO: Quadtree, or some such
        if 'unit' in ent and 'pos' in ent and criteria['rect'].collidepoint(ent.pos):
            return ent

class SpriteClickedFilter(ecs.Filter):
    def __init__(self, sprites):
        self.sprites = sprites

    def apply(self, ents, criteria):
        # TODO: This is a bit of a hack, just doing a radius
        x, y = criteria['point']
        for ent in ents.values():
            if 'pos' in ent and 'sprite' in ent and 'unit' in ent:
                radius = self.sprites[ent.sprite].width / 2

                distance = math.sqrt(
                    ((ent.pos[0] - x) ** 2) +
                    ((ent.pos[1] - y) ** 2)
                )

                if distance < radius:
                    return [ent.id]
        return []


class SelectionDrawSystem(ecs.DrawSystem):
    def __init__(self, screen, gui, sprite):
        self.criteria = ['pos']
        self.gui = gui
        self.sprite = sprite

    def draw_all(self, ents, offset):
        for ent in ents:
            if ent.id in self.gui.selected_units:
                self.sprite.draw(x=ent.pos[0] - offset[0], y=ent.pos[1] - offset[1],
                        frame=0 if ent.owner and
                            # TODO: Why does this break for player 0?
                            ent.owner == self.gui.player_id 
                            else 1,
                        screen=self.gui.screen)

class GoalDrawSystem(ecs.DrawSystem):
    def __init__(self, gui, sprite):
        self.criteria = ['move_goal']
        self.gui = gui
        self.sprite = sprite

    def draw_all(self, ents, offset):
        for ent in ents:
            if ent.id in self.gui.selected_units:
                self.sprite.draw(x=ent.move_goal[0] - offset[0],
                        y = ent.move_goal[1] - offset[1], frame=8, screen=self.gui.screen)


class PathDrawSystem(ecs.DrawSystem):
    def __init__(self, gui, sprite, tile_height, tile_width):
        self.criteria = ['path']
        self.gui = gui
        self.sprite = sprite
        self.tile_height = tile_height
        self.tile_width = tile_width

    def draw_all(self, ents, offset):
        for ent in ents:
            if ent.id in self.gui.selected_units:
                for node in ent.path:
                    self.sprite.draw(
                            x=(node[0] * self.tile_width) - offset[0],
                            y=(node[1] * self.tile_height) - offset[1],
                            frame=9,
                            screen=self.gui.screen
                        )

SELECTORS = {
        'crosshairs': CrosshairsMouse,
        'unitpicker': CrosshairsUnitPicker,
}
