import json
import os

import pygame

from graphics import Sprite


class DataLoader:
    def __init__(self, directory):
        self.root_dir = directory
        self.sprites = {}
        self.data = {}

    def _get_cfg(self, name):
        ''' Gets json from a file in the data dir '''
        # TODO: Add support for yaml, etc.
        return json.load(open(self._fname('sprites.json')))

    def _fname(self, fname):
        return os.path.join(self.root_dir, fname)
    def preload(self):
        ''' This loads textual data, but does not load images.'''
        self.data['sprites'] = self._get_cfg('sprites.json')
    def load(self):
        ''' Loads images  '''
        for name, data in self.data['sprites'].items():
           self.sprites[name] = Sprite(
               pygame.image.load(self._fname(data['file'])).convert_alpha(),
               data['x_frames'],
               data['y_frames'],
               data['width'],
               data['height'],
           )
        
