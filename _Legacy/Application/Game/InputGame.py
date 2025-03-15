from typing import Literal
import pygame
from ..Utils.Math.Vector import Vector2
from ...GuiFramework.Input import Input



Binary = Literal[0,1]
#Mouse
wheel:Literal[-1,0,1] # wheel is a special case
m_1:Binary
'''Mouse Button 1'''
m_2:Binary
'''Mouse Button 2'''
m_3:Binary
'''Mouse Button 3'''

m_d1:bool
m_u1:bool
m_d2:bool
m_u2:bool
m_d3:bool
m_u3:bool
m_x:bool
m_y:bool 
m_pos:Vector2 = Vector2.zero()
m_pos_normalized:Vector2 = Vector2.zero()
m_rel:Vector2 = Vector2.zero()

def _update_mouse(input:Input):
    global wheel,m_1,m_2,m_3,m_x,m_y,m_pos,m_pos_normalized
    m_1,m_2,m_3 = pygame.mouse.get_pressed() #type: ignore
    m_pos.x,m_pos.y = pygame.mouse.get_pos()
    m_rel.x,m_rel.y = pygame.mouse.get_rel()
    m_x,m_y = m_pos #type: ignore

#Keyboard
w = 0
a = 0
s = 0
d = 0

space = 0
space_d = 0


lshift = 0
rshift = 0

lctrl = 0
rctrl = 0

alt = 0

KDQueue = []

def update(input:Input):
    global w,a,s,d,space,space_d,lshift,rshift,lctrl,rctrl,alt,KDQueue,m_d1,m_u1,m_d2,m_u2,m_d3,m_u3
    _update_mouse(input)
    m_d1 = input.mb1d
    m_d2 = input.mb2d
    m_d3 = input.mb3d
    m_u1 = input.mb1u
    m_u2 = input.mb2u
    m_u3 = input.mb3u
    #Keyboard
    w = input.w
    a = input.a
    s = input.s
    d = input.d

    space = input.space
    space_d = ' ' in  input.KDQueue

    lshift = input.lshift
    rshift = input.rshift

    lctrl = input.lctrl
    rctrl = input.rctrl

    alt = input.lalt or input.ralt

    KDQueue = input.KDQueue