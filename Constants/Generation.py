'''Chunk Generation Variables'''
CHUNK_SIZE = 8 #must be divisible by 2
HALF_CHUNK_SIZE = CHUNK_SIZE//2 # cause of this
BLOCK_SIZE = 48
HALF_BLOCK_SIZE = BLOCK_SIZE//2
PLAYER_PLACEMENT_IRREGULARITY = 5
OCTAVES = 6
MAPWIDTH  = 700
MAPHEIGHT = 700
SCALE     = .01 #should be .001 for production

'''Initial Generation Variables'''
INITIAL_GEN_SIZE = 2 #for both x and y
TOTAL_GENERATED_CHUNKS = INITIAL_GEN_SIZE * INITIAL_GEN_SIZE

'''Biomes that exist'''
PLAINS = 0
SAVANAH = 1