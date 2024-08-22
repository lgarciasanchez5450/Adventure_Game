from typing import Literal, Callable
from Constants import BLOCK_SIZE,HALFWIDTH,HALFHEIGHT
from Utils.Math.Vector import Vector2
from Utils.Math.Collider import Collider
import pygame,Time,Window
from pygame import Surface
from math import sqrt
from InputGame import m_pos_normalized
from Events import add_OnResize, call_OnResize
from Game_Typing import ImplementsDraw, assert_type
#####Variables#####


HITBOX_COLOR:tuple[int,int,int] = (200,100,100) # a light red

#Display Constants
WIDTH:int
HEIGHT:int
HALFWIDTH:int 
HALFHEIGHT:int
HALF_WIDTH_OVER_BLOCK_SIZE:float
HALF_HEIGHT_OVER_BLOCK_SIZE:float

queue = []
collider_queue = []
background_queue = []
UIs:list[tuple[ImplementsDraw,int]] = []
focus = Vector2.zero()
halfscreensize:Vector2
screen_size:Vector2
camera_pos = focus.copy()
tracking_system:Literal['fixed','smooth'] = 'fixed'
mouse_assisted:bool = False
mouse_pull_strength = 0
#variables for smooth tracking
smooth_speed = 4
max_camera_distance = 2
min_camera_distance = 0
width:int
height:int
def onResize(_width,_height):
    global width,height,screen_size,HALFWIDTH,HALFHEIGHT
    width, height = _width, _height
    halfscreensize.x = _width//2
    halfscreensize.y = _height//2
    screen_size.x = width-1
    screen_size.y = height-1
    HALFWIDTH = _width
    HALFHEIGHT = _height
add_OnResize(onResize)
def ui_draw_method(object:ImplementsDraw,order:int = 0):
    UIs.append((object,order))
    UIs.sort(key = lambda x:x[1])
    return object

def ui_draw_method_remove(object):
    for i,(obj,order) in enumerate(UIs):
        if (obj is object):
            UIs.pop(i)
            return

