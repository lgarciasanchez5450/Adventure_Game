#Any constants needed for any scripts should go here
#variables here should not change (eg. be Final) so it is safe to do from Constants import *
#there should not be ANY imports in this module as it contains only pure python constants
DEBUG = True

_:object = object()
'''Display Variables'''
WINDOW_WIDTH = 900 #these are starting numbers and can change thoughout the lifespan of the program 
WINDOW_HEIGHT = 600 #these are starting numbers and can change thoughout the lifespan of the program 
WIDTH = 900
HEIGHT = 600
HALFWIDTH = WIDTH//2
HALFHEIGHT = HEIGHT//2
FPS = 0 #Target Framerate

_:object
'''Chunk Generation Variables'''
CHUNK_SIZE = 8 #must be divisible by 2
HALF_CHUNK_SIZE = CHUNK_SIZE//2 # cause of this
BLOCK_SIZE = 64
OCTAVES = 6
MAPWIDTH  = 700
MAPHEIGHT = 700
SCALE     = .1


_:object
'''Miscalleneous Variables'''
PLAYER_PLACEMENT_IRREGULARITY = 5
SLEEP_VELOCITY_THRESHOLD = .0001
ITEM_PICKUP_TIME = 3.0
ENTITY_MAX_LIFESPAN = 1 * 10 #seconds
ITEM_SIZE = BLOCK_SIZE//2
PARTICLE_SIZE = BLOCK_SIZE // 8
ZERO = 0

_:object
'''MUSIC'''
MUSIC_FOLDER = 'Music'
SOUND_FOLDER = 'Sounds'
STARTING_SOUND_VOLUME = 0 #percent, should be int [0,100]

_:object
'''Game States'''
MAIN_MENU = 0
RUNNING = 1
SETTINGS = 2

_:object
'''Types of Damage that can be dealt'''
FIRE_DAMAGE = 'fire'
ICE_DAMAGE = 'ice'
PHYSICAL_DAMAGE = 'physical'
ETHEREAL_DAMAGE = 'ethereal'
EXPLOSION_DAMAGE = 'explosion'
INTERNAL_DAMAGE = 'internal' # this one is like for if an entity needs to do an action that it cant afford to(energy wise) it will take damage proportional to the amount of energy needed
#more can be added


_:object
'''All Items Name''' #this is the name that will pop up in-game
ITAG_WOODEN_SWORD = 'Wooden Sword'
ITAG_HAT= 'hat'
ITAG_DIRT = 'Dirt'
ITAG_BOW = 'Bow'
ITAG_BUNNY_EGG = 'bunny egg'


_:object
'''All types of armour that can be worn'''
HEADWEAR = 'headwear'
CHESTWEAR = 'chestwear'
LEGWEAR = 'legwear'
ROBEWEAR = 'robewear' # im not sure if this is a real word
FOOTWEAR = 'footwear'
HANDWEAR = 'glove'


_:object
'''Biomes that exist'''
PLAINS = 0
SAVANAH = 1

_:object
'''Types of Ground'''

GROUND_DIRT = 1
GROUND_STONE = 2
GROUND_WATER = 3
GROUND_GRASS = 4

_:object
'''Types of Blocks'''
DIRT = 'dirt'

del _


