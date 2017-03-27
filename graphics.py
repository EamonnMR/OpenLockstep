import pygame

class Sprite:
    def __init__(self, image, x_frames, y_frames, x_size, y_size):
        self.image = image
        self.x_frames = x_frames
        self.y_frames = y_frames
        self.width = x_size
        self.height = y_size

        # These are modified on each draw
        # would it be more efficient to instantiate a bunch of rects?
        self.draw_rect = pygame.Rect((0,0), (self.width, self.height))
        self.pos_rect = pygame.Rect((0,0), (self.width, self.height))

    def draw(self, x, y, frame, screen):
        frame_offset = frame * self.width

        self.draw_rect.move_ip(0, frame_offset)
        self.pos_rect.move_ip(x, y)

        screen.blit(self.image, self.pos_rect, area=self.draw_rect)
        
        self.draw_rect.move_ip(0, -1 * frame_offset)
        self.pos_rect.move_ip(-1 * x, -1 * y)
