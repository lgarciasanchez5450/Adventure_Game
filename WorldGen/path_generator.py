import numpy as np
from typing import Callable, Protocol
class PerlinPath:
    def __init__(self,map:np.ndarray,noise_function:Callable[[float],float],start_pos:np.ndarray,start_vel:np.ndarray):
        from math import atan2
        self.map = map
        self.noise = noise_function
        self.pos = start_pos.astype(np.float32)
        self.theta = atan2(start_vel[1],start_vel[0])

    def carve(self,length:int):
        from math import sin, cos
        vel = np.empty(2,np.float32)
        for t in range(length):
            #self.theta += self.noise(t) * self.dt


            vel[0] = cos(self.theta)
            vel[1] = sin(self.theta) 
            self.pos += vel
            
            if 0:
                pass

class Vector(Protocol):
    def __add__(self,other:"Vector") -> "Vector": ...
    def __sub__(self,other:"Vector") -> "Vector": ...
    def __mul__(self,other:float) -> "Vector": ...


class LerpPath:
    def __init__(self,map:np.ndarray,noise_function:Callable[[float],float],start_pos:np.ndarray,start_vel:np.ndarray):
        from math import atan2
        self.map = map
        self.noise = noise_function
        self.pos = start_pos.astype(np.float32)
        self.theta = atan2(start_vel[1],start_vel[0])
        self.points = self.make_points(5)

        
        
    
    @staticmethod
    def lerp(a:Vector,b:Vector,t:float):
        return a + (b-a) * t
    
    @staticmethod
    def binomial_bezier(a:Vector,b:Vector,c:Vector,t:float):
        l1 = LerpPath.lerp(a,b,t)
        l2 = LerpPath.lerp(b,c,t)
        return LerpPath.lerp(l1,l2,t)

 
    def make_points(self,max_points:int):
        path_points = [(self.pos[0],self.pos[1])]
        def isValid(px:float,py:float) -> bool:
            px = int(px)
            py = int(py)
            return px > -1 and py > -1 and px < self.map.shape[1] and py < self.map.shape[0] and self.map[py][px] == 0 and all(((px-x)**2 + (py-y)**2) < 4*4 for x,y in path_points)
        while len(path_points) < max_points:
            for i in range(8):# try 8 times to spawn a particle
                t = self.theta + np.random.rand() * 2 - 1
                dist = np.random.rand() * 5 + 5 # [5, 10)
                rel_x = np.cos(t) * dist
                rel_y = np.sin(t) * dist
                new_point_x = path_points[-1][0] + rel_x
                new_point_y = path_points[-1][1] + rel_y
                if isValid(new_point_x,new_point_y):
                    path_points.append((new_point_x,new_point_y))
                    self.theta = t
                    break #break to spawn the next particle
            else: 
                break#break from the while loop because in 5 tries we didn't get a good one and therefore we give up
        return path_points