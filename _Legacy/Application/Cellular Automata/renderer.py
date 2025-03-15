import numpy as np
import pygame
from pygame import surfarray
block_size = 4
s = None
def render(arr:np.ndarray):
    global s
    size = arr.shape
    pygame.init()
    if s is None:
        s = pygame.display.set_mode((size[0] * block_size, size[1] * block_size),depth = 32)
    s.blit(pygame.transform.scale_by(surfarray.make_surface(arr),block_size),(0,0))
    pygame.display.flip()



    
import numba,math

def to_grayscale(x:np.ndarray):
    rgb = np.empty(x.shape+(3,),np.uint8)
    rgb[:,:,0] = x
    rgb[:,:,1] = x
    rgb[:,:,2] = x
    return rgb  * (255 / 100)

def hsv_to_rgb(hsv):
    # Translated from source of colorsys.hsv_to_rgb
    rgb=np.empty_like(hsv)
    rgb[...,3:]=hsv[...,3:]    
    h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]   
    i = (h*6.0).astype('uint8')
    f = (h*6.0) - i
    p = v*(1.0 - s)
    q = v*(1.0 - s*f)
    t = v*(1.0 - s*(1.0-f))
    i = i%6
    conditions=[s==0.0,i==1,i==2,i==3,i==4,i==5]
    rgb[...,0]=np.select(conditions,[v,q,p,p,t,v],default=v)
    rgb[...,1]=np.select(conditions,[v,v,v,q,p,p],default=t)
    rgb[...,2]=np.select(conditions,[v,p,t,v,v,q],default=p) 
    return rgb