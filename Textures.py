from Constants import BLOCK_SIZE,PARTICLE_SIZE,ITEM_SIZE
from os import walk,scandir
from time import sleep
from pygame import Surface
from Constants.Misc import TEXTURE_FANCY_IMPORT
if TEXTURE_FANCY_IMPORT:
	from pygame.image import load as _load
	### INNER VARIABLES ###
	loaded_counter = 0
	done_loading = False
	ready_for_next = True
	current_load_name:str = ''
	def load(file) -> Surface:
		global ready_for_next,current_load_name,loaded_counter
		while (not ready_for_next):
			sleep(0.001)
		ready_for_next = False
		current_load_name = file
		loaded_counter += 1
		return _load(file)
else: 
	from pygame.image import load
from pygame.transform import scale,flip,rotate
from game_math import GAME_PATH
from Game_Typing import PATH_DICT_TYPE

__all__ = [
	'NULL',
	'player_attack',
	'player_death',
	'player_destruction',
	'player_idle',
	'player_run',
	'player_walk',	
	'tnt',
	'items',
	'blocks',
	'entities',
	'entity_arrow',
	'enitity_spirit_idle',
	'particles_opaque',
	'particles_transparent',
	'ground',
	'user_interface', 
]

NULL = Surface((BLOCK_SIZE,BLOCK_SIZE))

player_attack:tuple[Surface,...]
player_death:tuple[Surface,...]
player_destruction:tuple[Surface,...]
player_idle:tuple[Surface,...]
player_run:tuple[Surface,...]
player_walk:tuple[Surface,...]

tnt:tuple[Surface,Surface]

items:dict[str,tuple[Surface,...]] = {}
blocks:dict[str,tuple[Surface,...]] = {}

entities:PATH_DICT_TYPE = {} #this will be totaly, and dynamically created by the order of the filing system

entity_arrow:Surface
enitity_spirit_idle:tuple[Surface,...]

particles_opaque:dict[str,Surface]
particles_transparent:dict[str,Surface]  

ground:dict[str,Surface]
user_interface:PATH_DICT_TYPE

### HELPER FUNCTIONS ###
def getFolders(path:str):
	for f in scandir(GAME_PATH+path):
		if f.is_dir():
			yield f.path.split('\\')[-1]
def getFiles(path:str):
	for f in scandir(GAME_PATH+path):
		if f.is_file():
			yield f.path.split('\\')[-1]
def isImage(path:str):
	return path.split('.')[-1] in {'png','jpg','jpeg','bmp'}
### END HELPER FUNCTIONS ###


##############################
### IMAGE IMPORT FUNCTIONS ###
##############################

def importTexture(path:str,alpha = True,size:None|tuple[int,int] = None):
	full_path = GAME_PATH + path
	image_surf = load(full_path)
	## Handle image conversion
	image_surf = image_surf.convert_alpha() if alpha else image_surf.convert()
	## Handle Resizing
	if size is not None:
		image_surf = scale(image_surf,size)
	return image_surf

def importFolders(path:str,alpha=True,size:None|tuple[int,int] = None):
	surfs:dict[str,Surface] = {}
	for _root,_dirs,img_files in walk(GAME_PATH + path):
		for image in filter(isImage ,img_files):
			full_path = _root + '\\' + image
			image_surf = load(full_path)
			#remove the file type suffix
			image = '.'.join(image.split('.')[:-1]) 
			## Handle image conversion
			image_surf = image_surf.convert_alpha() if alpha else image_surf.convert()
			## Handle Resizing
			if size is not None:
				image_surf = scale(image_surf,size)
			assert image not in surfs, 'duplicate fount in files: '  + image
			surfs[image] = image_surf

	assert len(surfs),'Empty Texture Path: '+path
	return surfs

def recursivelyImportPath(path:str) -> PATH_DICT_TYPE: # this will assume that images ARE ALPHA and SIZE IS NATIVE
	maths:PATH_DICT_TYPE = {}
	for dir in getFolders(path):
		maths[dir] = recursivelyImportPath(path+'\\'+dir)
	
	for file in getFiles(path):
		if isImage(file):
			maths['.'.join(file.split('.')[:-1])] = importTexture(path+'\\'+file)
	
	return maths

##############################
# END IMAGE IMPORT FUNCTIONS #
##############################

