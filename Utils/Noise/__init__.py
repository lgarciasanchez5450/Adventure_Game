'''
This module is meant to capture all the possible variations of noise for game development
By Hithere32123
'''
from array import array
import numpy as np
import numpy.typing as np_typing

__all__ = [
    'noise1',
    'noise2',
    'noise2_array',
    'set_seed',
    'LayeredNoiseMap',
    'WorleyNoise',
    'WorleyNoiseSimple',
    'unit_smoothstep',
    'rescale',
]

try:
    from .Worley import WorleyNoise, WorleyNoiseSimple,WorleyNoiseSmooth
except Exception:
    from Worley import WorleyNoise, WorleyNoiseSimple,WorleyNoiseSmooth #if we are running from this script

try:
    from Perlin import noise2,noise2_array,set_seed #type: ignore
except ImportError:
    print("Custom C Module Has not been built, defaulting back to pure python suport, this will slow down Noise creation significantly")
    try:
        from .perlin2 import noise2,noise2_array,set_seed
    except ImportError:
        from Noise.perlin2 import noise2,noise2_array,set_seed

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    def noise2(x:float,y:float) -> float: ...
    def noise2_array(xs:np.ndarray,ys:np.ndarray) -> np_typing.NDArray[np.floating] : ...

class LayeredNoiseMap:
    __slots__ = 'noise_scales','noise_strengths','noise_counts','noise_normalizer'
    def __init__(self,noise_scales:list[float]|tuple[float,...],noise_strengths:list[float]|tuple[float,...]):
        assert len(noise_scales) == len(noise_strengths), "all arguments must be of the same length"

        self.noise_scales = array('d',noise_scales)
        self.noise_strengths = array('d',noise_strengths)
        self.noise_counts = tuple(range(len(self.noise_scales)))
        self.noise_normalizer = 1/sum(noise_strengths)
    
    def getAt(self,x,y):
        data = 0
        for scale,strength in zip(self.noise_scales,self.noise_strengths):
            data += noise2(x*scale,y*scale) * strength
        data *= self.noise_normalizer
        return data
    
    def getArr(self,xs:np.ndarray,ys:np.ndarray):
        data = np.zeros(shape=(ys.size,xs.size),dtype=np.float32)
        for scale,strength in zip(self.noise_scales,self.noise_strengths):
            data += noise2_array(xs*scale,ys*scale) * strength
        data *= self.noise_normalizer
        return data
    
    def getArrShifted(self,xs:np.ndarray,ys:np.ndarray):
        xshift = 3.141 # ~pi
        yshift = 2.718 # ~e
        data = np.zeros(shape=(ys.size,xs.size),dtype = np.float32)
        for scale,strength,i in zip(self.noise_scales,self.noise_strengths,self.noise_counts):
            data += noise2_array((xs+xshift*i)*scale,(ys+yshift*i)*scale) * strength
        data *= self.noise_normalizer
        return data
    
def noise1(x:float):
    '''Returns pseudo-random smooth gradient noise 
    Range: [-1, 1]'''
    return noise2(2.718281828459045,x)

def lerp(a,b,t):
    return a + (b-a) * t

def unit_smoothstep(i:np.ndarray):
    return i * (-i*i+3) / 2
def rescale(i):
    '''[-1,1] -> [0,1]'''
    return (i + 1) / 2
def inverse_rescale(i:np.ndarray):
    '''[0,1] -> [-1,1]'''
    return i * 2 - 1

if __name__ == '__main__':

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