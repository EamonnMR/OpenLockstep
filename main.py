'''
Main module - interprets settings and args, runs client or server.
'''

import argparse

import pygame
import yaml

import net
import commands
import game
import gui
import ecs
import movement
import combat
import graphics
from data import DataLoader

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Runs OpenLockstep')
    parser.add_argument('--server', action='store_true')
    parser.add_argument('--client', action='store_true')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--host', type=str, default='localhost')
    parser.add_argument('--clients', type=int, default=1)
    parser.add_argument('--settings_file', type=str, default='settings.yaml')
    parser.add_argument('--settings', type=str, default='{}')
    parser.add_argument('--player_id', type=int, default=0)

    args = parser.parse_args()

    settings = yaml.load(open(args.settings_file))
    settings.update(yaml.load(args.settings))
    data = DataLoader(settings['assets'])
    data.preload()

    ent_manager = ecs.EntityManager(
        systems=[
            graphics.ExplosionAnimationSystem(data),
            movement.FlySystem(),
            movement.PathFollowSystem(), #FIXME: We need tile dimensions earlier
            combat.HitPointSystem(),
            combat.CooldownSystem(),
        ],
        filters={
            'RectFilter': gui.RectFilter(),
        }
    )
    ent_manager.add_system(combat.AttackSystem(ent_manager, data),
            index=1)
    ent_manager.add_system(ecs.DeletionSystem(ent_manager))

    if args.client:
        screen = pygame.display.set_mode(settings['screen_size'])
        data.load()
        game.Game(settings, args, ent_manager, data, screen).start()
    elif args.server:
        net.Server(settings, args.port, host=args.host,
                client_count=args.clients,
                ent_manager=ent_manager).run()
