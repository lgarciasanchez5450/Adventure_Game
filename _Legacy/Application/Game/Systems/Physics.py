from ...Utils.Math.Vector import Vector2
from ...Utils.Math.Collider import Collider
from .. import Time
from .. import Entities
from ..Entities import GameObject
from ..Components import Rigidbody, Position, Velocity
from .Systems import register

@register
class Physics:
    required_components = [Rigidbody.Rigidbody,Position.Position]

    @classmethod
    def Start(cls): #right before first frame of the game
        pass

    @classmethod
    def Update(cls): #every frame of the game
        entities = list(Entities.findAllEntitiesWithComponents(*cls.required_components))
        blocks = list(filter(lambda x: not x.hasComponent(Velocity.Velocity),entities))
        for entity in entities:
            v = entity.tryGetComponent(Velocity.Velocity)
            if v is None: continue
            position = entity.getComponent(Position.Position) 
            rb = entity.getComponent(Rigidbody.Rigidbody)
            rb.move_x(v.x*Time.fixedDeltaTime)
            Physics._collide_horizontal(rb,v,blocks)
            rb.move_y(v.y*Time.fixedDeltaTime)
            Physics._collide_vertical(rb,v,blocks) 
            position.fromTuple(rb.center)

    @staticmethod
    def _collide_horizontal(collider:Collider,velocity:Vector2,blocks:list[GameObject]):
        vx = velocity.x
        if not vx: return False
        hit_smthng = False
        for obstacle in blocks:
            obstacle_collider = obstacle.getComponent(Rigidbody.Rigidbody) #type: ignore
            assert isinstance(obstacle_collider,Rigidbody.Rigidbody)
            if collider.collide_collider(obstacle_collider):
                if vx > 0: # moving right
                    collider.setRight(obstacle_collider.left)
                else: # moving left, we can guarantee this because vx != zero due to the safety clause earlier
                    collider.setLeft(obstacle_collider.right)
                hit_smthng = True   
        return hit_smthng
    
    @staticmethod
    def _collide_vertical(collider:Collider,velocity:Vector2,blocks:list[GameObject]):
        vy = velocity.y
        if not vy: return False
        hit_smthng = False
        for obstacle in blocks:
            obstacle_collider = obstacle.getComponent(Rigidbody.Rigidbody) #type: ignore
            assert isinstance(obstacle_collider,Rigidbody.Rigidbody)
            if collider.collide_collider(obstacle_collider):
                if vy > 0: # moving down
                    collider.setBottom(obstacle_collider.top)
                if vy < 0: # moving up
                    collider.setTop(obstacle_collider.bottom)
                hit_smthng = True
        return hit_smthng


    @classmethod
    def End(cls): #after last frame of game, should release all resources
        pass
