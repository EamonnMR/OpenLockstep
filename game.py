import sys
import math

import pygame
from pytmx.util_pygame import load_pygame
import pyscroll

import net
import commands
from ecs import System, DrawSystem, EntityManager, Entity
import gui
import graphics
import movement

TIMER_EVENT = pygame.USEREVENT + 1
STEP_LENGTH = 250 # ms (250 is 4 times per second)
class Game:
    '''
    Calling "start" runs the game loop. Inside the game loop, the event loop
    processes input and times when to finish and send a step.
    '''
    def __init__(self, settings, args, entities, data, screen): # The settings/args split may be a pain
        pygame.display.set_caption("OpenLockstep RTS")
        self.client = net.Client(args.host, args.port)
        self.step = None
        self.command_list = None
        self.data = data
        self.screen = screen
        self.entities = entities
        self.entities.add_draw_system(
                graphics.SpriteDrawSystem(screen=self.screen,
                sprites=self.data.sprites)
        )

        self.player_id = None
        self.map = None
        self.map_layer = None
        self.screen_size = settings['screen_size']
        self.offset = [0,0]
        self.grabbed = False
        self.pathmap = []
        self.settings = settings

    def do_handshake(self):
        hs_step = self.client.block_until_get_step(net.HANDSHAKE_STEP)
        for command in hs_step.commands:
            if type(command) == commands.Handshake:
                # Create players with entity IDs corresponding to their player IDs
                for player_id in sorted(command.startlocs):
                    self.entities.add_ent(Entity({'player_id': int(player_id),
                        'faction': command.startlocs[player_id]['fac']}))
                # Now that we have player ents with the right IDs, spawn other stuff
                for player_id in sorted(command.startlocs):
                    info = command.startlocs[player_id]
                    start_building = self.data.data['factions'][info['fac']]['start_building']
                    self.entities.add_ent(self.data.spawn(
                        utype=start_building, pos=info['start'], owner=int(player_id)))

            self.player_id = command.your_id

            self.map = load_pygame(command.map)
            
            self.map_layer = pyscroll.BufferedRenderer(pyscroll.TiledMapData(self.map),
                    self.screen_size) 
        
        print("Handshake complete. Your player ID: {}".format(self.player_id))

        self.state_hash = net.EMPTY_HASH 

        # TODO: When implementing factions/game modes, use this area to
        # instantiate the GUI differently based on the handshake.
        # For now we hard code how the GUI will look.
        self.gui = gui.GUI(self.entities,
                self.data.sprites['scand_mouse'],
                self.screen,
                self.data.data,
                self.player_id,
                self,
                ((self.map.width * self.map.tilewidth) + self.screen_size[0],
                 (self.map.height * self.map.tileheight) + self.screen_size[1])
        ) # TODO: Clean up this leaky abstraction

        self.entities.add_draw_system(
                gui.SelectionDrawSystem(screen=self.screen, gui=self.gui,
                    sprite=self.data.sprites['scand_selection']),
                0) # We want it at 0 so as to be below the sprites.

        self.entities.add_draw_system(
                gui.GoalDrawSystem(gui=self.gui,
                    sprite=self.data.sprites['scand_mouse'])
                )

        self.entities.add_filter(
                gui.SpriteClickedFilter(self.data.sprites)
                )
        # Pathing data - loading & displaying

        self.pathmap = movement.Pathmap(self.map)

        if 'show_pathing' in self.settings:
            self.entities.add_draw_system(
                    movement.PathabilityDrawSystem(
                        pathmap=self.pathmap,
                        tile_height=self.map.tileheight,
                        tile_width=self.map.tilewidth,
                        sprite=self.data.sprites['path'],
                        screen=self.screen
                    )
            )

    def start(self):
        self.command_list = []
        self.do_handshake()
        self.step = net.INITIAL_STEP
        pygame.time.set_timer(TIMER_EVENT, STEP_LENGTH)
        while True:
            for event in pygame.event.get():
                self.process_event(event)
            self.offset = self.gui.get_offset()
            self.map_layer.center(self.get_center())
            self.map_layer.draw(self.screen,
                    pygame.Rect((0,0), self.screen_size))
            self.entities.draw(self.offset)
            self.gui.draw()
            pygame.display.flip()

    def process_event(self, event):
        if event.type == TIMER_EVENT:
            self.advance_step()
        elif event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(1)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.grabbed = not self.grabbed
            pygame.event.set_grab(self.grabbed)
        else:
            command = self.gui.handle_event(event)
            if command:
                self.command_list.append(command)

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
        for command in step.commands:
            command.execute(self.entities, self.data)

    def get_center(self):
        return self.screen_size[0]/2 + self.offset[0], self.screen_size[1]/2 + self.offset[1]

