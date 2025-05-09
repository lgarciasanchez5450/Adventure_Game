# import typing
# import pygame
# import numpy as np
# import moderngl as mgl

# from pygame import Surface
# from pygame import constants as const
# from pygame import Event


# from collections import deque
# from Systems.PlayerController import PlayerController
# from Systems.ChunkManager import ChunkManager
# from Systems.DebugInfo import DebugInfo
# from Systems.Physics import Physics

# from Scripts.Camera import Camera
# from Scripts import load

# from Entities.AliveEntity import AliveEntity
# from Entities.Entity import Entity
# from Entities.Player import Player

# if typing.TYPE_CHECKING:
#     from GameApp import Engine
   
# cube_verticies = np.array([
#         # Top Face
#         (-0.001, 1.001, -0.001),
#         (1.001, 1.001, -0.001),

#         (-0.001, 1.001, -0.001),
#         (-0.001, 1.001, 1.001),

#         (1.001, 1.001, 1.001),
#         (1.001, 1.001, -0.001),

#         (1.001, 1.001, 1.001),
#         (-0.001, 1.001, 1.001),

#         # Bottom Face
#         (-0.001,  -0.001, -0.001),
#         (1.001,  -0.001, -0.001),

#         (-0.001,  -0.001, -0.001),
#         (-0.001,  -0.001, 1.001),

#         (1.001,  -0.001, 1.001),
#         (1.001,  -0.001, -0.001),

#         (1.001,  -0.001, 1.001),
#         (-0.001,  -0.001, 1.001),

#         # Sides
#         (-0.001, 1.001, -0.001),
#         (-0.001, -0.001, -0.001),

#         (1.001, 1.001, -0.001),
#         (1.001, -0.001, -0.001),

#         (-0.001, 1.001, 1.001),
#         (-0.001, -0.001, 1.001),

#         (1.001, 1.001, 1.001),
#         (1.001, -0.001, 1.001),
# ], dtype=np.float32)

# class Scene:
#     '''For all things diagetic (in game world/space)'''
#     def __init__(self,engine:"Engine",output:Surface):
#         self.engine = engine
#         self.ctx = engine.ctx
#         self.output = output
#         #Initialize Scene Objects
#         self.program = self.engine.program_manager.getProgram('Assets/shaders/chunk.vert','Assets/shaders/chunk.frag')
#         self.program_blit = self.engine.program_manager.getProgram('Assets/shaders/blit.vert','Assets/shaders/blit.frag')
#         self.program_blit['dest'] = 1
#         self.program_blit['source'] = 2
#         self.program_outline = self.engine.program_manager.getProgram('Assets/shaders/outline.vert','Assets/shaders/outline.frag')
#         self.player = Player(self,(1,10,1),(0.6,1.8,.6),21,20,20)
#         self.camera = Camera((1,5,1))

#         #Initialize Framebuffers
#         self.framebuffer_world = Framebuffer(self.ctx,output.size)
#         self.texture_2 = makeTexture(self.ctx,output.size,(mgl.NEAREST,mgl.NEAREST))
#         self.surface_ui = pygame.Surface(output.size,const.SRCALPHA)

#         self.buffer =self.ctx.buffer(data=np.array([
#             1.0, -1.0, 1.0, 0.0,
#             1.0,  1.0, 1.0, 1.0,
#             -1.0,-1.0, 0.0, 0.0,
#             -1.0, 1.0, 0.0, 1.0,
#         ],np.float32))
#         self.vao_blit = self.ctx.vertex_array(self.program_blit,[(self.buffer,'2f 2f','vert','texcoord')],mode=mgl.TRIANGLE_STRIP)
#         self.vao_outline = self.ctx.vertex_array(self.program_outline,[(self.ctx.buffer(cube_verticies),'3f','in_position')],mode=mgl.LINES)

#         #Load Voxels
#         import time
#         t_start = time.perf_counter()
#         self.tex, indices = load.loadVoxels('Assets/Blocks/_blocks.txt',self.ctx)
#         self.tex.use(5)
#         self.program['tex'] = 5
#         self.program['texture_indices'] = indices
#         t_end = time.perf_counter()
#         print('Time to Create Textures:',round(1000*(t_end-t_start),2),'ms')