class CSurface:
    __slots__ = 'surf','pos' ,'offset'
    def __init__(self,surface:Surface,position:Vector2,offset:tuple[int,int]):
        self.surf = surface
        self.pos = position
        self.offset = offset

    @classmethod
    def inferOffset(cls,surface:Surface,position:Vector2):
        return cls(surface,position,(-surface.get_width()//2,-surface.get_height()//2))

    def copy(self):
        return CSurface(self.surf,self.pos.copy(),self.offset)

NullCSurface = CSurface(Surface((0,0)),Vector2.zero(),(0,0))

'''Setting functions'''
def set_tracking(system:str):
    assert system in ('fixed','smooth')
    global tracking_system,camera_pos,effective_camera_pos
    match system:
        case 'fixed':
            camera_pos = focus
        case 'smooth':
            camera_pos = camera_pos.copy()
    tracking_system = system
    if not mouse_assisted:
        effective_camera_pos = camera_pos

def set_focus(position:Vector2):
    global focus,camera_pos #this works because unlike C, python 'globals' are global to a module, not across all files, unless ofcourse you add it to the builtins module
    focus = position # type: ignore
    if tracking_system == 'fixed':
        camera_pos = focus

def stop_focus():
    global focus
    focus = focus.copy()

def set_camera_position(position:Vector2):
    global camera_pos
    camera_pos = position

def set_mouse_assist(assist:bool):
    global effective_camera_pos,mouse_assisted
    if not assist:
        effective_camera_pos = camera_pos
    mouse_assisted = assist
    
def set_mouse_pull_strength(strength:float):
    global mouse_pull_strength
    mouse_pull_strength = strength*strength / (strength + 20)

def set_camera_convergence_speed(speed:float):
    global smooth_speed
    smooth_speed = speed

'''Getting functions'''
def get_camera_convergence_speed() -> float:
    return smooth_speed

'''Functions used by Sprites'''
def add_background(camera_surf:CSurface):
    global background_queue
    assert camera_surf not in background_queue,"The same csurface was loaded into the camera twice!"
    background_queue.append(camera_surf)

def remove_background(camera_surf:CSurface):
    global background_queue
    background_queue.remove(camera_surf)

def add(camera_surface:CSurface):
    global queue
    assert camera_surface not in queue,"The same csurface was loaded into the camera twice!"
    queue.append(camera_surface)

def remove(camera_surface:CSurface) -> None:
    assert camera_surface in queue, "CSurface not found in queue"
    queue.remove(camera_surface)

def add_collider(collider:Collider):
    assert collider not in collider_queue, "The same collider was loaded into the camera twice!"
    collider_queue.append(collider)

def remove_collider(collider:Collider):
    collider_queue.remove(collider)       

def update():
    global camera_offset_x,camera_offset_y,camera_pos
    if tracking_system == 'smooth':
        dist = focus - camera_pos 
        sqr_dist = dist.magnitude_squared()
        if  sqr_dist > max_camera_distance * max_camera_distance:
            extra_distance = sqrt(sqr_dist) - max_camera_distance
            camera_pos += dist.asMagnitudeOf(extra_distance)
        elif sqr_dist < min_camera_distance * min_camera_distance:
            pass
        else:
            dist = dist.asMagnitudeOf(sqrt(sqr_dist) - min_camera_distance)
            camera_pos += dist * (smooth_speed * Time.deltaTime)
    elif tracking_system == 'fixed':
        pass
    else:
        raise RuntimeError(f'Tracking System is {tracking_system}, but that is not a valid system') # TODO: in prod this path should never run so it could be deletd
    if mouse_assisted:
        # effective_camera_pos = camera_pos + m_pos_normalized*(mouse_pull_strength/BLOCK_SIZE) # old buggy
        #BUG - when m_pos_normalized * mouse_pull_strength is close to an integer, everything is fine but as the ending approaches .5 the player appears fuzzy, 
        #as a fix the m_pos_normalized will be floored 
        camera_offset_x = (camera_pos.x*BLOCK_SIZE + (m_pos_normalized.x*mouse_pull_strength).__floor__()).__floor__() #the inner __floor__ IS NECESSARY
        camera_offset_y = (camera_pos.y*BLOCK_SIZE + (m_pos_normalized.y*mouse_pull_strength).__floor__()).__floor__()
    else:
        camera_offset_x = (camera_pos.x*BLOCK_SIZE).__floor__()
        camera_offset_y = (camera_pos.y*BLOCK_SIZE).__floor__()

def screen_position(pos:Vector2):
    #return (floor(pos.x*BLOCK_SIZE-floor(effective_camera_pos.x*BLOCK_SIZE)+HALFWIDTH) * (width/ WIDTH),floor(pos.y*BLOCK_SIZE-floor(effective_camera_pos.y*BLOCK_SIZE)+ HALFHEIGHT)* ( width/WIDTH)) 
    return Vector2((pos.x*BLOCK_SIZE-camera_offset_x+HALFWIDTH),(pos.y*BLOCK_SIZE-camera_offset_y+ HALFHEIGHT))

def screen_position_normalized(world_pos:Vector2):
    return (((world_pos-effective_camera_pos) )@(Vector2(width/WIDTH,height/HEIGHT)) ) @((halfscreensize).inverse)

def world_position(screen_pos:Vector2):
    return (screen_pos - halfscreensize) / BLOCK_SIZE + effective_camera_pos

def world_position_from_normalized(screen_normalized_pos:Vector2):
    return Vector2(screen_normalized_pos.x * HALF_WIDTH_OVER_BLOCK_SIZE + effective_camera_pos.x, screen_normalized_pos.y *HALF_HEIGHT_OVER_BLOCK_SIZE + effective_camera_pos.y )
    return screen_normalized_pos.vector_mul(Vector2(WIDTH//2,HEIGHT//2)) / BLOCK_SIZE + effective_camera_pos


'''Helper Functions'''
def _rank_csurface(csurf:CSurface):
    '''Helper function to sort csurface by y position'''
    return csurf.pos.y



'''Drawing Functions'''
#to calculate screen_position (worldpos-playerpos) * BLOCKSIZE + halfwidth?halfheight + offset(if any)
def draw_hitbox(collider:Collider):
    x,y = collider.topleft
    pygame.draw.rect(Window.window.world_surface,HITBOX_COLOR,pygame.Rect((x*BLOCK_SIZE-camera_offset_x+HALFWIDTH).__floor__(),(y*BLOCK_SIZE-camera_offset_y+HALFHEIGHT).__floor__(),collider.width*BLOCK_SIZE,collider.height*BLOCK_SIZE),1)

def blit(surface,position,s_offset_x = 0, s_offset_y = 0):
    wx,wy = position
    Window.window.world_surface.blit(surface,((wx-effective_camera_pos.x)*BLOCK_SIZE+HALFWIDTH+s_offset_x,(wy-effective_camera_pos.y)*BLOCK_SIZE+ HALFHEIGHT+s_offset_y))


def blit_csurface(csurface:CSurface):
    Window.window.world_surface.blit(csurface.surf,((csurface.pos.x*BLOCK_SIZE-camera_offset_x+HALFWIDTH+csurface.offset[0]).__floor__(),(csurface.pos.y*BLOCK_SIZE-camera_offset_y+ HALFHEIGHT+csurface.offset[1]).__floor__()))
# def resize_screen(width:int,height:int) -> Surface:
#     call_OnResize(width,height)
#     return pygame.display.set_mode((width,height),pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZEABLE)

def draw_sprites():
    queue.sort(key = _rank_csurface)
    for thing in queue:
        blit_csurface(thing)
        
def draw_colliders():
    for thing in collider_queue:
        draw_hitbox(thing)

def draw_background():
    for thing in background_queue:
        blit_csurface(thing)

def draw_UI():
    for ui,_ in UIs:
        ui.draw(Window.window.world_surface)


    
