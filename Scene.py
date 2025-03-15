from Scripts.Player import Player
from Scripts.LivingEntity import AliveEntity
from Scripts.ChunkManager import ChunkManager
from Scripts.Physics import Physics
from Scripts.Camera import RasterCamera
import pygame
import numpy as np
from pygame import constants as const
from pygame import Window
import moderngl as mgl
from Scripts.PlayerController import PlayerController
import typing
if typing.TYPE_CHECKING:
    from GameApp import Engine

from collections import deque


# class Cube:
#     face_buffer = None
#     def __init__(self,position,program:mgl.Program,ctx:mgl.Context):
#         verts = [(0,0,0),(0,0,1),(1,0,1),(1,0,0),
#                  (0,1,0),(0,1,1),(1,1,1),(1,1,0)]
#         indices_data = [
#             (2,1,0),(0,3,2), #y-
#             (4,5,6),(6,7,4), #y+
#             (2,3,6),(6,3,7), #x+ side
#             (5,0,1),(4,0,5), #x- side
#             (1,2,5),(6,5,2), #z+ side
#             (4,3,0),(3,4,7), #z- side
#             ]
#         if self.face_buffer is None:

#             face_data = np.array([0,0,0,0,0,0,1,1,1,1,1,1,2,2,2,2,2,2,3,3,3,3,3,3,4,4,4,4,4,4,5,5,5,5,5,5],np.int32)
#             Cube.face_buffer = ctx.buffer(face_data) #type: ignore
#         vertex_data = np.array([verts[i] for triangle in indices_data for i in triangle],np.int32)
#         self.vbo = ctx.buffer(vertex_data)
#         self.program = program
#         self.position = position
#         self.vao = ctx.vertex_array(program,[(self.vbo,'3i','in_position'),(self.face_buffer,'i','in_face')])

#     def render(self):
#         self.program['m_model'].write(glm.translate(self.position)) #type: ignore
#         self.vao.render()

#     def release(self):
#         self.vbo.release()
#         self.vao.release()

def loadVoxels():
    #block_id top_face bottom_face
    #0          

    # with open
    pass


