import glm
import time
import typing
import pygame
import pygame.constants as const
from Scripts.Camera import Camera
from Entities.IControllableEntity import IControllableEntity
from Entities.IAliveEntity import IAliveEntity
from Utils.Math.game_math import smoothFollow

if typing.TYPE_CHECKING:
    from _Legacy.Scene import Scene

class PlayerController:
    __slots__ = 'scene','player','camera','last_wd_time','sprinting','sprint_speed_increase','jump_strength','reach','player_selected_block','player_speed'
    def __init__(self,scene:'Scene',camera:Camera,player:IControllableEntity):
        self.scene = scene
        self.player = player
        self.camera = camera
        self.last_wd_time = 0
        self.sprinting = 0
        self.sprint_speed_increase = 0.26
        self.jump_strength = 8.71
        self.reach = 5 #in blocks
        self.player_selected_block = None
        self.player_speed = 3.921 * (10*1/60)*1.2

    def update(self):
        camera = self.camera
        player = self.player
        camera.view_matrix = camera.get_view_matrix()
        camera.proj_matrix = camera.get_projection_matrix()
        rel_x, rel_y = pygame.mouse.get_rel()
        if self.scene.output.mouse_grabbed: 
            camera.yaw += rel_x * 0.05
            camera.pitch -= rel_y * 0.05
            camera.yaw = camera.yaw % 360
            camera.pitch = max(-90, min(90, camera.pitch))
            yaw, pitch = glm.radians(camera.yaw), glm.radians(camera.pitch)
            camera.forward = glm.vec3(
                glm.cos(yaw) * glm.cos(pitch),
                glm.sin(pitch),
                glm.sin(yaw) * glm.cos(pitch),
            )
            r = camera.right
            r.x = glm.cos(yaw + 3.1415/2)
            r.y = 0
            r.z = glm.sin(yaw + 3.1415/2)
            camera.up = glm.normalize(glm.cross(camera.right, camera.forward))

        player.forward = camera.forward
        player.up = camera.up
        player.right = camera.right

        #move player
        if self.scene.output.mouse_grabbed:
            keys = pygame.key.get_pressed()
            keysd = pygame.key.get_just_pressed()

            if keysd[const.K_w]:
                t_curr = time.perf_counter()
                if not self.sprinting:
                    if abs(self.last_wd_time - t_curr) < 0.2:
                        self.sprinting = 1
                else:
                    self.sprinting = 0
                self.last_wd_time = t_curr
            
            flat_forward = glm.vec3(glm.cos(yaw),0,glm.sin(yaw))

            movement = player.right * (keys[const.K_d] - keys[const.K_a]) + flat_forward* (keys[const.K_w] - keys[const.K_s]) 
            if glm.any(glm.bvec3(movement)):
                movement = glm.normalize(movement)*self.player_speed * (1+self.sprint_speed_increase*self.sprinting)
            if not keys[const.K_w]:
                self.sprinting = 0  
            player.vel += movement
            if player.vel.y == 0:
                player.vel.y += keysd[const.K_SPACE] * self.jump_strength

        camera.position = self.player.pos + glm.vec3(0,player.collider.s.y*0.403,0)

        #Camera FOV change w.r.t. sprint state
        camera.target_fov = 90 + self.sprinting*33*self.sprint_speed_increase
        camera.real_fov = smoothFollow(camera.real_fov,camera.target_fov,8,0.016,0.001)
       
        if self.scene.output.mouse_grabbed:
            mouse_keys = pygame.mouse.get_just_pressed()
            self.player_selected_block = self.scene.s_physics.RayCast(self.camera.position,self.camera.forward,self.reach)
            if self.player_selected_block is not None:
                if mouse_keys[0]: #left click
                    self.scene.s_chunk_manager.placeBlock(self.player_selected_block[2],0)
                if mouse_keys[2]: #right click
                    block_pos = self.player_selected_block[1]
                    #check if there is an entity at the block position
                    if block_pos.to_tuple() not in self.scene.s_physics.getCollidingBlocks(self.player.collider):
                        self.scene.s_chunk_manager.placeBlock(self.player_selected_block[1],1)

    def draw(self):
        if self.player_selected_block is not None:
            self.scene.program_outline['m_proj'].write(self.camera.proj_matrix) #type: ignore
            self.scene.program_outline['m_view'].write(self.camera.view_matrix) #type: ignore
            self.scene.program_outline['voxel_position'] = self.player_selected_block[2]
            self.scene.vao_outline.render()

        #Draw Inventory
        ui_surf = self.scene.surface_ui
        ui_surf.fill((255,0,0,100))



