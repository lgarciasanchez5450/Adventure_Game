#idea. let the game simply take items in and out of the draw queue while the camera only repeatedly draws it
import pygame,game_math,Time
from typing import Literal, Callable
from Constants import BLOCK_SIZE
from Input import m_pos_normalized
import moderngl
from array import array
from Events import add_OnResize, call_OnResize
from pygame import Surface
from game_math import floor
from Game_Typing import ImplementsDraw, assert_type
#####Variables#####

##### OPENGL MAGIC #####

HITBOX_COLOR:tuple[int,int,int] = (200,100,100) # a light red
ctx:moderngl.Context 
quad_buffer:moderngl.Buffer


def get_shader(path:str) -> str:
    with open(path,'r') as file:
        return file.read()


program:moderngl.Program
render_object:moderngl.VertexArray
opengl_screen:moderngl.Texture

def create_new_render_object(vertex_path,frag_path,size:tuple[float,float] = (1,1),offset = (0,0)):
    global ctx
    program = ctx.program(vertex_shader=get_shader(vertex_path), fragment_shader=get_shader(frag_path))
    vbo = ctx.buffer(data = array('f',[
    -1.0 * size[0]+offset[0] , 1.0 * size[1]+offset[1], 0.0, 0.0,
     1.0 * size[0]+offset[0], 1.0 * size[1]+offset[1], 1.0, 0.0,
    -1.0 * size[0]+offset[0], -1.0 * size[1]+offset[1], 0.0, 1.0,
    1.0 * size[0]+offset[0], -1.0 * size[1]+offset[1], 1.0, 1.0,    
    ]))
    render_object = ctx.vertex_array(program,[(vbo,'2f 2f', 'vert', 'texcoord')],mode=moderngl.TRIANGLE_STRIP)
    return program,render_object

def surf_to_texture(surf:Surface):
    global ctx
    tex = ctx.texture(surf.get_size(),4)
    tex.filter = (moderngl.NEAREST,moderngl.NEAREST) #type: ignore
    tex.swizzle = 'BGRA'
    tex.write(surf.get_view('1')) 
    return tex
##### END OPENGL MAGIC #####



#Display Constants
screen:Surface
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
focus = game_math.Vector2.zero
halfscreensize:game_math.Vector2
screen_size:game_math.Vector2
camera_pos = focus.copy()
tracking_system:Literal['fixed','smooth'] = 'fixed'
mouse_assisted:bool = False
#variables for smooth tracking
smooth_speed = 4
maximum_camera_distance = 2
using_max_camera_distance = False
minimum_camera_distance = 0.2
using_min_camera_distance = False
mouse_pull_strength = 1/3
width:int
height:int
def init(display:Surface):
    global screen,WIDTH,HEIGHT,HALFWIDTH,HALFHEIGHT,halfscreensize,width,height,screen_size,HALF_HEIGHT_OVER_BLOCK_SIZE,HALF_WIDTH_OVER_BLOCK_SIZE

    screen = display
    WIDTH,HEIGHT = width,height = screen.get_size()
    HALFWIDTH = WIDTH//2
    HALFHEIGHT = HEIGHT//2
    HALF_HEIGHT_OVER_BLOCK_SIZE = HEIGHT/(2 * BLOCK_SIZE)
    HALF_WIDTH_OVER_BLOCK_SIZE = WIDTH/(2 * BLOCK_SIZE)
    halfscreensize = game_math.Vector2(HALFWIDTH,HALFHEIGHT)
    screen_size = game_math.Vector2(width-1,height-1)

    global ctx, quad_buffer, vertex_src, fragment_src

    ctx = moderngl.create_context()
    ctx.enable(moderngl.BLEND) # type: ignore
    ctx.blend_func = ctx.SRC_ALPHA, ctx.ONE_MINUS_SRC_ALPHA # type: ignore
    quad_buffer = ctx.buffer(data = array('f',[
        #position(x,y) uv coords (x,y)
        -1.0 , 1.0, 0.0, 0.0,
        1.0, 1.0, 1.0, 0.0,
        -1.0, -1.0, 0.0, 1.0,
        1.0, -1.0, 1.0, 1.0,
        
    ]))
    with open('shaders/everything.vert','r') as f:
        vertex_src = f.read()

    with open('shaders/game.frag','r') as f:
        fragment_src = f.read()

    global program, render_object, opengl_screen
        
    program = ctx.program(vertex_shader=vertex_src, fragment_shader=fragment_src)
    render_object = ctx.vertex_array(program,[(quad_buffer,'2f 2f', 'vert', 'texcoord')],mode = moderngl.TRIANGLE_STRIP)
    opengl_screen = ctx.texture((WIDTH,HEIGHT),4)
    opengl_screen.filter = moderngl.BLEND,moderngl.BLEND # type: ignore
    opengl_screen.swizzle = 'BGRA'
    opengl_screen.use(0)

