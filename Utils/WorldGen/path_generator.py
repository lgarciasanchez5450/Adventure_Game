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

SimpleVec = tuple[float,float]

class Vector(Protocol):
    def __add__(self,other:"Vector") -> "Vector": ...
    def __sub__(self,other:"Vector") -> "Vector": ...
    def __mul__(self,other:float) -> "Vector": ...
    def __getitem__(self,i:int) -> float: ...

from math import dist as distance, hypot

class LerpPath:
    PATH_NUMBER = 1
    def __init__(self,map:np.ndarray,noise_function:Callable[[float],float],start_pos:np.ndarray,start_vel:np.ndarray):
        from math import atan2
        self.map = map
        self.noise = noise_function
        self.pos = start_pos.astype(np.float32)
        self.theta = atan2(start_vel[1],start_vel[0])
        print('intial angle is ',self.theta)
        self.points = self.make_points(5)
        self.splines = self.generateSplines()

    def generateSplines(self) -> list[tuple[SimpleVec,SimpleVec,SimpleVec,SimpleVec] | tuple[SimpleVec,SimpleVec,SimpleVec]]:
        print('generating splines')
        splines:list[tuple[SimpleVec,SimpleVec,SimpleVec,SimpleVec] | tuple[SimpleVec,SimpleVec,SimpleVec]] = []
        tangents:list[tuple[float,float]] = []
        directions:list[tuple[float,float]] = []
        for i in range(len(self.points)-1): # Generate directions
            curr = self.points[i]
            next = self.points[i+1]
            directions.append((next[0]-curr[0],next[1]-curr[1]))

        for i in range(len(self.points)-1): # Generate tangents
            if i==0:
                tangents.append(directions[0])
            else:
                prev = directions[i-1]
                curr = directions[i]
                sum = (prev[0] + curr[0], prev[1] + curr[1])
                t = hypot(*sum)
                sum = (sum[0]/t,sum[1]/t)
                tangents.append(sum)
        
        for i in range(len(self.points)-2): # Generate Splines
            if i == 0: #special case the first point
                mid_point = (self.points[1][0] - tangents[1][0] * directions[1][0]/2,self.points[1][1] - tangents[1][1] * directions[1][1]/2)
                splines.append((self.points[0],mid_point,self.points[1]))
            else:
                first = self.points[i]
                last = self.points[i+1]
                dist = distance(first,last)
                mid1 = (first[0] + tangents[i][0]* dist / 2,first[1] + tangents[i][1] * dist / 2)
                mid2 = (last[0] - tangents[i+1][0]* dist / 2,last[1] - tangents[i+1][1] * dist / 2)
                splines.append((first,mid1,mid2,last))
        
        #special case the last point
        
        print("TO THIS TO USE DISTANCE FUNCTION LIKE IN LINE 75") 
        mid_point = (self.points[-2][0] + tangents[-2][0] * directions[-2][0]/2,self.points[-2][1] + tangents[-2][1] * directions[-2][1]/2)
        splines.append((self.points[-2],mid_point,self.points[-1]))
        return splines


    def addPoint(self,tup:tuple[int,int]):
        self.points.append(tup)    
        
    
    @staticmethod
    def lerp(a:Vector,b:Vector,t:float):
        return a + (b-a) * t
    
    @staticmethod
    def quadratic_bezier(a:Vector,b:Vector,c:Vector,t:float):
        l1 = LerpPath.lerp(a,b,t)
        l2 = LerpPath.lerp(b,c,t)
        return LerpPath.lerp(l1,l2,t)
    
    @staticmethod
    def cubic_bezier(a:Vector,b:Vector,c:Vector,d:Vector,t:float):
        l1 = LerpPath.lerp(a,b,t)
        l2 = LerpPath.lerp(b,c,t)
        l3 = LerpPath.lerp(c,d,t)
        ll1 = LerpPath.lerp(l1,l2,t)
        ll2 = LerpPath.lerp(l2,l3,t)
        return LerpPath.lerp(ll1,ll2,t)

 
    def make_points(self,max_points:int):
        print('making points')
        path_points = [(float(self.pos[0]),float(self.pos[1]))]
        def isValid(px:float,py:float) -> bool:
            px = int(px)
            py = int(py)
            a =  px > -1 and py > -1 and px < self.map.shape[1] and py < self.map.shape[0] and self.map[py][px] == 0 

            b = all(((px-x)**2 + (py-y)**2) > 40*40 for x,y in path_points)
            print("Testing point for validity",a,b)
            return a and b
        while len(path_points) < max_points:
            for i in range(8):# try 8 times to spawn a particle
                t = self.theta + np.random.rand() * 3 - 1.5
                dist = np.random.rand() * 40 + 20 # [5, 17)
                rel_x = np.cos(t) * dist
                rel_y = np.sin(t) * dist
                new_point_x = path_points[-1][0] + rel_x
                new_point_y = path_points[-1][1] + rel_y
                if isValid(new_point_x,new_point_y):
                    path_points.append((new_point_x,new_point_y))
                    self.theta = t
                    break #break to spawn the next particle
            else: 
                print("couldn't make another point so breaking")
                break#break from the while loop because in 5 tries we didn't get a good one and therefore we give up
        self.pos = path_points[-1]
        print('generated',len(path_points),"points")
        return path_points
    
    def carve(self):
        SAMPLES_PER_SPLINE = 100
        for spline in self.splines:
            func = LerpPath.cubic_bezier if len(spline)==4 else LerpPath.quadratic_bezier
            for j in range(SAMPLES_PER_SPLINE):
                t = j/SAMPLES_PER_SPLINE
                point = func(*spline,t) #type: ignore
                self.map[int(point[1])][int(point[0])] = 255







if __name__ == '__main__':
    import pygame,random
    pygame.init()
    s = pygame.display.set_mode((900,600))
    disp = pygame.Surface((500,500))
    map = np.zeros((500,500),dtype = np.int32)
    path = LerpPath(map,lambda x: random.random()*x,np.array([250,100],dtype=np.float32),np.array([0,-1],dtype=np.float32))
    path.carve()
    for y in range(map.shape[0]):
        for x in range(map.shape[1]):
            disp.set_at((x,y),(map[y][x],map[y][x],map[y][x]))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                print('hehehehaw')
         
        s.blit(disp,(900/2-250,600/2-250))
        pygame.display.flip()