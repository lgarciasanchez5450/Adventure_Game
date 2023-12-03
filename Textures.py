from Constants import BLOCK_SIZE,PARTICLE_SIZE,WIDTH,HEIGHT,HALFHEIGHT,HALFWIDTH,ITEM_SIZE
from os import walk,listdir
from pygame.image import load
from pygame.transform import scale,flip,rotate
from pygame import Surface
from Constants.Items import *
from game_math import GAME_PATH

NULL = Surface((BLOCK_SIZE,BLOCK_SIZE))
## Make NULL the recognizable ugly purple
from pygame import draw
draw.rect(NULL,(255,0,255),(0,0,BLOCK_SIZE//2,BLOCK_SIZE//2))
draw.rect(NULL,(255,0,255),(BLOCK_SIZE//2,BLOCK_SIZE//2,BLOCK_SIZE//2,BLOCK_SIZE//2))
del draw

player_attack:tuple[Surface,...]
player_death:tuple[Surface,...]
player_destruction:tuple[Surface,...]
player_idle:tuple[Surface,...]
player_run:tuple[Surface,...]
player_walk:tuple[Surface,...]

tnt:tuple[Surface,Surface]

items:dict[str,tuple[Surface,...]] = {}
blocks:dict[str,tuple[Surface,...]] = {}

entity_arrow:Surface
enitity_spirit_idle:tuple[Surface,...]


def scale_image(surface,newSize):
	return scale(surface,newSize)
def is_image(path:str):
	return path.split('.')[-1].lower() in {'png','jpg','jpeg','bmp'}

def importTexture(path:str,alpha = True,size:None|tuple[int,int] = None):
	full_path = GAME_PATH + path
	image_surf = load(full_path)
	## Handle image conversion
	image_surf = image_surf.convert_alpha() if alpha else image_surf.convert()
	## Handle Resizing
	if size is not None:
		image_surf = scale(image_surf,size)
	return image_surf


def importFolderRecursive(path:str,alpha=True,size:None|tuple[int,int] = None):
	surfs:dict[str,Surface] = {}
	for _root,_dirs,img_files in walk(GAME_PATH + path):
		for image in filter(lambda x: x.split('.')[-1] in {'png','jpg','jpeg','bmp'} ,img_files):
			full_path = _root + '\\' + image
			print(full_path)
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
	assert len(surfs),'Empty Texture Path!'
	return surfs

def init():

	'''PLAYER ASSETS'''
	global player_attack,player_death,player_destruction,player_idle,player_run,player_walk
	player_attack = tuple(importFolderRecursive('Images\\Entities\\player\\attack').values())
	player_death = tuple(importFolderRecursive('Images\\Entities\\player\\death').values())
	player_destruction = tuple(importFolderRecursive('Images\\Entities\\player\\destruction').values())
	player_idle = tuple(importFolderRecursive('Images\\Entities\\player\\idle').values())
	player_run = tuple(importFolderRecursive('Images\\Entities\\player\\run').values())
	player_walk = tuple(importFolderRecursive('Images\\Entities\\player\\walk').values())

	'''TNT ASSETS'''
	global tnt
	tnt = (importTexture('Images\\objects\\tnt.png',False),importTexture('Images\\objects\\tnt1.png',False))

	global entity_arrow
	entity_arrow = scale(rotate(importTexture('Images/Entities/arrow/default_arrow.png').convert_alpha(),90+47),(BLOCK_SIZE,BLOCK_SIZE))

	global enitity_spirit_idle
	enitity_spirit_idle = tuple(importFolderRecursive('Images\\Entities\\spirit\\idle').values())
	
	'''ITEMS ASSETS'''
	for item_folder in listdir(GAME_PATH + 'Images\\Items'):
		items[item_folder] = tuple(importFolderRecursive("Images\\Items\\"+item_folder,True,(ITEM_SIZE,ITEM_SIZE)).values())

	for item_folder in listdir(GAME_PATH + 'Images\\Items'):
		items[item_folder] = tuple(importFolderRecursive("Images\\Items\\"+item_folder,True,(ITEM_SIZE,ITEM_SIZE)).values())

	s = Surface((PARTICLE_SIZE,PARTICLE_SIZE))
	s.fill('red')
	texture['death.png'] = s
	s = Surface((PARTICLE_SIZE,PARTICLE_SIZE))
	s.fill('white')
	texture['white.png'] = s
	s = Surface((PARTICLE_SIZE,PARTICLE_SIZE))
	s.fill('grey')
	texture['grey.png'] = s
	load_item_anim(ITAG_BOW)
	load_item_anim(ITAG_ARROW)
	texture['entity_arrow.png'] = scale(rotate(load_image('Images/Entities/arrow/default_arrow.png').convert_alpha(),90+47),(BLOCK_SIZE,BLOCK_SIZE))
	del s

def importItemTextures():
	import os
	from game_math import getNamesOfObject
	from Constants import Items
	path = f'{GAME_PATH}Images\\Items'
	items =[Items.__dict__[n] for n in getNamesOfObject(Items) if n.startswith("ITAG")]
	item_texture_implemented = os.listdir(path)
	missing_items = []
	for item in items:
		if item not in item_texture_implemented:
			missing_items.append(item)

	print("Items Without Textures:", missing_items)


	print("Items Without Textures:", missing_items)
if __name__ == '__main__':
	importItemTextures()
	quit()

def flipX(surf:Surface)-> Surface:
	return flip(surf,True,False)

def flipXArray(surfs:tuple[Surface,...]|list[Surface]) -> tuple[Surface,...]:
	return tuple(flipX(s) for s in surfs)

if __name__ == "__main__":
	print('Running Tests on Module Textures')
	import pygame
	pygame.init()
	pygame.display.set_mode((1,1),pygame.NOFRAME)
	print(len(load_item_anim('bow')) == 0)
	init()
	print('All Tests Passed')







#### HELPER FUNCTIONS ####

def load_top(path:str):
	surfs:list[Surface] = []
	path = path.replace('/','\\')
	if not path.endswith('\\'): path += '\\' #make sure our path ends with a "\"
	return tuple((load(path+file) for file in listdir(path)))
	



'''
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