#         self.fpsqueue = deque([0.0]*20,maxlen=20)
#         self.fps_sum = sum(self.fpsqueue)
#         self.p_viewport_size = output.size

#         self.entities:list[Entity] = []

#         # Scene Systems
#         self.s_player_controller = PlayerController(self,self.camera,self.player)
#         self.s_chunk_manager = ChunkManager(self)
#         self.s_physics = Physics(self)
#         self.s_debug_info = DebugInfo(self)

#         self.s_chunk_manager.recalculateActiveChunks(0,0,0)

#     def update(self,events:list[Event]):
#         if self.p_viewport_size != self.output.size:
#             self.onResize(self.output.size)
#             self.p_viewport_size = self.output.size
#         for event in events:
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_m:
#                     self.entities.append(self.player)
#                 elif event.key == const.K_ESCAPE:
#                     # if self.output.mouse_grabbed:
#                     #     self.output.grab_mouse = False
#                     #     pygame.mouse.set_relative_mode(False)
#                     #     pygame.mouse.set_pos(self.output.size[0]//2,self.output.size[1]//2)
#                     # else:
#                     #     self.output.grab_mouse = True
#                     #     # pygame.mouse.set_pos(self.output.size[0]//2,self.output.size[1]//2)
#                     #     pygame.mouse.set_relative_mode(True)
#                     pass
#         self.s_chunk_manager.update()
#         for entity in self.entities:
#             entity.update()
#         self.s_player_controller.update()
#         self.s_debug_info.update()
#         self.s_physics.update()
        
#         self.fps_sum -= self.fpsqueue.popleft()
#         fps = self.engine.time.getFPS()
#         self.fps_sum += fps
#         self.fpsqueue.append(fps)
#         # self.output.title = (str(self.fps_sum // 20)+'  '+str(len(self.s_chunk_manager.chunks)))

#     def start(self): ...

#     def onResize(self,newSize:tuple[int,int]):
#         self.ctx.viewport = (0, 0, *newSize) #Without this line the opengl context still thinks its the old size
#         self.framebuffer_world.release()
#         self.framebuffer_world = Framebuffer(self.ctx,newSize)

#         self.texture_2.release()
#         self.texture_2 = makeTexture(self.ctx,newSize,(mgl.NEAREST,mgl.NEAREST))

#         self.surface_ui = pygame.Surface(newSize,const.SRCALPHA)

#     def renderUI(self,surf:pygame.Surface):
#         surf.fill((0,0,0,0)) 
#         pygame.draw.line(surf,'black',(surf.get_width()//2-10,surf.get_height()//2),(surf.get_width()//2+10,surf.get_height()//2))
#         pygame.draw.line(surf,'black',(surf.get_width()//2,surf.get_height()//2-10),(surf.get_width()//2,surf.get_height()//2+10))

#     def draw(self):
#         #render worldview to screen
#         self.framebuffer_world.framebuffer.use()
#         self.program['m_proj'].write(self.camera.proj_matrix) #type: ignore
#         self.program['m_view'].write(self.camera.view_matrix) #type: ignore
#         self.ctx.clear(0.3,0.6,0.80)
#         self.s_chunk_manager.draw()
#         self.s_player_controller.draw()
            
#         #render ui
#         #we just want to render a simple plus sign 
#         self.ctx.screen.use()
#         self.program_blit['dest'] = 1
#         self.program_blit['source'] = 2
#         self.ctx.clear(0,0,0)
#         self.renderUI(self.surface_ui)
#         self.s_debug_info.draw()

#         #Combine both the world framebuffer and ui texture to final screen
#         self.texture_2.write(pygame.transform.flip(self.surface_ui,False,True).get_view('1'))
#         self.framebuffer_world.frame_texture.use(1)
#         self.texture_2.use(2)
#         self.vao_blit.render()
        
# def makeTexture(ctx:mgl.Context,size:tuple[int,int],filter:tuple):
#     tex = ctx.texture(size,4)
#     tex.filter = filter
#     tex.swizzle = 'BGRA'
#     return tex

