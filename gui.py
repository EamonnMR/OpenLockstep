import pygame

class GUI:
    def __init__(self, mouse_spr, screen):
        self.mouse = NormalMouse(mouse_spr, self)
        self.screen = screen

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

        self.sprite.draw(x=x, y=y,
                frame=11 if self.dragging else 12, 
                # TODO: Idea: sprites with named frames?
                screen=self.parent.screen)
    
    def up(self):
        self.dragging = False
        self.selection_box = None # Select all units in this box

    def down(self):
        self.dragging = True
        self.initial_drag_pos = pygame.mouse.get_pos()
        self._update_selection_box()

    def _update_selection_box(self):
        x, y = self.initial_drag_pos
        nx, ny = pygame.mouse.get_pos()
        w = nx - x
        h = ny - y
        self.selection_box = pygame.Rect(x, y, w, h)
