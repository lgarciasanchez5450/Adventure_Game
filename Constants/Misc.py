from typing import Final
from .Generation import BLOCK_SIZE
import os
'''Miscalleneous Variables'''
GAME_PATH = os.path.dirname(os.path.realpath(__file__))
SLEEP_VELOCITY_THRESHOLD = .0001
ITEM_PICKUP_TIME = 3.0 #time to wait between pickups
PARTICLE_SIZE = BLOCK_SIZE // 8
ZERO = 0
POSITIVE_INFINITY = float('inf')
NEGATIVE_INFINITY = float('-inf')
DEBUG:Final = True
TEXTURE_FANCY_IMPORT:Final = False
TWO_PI = 6.283185307197959

'''Game States'''
MAIN_MENU = 0
RUNNING = 1
SETTINGS = 2
GENERATING_WORLD = 3
CHARACTER_CREATION = 4
WORLD_SELECT = 5


'''Types of Ground'''
GROUND_TEST = -1
GROUND_INVALID = 0
GROUND_DIRT = 1
GROUND_STONE = 2
GROUND_WATER = 3
GROUND_GRASS = 4
GROUND_SAND = 5

del os