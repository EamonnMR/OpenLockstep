#!/usr/bin/python3

import argparse
import pygame
import json
import net

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs OpenLockstep')
    parser.add_argument('--server', action='store_true')
    parser.add_argument('--client', action='store_true')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--host', type=str, default='localhost')
    parser.add_argument('--clients', type=int, default=1)
    parser.add_argument('--settings_file', type=str, default='settings.json')
    parser.add_argument('--settings', type=str, default='{}')

    args = parser.parse_args()

    settings = json.load(open(args.settings_file))
    settings.update(json.loads(args.settings))

    if args.client:
        screen = pygame.display.set_mode(settings['screen_size'])
        pygame.display.set_caption("OpenLockstep RTS")
        client = net.Client(args.host, args.port)
        mousedown = False

        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP and mousedown:
                    print('click')
                    mousedown = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not mousedown:
                    mousedown = True

        #while True:
        #    text = input("> ")[:255]
        #    client.send(bytes([len(text)]))
        #    client.send(text.encode('utf-8'))
    elif args.server:
        net.Server(args.port, host=args.host, client_count=args.clients).run()

