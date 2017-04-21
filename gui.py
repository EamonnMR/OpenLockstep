import pygame

import ecs

class GUI:
    def __init__(self, ecs, mouse_spr, screen):
        self.mouse = NormalMouse(mouse_spr, self)
        self.screen = screen
        self.selected_units = []
        self.ecs = ecs

    def handle_event(self, event):
        ''' Returns commands if any'''
        if event.type == pygame.MOUSEBUTTONUP:
            return self.mouse.up()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self.mouse.down()
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

    def left_press(self):
        pass

    def left_release(self):
        pass

    def up(self):
        pass

    def down(self):
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
    
    def up(self):
        self.dragging = False
        self.parent.selected_units = \
                self.parent.ecs.filter('RectFilter',
                        rect=self.selection_box)
        self.selection_box = None

    def down(self):
        self.dragging = True
        self.initial_drag_pos = pygame.mouse.get_pos()
        self._update_selection_box()

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
        # TODO: Quadtre or some such
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
                        frame=0, screen=self.gui.screen)
