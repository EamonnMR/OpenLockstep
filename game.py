import pygame

import net
import commands
from ecs import System, EntityManager, Entity
from data import DataLoader

TIMER_EVENT = pygame.USEREVENT + 1
STEP_LENGTH = 250 # ms (250 is 4 times per second)
class Game:
    '''
    Calling "start" runs the game loop. Inside the game loop, the event loop
    processes input and times when to finish and send a step.
    '''
    def __init__(self, settings, args): # The settings/args split may be a pain
        self.screen = pygame.display.set_mode(settings['screen_size'])
        pygame.display.set_caption("OpenLockstep RTS")
        self.client = net.Client(args.host, args.port)
        self.step = None
        self.command_list = None
        self.mousedown = 0
        self.data = DataLoader(settings['assets'])
        self.data.preload()
        self.data.load()
        self.entities = EntityManager(systems=[
            SpriteDrawSystem(screen=self.screen, sprites=self.data.sprites),
            SpriteRotateSystem()
        ])

        self.state_hash = b'0'.join([b'' for x in range(0,31)]) # 32 zeroes
    def start(self):
        self.command_list = []
        self.mousedown = False
        self.step = 0
        pygame.time.set_timer(TIMER_EVENT, STEP_LENGTH)
        while True:
            for event in pygame.event.get():
                self.process_event(event)
            pygame.display.flip()

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and self.mousedown:
            self.command_list += [commands.Ping(position=event.pos)]
            self.mousedown = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not self.mousedown:
            self.mousedown = True
        elif event.type == TIMER_EVENT:
            self.advance_step()

    def advance_step(self):
        # Transmit accumulated commands then clear list
        self.client.send(self.step, self.command_list, self.state_hash)
        self.command_list = [] # Set-to-new-empty, not delete

        # Wait for the server
        # See net for why this should not lag the game
        # TODO: Handle lag more gracefully (show "lag" screen?)
        self.execute_step(self.client.block_until_get_step(self.step))
        self.state_hash = self.entities.do_step()
        # TODO: Game logic goes here
        self.step += 1 # Only advance after we've recieved a new step

    def execute_step(self, step):
        for ping in step.commands:
            # Dummy code to draw pings
            self.entities.add_ent(Entity({'pos': tuple(ping.position), 'dir': 0}))


# Test stuff for ent-comp
class SpriteDrawSystem(System):

    criteria = ['pos', 'dir']

    def __init__(self, screen, sprites):
        self.sprites = sprites
        self.screen = screen

    
    def do_step_individual(self, ent):
        self.sprites['tank'].draw(ent.pos[0], ent.pos[1], ent.dir, self.screen)

class SpriteRotateSystem(System):
    criteria = ['dir']

    def do_step_individual(self, ent):
        ent.dir += 1;
        ent.dir = ent.dir % 8
