'''
This module is meant to capture all the possible variations of noise for game development
By Hithere32123
'''
from array import array
from numpy import ndarray, zeros,float32

__all__ = [
    'noise2',
    'noise2_array',
    'set_seed',
    'LayeredNoiseMap',
    'WorleyNoise',
    'WorleyNoiseSimple',
    'unit_smoothstep',
    'rescale',
    'noise1',
]

try:
    from Noise.Worley import WorleyNoise, WorleyNoiseSimple,WorleyNoiseSmooth
except Exception as err:
    from Worley import WorleyNoise, WorleyNoiseSimple,WorleyNoiseSmooth #if we are running from this script

try:
    from Perlin import noise2,noise2_array,set_seed #type: ignore
except ImportError as err:
    print("Custom C Module Has not been built, defaulting back to pure python suport, this will slow down Noise creation significantly")
    from Noise.perlin2 import noise2,noise2_array,set_seed

class LayeredNoiseMap:
    def __init__(self,noise_scales,noise_strengths):
        assert len(noise_scales) == len(noise_strengths), "all arguments must be of the same length"

        self.noise_scales = array('d',noise_scales)
        self.noise_strengths = array('f',noise_strengths)
        self.noise_counts = tuple(range(len(self.noise_scales)))
        self.noise_normalizer = sum(noise_strengths)
    
    def getAt(self,x,y):
        data = 0
        for scale,strength in zip(self.noise_scales,self.noise_strengths):
            data += noise2(x*scale,y*scale) * strength
        data /= self.noise_normalizer
        return data
    
    def getArr(self,xs:ndarray,ys:ndarray):
        data = zeros(shape=(ys.size,xs.size))
        for scale,strength in zip(self.noise_scales,self.noise_strengths):
            data += noise2_array(xs*scale,ys*scale) * strength
        data /= self.noise_normalizer
        return data
    
    def getArrShifted(self,xs:ndarray,ys:ndarray):
        xshift = 3.141 # ~pi
        yshift = 2.718 # ~e
        data = zeros(shape=(ys.size,xs.size),dtype = float32)
        for scale,strength,i in zip(self.noise_scales,self.noise_strengths,self.noise_counts):
            data += noise2_array((xs+xshift*i)*scale,(ys+yshift*i)*scale) * strength
        data /= self.noise_normalizer
        return data
    
def noise1(x:float):
    return noise2(2.71828,x)
    
    
def unit_smoothstep(i:ndarray):
    return i * (-i*i+3) / 2
def rescale(i):
    return (i + 1) / 2
def inverse_rescale(i:ndarray):
    return i * 2 - 1

if __name__ == '__main__':
    def lerp(a,b,t):
        return a * (1-t) + b * t
    import numpy as np
    import pygame
    pygame.init()


    screen = pygame.display.set_mode((500,500))
    pos = np.array([0,0])
    xs = np.arange(500) 
    ys = np.arange(500) 
    scale = 2.0

    n  = WorleyNoiseSmooth(0,.01* scale)

    def draw(a):
        for y,row in enumerate((a + 1)/2 * 255):
            for x, height in enumerate(row):
                screen.set_at((x,y),(height,height,height))
    running = True
    while running:
        print(pos,end = '\r')
        pos = pygame.mouse.get_pos()

        if pygame.mouse.get_pressed()[0]:
            draw(
                    inverse_rescale(n.getArr(xs + pos[0],ys + pos[1])) # continents
                ) 
        
        pygame.event.pump()
        pygame.time.Clock().tick(60)
        pygame.display.flip()



    pygame.quit()