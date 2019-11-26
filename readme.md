# OpenLockstep: Networked RTS engine in python

The basic idea for this project is the twin concepts of an entity/component game arcatecture and a lockstep network model (as described in the classic paper [1500 Archers on a 28.8](https://www.gamasutra.com/view/feature/131503/1500_archers_on_a_288_network_.php). It's data driven and attempts to mess with the data as little as possible so that it's obvious how you get from YAML to game entities. The goal, beyond playing with those concepts (and maybe ending up with a playable PVP RTS) is to leave a foundation that anyone can pick up and use to experiment with RTS concepts - it's a type of game I very much enjoy, and one that I'd like to see continued innovation in.


## Installation:
Like most Python projects, you can install the dependancies like this:
`pip3 install -r requirements.txt`

You should probably do this in a python 3 [venv](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

See below for a more in-depth installation guide


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

The graphics are DanC's classic [Tyrian](http://www.lostgarden.com/2007/04/free-game-graphics-tyrian-ships-and.html) and [HardVaccum](http://www.lostgarden.com/2005/03/game-post-mortem-hard-vacuum.html) collections, under [CC BY 3](https://creativecommons.org/licenses/by-sa/3.0/). Much of it is re-used from tweaks I made for [Scandium](http://github.com/eamonnmr/scandium_rts), including the double-sized pixels and the tiled map tileset. I'm a huge fan of these graphics. They're not placeholders-they're final art.

### Tech

OLS is written in  Python 3. Graphics are displayed with [pygame](http://pygame.org). Yaml is parsed with [pyyaml](http://pyyaml.org/wiki/PyYAML). I didn't want to focus on tile-based game stuff so I'm using some libraries-maps are created in [Tiled](http://www.mapeditor.org/) loaded with [PyTMX](https://github.com/bitcraft/PyTMX) and drawn with [pyscroll](https://github.com/bitcraft/pyscroll). I followed Red Blob Games' pathfinding [tutorial](https://www.redblobgames.com/pathfinding/a-star/introduction.html) for the pathfinding.

### In-Depth Installation Guide

Install Pyenv
https://github.com/pyenv/pyenv

Install Python 3.8.0
`pyenv install 3.8.0`

Create Python 3.8.0 venv
`virtualenv -p /home/eamonn/.pyenv/versions/3.8.0/bin/python venv && source venv/bin/activate`

Install SDL deps (https://stackoverflow.com/a/15368766)
`sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl git`

Install dependencies 
`pip install -r requirements.txt`

