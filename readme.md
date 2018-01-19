# OpenLockstep: Networked RTS engine in python

The basic idea for this project is the twin concepts of an entity/component game arcatecture and a lockstep network model (as described in the classic paper [1500 Archers on a 28.8](https://www.gamasutra.com/view/feature/131503/1500_archers_on_a_288_network_.php). It's data driven and attempts to mess with the data as little as possible so that it's obvious how you get from YAML to game entities.


## Installation:
Like most Python projects, you can install the dependancies like this:
`pip3 install -r requirements.txt`

You should probably do this in a python 3 [venv](http://docs.python-guide.org/en/latest/dev/virtualenvs/).


# Running OLS

The client and server should have the same maps, data, and version of the code. The protocol between the client and server isn't meant to be a public API and will not affect the semver. In order to run a singleplayer game, run the server and a single client. 

## Server

`python3 main.py --server`

For multiple players, run the server with the `--clients n` argument to set the number of clients to wait for, then connect that number of clients. 

## Client

`python3 main.py --client`

Remote clients can connect with the `--port` and`--host` arguments.  
# Acknowledgements

### Graphics

The graphics are DanC's classic Tyrian and HardVaccum collections, under the Lost Garden liscense. Much of it is re-used from tweaks I made for Scandium, including the double-sized pixels and the tiled map tileset. I'm a huge fan of these graphics. They're not placeholders-they're final art.

### Tech

OLS is written in  Python 3. Graphics are displayed with [pygame](http://pygame.org). Yaml is parsed with [pyyaml](http://pyyaml.org/wiki/PyYAML). I didn't want to focus on tile-based game stuff so I'm using some libraries-maps are created in [Tiled](http://www.mapeditor.org/) loaded with [PyTMX](https://github.com/bitcraft/PyTMX) and drawn with [pyscroll](https://github.com/bitcraft/pyscroll). I followed Red Blob Games' pathfinding [tutorial](https://www.redblobgames.com/pathfinding/a-star/introduction.html) for the pathfinding.

