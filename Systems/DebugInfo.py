import typing

import pygame
import pygame.constants as const
from Scripts.Chunk import Chunk

if typing.TYPE_CHECKING:
    from _Legacy.Scene import Scene


class DebugInfo:
    def __init__(self,scene:'Scene') -> None:
        self.scene = scene
        self.showing = False
        self.font = pygame.font.Font('Assets/Fonts/minecraft_font.ttf',18)
        self.left_y = 0
        self.right_y = 0


    def update(self):
        keysu = pygame.key.get_just_released()
        if keysu[const.K_F3]:
            self.showing = not self.showing
            print(self.showing)
        if self.showing:
            self.p_pos = self.scene.player.pos * 1
            self.p_pos.y = self.scene.player.collider.y_negative

    def render_left(self,text:str,surf:pygame.Surface):
        s = pygame.Surface(self.font.size(text),pygame.SRCALPHA)
        s.fill((100,100,100,100))
        surf.blit(s,(0,self.left_y))
        s = self.font.render(text,False,'white')
        surf.blit(s,(0,self.left_y))
        self.left_y += s.get_height()
        
    def render_right(self,text:str,surf:pygame.Surface):
        s = self.font.render(text,False,'white',(100,100,100,100))
        surf.blit(s,(surf.get_width()-s.get_width(),self.left_y))
        self.right_y += s.get_height()
        

    def draw(self):
        if self.showing:
            self.left_y = 0
            self.right_y = 0
            player = self.scene.player
            p_pos = self.p_pos
            surface_ui = self.scene.surface_ui
            self.render_left('Mincecraft Alpha',surface_ui)
            self.render_left(f'XYZ: {p_pos.x:.4f} / {p_pos.y:.4f} / {p_pos.z:.4f}',surface_ui)
            self.render_left(f'Block: {p_pos.x.__floor__()} {p_pos.y.__floor__()} {p_pos.z.__floor__()}',surface_ui)
            self.render_left(f'Chunk: {p_pos.x.__floor__()//Chunk.SIZE} {p_pos.y.__floor__()//Chunk.SIZE} {p_pos.z.__floor__()//Chunk.SIZE}',surface_ui)
            self.left_y += 10
            self.render_left(f'V: {player.vel.x:.3f} / {player.vel.y:.3f} / {player.vel.z:.3f}',surface_ui)