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

    step_ahead = 2 # This should get bigger for larger latentcy compensation

    if args.client:
        screen = pygame.display.set_mode(settings['screen_size'])
        pygame.display.set_caption("OpenLockstep RTS")
        client = net.Client(args.host, args.port)
        mousedown = False
        step = 0
    
        while True:
            # Event portion of the loop
            command_list = []
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP and mousedown:
                    command_list = [commands.Ping(position=event.pos)]
                    mousedown = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not mousedown:
                    mousedown = True
            client.send(net.Step(step + step_ahead, command_list))
            # Network recieving portion of the loop
            in_step = client.recieve()
            if in_step is not None:
                for ping in in_step.commands:
                    pygame.draw.circle(screen, (200, 200, 200),
                                   ping.position, 10, 2)
            # Make sure this stays at the end of the game loop
            pygame.display.flip()

            step += 1 # TODO: Add timer
    elif args.server:
        net.Server(args.port, host=args.host, client_count=args.clients).run()

