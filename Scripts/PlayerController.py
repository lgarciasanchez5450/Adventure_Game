import glm
import time
import pygame
from pygame import constants as const

from Scene import RasterCamera
from Scripts.LivingEntity import AliveEntity
from Utils.Math.game_math import smoothFollow

class PlayerController:
    __slots__ = 'player','camera','last_wd_time','sprinting','sprint_speed_increase','jump_strength'
    def __init__(self,camera:RasterCamera,player:AliveEntity):
        self.player = player
        self.camera = camera
        self.last_wd_time = 0
        self.sprinting = 0
        self.sprint_speed_increase = 0.6
        self.jump_strength = 8


    def update(self):
        camera = self.camera
        player = self.player
        rel_x, rel_y = pygame.mouse.get_rel()
        camera.yaw += rel_x * 0.05
        camera.pitch -= rel_y * 0.05
        camera.yaw = camera.yaw % 360
        camera.pitch = max(-89, min(89, camera.pitch))
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
            movement = glm.normalize(movement) * (1+self.sprint_speed_increase*self.sprinting)
        else:
            self.sprinting = 0  
        player.vel += movement
        # player.vel.y += (keys[const.K_SPACE] - keys[const.K_LSHIFT])
        player.vel.y += keysd[const.K_SPACE] * self.jump_strength
        camera.position = self.player.pos + glm.vec3(0,player.collider.s.y*0.3,0)

        #Camera FOV change w.r.t. sprint state
        camera.target_fov = 90 + self.sprinting*33*self.sprint_speed_increase
        camera.real_fov = smoothFollow(camera.real_fov,camera.target_fov,8,0.016,0.001)
        