def initInThread():
	import threading
	t = threading.Thread(target=_init,daemon=True)
	t.start()



def _init():
	'''PLAYER ASSETS'''
	global player_attack,player_death,player_destruction,player_idle,player_run,player_walk
	player_attack = tuple(importFolders('Images\\Entities\\player\\attack').values())
	player_death = tuple(importFolders('Images\\Entities\\player\\death').values())
	player_destruction = tuple(importFolders('Images\\Entities\\player\\destruction').values())
	player_idle = tuple(importFolders('Images\\Entities\\player\\idle').values())
	#player_run = tuple(importFolders('Images\\Entities\\player\\run').values())
	player_walk = tuple(importFolders('Images\\Entities\\player\\walk').values())


	global entity_arrow
	entity_arrow = scale(rotate(importTexture('Images\\Entities\\arrow\\default_arrow.png').convert_alpha(),90+47),(BLOCK_SIZE,BLOCK_SIZE))

	global enitity_spirit_idle
	enitity_spirit_idle = tuple(importFolders('Images\\Entities\\spirit\\idle').values())
	
	'''ITEMS ASSETS'''
	for item_folder in getFolders('Images\\Items'):
		items[item_folder] = tuple(importFolders("Images\\Items\\"+item_folder,True,(ITEM_SIZE,ITEM_SIZE)).values())

	'''BLOCK ASSETS'''
	for block_folder in getFolders('Images\\Blocks'):
		items[block_folder] = tuple(importFolders("Images\\Blocks\\"+block_folder,False,(BLOCK_SIZE,BLOCK_SIZE)).values())

	'''ENTITY ASSETS'''
	global entities
	entities = recursivelyImportPath('Images\\Entities')

	'''PARTICLE ASSETS'''
	global particles_opaque, particles_transparent
	particles_opaque = importFolders('Images\\Particles',False,(PARTICLE_SIZE,PARTICLE_SIZE))
	## Get Solild Particles from json
	import json
	with open('Images\\Particles\\Opaque\\Solids.json', 'r') as solids_file:
		for key, value in json.load(solids_file).items():
			particles_opaque.update({key:value})
	del solids_file, key, value #type: ignore
	del json

	particles_transparent = importFolders('Images\\Particles',True,(PARTICLE_SIZE,PARTICLE_SIZE))

	'''GROUND ASSETS'''
	global ground
	ground = importFolders('Images\\Ground')

	global user_interface
	user_interface = recursivelyImportPath('Images\\UI')

	global done_loading
	done_loading = True
	


### EXPORTED FUNCTIONS ###
def flipX(surf:Surface)-> Surface:
	return flip(surf,True,False)

def flipXArray(surfs:tuple[Surface,...]|list[Surface]) -> tuple[Surface,...]:
	return tuple(flipX(s) for s in surfs)
### END EXPORTED FUNCTIONS ###

## Make NULL the recognizable ugly purple
from pygame import draw
draw.rect(NULL,(255,0,255),(0,0,BLOCK_SIZE//2,BLOCK_SIZE//2))
draw.rect(NULL,(255,0,255),(BLOCK_SIZE//2,BLOCK_SIZE//2,BLOCK_SIZE//2,BLOCK_SIZE//2))
del draw

if __name__ == "__main__":
	print('Running Tests on Module Textures')
	import pygame
	pygame.init()
	pygame.display.set_mode((1,1),pygame.NOFRAME)
	_init()
	print('All Tests Passed')





#### LEGACY FUNCTIONS ####
'''

def load_top(path:str):
	surfs:list[Surface] = []
	path = path.replace('/','\\')
	if not path.endswith('\\'): path += '\\' #make sure our path ends with a "\"
	return tuple((load(path+file) for file in listdir(path)))
	



def _compress_and_save():
	from pygame.image import load,save
	p = 'Images\\Entities\\player\\walk'
	o = p.replace("Entities","_LegacyUncompressedImages")
	c = import_folder(p,True,(BLOCK_SIZE,BLOCK_SIZE))
	unc = import_folder(p,True)
	for csurf,usurf,x in zip(c,unc,range(100000)):
		save(csurf,f"{p}\\{x}.png",'png')
		save(usurf,f"{o}\\{x}.png",'png')
'''