from Constants import BLOCK_SIZE,PARTICLE_SIZE,WIDTH,HEIGHT,HALFHEIGHT,HALFWIDTH,ITEM_SIZE
from os import walk,listdir
from os.path import dirname,realpath
from pygame.image import load
from pygame.transform import scale,flip,rotate
from pygame import Surface
from Constants.Items import *
from game_math import cache,GAME_PATH

########################################################
#  MAIN DICTIONARY THAT HOLDS ALL TEXTURES USED IN GAME#
texture:dict[str,Surface] = {}
########################################################


item_textures:dict[str,Surface] = {}
entity_textures:dict[str,Surface] = {}
particle_textures:dict[str,Surface] = {}

def scale_image(surface,newSize):
	return scale(surface,newSize)
def is_image(path:str):
	extension = path.split('.')[-1]
	return extension.lower() in {'png','jpg','jpeg','bmp'}

@cache
def load_image(path:str):
	return load(GAME_PATH+path)

@cache
def load_item_anim(tag,alpha=True):
	# the directory path should be as follows:
	# C:\\ ... Adventure_Game\\Images\\items\\<tag>\\
	path = f'{GAME_PATH}Images\\Items\\{tag}'
	item_images = []
	for root,_dirs,files in walk(path):
		for image in files:
			image_path = root + '\\' + image
			print(image_path)
			surf = load(image_path)
			surf = surf.convert_alpha() if alpha else surf.convert()
			item_images.append(surf)
	return item_images

@cache
def load_entity_anim(species:str,subspecies:str = ''):
	'''Will return a dictionary with each key being a folder holding a list of the 
	Images stored in the folders
	Only supports single depth of folders past the entity folder'''
	anims:dict[str,tuple[Surface,...]] = dict()

	path = f"{GAME_PATH}Images\\Entities\\{species}"
	if subspecies != '':#if a subspecies exists then append it to the path 
		path += "\\"+subspecies
		
	dirpath,dirnames,filenames = next(walk(path),(None,None,None))

	if dirnames is None or dirpath is None or filenames is None: #the path doesn't exist
		raise RuntimeError(f"Entity Animation does not exist in path {path}")
	
	#if we reach here then we should be in a directory holding a bunch of folders, each having an array of surfaces
	for folder in dirnames:
		anims[folder] = load_top(f'{path}\\{folder}')
	
	return anims


@cache
def import_folder(path:str,alpha=True,size:None|tuple[int,int] = None,return_flipped_too:bool = False):
	surface_list = []
	flipped_list = []
	for _root,_dirs,img_files in walk(GAME_PATH + path):
		#print(_root)
		for image in img_files:
			image:str
			if not is_image(GAME_PATH +image): continue #only will get image files
			full_path = _root + '/' + image
			print(full_path)
			if size is None:
				image_surf = load(full_path).convert_alpha() if alpha else load(full_path).convert()
			else:
				image_surf = scale(load(full_path).convert_alpha(),size) if alpha else scale(load(full_path).convert(),size)
		

			surface_list.append(image_surf)
			if return_flipped_too:
				flipped_list.append(flip(image_surf,True,False))
			texture[image] = image_surf
	if len(surface_list) == 0: print('Empty List! Trying to get',GAME_PATH +path)

	if return_flipped_too:
		return tuple(surface_list), tuple(flipped_list)
	else:
		return tuple(surface_list)
	

def getSpriteAnimation(entityTag:str,animationName:str): # assumes that the entity's assets have been loaded into the game

	pass
	


def init():
	import_folder('Images\\objects')
	import_folder('Images\\items',True,(ITEM_SIZE,ITEM_SIZE))
	import_folder('Images\\blocks',False,(BLOCK_SIZE,BLOCK_SIZE))
	import_folder('Images\\UI\\hotbar')
	import_folder('Images\\particles\\Transparent',True,(PARTICLE_SIZE,PARTICLE_SIZE))
	import_folder('Images\\particles\\Opaque',False,(PARTICLE_SIZE,PARTICLE_SIZE))
	
	
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