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
    'unit_smoothstep',
    'rescale',
    'noise1',
]

from Noise.Worley import WorleyNoise

try:
    from Perlin import noise2,noise2_array,set_seed
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
    return noise2(2.7181,x)
    
    
def unit_smoothstep(i:ndarray):
    return i * (-i*i+3) / 2
def rescale(i:ndarray):
    return (i + 1) / 2


