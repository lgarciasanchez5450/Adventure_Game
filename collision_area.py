#the idea for a collision area is that just like the camera, each sprite will put their collider in here and remove it dynamically.
#what this should do is just move colliders so they dont collide with stuff.

from game_math import Collider,is_collider,Has_Collider
_DEBUG_ = True



'''Physical Objects that block the player'''
obstacles = []
def add_obstacle(collider:Collider):
    if not is_collider(collider): raise RuntimeError("<collider> argument must be of type<settings.Collider>")
    if _DEBUG_ and collider in obstacles: raise RuntimeError("Cannot add collider to collision area twice!")
    obstacles.append(collider)

def remove_obstacle(collider:Collider):
    if not is_collider(collider): raise RuntimeError("<collider> argument must be of type<settings.Collider>")
    if _DEBUG_ and collider not in obstacles: raise RuntimeError("Cannot remove non-existent collider from collision area!")
    obstacles.remove(collider)

def collision_horizontal(collider:Collider,vx):
    if not is_collider(collider): raise RuntimeError("<collider> argument must be of type<settings.Collider>")
    for sprite in obstacles:
        sprite:Collider
        if sprite.collide_collider(collider):
            if vx > 0: # moving right
                collider.setRight(sprite.left)
            if vx < 0: # moving left
                collider.setLeft(sprite.right)

def collision_vertical(collider:Collider,vy:float):
    if not is_collider(collider): raise RuntimeError("<collider> argument must be of type<settings.Collider>")
    for other_collider in obstacles:
        other_collider:Collider
        if other_collider.collide_collider(collider):
            if vy > 0: # moving down
                collider.setBottom(other_collider.top)
            if vy < 0: # moving up
                collider.setTop(other_collider.bottom)


'''Objects that can be manipulated in the physical world'''
physical_world:list[Has_Collider] = []
def add_physical_object(object:Has_Collider):
    physical_world.append(object)

def remove_physical_object(object:Has_Collider):
    physical_world.remove(object)

def get_colliding_physical_items(collider:Collider):
    for object in physical_world:
        if collider.collide_collider(object.collider):
            yield object


'''Objects that can be manipulated in the ethereal world'''
ethereal_world:list[Has_Collider] = []
def add_ethereal_object(object:Has_Collider):
    ethereal_world.append(object)

def remove_ethereal_object(object:Has_Collider):
    ethereal_world.remove(object)


def get_colliding_ethereal_items(collider:Collider):
    for object in ethereal_world:
        if collider.collide_collider(object.collider):
            yield object


