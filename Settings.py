from Constants import *
TREE_SPACING_BY_BIOME = {
    PLAINS: 5,
    SAVANAH:10
}
SURFACE_FRICTION_BY_GROUND = {
    GROUND_DIRT:9,
    GROUND_STONE:20,
    GROUND_WATER:2
}
HITBOX_SIZE = {
    'player':(.5,.6),
    'object':(1,1),
    'tree':(.6,1),
    'enemy':(.3,.3),
    'spirit':(.3,.3),
    'tnt':(1,1),
    'human':(.5,.6),
    'bunny':(.3,.2),
    'arrow':(.1,.1),
    'item':(.4,.4)
}
SURFACE_OFFSET = {
    'player'    : (-32,-45),
    'object'    : (0,0),
    'grass'     : (0,0),
    'tree'      : (-BLOCK_SIZE//2,-BLOCK_SIZE-29),
    'invisible' : (0,0),
    'enemy'     : (-16,-18),
    'tnt'       : (-BLOCK_SIZE//2,-BLOCK_SIZE//2- BLOCK_SIZE//4),
    
    'full_block': (-BLOCK_SIZE//2,-BLOCK_SIZE//2),
    'human'     : (-32,-45),
    'spirit'    : (-16,-16),
    'bunny'     : (-16,-16),
    'arrow'     : (-BLOCK_SIZE//2,-BLOCK_SIZE//2),
    'item'      : (-ITEM_SIZE//2,-ITEM_SIZE//2),
    }
ENEMIES_TYPES = ['spirit','bamboo','raccoon','squid']
SPECIES = ENEMIES_TYPES + ['human']
BASE_STATS = {'health':1,'base_attack':1,'defense':0,'speed':1,'base_attack_cooldown':1000,}
#ENEMY_STATS = {	'spirit': {'base_attack':15,'defense':3,'speed':.7,'base_attack_cooldown':1500,'health':100,'vision':4,'vision_time':1000,'range': .4},
#				'bamboo': {'base_attack':10,'defense':5,'speed':1,'base_attack_cooldown':1500,'health':100,'vision':5,'vision_time':1000,'range': .3}}
ACTION_ENERGY_CONSUMPTION = {
    'RUN':1,
}
ACTIONS_BY_SPECIES = {
    'human': set(),
    'spirit': {'RUN',},
    'bunny': {'RUN',}
}
APPEARANCE_BY_SPECIES = {
    'human' : (.8,1.5,1.0), #color, size, shape
    'spirit': (1,.8,.95),
    'bunny' : (.5,.3,.5),
    'item'  : (0.0,.1,.5),
    'arrow' : (0.0,.1,1.0),
}
STATS_BY_SPECIES = {'human':{'constitution': 5,'energy':5,'attack': 5,'defense':0,'speed': 80, 'strength':5,'stamina':5,'attack_range':.3},
                    'spirit':{'constitution': 7, 'energy':8,'attack':3,'defense':5,'speed':9,'strength':1,'stamina':3,'attack_range':.3}, #Reasons: Spirits are by definition ethereal creatures therefore are physically weaker in the real world
                    'bunny':{'constitution': 3, 'energy':11,'attack':1,'defense':2,'speed':3,'strength':1,'stamina':6,'attack_range':.3}, #Reasons: bunnies are by very small yet very energetic a fast, so therefore they are lightweight
                    
                    }
MAX_SPEED_BY_SPECIES = {'human':200,
                        'spirit':15,
                        'bunny':30
                        } # in blocks per second

ARMOUR_SLOTS_BY_SPECIES = {
    'human': ['headwear','chestwear','legwear','footwear'],
    'spirit':[],
    'bunny':['headwear'],

}

VISION_BY_SPECIES = {
    'human':10,
    'spirit': 3,
    'bunny': 3.5,
}
INVENTORY_SPACES_BY_SPECIES = {'human':27,'spirit':0,'bamboo':0,'raccoon':1,'squid':0,'bunny':0}
GROUND_NAME_BY_NUMBER = {}#to be filled by the groundRegisterer at runtime

#Variables that can change
RenderDistance = 6

game_state = RUNNING