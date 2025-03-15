from typing import Protocol
from opensimplex import OpenSimplex
import numpy as np
from collections.abc import Callable,Iterable

  
class LayeredOpenSimplex(object):
    def __init__(self,scale:float,octaves:int,lacunarity:float,persistance:float,seeds =lambda a: list(range(3,a+3,1))):
        assert octaves > 0
        self._seeds = seeds
        self.scale = scale
        self.octaves = octaves
        self.lacunarity = lacunarity
        self.persistance = persistance

    @property
    def seeds(self):
        return self._seeds
    
    @seeds.setter
    def seeds(self,val:Callable[[int],Iterable[int]]):
        self._seeds = val
        self.simplexes = tuple(OpenSimplex(s) for s in self._seeds(self.octaves))
        assert len(self.simplexes) == self.octaves

    @property
    def octaves(self):
        return self._octaves
    
    @octaves.setter
    def octaves(self,_val:int):
        assert _val > 0
        self._octaves = _val
        self.simplexes = tuple(OpenSimplex(s) for s in self._seeds(self.octaves))
        assert len(self.simplexes) == self.octaves


    def noise2(self,x:float,y:float):
        p = 1
        n = 0
        x *= self.scale
        y *= self.scale
        t = 0
        for simplex in self.simplexes:
            n += simplex.noise2(x,y) * p
            t += p
            x *= self.lacunarity
            y *= self.lacunarity
            p *= self.persistance
        return n / t

    def noise2array(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        x *= float(self.scale)
        y *= float(self.scale)
        n = self.simplexes[0].noise2array(x,y) 
        p = self.persistance
        t = 1
        for simplex in self.simplexes[1:]:
            n += simplex.noise2array(x,y) * p               
            t += p
            x *= self.lacunarity
            y *= self.lacunarity
            p *= self.persistance
        return n / t
    def noise3(self, x: float, y: float, z: float) -> float: 
        x *= self.scale
        y *= self.scale
        z *= self.scale
        n = self.simplexes[0].noise3(x,y,z)
        p = self.persistance
        t = 1
        for simplex in self.simplexes[1:]:
            n += simplex.noise3(x,y,z) * p               
            t += p
            x *= self.lacunarity
            y *= self.lacunarity
            p *= self.persistance
        return n / t
    
    def noise3array(self, x: np.ndarray, y: np.ndarray, z: np.ndarray) -> np.ndarray:
        x *= self.scale
        y *= self.scale
        z *= self.scale
        n = self.simplexes[0].noise3array(x,y,z)
        p = self.persistance
        t = 1
        for simplex in self.simplexes[1:]:
            n += simplex.noise3array(x,y,z) * p               
            t += p
            x *= self.lacunarity
            y *= self.lacunarity
            z *= self.lacunarity
            p *= self.persistance
        return n / t
    def noise4(self, x: float, y: float, z: float, w: float) -> float:
        x *= self.scale
        y *= self.scale
        z *= self.scale
        w *= self.scale
        n = self.simplexes[0].noise4(x,y,z,w)
        p = self.persistance
        t = 1
        for simplex in self.simplexes[1:]:
            n += simplex.noise4(x,y,z,w) * p               
            t += p
            x *= self.lacunarity
            y *= self.lacunarity
            z *= self.lacunarity
            w *= self.lacunarity
            p *= self.persistance
        return n / t
    def noise4array(self, x: np.ndarray, y: np.ndarray, z: np.ndarray, w: np.ndarray) -> np.ndarray:
        x *= self.scale
        y *= self.scale
        z *= self.scale
        w *= self.scale
        n = self.simplexes[0].noise4array(x,y,z,w)
        p = self.persistance
        t = 1
        for simplex in self.simplexes[1:]:
            n += simplex.noise4array(x,y,z,w) * p               
            t += p
            x *= self.lacunarity
            y *= self.lacunarity
            z *= self.lacunarity
            w *= self.lacunarity
            p *= self.persistance
        return n / t