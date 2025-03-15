from Constants import *
import Perlin
import rng
from pygame import display, Surface
from os import walk,mkdir
from os.path import dirname,realpath
import json
def PATH():
  return dirname(realpath(__file__)) + '\\'
STRUCTURE_VOID = 0
PLACE_DECORATION = 1
PLACE_GRASS = 2
block_range = [0,2]

import Application.Textures as Textures
import Application.Game.ground as g
import pygame
if __name__ =='__main__':

    import pygame
    pygame.init()
    size = 32
    screen = pygame.display.set_mode((700,500))
    font = pygame.font.SysFont("Arial",25,True)
texs = ['Images/structure_void.png','','Images/tiles/grasstiled.png','Images/wooden_plank.png']
decor = pygame.Surface((size,size))
decor.set_colorkey((0,0,0))
decor.blit(font.render("D",True,'white'),(0,0))
ground = [
    Textures.scale(Textures._load('Images/structure_void.png'),(size,size)),
    decor,
    Textures.scale(Textures._load('Images/Ground/'+g.Settings.GROUND_TEXTURE_BY_ID[g.Dirt.id] + ".png"),(size,size)),
]
    
blocks = ground


class Decoration:
    pass
import numpy as np
def arrary_to_dict(array:np.ndarray):
    myDict = {}

    myDict['shape'] = array.shape
    if len(array.shape) == 1:
        for index,val in enumerate(array):
            myDict[index] = val
    elif len(array.shape) == 2:
        for y, row in enumerate(array):
            for x, val in enumerate(row):
                myDict[';'.join([str(x),str(y)])] = int(val)
    else:
        raise RuntimeError(f"This type of array is not supported! -> Shape:{array.shape}")
    return myDict
def dict_to_array(dict:dict):
    try:
        shape = dict['shape']
    except:
        raise RuntimeError("Dictionary did not have required key <'shape'>") 
    
    array = np.ndarray(shape,np.int16)
    if len(shape) == 1:
        for i in range(shape[0]):
            array[i] = dict[i]
    elif len(shape) == 2:
        for y in range(shape[0]):
            for x in range(shape[1]):
                array[y][x] = dict[';'.join([str(x),str(y)])]
    else:
        raise RuntimeError(f"This type of array is not supported! -> Shape:{array.shape}")
    return array 

def is_struct(path:str):
    return path.endswith('.struct')
def load_struct(path):
    if not is_struct(path): raise RuntimeError("This path is not a struct!")
    with open(PATH() +path,'r') as file:
        main_dict = json.load(file)
        ground = dict_to_array(main_dict['ground'])
        blocks = dict_to_array(main_dict['blocks'])
        return ground,blocks
    
def struct_exists(path):

    if not is_struct(path): return False
    
    try: 
        with open(PATH() + path,'r') as f:
            pass
        return True
    except FileNotFoundError:
        return False


def file_path_exists(path):
    dirs = path.split('\\')[:-1] # the [:-1] is only needed to take away the file.extension at the end
    passed = False
    i = 0
    for root,_dirs,_files in walk(dirs[0],topdown=True):
        if dirs[i] == root:
            if i + 1 == len(dirs):
                passed = True
                break
            i += 1
        else:
            i = 0 
    return passed
    

def save_struct(path:str,ground:np.ndarray,blocks:np.ndarray,):
    if not is_struct(path): raise RuntimeError("Path must end in '.struct'! ")
    if ground.shape != blocks.shape: raise RuntimeError("Ground and blocks should be the same size")
    if not path.startswith(PATH()): 
        path = PATH() + path
    dirs = path.split('\\')[:-1] 
    dirs[0] = '\\'.join([dirs[0],dirs.pop(1)])
    #from os.path import isdir
    from os import listdir
    
    for i,dir in enumerate(dirs,start = 1):
        if i == len(dirs): # we are comparing the last item
            break
        if dirs[i] in listdir('\\'.join(dirs[:i])):
            pass
        else:
            mkdir('\\'.join(dirs[:i+1]))


    ground_dict = arrary_to_dict(ground)
    blocks_dict = arrary_to_dict(blocks)
    main_dict = {"ground":ground_dict,"blocks":blocks_dict}
    with open(path,'w+') as file:
        json.dump(main_dict,file,indent = 4)

def get_path_to_struct(type,variant):
    return PATH() + '/'.join([type,variant,'model.struct']) 

