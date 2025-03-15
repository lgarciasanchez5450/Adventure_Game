import typing
import glm
from Scripts.LivingEntity import AliveEntity
from pygame import constants as const
from Scripts.Chunk import Chunk
if typing.TYPE_CHECKING:
    from Scene import RasterScene
class Player(AliveEntity):
    species ='human'
    __slots__ = 'cx','cy','can_move','attacking','state','showingInventory','hotbar','ui','hbui','walking_particle'
    def __init__(self,scene:"RasterScene",position:tuple[int,int,int],size:tuple[float,float,float]|glm.vec3,health:float,max_health:float):
        super().__init__(scene,position,size,health,max_health)
        self.set_up_animation()
        self.time = scene.engine.time
        self.engine = scene.engine
        self.speed = 4
        self.cx = position

        # stats
        # self.exp = 5000 #dont make attribute points (overused). make exp have another purpose. attribute points can lead to severely op setups and the player getting exactly what they want. 
        # damage timer
        self.can_move = True
        self.attacking = False
        self.states = ['relaxed','focused']
        self.state = None
        self.showingInventory = False
        
        #humans have 27 inventory spots and 9 hotbar spots
        # self.hotbar = Hotbar(self.inventory,27,28,29,30,31,32,33,34,35) # the numbers at the end mean the inventory slots that the hotbar should use in order
        
        self.direction = 'right'

    def set_up_animation(self):
        # walk_right = Textures.player_walk
        # walk_left = Textures.flipXArray(walk_right)
        # idle_right = Textures.player_idle
        # idle_left = Textures.flipXArray(idle_right)
        # attack_right = Textures.player_attack
        # attack_left = Textures.flipXArray(attack_right)

        # self.walking_particle = Textures.particles_opaque['dirt_particle']
        # self.animation.add_state('walk',4,walk_right,walk_left)
        # self.animation.add_state('idle',1.2,idle_right,idle_left)
        # self.animation.add_state('attack',5,attack_right,attack_left)
        # self.animation.set_state('idle')
        # self.animation.on_animation_done = self.on_animate_done
        pass

    # def set_state(self, number: int):
    #     if self.state is self.states[number]: return False
    #     self.state = self.states[number]
    #     if number == 0:
    #         Camera.set_mouse_assist(True)
    #     elif number == 1:
    #         Camera.set_mouse_assist(False)
    #         #Textures.texture['danger.png'].set_alpha(255)

    # def attack(self):
    #     self.animation.set_state('attack')

    # def _attack(self):
    #     if self.direction == 'right':
    #         c = Collider(self.pos.x+.2,self.pos.y-.5,.5,1)
    #     elif self.direction == 'left':
    #         c = Collider(self.pos.x-.7,self.pos.y-.5,.5,1)

    
    def input(self): #Time.deltaTime is in seconds
        pass
        # if 'r' in Input.KDQueue:
        #     pos = Camera.world_position(Input.m_pos).floored()
        #     place_block(WoodenPlank(Vector2Int(int(pos.x),int(pos.y))))

        # if 'b' in Input.KDQueue:
        #     b = Bunny(self.pos.copy())
        #     spawn_entity(b)
        
        # if 'h' in Input.KDQueue:
        #     create_explosion(Camera.world_position(Input.m_pos) ,20)
    
        # if 'n' in Input.KDQueue:
        #     return
        #     velocity = (Camera.world_position_from_normalized(Input.m_pos_normalized) - self.pos).normalized
        #     if velocity.isZero:
        #         velocity = Vector2.randdir
        #     spawn_entity(ArrowInciendiary(self.pos + velocity/2,velocity*3,self))
        # if Input.space_d:
        #     spawn_item(Application.Game.Items.BunnyEgg(),self.pos,Vector2.randdir())
        # if self.animation.state != 'attack':
        #     v = Vector2(Input.d-Input.a,Input.s-Input.w)
        #     v.setMagnitude(self.getTotalSpeed() * self.ground.surface_friction)
        #     self.accelerate(v.x,v.y)
        # else:
        #     self.vel.reset() #set to 0,0

        # if self.vel.x > 0:
        #     self.animation.direction = 'right' 
        # elif self.vel.x < 0:
        #     self.animation.direction = 'left'

        #item usage

        # if Input.m_1 and self.animation.state != 'attack':
        #     #use_item(self.inventory.)
        #     pass

        # if Input.m_d1:
        #     item = self.hotbar.seeSelected()
        #     print('attacked with item',item)
        # if Input.m_d3:
        #     self.hotbar.start_use_selected()
        # elif Input.m_u3:
        #     self.hotbar.stop_use_selected()
        # elif Input.m_3:
        #     self.hotbar.during_use_selected()

        # if Input.m_2 and Time.frameCount%21 == 0:
        #     Particles.spawn_smoke_particle(Camera.world_position_from_normalized(Input.m_pos_normalized),Vector2.randdir(),(Vector2.random().x*100).__trunc__())

    def get_movement(self):
        xz_movement = self.right * (self.engine.keys[const.K_d] - self.engine.keys[const.K_a]) + self.forward * (self.engine.keys[const.K_w] - self.engine.keys[const.K_s])

        if glm.length(xz_movement):
            xz_movement = glm.normalize(xz_movement)
        out= xz_movement * self.speed
        if self.engine.active_scene.physics.isGrounded(self) and self.engine.keys[const.K_SPACE]:
            out += glm.vec3(0,8.44084934277,0)
            
        # print(out)
        # print(xz_movement, glm.vec3(0,1,0) * (self.engine.keys[const.K_SPACE] - self.engine.keys[const.K_LSHIFT]))
        return out
   
    def in_chunk(self,cx,cy):
        '''accepts coords in world chunk position'''
        return (cx == self.cx) and (cy == self.cy)

    def on_animate_done(self):
        # if self.animation.state == 'attack':
        #     if self.vel:
        #         self.animation.set_state('walk')
        #     else:
        #         self.animation.set_state('idle')
        # self.collect_items()
        pass
     
    # def animate(self):
    #     if self.vel and self.animation.state == 'idle': self.animation.set_state('walk')
    #     elif not self.vel and self.animation.state == 'walk': self.animation.set_state('idle')
        
    #     if FPS != 0 and self.vel and self.animation.frame_in_frame % (FPS//3) == 0:
    #         #spawn a particle
    #         if self.ground.id == GROUND_INVALID:
    #             pass
    #         elif self.ground.id == GROUND_GRASS:
    #             Particles.spawn(CSurface.inferOffset(self.walking_particle,self.pos + Vector2(0,.4)),.5,Vector2.random() * 0.5)
    #         elif self.ground.id == GROUND_WATER:
    #             Particles.spawn(CSurface.inferOffset(Textures.particles_opaque['water'],self.pos + Vector2(0,.4)),.5,Vector2.random() * 0.5)
 
    # def collect_items(self): ## TODO : Make it so that in order to pick up items you click on them instead of just getting close to them

    #     for item in collide_entities_in_range_species(self.pos,self.pickup_range,'item'): # type: ignore
    #         item:ItemWrapper
    #         if item.pickup_time < 0 :
    #             i = self.hotbar.fitItem(item.item)
    #             if i is not None:
    #                 i = self.inventory.fitItem(i) #this will never add the same object to both hotbar and inventory becasue the or will only try to add to inventory if the item couldn't be added to the hotbar
    #             if i is None:
    #                 item.onDeath()

    def update(self):
        #Camera.program['danger'] = 1-(self.health / self.total_health)
        self.input()
        self.vel += self.get_movement()
        # print(self.vel)
        # self.animate()
