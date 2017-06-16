import math

import pygame

import ecs

class Sprite:
    def __init__(self, image, x_frames, y_frames,
            x_size, y_size, x_offset, y_offset):
        self.image = image
        self.x_frames = x_frames
        self.y_frames = y_frames
        self.width = x_size
        self.height = y_size
        self.x_offset = x_offset
        self.y_offset = y_offset

        # These are modified on each draw
        # would it be more efficient to instantiate a bunch of rects?
        self.draw_rect = pygame.Rect((0,0), (self.width, self.height))
        self.pos_rect = pygame.Rect((0,0), (self.width, self.height))

    def draw(self, x, y, frame, screen):
        x = x - self.x_offset
        y = y - self.y_offset

        frame_offset = frame * self.width
        self.draw_rect.move_ip(frame_offset, 0)
        self.pos_rect.move_ip(x, y)

        screen.blit(self.image, self.pos_rect, area=self.draw_rect)
        
        self.draw_rect.move_ip(frame_offset * -1, 0)
        self.pos_rect.move_ip(-1 * x, -1 * y)


def angle_to_frame(angle):
    # TODO: Cleanly factor this
    # TODO: Make this work with fixed point math
    # TODO: Look at a graph of this function and make sure it works right
    degrees = 180 + (360 * (angle / (2 * math.pi)))
    if degrees < 0:
        degrees = 360 + degrees
    frame = (4 +  round(8 * (degrees / 360))) % 8
    return frame

class SpriteDrawSystem(ecs.DrawSystem):
    def __init__(self, screen, sprites):
        self.sprites = sprites
        self.screen = screen
        self.criteria = ['pos', 'sprite']

    def draw_individual(self, ent):
        frame = 0
        if 'dir' in ent:
            frame = ent.dir
        if 'frame' in ent:
            frame = ent.frame
        self.sprites[ent.sprite].draw(ent.pos[0], ent.pos[1], frame, self.screen)

class ExplosionAnimationSystem(ecs.System):
    def __init__(self, data):
        self.criteria = ['explosion', 'frame', 'sprite']
        self.data = data

    def do_step_individual(self, ent):
        ent.frame = ent.frame + 1
        if ent.frame >= self.data.sprites[ent.sprite].x_frames:
            ent.delete = True
