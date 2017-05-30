import json
import os
import copy

import pygame
import yaml

from graphics import Sprite
from ecs import Entity

class DataLoader:
    def __init__(self, directory):
        self.root_dir = directory
        self.sprites = {}
        self.data = {}

    class UnknownFileType(Exception):
        ''' Tried to parse a file with an unsupported or unknown
        type'''
        pass

    def _get_cfg(self, name):
        ''' Gets json from a file in the data dir '''
        # TODO: Add support for yaml, etc.
        text = open(self._fname(name))
        if name.endswith('.json'):
            return json.load(text)
        elif name.endswith('.yml') or name.endswith('.yaml'):
            return yaml.load(text)
        else:
            print('unknown file type: ' + name)
            #raise UnknownFileTypeException


    def _fname(self, fname):
        return os.path.join(self.root_dir, fname)
    def preload(self):
        ''' This loads textual data, but does not load images.'''
        for file_name in os.listdir(self.root_dir):
               
            if os.path.isfile(os.path.join(self.root_dir, file_name)):
                self.data[file_name.split('.')[0]] = self._get_cfg(file_name)
    def load(self):
        ''' Loads images  '''
        for name, data in self.data['sprites'].items():
           self.sprites[name] = self._get_sprite_with_defaults(data)
        
    def _get_sprite_with_defaults(self, data):
        ''' Applies default derived values to sprite data
        Intended to save a bunch of typing.'''
        # TODO: Is there a more terse way to write this?
        # You could probably make a really sophisticated prolog
        # subsystem to determine all traits of a sprite from
        # any minimal set of data.

        image = pygame.image.load(
                    self._fname(data['file'])
                ).convert_alpha()
        
        x_frames = 1
        if 'x_frames' in data:
            x_frames = data['x_frames']

        y_frames = 1
        if 'y_frames' in data:
            y_frames = data['y_frames']

        width = image.get_width() / x_frames
        if 'width' in data:
            width = data['width']

        height = image.get_height() / y_frames
        if 'height' in data:
            height = data['height']

        x_offset = width / 2
        if 'x_offset' in data:
            x_offset = data['x_offset']

        y_offset = height / 2
        if 'y_offset' in data:
            y_offset = data['y_offset']

        return Sprite(image, x_frames, y_frames,
                width, height, x_offset, y_offset)

    def spawn(self, utype, **kwargs):
        mutable = copy.deepcopy(self.data['units'][utype])
        mutable.update(kwargs)

        print(mutable)

        return Entity(mutable)