class Structure:
    blocks:np.ndarray
    ground:np.ndarray
    def __init__(self,type,variant,x,y,rotation):
        self.type = type
        self.variant = variant
        self.x = x
        self.y = y
        if struct_exists(self.path):
            self.load()
        else:
            print('this struct does not currently exist in storage\ncreating a copy in path:',self.path)
            self.save()
            self.load()
        self.rotation = rotation
        self.e_ground = self.get_ground()
        self.e_blocks = self.get_blocks()
        
    
    def load(self):
        self.ground,self.blocks = load_struct(self.path)
        self.rotation  = 0
        return self
    
    def save(self):
        save_struct(self.path,self.ground,self.blocks)

    @property
    def path(self):
        return '\\'.join(['structures',self.type,self.variant,'model.struct'])
    
    @property
    def rotation(self):
        return self._rotation
    
    @rotation.setter
    def rotation(self,newVal):
        self._rotation = newVal
        self.e_ground = self.get_ground()
        self.e_blocks = self.get_blocks() 

    def get_blocks(self):
        return np.rot90(self.blocks,-self.rotation)

    def get_ground(self):
        return np.rot90(self.ground,-self.rotation)

class House(Structure):
    blocks = np.zeros((5,8),np.int16)
    ground = np.zeros((5,8),np.int16)
    def __init__(self,x,y,rotation):
        self.blocks = self.__class__.blocks.copy()
        self.ground = self.__class__.ground.copy()
        super().__init__('house','large',x,y,rotation)

    

class Village:
    def __init__(self,seed:int,x:int,y:int):
        self.seed = seed
        self.x = x
        self.y = y
        self.perm = perlin._init(seed)
        rng.pcg_set_seed(seed + (perlin.scramble(x)& 0xFFFF) +(perlin.scramble(y)& 0xFFFF))
        _x= rng.pcg_less_than(CHUNK_SIZE)
        _y= rng.pcg_less_than(CHUNK_SIZE)
        self.center = (_x,_y)
        self.village = np.zeros((100,100))


        
        
    def post_process_chunk(self,cx,cy,ground,blocks):
        pass

    def isPath(self,x,y):
        n = perlin._noise2_layered(x,y,1,.02,self.perm)
        x= 1-abs(n)
        return x*x*x*x*x*x > .5
        return 1-abs(perlin._noise2_layered(x,y,2,.02,self.perm))

        return False


    def __str__(self):
        return f"Center:{self.center}"

if __name__ =='__main__':

    import pygame
    pygame.init()
    screen = pygame.display.set_mode((700,500))
    font = pygame.font.SysFont("Arial",10,True)

    cam_offset = np.array([screen.get_width()//2,screen.get_height()//2])
    m_movement = False
    structure = Structure('house','large',0,0,0)
    print(structure.ground)
    width = structure.e_blocks.shape[1] * size / 2
    height = structure.e_blocks.shape[0] * size / 2
    draw_ground = True
    block_to_place = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEMOTION:
                if m_movement:
                    cam_offset += np.array(event.rel)
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    
                    m_movement = not m_movement
                    if not m_movement:
                        structure.rotation = 0
                elif event.key == pygame.K_SPACE:
                    draw_ground = not draw_ground
                elif event.key == pygame.K_o:
                    structure.save()
                elif event.key == pygame.K_l:
                    structure.load()
            elif event.type == pygame.MOUSEWHEEL:
                if m_movement:
                    structure.rotation += event.y
                    width = structure.e_blocks.shape[1] * size / 2
                    height = structure.e_blocks.shape[0] * size / 2
                else:
                    block_to_place = min(block_range[1],max(block_range[0],block_to_place + event.y))
                    pygame.display.set_caption(str(block_to_place))
        to_draw = structure.e_ground if draw_ground else structure.e_blocks
        if not m_movement and pygame.mouse.get_pressed()[0]:
            x,y = pygame.mouse.get_pos()
            indexy = int((y-cam_offset[1] + height) // size)
            indexx = int((x-cam_offset[0] + width) // size)
            if draw_ground:
                if 0 <=indexx < structure.ground.shape[1]:
                    if 0 <=indexy < structure.ground.shape[0]:
                        structure.ground[indexy][indexx] = block_to_place
            else:
                if 0 <=indexx < structure.blocks.shape[1]:
                    if 0 <=indexy < structure.blocks.shape[0]:
                        structure.blocks[indexy][indexx] = block_to_place

            
        screen.fill('black')

        for y,row in enumerate(to_draw):
            for x,val in enumerate(row):
                screen.blit(ground[val],(np.array([x,y]) * size - np.array([width,height])+ cam_offset).tolist())

        screen.blit(ground[block_to_place],(0,0))

        pygame.display.flip()


