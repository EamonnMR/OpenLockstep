import pygame

import ecs
import commands

class GUI:
    def __init__(self, ecs, mouse_spr, screen, data, player_id):
        self.mouse = NormalMouse(mouse_spr, self)
        self.screen = screen
        self.selected_units = []
        self.ecs = ecs
        self.buttons = []
        self.active_hotkeys = {}
        self.data = data
        self.player_id = player_id

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
        ''' Returns commands if any'''
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
        elif event.type == pygame.KEYDOWN:
            # This is fine as an MVP but I think that determining the order
            # set at selection-time might be saner.
            hotkey = chr(event.key)
            if hotkey in self.active_hotkeys:
                order = self.active_hotkeys[hotkey]
                print(self.active_hotkeys)
                return commands.get_mapped(order['cmd'])(
                        ids=self.selected_units, **(order['args'] if 'args' in order else {})
                )
            else:
                return None
    

    def draw(self):
        # TODO: Draw gui stuff here
        self.mouse.draw()

    def update(self):
        pass

class MouseMode:
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

class NormalMouse(MouseMode):
    def __init__(self, sprite, parent):
        pygame.mouse.set_visible(False)
        self.parent = parent
        self.sprite = sprite
        self.dragging = False
        self.initial_drag_pos = None
        self.selection_box = None

    def draw(self):
        x, y = pygame.mouse.get_pos()


        if self.dragging:
            self._update_selection_box()
            pygame.draw.rect(self.parent.screen,
                             (200, 200, 250),
                             self.selection_box, 
                             1)
        self.sprite.draw(x, y,
                11 if self.dragging else 12, 
                # TODO: Idea: sprites with named frames?
                self.parent.screen)
    
    def left_up(self):
        self.dragging = False
        # Logic to determine what ends up being selected
        
        units_in_rect_ids = self.parent.ecs.filter('RectFilter', rect=self.selection_box)
        
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
                    to=pygame.mouse.get_pos())

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

class RectFilter(ecs.Filter):
    def apply_individual(self, ent, criteria):
        ''' criteria: {'rect': pygame.Rect}
        Checks to see if the entity is within the selected rect.'''
        # TODO: Quadtree, or some such
        if 'pos' in ent and criteria['rect'].collidepoint(ent.pos):
            return ent


class SelectionDrawSystem(ecs.DrawSystem):
    def __init__(self, screen, gui, sprite):
        self.criteria = ['pos']
        self.gui = gui
        self.sprite = sprite

    def draw_all(self, ents):
        for ent in ents:
            if ent.id in self.gui.selected_units:
                self.sprite.draw(x=ent.pos[0], y=ent.pos[1],
                        frame=0 if ent.owner and
                            ent.owner == self.gui.player_id 
                            else 1,
                        screen=self.gui.screen)
