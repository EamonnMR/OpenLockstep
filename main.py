#!/usr/bin/python3

import argparse
import pygame
import json

import net
import commands

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs OpenLockstep')
    parser.add_argument('--server', action='store_true')
    parser.add_argument('--client', action='store_true')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--host', type=str, default='localhost')
    parser.add_argument('--clients', type=int, default=1)
    parser.add_argument('--settings_file', type=str, default='settings.json')
    parser.add_argument('--settings', type=str, default='{}')
    parser.add_argument('--player_id', type=int, default=0)

    args = parser.parse_args()

    settings = json.load(open(args.settings_file))
    settings.update(json.loads(args.settings))

    if args.client:
        screen = pygame.display.set_mode(settings['screen_size'])
        pygame.display.set_caption("OpenLockstep RTS")
        client = net.Client(args.host, args.port)
        mousedown = False
        step = 0
        
        TIMER_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(TIMER_EVENT, 250) # 4 times / second (SC does 217)
        command_list = [] 
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP and mousedown:
                    command_list += [commands.Ping(position=event.pos)]
                    mousedown = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not mousedown:
                    mousedown = True
                elif event.type == TIMER_EVENT:
                    # Transmit accumulated commands then clear list
                    client.send(step, command_list)
                    command_list = [] # Set-to-new-empty, not delete

                    # Wait for the server
                    # See net for why this should not lag the game
                    # TODO: Handle lag more gracefully (show "lag" screen?)
                    in_step = client.block_until_get_step(step)
                    # TODO: Game logic goes here
                    for ping in in_step.commands:
                        pygame.draw.circle(screen, (200, 200, 200),
                                           ping.position, 10, 2)
                    step += 1 # Only advance after we've recieved a new step
            pygame.display.flip()

    elif args.server:
        net.Server(args.port, host=args.host, client_count=args.clients).run()

