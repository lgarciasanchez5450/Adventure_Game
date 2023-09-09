from os import walk
from os.path import dirname,realpath
from pygame.image import load
from pygame.transform import scale,flip,rotate
from pygame import Surface


def PATH():
  return dirname(realpath(__file__)) + '\\'

texture:dict[str,Surface] = {}
def scale_image(surface,newSize):
	return scale(surface,newSize)
accepted_image_extentions = {'png','jpg','jpeg','bmp'}
def is_image(path):
	extension = path.split('.')[-1]
	if extension in accepted_image_extentions:
		return True
	else:
		return False
	
def load_image(path:str):
	return load(PATH()+path)

def import_folder(path,alpha=True,size:None|tuple = None,return_flipped_too:bool = False):
	surface_list = []
	flipped_list = []
	for _root,_dirs,img_files in walk(PATH() + path):
		#print(_root)
		for image in img_files:
			image:str
			if not is_image(PATH() +image): continue #only will get image files
			full_path = _root + '/' + image
			if size is None:
				image_surf = load(full_path).convert_alpha() if alpha else load(full_path).convert()
			else:
				image_surf = scale(load(full_path).convert_alpha(),size) if alpha else scale(load(full_path).convert(),size)
		

			surface_list.append(image_surf)
			if return_flipped_too:
				flipped_list.append(flip(image_surf,True,False))
			texture[image] = image_surf
	if len(surface_list) == 0: print('Empty List! Trying to get',PATH() +path)

	if return_flipped_too:
		return surface_list, flipped_list
	else:
		return surface_list
	

from Constants import BLOCK_SIZE,PARTICLE_SIZE,WIDTH,HEIGHT,HALFHEIGHT,HALFWIDTH,ITEM_SIZE
import memory_profiler
def init():
	import_folder('Images/objects')
	import_folder('Images/items',True,(ITEM_SIZE,ITEM_SIZE))
	import_folder('Images/blocks',False,(BLOCK_SIZE,BLOCK_SIZE))
	s = Surface((PARTICLE_SIZE,PARTICLE_SIZE))
	s.fill('red')
	texture['death.png'] = s
	s = Surface((PARTICLE_SIZE,PARTICLE_SIZE))
	s.fill('white')
	texture['white.png'] = s
	s = Surface((PARTICLE_SIZE,PARTICLE_SIZE))
	s.fill('grey')
	texture['grey.png'] = s

	del s


if __name__ == "__main__":
	print('Running Tests on Module Textures')
	import pygame
	pygame.init()
	pygame.display.set_mode((1,1),pygame.NOFRAME)
	init()
	print('All Tests Passed')