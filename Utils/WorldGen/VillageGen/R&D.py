#make a room
import numpy as np 
import numpy.typing as nptype
import typing as t
class RoomMask:
    NO_MASK = 0
    REMAIN_EMPTY = 2
    ROOM_LIMIT = 1
    AIR = 3
    DOOR = 4

class RoomBlock:
    VOID = 0
    AIR = 1
    DOOR = 2
    DECOR = 3
    WALL = 4
    CHAIR = 5
    STORAGE = 6

class RoomBuilder:
    @classmethod
    def simple(cls,size:t.Sequence):
        mask = np.zeros(size[::-1],np.uint8)
        return cls(mask)
    def __init__(self,mask:nptype.NDArray[np.uint8],seed:int = 1):
        self.mask = mask
        self.size = mask.shape[::-1]
        self.room = np.zeros_like(mask,dtype = np.uint8)
        self.consider_making_doors = True
        self.seed = seed

    def addWallsToBorder(self):
        self.room[:,0] = RoomBlock.WALL
        self.room[0,:] = RoomBlock.WALL
        self.room[:,-1] = RoomBlock.WALL
        self.room[-1,:] = RoomBlock.WALL
        self.room[self.mask == RoomMask.ROOM_LIMIT] = RoomBlock.WALL
        self.room[self.mask == RoomMask.REMAIN_EMPTY] = RoomBlock.AIR
       
        return self
    
    def getEdges(self):
        edge = np.zeros_like(self.room)
        edge[:,0] = 1
        edge[:,-1] = 1
        edge[0,:] = 1
        edge[-1,:]=1
        edge[0,0] = 0
        edge[-1,-1] = 0
        edge[-1,0] = 0
        edge[0,-1] = 0
        return edge
    
    def addDoors(self):
        self.room[self.mask == RoomMask.DOOR] = RoomBlock.DOOR
        if self.consider_making_doors:

            #now we get serious
            #here we have to make doors where there are currently walls
            #lets see some cases where we should definitely make a door
            #1) if its the end of a hallway
            #on the other hand we can consider a wall and have a chance to put a door there
            #only count walls 
          
            edges = self.getEdges()
            wall_edges = np.logical_and(edges,self.room==RoomBlock.WALL)
            up    = np.roll(self.room,1,0)==RoomBlock.WALL
            up[0,:] = 0
            down  = np.roll(self.room,-1,0)==RoomBlock.WALL
            down[-1,:] = 0
            left  = np.roll(self.room,1,1)==RoomBlock.WALL
            left[:,0] = 0  
            right = np.roll(self.room,-1,1)==RoomBlock.WALL
            right[:,-1] = 0  

            potential_doors:nptype.NDArray = (up.astype(np.uint8) + down + left + right)
            #print(wall_edges.astype(int))
            potential_doors[~wall_edges]=0
            random_doors = potential_doors.copy()
            potential_doors[potential_doors != 3]=0
            pup    = np.roll(potential_doors,1,0)==3
            pup[0,:] = 0
            pdown  = np.roll(potential_doors,-1,0)==3
            pdown[-1,:] = 0
            pleft  = np.roll(potential_doors,1,1)==3
            pleft[:,0] = 0  
            pright = np.roll(potential_doors,-1,1)==3
            pright[:,-1] = 0  
            potential_doors[
                np.logical_or(
                    np.logical_and(pup,pdown),
                    np.logical_and(pleft,pright)
                )
            ] = 9
            
            self.room[potential_doors==9] = RoomBlock.DOOR

            random_doors[random_doors!=2] = 0
            
            random_arr = (np.random.Generator(np.random.MT19937(self.seed)).random(size = self.size[::-1]) * 255).astype(np.uint8)

            
            print(random_arr)


            #self.room[potential_doors] = 9
            #self.room[np.roll(self.mask,1,0)==RoomMask.ROOM_LIMIT] = RoomBlock.WALL
            #self.room[np.roll(self.mask,1,1)==RoomMask.ROOM_LIMIT] = RoomBlock.WALL
            #self.room[np.roll(self.mask,-1,1)==RoomMask.ROOM_LIMIT] = RoomBlock.WALL
            #self.room[np.roll(np.roll(self.mask,-1,1),1,0)==RoomMask.ROOM_LIMIT] = RoomBlock.WALL
            #self.room[np.roll(np.roll(self.mask,-1,1),-1,0)==RoomMask.ROOM_LIMIT] = RoomBlock.WALL
            #self.room[np.roll(np.roll(self.mask,1,1),1,0)==RoomMask.ROOM_LIMIT] = RoomBlock.WALL
            #self.room[np.roll(np.roll(self.mask,1,1),-1,0)==RoomMask.ROOM_LIMIT] = RoomBlock.WALL
            pass
        return self

    def build(self):
        return None
    
def random(state:nptype.NDArray[np.uint32]):
    state[0] = state[0] * 747796405 + 2891336453
    state[1] = ((state[0] >> ((state[0] >> 28) + 4)) ^ state[0]) * 277803737
    state[1] = (state[1] >> 22) ^ state[1]

if __name__ == '__main__':
    mask = np.array(
        [[2,2,2,1,0,0,0,0,0,1,0,1,0,0],
         [2,2,2,1,0,0,0,0,0,1,0,1,0,0],
         [1,1,1,1,0,0,0,0,0,0,0,0,0,0],
         [0,0,0,0,0,0,0,0,0,0,0,0,0,0],
         [4,0,0,0,0,0,0,0,0,0,0,0,0,0],
         [0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
    )
    rb = RoomBuilder(mask).addWallsToBorder().addDoors()
    print(rb.size)
    print(rb.room)