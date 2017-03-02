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

        while True:
            step = 0
            # Event portion of the loop
            command = None
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP and mousedown:
                    command = commands.Ping(position=event.pos,
                                            step=step + step_ahead)
                    mousedown = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not mousedown:
                    mousedown = True
            if command:
                client.send(command.serialize())
            # Network recieving portion of the loop
            in_command = client.recieve()
            if in_command is not None:
                print(in_command)
                ping = commands.deserialize(in_command)
                pygame.draw.circle(screen, (200, 200, 200),
                                   ping.position, 10, 2)
            # Make sure this stays at the end of the game loop
            pygame.display.flip()
    elif args.server:
        net.Server(args.port, host=args.host, client_count=args.clients).run()

