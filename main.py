#!/usr/bin/python3

'''
Main module - interprets settings and args, runs client or server.
'''

import argparse
import pygame
import json

import net
import commands
import game
import gui
import ecs
import movement

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
    ent_manager = ecs.EntityManager(
        systems=[
            movement.MoveSystem()
        ],
            filters={
                'RectFilter': gui.RectFilter(),
            }
        )

    if args.client:
        game.Game(settings, args, ent_manager).start()
    elif args.server:
        net.Server(args.port, host=args.host,
                client_count=args.clients,
                ent_manager=ent_manager).run()