def onResize(_width,_height):
    global width,height,screen_size
    width, height = _width, _height
    halfscreensize.x = _width//2
    halfscreensize.y = _height//2
    screen_size.x = width-1
    screen_size.y = height-1
add_OnResize(onResize)
def ui_draw_method(object,order:int = 0):
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
    def __init__(self,surface:Surface,position:game_math.Vector2,offset:tuple[int,int]):
        assert_type(position,game_math.Vector2)
        self.surf = surface
        self.pos = position
        self.offset = offset

    @classmethod
    def inferOffset(cls,surface:Surface,position:game_math.Vector2):
        return cls(surface,position,(-surface.get_width()//2,-surface.get_height()//2))

    def copy(self):
        return CSurface(self.surf,self.pos.copy(),self.offset)


NullCSurface = CSurface(Surface((0,0)),game_math.Vector2.zero,(0,0))

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

def set_focus(position:game_math.Vector2):
    global focus,camera_pos #this works because unlike C, python 'globals' are global to a module, not across all files, unless ofcourse you add it to the builtins module
    focus = position # type: ignore
    if tracking_system == 'fixed':
        camera_pos = focus

def stop_focus():
    global focus
    focus = focus.copy()

def set_camera_position(position:game_math.Vector2):
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

def set_camera_convergence_speed(speed:float|int):
    global smooth_speed
    smooth_speed = speed

'''Getting functions'''
def get_camera_convergence_speed() -> float|int:
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

def add_collider(collider:game_math.Collider):
    assert collider not in collider_queue, "The same collider was loaded into the camera twice!"
    collider_queue.append(collider)

def remove_collider(collider:game_math.Collider):
    collider_queue.remove(collider)       
    
def remove(camera_surface:CSurface) -> None:
    assert camera_surface in queue, "CSurface not found in queue"
    queue.remove(camera_surface)




def update():
    global camera_offset_x,camera_offset_y,effective_camera_pos,camera_pos
    if tracking_system == 'smooth':
        dist = focus - camera_pos 
        distance_squared = dist.magnitude_squared()
        if using_max_camera_distance and distance_squared > maximum_camera_distance * maximum_camera_distance:
            extra_distance = game_math.sqrt(distance_squared) - maximum_camera_distance
            displacement = dist.asMagnitudeOf(extra_distance)
            camera_pos += displacement
        elif using_min_camera_distance and distance_squared < minimum_camera_distance * minimum_camera_distance:
            pass
        else:
            if using_max_camera_distance:
                dist = dist.asMagnitudeOf(game_math.sqrt(distance_squared) - minimum_camera_distance)
            displacement = dist * (smooth_speed * Time.deltaTime)
            camera_pos += displacement
    elif tracking_system == 'fixed':
        pass
    else:
        raise RuntimeError(f'Tracking System is {tracking_system}, but that is not a valid system') # TODO: in prod this path should never run so it could be deletd
    if mouse_assisted:
        effective_camera_pos = camera_pos + m_pos_normalized*(mouse_pull_strength/BLOCK_SIZE)
    camera_offset_x = (effective_camera_pos.x*BLOCK_SIZE).__floor__()
    camera_offset_y = (effective_camera_pos.y*BLOCK_SIZE).__floor__()
    


def screen_position(pos:game_math.Vector2):
    #return (floor(pos.x*BLOCK_SIZE-floor(effective_camera_pos.x*BLOCK_SIZE)+HALFWIDTH) * (width/ WIDTH),floor(pos.y*BLOCK_SIZE-floor(effective_camera_pos.y*BLOCK_SIZE)+ HALFHEIGHT)* ( width/WIDTH)) 
    return game_math.Vector2((pos.x*BLOCK_SIZE-camera_offset_x+HALFWIDTH),(pos.y*BLOCK_SIZE-camera_offset_y+ HALFHEIGHT))



def screen_position_normalized(world_pos:game_math.Vector2):
    return (((world_pos-effective_camera_pos) ).vector_mul(game_math.Vector2(width/WIDTH,height/HEIGHT)) ).vector_mul((halfscreensize).inverse)

def world_position(screen_pos:game_math.Vector2):
    return (screen_pos - halfscreensize) / BLOCK_SIZE + effective_camera_pos

def world_position_from_normalized(screen_normalized_pos:game_math.Vector2):
    return game_math.Vector2(screen_normalized_pos.x * HALF_WIDTH_OVER_BLOCK_SIZE + effective_camera_pos.x, screen_normalized_pos.y *HALF_HEIGHT_OVER_BLOCK_SIZE + effective_camera_pos.y )
    return screen_normalized_pos.vector_mul(game_math.Vector2(WIDTH//2,HEIGHT//2)) / BLOCK_SIZE + effective_camera_pos


'''Helper Functions'''
def _rank_csurface(csurf:CSurface):
    '''Helper function to sort csurface by y position'''
    return csurf.pos.y



'''Drawing Functions'''
#to calculate screen_position (worldpos-playerpos) * BLOCKSIZE + halfwidth?halfheight + offset(if any)
def draw_hitbox(collider:game_math.Collider):
    x,y = collider.topleft
    pygame.draw.rect(screen,HITBOX_COLOR,pygame.Rect(x*BLOCK_SIZE-camera_offset_x+HALFWIDTH,y*BLOCK_SIZE-camera_offset_y+HALFHEIGHT,collider.width*BLOCK_SIZE,collider.height*BLOCK_SIZE),1)

def blit(surface,position,s_offset_x = 0, s_offset_y = 0):
    wx,wy = position
    screen.blit(surface,((wx-effective_camera_pos.x)*BLOCK_SIZE+HALFWIDTH+s_offset_x,(wy-effective_camera_pos.y)*BLOCK_SIZE+ HALFHEIGHT+s_offset_y))


def blit_csurface(csurface:CSurface):
    screen.blit(csurface.surf,((csurface.pos.x*BLOCK_SIZE-camera_offset_x+HALFWIDTH+csurface.offset[0]).__floor__(),(csurface.pos.y*BLOCK_SIZE-camera_offset_y+ HALFHEIGHT+csurface.offset[1]).__floor__()))




def resize_screen(width:int,height:int) -> Surface:
    call_OnResize(width,height)
    return pygame.display.set_mode((width,height),pygame.OPENGL|pygame.DOUBLEBUF|pygame.RESIZABLE)

def sorted_draw_from_queue():
    queue.sort(key = _rank_csurface)
    for thing in queue:
        blit_csurface(thing)
        
def draw_collider_queue():
    for thing in collider_queue:
        draw_hitbox(thing)

def draw_background():
    for thing in background_queue:
        blit_csurface(thing)

def draw_UI():
    for ui,_ in UIs:
        ui.draw()

def translate_to_opengl():
    opengl_screen.write(screen.get_view('1')) 
    render_object.render()

def flip():
    pygame.display.flip()