class RasterScene:
    '''For all things diagetic (in game world/space)'''
    def __init__(self,engine:"Engine",window:Window):
        self.engine = engine
        self.ctx = engine.ctx
        self.window = window
        self.program = self.engine.program_manager.getProgram('Assets/shaders/chunk.vert','Assets/shaders/chunk.frag')
        self.player = Player(self,(1,10,1),(0.85,1.8,.85),20,20)
        self.camera = RasterCamera((1,5,1))
        self.player_controller = PlayerController(self.camera,self.player)
        self.chunk_manager = ChunkManager(self)
        self.chunk_manager.recalculateActiveChunks(0,0,0)
        self.physics = Physics(self)
        import time
        t_start = time.perf_counter()
        surf_bottom = pygame.image.load('./Assets/Blocks/dirt.png').convert_alpha()
        surf = pygame.image.load('./Assets/Blocks/grass_side.png').convert_alpha()
        surf_top = pygame.image.load('./Assets/Blocks/grass_top.png').convert_alpha()
        surf = pygame.transform.flip(surf,False,True)
        
        self.tex = self.ctx.texture_array((surf.get_width(),surf.get_height(),3),4,
                                surf_top.get_view('1').raw+surf.get_view('1').raw+surf_bottom.get_view('1').raw
                               )
        self.tex.swizzle = 'BGRA'
        self.tex.anisotropy = 8
        self.tex.build_mipmaps()
        self.tex.filter = mgl.LINEAR_MIPMAP_LINEAR,mgl.NEAREST
        self.program['tex'] = 0
        self.tex.use(0)
        texture_indices = [0,2,1,1,1,1]
        texture_indices.extend((0 for _ in range(1000-len(texture_indices)))) #pad the list with 0's until reach len 1000
        self.program['texture_indices'] = np.array(texture_indices,np.int32)
        t_end = time.perf_counter()
        print('Time to Create Textures:',round(1000*(t_end-t_start),2),'ms')

        self.fpsqueue = deque([0.0]*20,maxlen=20)
        self.fps_sum = sum(self.fpsqueue)

    def update(self):
        if pygame.key.get_just_pressed()[const.K_m]:
            self.chunk_manager.addEntity(self.player)
        if self.window.mouse_grabbed:
            self.player_controller.update()
        if pygame.key.get_just_pressed()[const.K_ESCAPE]:
            if self.window.mouse_grabbed:
                self.window.grab_mouse = False
                pygame.mouse.set_relative_mode(False)
                pygame.mouse.set_pos(self.window.size[0]//2,self.window.size[1]//2)
            else:
                self.window.grab_mouse = True
                pygame.mouse.set_relative_mode(True)
        self.chunk_manager.update()
        self.physics.update()
        # mem_size = sys.getsizeof(self.chunk_manager.chunks)
        # mb = mem_size / 1_000_000
        # avg_chunk_size = mem_size//len(self.chunk_manager.chunks)
        self.fps_sum -=self.fpsqueue.popleft()
        fps = self.engine.time.getFPS()
        self.fps_sum += fps
        self.fpsqueue.append(fps)
        self.window.title = (str(self.fps_sum // 20)+'  '+str(len(self.chunk_manager.chunks)))# +'; ' +f'{mb:.2f}'+' MB'+'; '+f'{avg_chunk_size/1000:.2f} KB')
        # mb = mem_footprint / 1_000_000
        # pygame.display.set_caption(f'{mb:.2f} MB')

    def start(self): ...

    def draw(self):
        self.program['m_proj'].write(self.camera.get_projection_matrix()) #type: ignore
        self.program['m_view'].write(self.camera.get_view_matrix()) #type: ignore
        # self.ctx.clear(0.3,0.75,0.9)
        self.ctx.clear(0.3,0.3,0.35)
        self.chunk_manager.draw()


def color2I(r:int,g:int,b:int):
    return 255 | (r << 16) | (g << 8) | (b) 
# print(color2I((100,100,100)))
# class RayTraceScene:
#     '''For all things diagetic (in game world/space)'''

#     def __init__(self,engine:"Engine"):
#         #Assume that OpenGL Context has been initialized properly
#         #Do *not* assume that pygame display has been initialized

#         self.engine = engine
#         self.ctx = engine.ctx
#         self.camera = RayTraceCamera(self,(-2,2,-2))

#         # Make Compute Shader
#         with open('shaders/simple_raytrace.glsl','r') as file:
#             compute_shader_txt = file.read()
#         self.compute_shader = self.ctx.compute_shader(compute_shader_txt)

#         # Create Output Texture
#         self.output_texture = self.ctx.texture((800,600),4,dtype='f1')
#         self.output_texture.bind_to_image(0, read=False, write=True)
#         self.world_size = 64
#         self.input_texture = self.ctx.texture3d((self.world_size,self.world_size,self.world_size),4,dtype='u1')
#         voxels = self.generate_voxels()
#         print(f'World Size: {len(voxels)/1000:.2f} KB')
#         self.input_texture.write(voxels)

#         self.input_texture.bind_to_image(1,read=True,write=False)


#         # Set Uniforms

#         # Misc
#         self.mouse_captured = False
#         self.keydown_handle = self.engine.event_channel.getHandle(lambda x: x.type==const.KEYDOWN)
#         # self.chunk_manager = RayTraceChunkManager()

#     def generate_voxels(self):
#         '''This function WILL get expensive to calculate!'''
#         arr = np.zeros((self.world_size,self.world_size,self.world_size),dtype=np.uint32)

#         arr[:,:,:] = 0xFF_00_FF_FF
#         return arr.T.tobytes()

#     def capture_mouse(self):
#         self.mouse_captured = True
#         pygame.mouse.set_visible(False)
#         pygame.event.set_grab(True)

#     def release_mouse(self):
#         self.mouse_captured = False
#         pygame.mouse.set_visible(True)
#         pygame.event.set_grab(False)
        
#     def start(self): #Assume that Pygame and OpenGL have been initialized fully
#         self.raytrace_output = pygame.Surface((800,600))
#         # self.compute_shader['camera.position'] = self.camera.pos
#         # self.compute_shader['camera.forward'] = self.camera.forward
#         # self.compute_shader['camera.up'] = self.camera.up
#         # self.compute_shader['camera.right'] = self.camera.right

#     @Tracer().trace
#     def update(self):
#         pygame.display.set_caption(str(self.engine.time.getFPS()))
#         if event:=self.keydown_handle.poll():
#             if event.key == const.K_ESCAPE:
#                 if self.mouse_captured:
#                     self.release_mouse()
#                 else:
#                     self.capture_mouse()
#             elif event.key == const.K_w:
#                 self.camera.pos += self.camera.forward 
#             elif event.key == const.K_d:
#                 self.camera.pos += self.camera.right
#             elif event.key == const.K_s:
#                 self.camera.pos -= self.camera.forward
#             elif event.key == const.K_a:
#                 self.camera.pos -= self.camera.right
#             elif event.key == const.K_SPACE:
#                 self.camera.pos += glm.vec3(0,1,0)
#             elif event.key == const.K_LSHIFT:
#                 self.camera.pos -= glm.vec3(0,1,0)
                

#         if self.mouse_captured:
#             self.camera.update()
#             self.compute_shader['camera.position'] = self.camera.pos
#             self.compute_shader['camera.forward'] = self.camera.forward
#             self.compute_shader['camera.up'] = self.camera.up
#             self.compute_shader['camera.right'] = glm.cross(self.camera.forward,self.camera.up)
            
#             # self.compute_shader['camera_right'] = self.camera.right
            

#             # self.compute_shader['camera.position'] = self.camera.pos
#             # self.compute_shader['camera.forward'] = self.camera.forward
#             # self.compute_shader['camera.up'] = self.camera.up
#             # self.compute_shader['camera.right'] = self.camera.right

#     @Tracer().trace
#     def draw(self,surf:pygame.Surface): #Assume that Pygame and OpenGL have been initialized fully
#         # self.camera.right = glm.cross(self.camera.forward,self.camera.up)
#         # RayTrace(self.camera,self.voxels,self.raytrace_output)
#         # pygame.display.set_caption(str(self.engine.time.time.__trunc__()//2))
#         tex_to_surf(self.output_texture,self.raytrace_output)
#         self.compute_shader.run(800,600,1)
        
        
#         # print(stop-start)
#         # print(image_data.shape)
#         # s = pygame.surfarray.make_surface(image_data)
#         # pygame.surfarray.array_to_surface(self.raytrace_output,image_data)        
#         # print(self.raytrace_output.get_size(),surf.get_size())

#         # surf.blit(s)
#         surf.blit(self.raytrace_output)

# @Tracer().trace
# def tex_to_surf(texture:mgl.Texture,surf:pygame.Surface):
#     bytes = texture.read()
#     surf.get_view('2').write(bytes)
