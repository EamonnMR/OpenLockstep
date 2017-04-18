import pygame

class GUI:
    def __init__(self, mouse_spr, screen):
        self.mouse = NormalMouse(mouse_spr, self)
        self.screen = screen

    def handle_event(self, event):
        pass

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

class NormalMouse(MouseMode):
    def __init__(self, sprite, parent):
        pygame.mouse.set_visible(False)
        self.parent = parent
        self.sprite = sprite

    def draw(self):
        x, y = pygame.mouse.get_pos()
        self.sprite.draw(x=x, y=y,
                frame=12, # TODO: Idea: sprites with named frames?
                screen=self.parent.screen)

