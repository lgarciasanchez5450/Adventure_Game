import pygame
import game_math
from typing import Literal
import Music
from pygame.constants import *
import Constants
import Settings

from Events import call_OnResize,add_OnResize
HALF_SCREEN = game_math.Vector2(Constants.WIDTH//2,Constants.HEIGHT//2)
s_width,s_height = Constants.WINDOW_WIDTH,Constants.WINDOW_HEIGHT
_width_multiplier,_height_multiplier = 2/(s_width-1),2/(s_height-1)
def onResize(width,height):
    global s_width,s_height, HALF_SCREEN,_width_multiplier,_height_multiplier
    s_width = width
    s_height = height
    HALF_SCREEN = game_math.Vector2(s_width//2,s_height//2)
    _width_multiplier = 2/(s_width-1)
    _height_multiplier = 2/(s_height-1)
add_OnResize(onResize)
Binary = Literal[0,1]
#Mouse
wheel:Literal[-1,0,1] # wheel is a special case
m_1:Binary
'''Mouse Button 1'''
m_2:Binary
'''Mouse Button 2'''
m_3:Binary
'''Mouse Button 3'''

m_d1:Binary
m_d2:Binary
m_d3:Binary
m_x:Binary
m_y:Binary 
m_pos:game_math.Vector2 = game_math.Vector2.zero
m_pos_from_middle:game_math.Vector2 = game_math.Vector2.zero
m_pos_normalized:game_math.Vector2 = game_math.Vector2.zero
m_rel:game_math.Vector2 = game_math.Vector2.zero

def _update_mouse():
    global wheel,m_1,m_2,m_3,m_x,m_y,m_pos
    m_1,m_2,m_3 = pygame.mouse.get_pressed()
    m_pos.x,m_pos.y = pygame.mouse.get_pos()
    m_rel.x,m_rel.y = pygame.mouse.get_rel()
    m_x,m_y = m_pos
    m_pos_from_middle.set_to(m_pos-HALF_SCREEN)
    m_pos_normalized.x = m_pos.x*_width_multiplier - 1
    m_pos_normalized.y = m_pos.y*_height_multiplier - 1



#Keyboard
w:Binary = 0
a:Binary = 0
s:Binary = 0
d:Binary = 0

space:Binary = 0
space_d:Binary = 0


lshift:Binary = 0
rshift:Binary = 0

lctrl:Binary = 0
rctrl:Binary = 0

alt = 0

KDQueue = []

def update():
    _update_mouse()
    KDQueue.clear()
    global wheel,w,a,s,d,lshift,rshift,lctrl,rctrl,m_d1,m_d2,m_d3,pressed,space,space_d
    wheel = 0
    pressed = pygame.key.get_pressed()

    m_d1,m_d2,m_d3,space_d = 0,0,0,0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            KDQueue.append(event.unicode)
            if event.key == pygame.K_w:
                w = 1
            elif event.key == pygame.K_a:
                a = 1
            elif event.key == pygame.K_s:
                s = 1
            elif event.key == pygame.K_d:
                d = 1
            elif event.key == pygame.K_LSHIFT:
                lshift = 1
            elif event.key == pygame.K_RSHIFT:
                rshift = 1
            elif event.key == pygame.K_LCTRL:
                lctrl = 1
            elif event.key == pygame.K_RCTRL:
                rctrl = 1
            elif event.key == pygame.K_SPACE:
                space = 1
                space_d = 1
            elif event.key == pygame.K_ESCAPE:
                Settings.game_state = Settings.SETTINGS
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                w = 0
            elif event.key == pygame.K_a:
                a = 0
            elif event.key == pygame.K_s:
                s = 0
            elif event.key == pygame.K_d:
                d = 0  
            elif event.key == pygame.K_LSHIFT:
                lshift = 0
            elif event.key == pygame.K_RSHIFT:
                rshift = 0
            elif event.key == pygame.K_LCTRL:
                lctrl = 0
            elif event.key == pygame.K_RCTRL:
                rctrl = 0      
            elif event.key == pygame.K_SPACE:
                space = 0
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                m_d1 = 1
            elif event.button == 2:
                m_d2 = 1
            elif event.button == 3:
                m_d3 = 1
        elif event.type == pygame.MOUSEWHEEL:
            wheel = event.y
        elif event.type == pygame.MUSICEND:
            Music.onMusicEnd()
        elif event.type == pygame.VIDEORESIZE:
            call_OnResize(event.w,event.h)
        
        
