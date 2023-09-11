from memory_profiler import profile
from Constants import *
from collections import deque
from typing import final
from pygame import Surface,draw
from game_math import Collider,is_collider,Has_Collider, Vector2,hypot,inclusive_range, cap_magnitude,log2,make2dlist,ones,abssin,abscos,cache
import Textures
if __name__ == '__main__':
    import pygame
    display = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT),pygame.OPENGL| pygame.DOUBLEBUF|pygame.RESIZABLE) # can be Resizable with no problems
    screen = pygame.Surface((WIDTH,HEIGHT))
    Textures.init()
    import Camera
    Camera.init(screen)


from perlin import *
#from debug import profile
from ground import *
from pygame import font
import Settings
import Input
import Time
import Events
from debug import getrefcount
from UI import *
import UI
from Items import Item
import Items
import Animation
from Camera import CSurface
import Particles
from Inventory import Inventory,ArmorInventory,HotbarInventory
from UI_Elements import ItemSlot
#entity_manager.init(CHUNK_SIZE)
#from pygame import font
#myfont = font.SysFont("Arial",10)
village_creater = SpacedObject(25,4,.92)
dead_entities = []
half_sqrt_2 = sqrt(2)/2

@cache
def get_tnt_list():
    return Textures.import_folder('Images/particles/Explosion',True,(BLOCK_SIZE,BLOCK_SIZE))


def get_tnt_animation(pos:Vector2,fps=40):
    return Particles.Cheap_Animation(pos.copy(),get_tnt_list(),fps,None)

class Actions:
    def __init__(self):
        pass

class Appearance:
    """What an entity of 'somthing' looks like in game
    to be used for AI of npc's"""
    __slots__ = 'color','size','shape','species'
    def __init__(self,color,size,shape,species):
        self.color = color
        self.size = size
        self.shape = shape
        self.species = species

    def looks_like(self,other,tolerance): 
        '''A very simple model function to tell what others would look like in the future'''
        assert isinstance(other,Appearance)
        return abs(other.color - self.color) < tolerance and abs(other.size - self.size) < tolerance and abs(other.size - self.size) < tolerance

    def copy(self):
        return Appearance(self.color,self.size,self.shape,self.species)
    
#####
class Block:
    
    @staticmethod
    def spawnable_on(ground):
      return True
    __slots__ = 'collider','pos','type','tags','blast_resistance','hardness','surf_offset','surf','dead','csurface'
    def __init__(self,pos,type):
        hb = Settings.HITBOX_SIZE[type]
        self.collider = Collider.SpawnOnBlockCenter(*pos,*hb)
        self.pos = Vector2(*self.collider.center) #hp -> huan pablo
        self.type:str = type
        self.tags = set()
        self.blast_resistance = 0 
        self.hardness = 1
        self.surf_offset = Settings.SURFACE_OFFSET[type]
        self.surf = Surface((0,0))
        self.dead = False

        self.csurface = CSurface(self.surf, self.pos, self.surf_offset)      

    def take_damage(self,damage:int,type:str,entity = None):
        if type is EXPLOSION_DAMAGE:
            if damage > self.blast_resistance:
                self.onDeath()
        elif type is PHYSICAL_DAMAGE:
            pass 

    def onLoad(self) -> None: 
        Camera.add(self.csurface)

    def onLeave(self) -> None: 
        Camera.remove(self.csurface)

    def onDeath(self):
        if self.dead:return
        chunk = chunks[(self.pos//CHUNK_SIZE).tuple]
        chunk.dead_blocks.append(self)
        self.dead = True
        self.onLeave()

    def update(self) -> None: ...

class Tree(Block):
    oak_tex = '03.png'
    @staticmethod
    def spawnable_on(ground:Ground) -> bool:
        return ground.name is DIRT
    #this class is an "obstacle" 
    def __init__(self,pos,ground:Ground):
        assert Tree.spawnable_on(ground), f"Tree was spawned on illegal block: {ground}"
        super().__init__(pos,'tree')
        self.surf = Textures.texture[Tree.oak_tex]
        self.csurface.surf = self.surf
        self.blast_resistance = 10

    def update(self):
        pass

class TNT(Block):
    tnt_tex = 'tnt.png'
    @staticmethod
    def spawnable_on(ground:Ground):
        return ground.name is DIRT
    __slots__ = 'timer','energy'
    def __init__(self, pos):
        super().__init__(pos, 'tnt')
        self.blast_resistance = 10
        self.surf = Textures.texture[TNT.tnt_tex]
        self.csurface.surf = self.surf
        self.timer = 4
        self.energy = 15

    def take_damage(self, damage: int, type: str,entity = None):
        if self.dead:return
        if type is FIRE_DAMAGE:
            self.onDeath()
            return

        return super().take_damage(damage, type,entity)


     
    def onDeath(self):
        spawn_entity(LiveTNT(self.pos,4,15))
        return super().onDeath()

class WoodenPlank(Block):
    @staticmethod
    def spawnable_on(ground:Ground):
        return ground.is_solid
    
    def __init__(self,pos:Vector2):
        super().__init__(pos,'woodenplank')
        self.surf = Textures.texture['15.png']
        self.csurface.surf = self.surf

class Entity:
    def __init__(self,pos,species):
        self.pos = Vector2(*pos)
        self.vel = Vector2.zero
        species = intern(species)
        self.species = species
        self.image = CSurface(Textures.texture['null.png'],self.pos,Settings.SURFACE_OFFSET[species])
        self.collider = Collider(0,0,*Settings.HITBOX_SIZE[species])
        self.collider.setCenter(*self.pos)
        self.animation = Animation.Animation(self.image)
        self.speed = 1.0

        self.direction = 'right'
        self.appeareance = Appearance(*Settings.APPEARANCE_BY_SPECIES[species],species=species)
        
        self.dead = False

    def onLoad(self): 
        Camera.add(self.image)
    def onLeave(self):
        Camera.remove(self.image)

    def onDeath(self):
        if self.dead: return
        self.dead = True
        dead_entities.append(self)
        self.onLeave()

    def update(self):
        if self.dead: return
        frame_speed = self.speed * Time.deltaTime
        #move x rect 
        self.collider.move_x(self.vel.x * frame_speed) # move in world coordinates
        collision_horizontal(self.collider,self.vel.x)
        #move y rect 
        self.collider.move_y(self.vel.y * frame_speed) # move in world coordinates
        collision_vertical(self.collider,self.vel.y)
        self.pos.from_tuple(self.collider.center)
        self.animation.animate()


    def attack(self,entity):
        assert isinstance(entity,(Entity,Block))
        entity.take_damage(self.get_attack_damage(),self.get_attack_type(),self.appeareance)

    def take_damage(self,damage:int,type:str,appearance:Appearance|None = None):
        self.onDeath()

    def get_attack_damage(self) -> int: ...

    def get_attack_type(self) -> str:
        return PHYSICAL_DAMAGE

class ItemWrapper(Entity):
    def __init__(self,pos,item:Item):
        self.pickup_time = ITEM_PICKUP_TIME
        super().__init__(pos,'item')
        assert isinstance(item,Item)
        self.item = item
        item.animation.csurface = self.image
        self.animation = item.animation
        self.alive_time = ENTITY_MAX_LIFESPAN
        

    def update(self):
        self.pickup_time -= Time.deltaTime
        self.alive_time -= Time.deltaTime
        if self.alive_time <= 0: self.onDeath()
        super().update()
        if self.vel.isZero: return
        ground = Chunk.get_ground_at(self.pos.x,self.pos.y)
        if ground is not None:
            friction = ground.surface_friction * Time.deltaTime *.1
            if friction*friction > self.vel.magnitude_squared():
                self.vel.reset()
            else:
                self.vel += self.vel.opposite_normalized() * friction

class LiveTNT(Entity):
    whited = Textures.load_image('Images/objects/tnt1.png')
    @staticmethod
    def damage_func_getter(joules):
        joules_squared = joules*joules
        return lambda dist_squared:  (-2.5 * log2(dist_squared/joules_squared)).__trunc__() if dist_squared < joules_squared else 0
    
    def __init__(self,pos:Vector2,time:float|int,energy:int):
        super().__init__(pos,'tnt')
        self.animation.add_state('1',1,[Textures.texture['tnt.png'],self.whited],[Textures.texture['tnt.png'],self.whited])
        self.animation.set_state('1')
        self.animation.animate()
        self.timer = time
        self.energy = energy
        self.particle_timer= .15
        self.particle_emit = Vector2(0,-0.7)



    def onDeath(self):
        c = Collider.spawnFromCenter(self.pos.x,self.pos.y,self.energy*2,self.energy*2)
        for x in range(5):
            Particles.spawn_animated(get_tnt_animation(self.pos+Vector2.randdir/3,38+x),False,0)
        damage_function = self.damage_func_getter(self.energy)
        for entity in collide_entities(c):
            if entity.species == 'tnt':continue #tnt in entity form will be immune to other exploding tnt

            entity.take_damage(damage_function((self.pos - entity.pos).magnitude_squared()),self.get_damage_type(),None)   
        for block in collide_blocks(c):
            block.take_damage(damage_function((self.pos-block.pos).magnitude_squared()),self.get_damage_type(),None)     
        return super().onDeath()
    

    def update(self):
        super().update()
        self.timer -= Time.deltaTime
        self.particle_timer -= Time.deltaTime
        while self.particle_timer <= 0:
            Particles.after_spawn(self.pos+self.particle_emit,Vector2.randdir*1.5,Textures.texture['grey.png'],1,(-4,-4),True,slows_coef=1)
            self.particle_timer += .15
        if self.timer <= 0:
            self.onDeath()


    def get_damage_type(self):
        return EXPLOSION_DAMAGE

class AliveEntity(Entity):
    def __init__(self,pos,species):
        super().__init__(pos,species)
        self.actions = Settings.ACTIONS_BY_SPECIES[species]
        self.pickup_range = max(*Settings.HITBOX_SIZE[species]) * half_sqrt_2 # just a shortcut for finding the length to the corner of a box from the middle when you only know a side length
        self.inventory = Inventory(Settings.INVENTORY_SPACES_BY_SPECIES[species])
        self.armour_inventory = ArmorInventory(*Settings.ARMOUR_SLOTS_BY_SPECIES[species])

        #Stats
        self.stats = Settings.STATS_BY_SPECIES[species].copy()
        self.exp = 5000 #dont make attribute points (overused). make exp have another purpose. attribute points can lead to severely op setups and the player getting exactly what they want. 
        speed = self.stats['speed'] 
        self.speed = Settings.MAX_SPEED_BY_SPECIES[species] * speed / (speed + 100)
        self.total_health = self.stats['constitution'] * 5 + self.stats['strength'] + self.stats['stamina']
        self.regen_multiplier = self.stats['constitution'] + self.stats['strength']
        self.regen_multiplier = self.regen_multiplier / (self.regen_multiplier + 100) + 1
        self.health = self.total_health
        self.strength = self.stats['strength'] * 5 + self.stats['constitution'] + self.stats['stamina']
        self.energy = self.stats['energy']
        self.attack_speed = self.energy / 10
        self.time_between_attacks = 1/self.attack_speed
        self.time_to_attack = self.time_between_attacks
        self.vision_collider = Collider(0,0,Settings.VISION_BY_SPECIES[species]*2,Settings.VISION_BY_SPECIES[species]*2)
        self.vision_squared = Settings.VISION_BY_SPECIES[species] ** 2
        self.states = []
        self.ground = getGround(GROUND_DIRT)
        # damage timer
        self.invulnerability_time = 0.5
        self.time_til_vulnerable = 0.0

        self.direction = 'right'

    def depleteEnergy(self,action):
        assert action in self.actions, f'{self.species} has tried to do actions: {action}, which is not in its list of actions!'
        self.energy -= Settings.ACTION_ENERGY_CONSUMPTION[action]
        if self.energy < 0:
            self.take_damage(-self.energy,INTERNAL_DAMAGE,None)
            self.energy = 0
        
    def canDoAction(self,action):
        '''Returns if self HAS ENOUGH ENERGY to do the action, keep in mind that the action can still be taken if this returns False, just with consequences...'''
        assert action in self.actions,  f'{self.species} has tried to do actions: {action}, which is not in its list of actions!'
        return self.energy >= Settings.ACTION_ENERGY_CONSUMPTION[action]

    def get_entities_seen(self):
        for entity in collide_entities(self.vision_collider):
            if entity is not self and (entity.pos - self.pos).magnitude_squared() <= self.vision_squared and can_see_each_other(self,entity):
                yield entity    

    def onDeath(self):
        super().onDeath()
        for i in range(10):
            Particles.spawn(self.pos + Vector2.random/5,Vector2.random/2,Textures.texture['white.png'],1,slows_coef=0)
        Particles.spawn(self.pos.copy(),Vector2.zero,self.animation.surf.copy(),1,self.image.offset,False,False)

    def set_state(self,number:int):
        if self.state is self.states[number]: return False
        self.state = self.states[number]
        self.animation.set_state(self.state)

    def update_state(self): ...

    def accelerate(self,x,y):
        self.vel.x += x *Time.deltaTime * self.ground.surface_friction
        self.vel.y += y *Time.deltaTime * self.ground.surface_friction
        mag_sqrd = self.vel.magnitude_squared()
        if mag_sqrd > 1:
            self.vel /= sqrt(mag_sqrd)

    def update(self):
        if self.dead: return
        if self.time_til_vulnerable == -float('inf'):
            self.time_til_vulnerable = self.invulnerability_time
        self.time_to_attack -= Time.deltaTime
        self.time_til_vulnerable -= Time.deltaTime
        frame_speed = (self.speed + self.inventory.added_spd) * Time.deltaTime
        #move x rect 
        self.collider.move_x(self.vel.x * frame_speed) # move in world coordinates
        collision_horizontal(self.collider,self.vel.x)
        #move y rect 
        self.collider.move_y(self.vel.y * frame_speed) # move in world coordinates
        collision_vertical(self.collider,self.vel.y)
        self.pos.from_tuple(self.collider.center)
     
        self.ground = Chunk.get_ground_at(self.pos.x,self.pos.y)
        if self.ground is not None:
            friction = self.ground.surface_friction * Time.deltaTime
            if friction*friction > self.vel.magnitude_squared():
                self.vel.reset()
            else:
                self.vel += self.vel.opposite_normalized() * friction
        else:
            self.ground = getGround(GROUND_DIRT)
        
        self.animation.animate()

    def get_damage_resisted(self,damage:int,type:str) -> int:
        '''Returns damage resisted'''
        if type is INTERNAL_DAMAGE: return 0

        defense:int = self.stats['defense'] + self.inventory.added_def
        damage_reduction = damage * defense/ (defense+100) 
        return damage_reduction.__trunc__()
    
    def take_damage(self,damage:int,type:str,appearance:Appearance = None) -> None:
            
        if self.time_til_vulnerable < 0 or type is INTERNAL_DAMAGE: 
            damage -= self.get_damage_resisted(damage,type)
            if damage == 0:
                return
            Particles.spawn_hit_particles(self.pos,.5)
            self.health -= damage
            print('taking damage',damage,'now health is',self.health)
            if self.health <= 0:
                self.onDeath()
            self.time_til_vulnerable = -float('inf')
    
    def get_energy_multiplier(self) -> float:
        return (self.energy/self.stats['energy'] + 1)/2

    def get_attack_damage(self) -> int:
        '''Returns final attack damage'''
        #get base damage
        damage:int = self.stats['attack']

        #get total inventory added damage
        damage += self.inventory.added_atk

        damage *= 1 + self.stats['strength'] / 100 * self.get_energy_multiplier()

        return damage.__trunc__()

    def get_attack_type(self) -> str:
        return PHYSICAL_DAMAGE
    
    def natural_regen(self):
        if self.health != self.total_health and self.time_til_vulnerable < -10:

            self.health += self.total_health/100 * Time.deltaTime * self.regen_multiplier * self.get_energy_multiplier()
            if self.health > self.total_health:
                self.health = self.total_health

    def collect_items(self):
        for item in collide_entities_in_range(self.pos,self.pickup_range):
            item:ItemWrapper
            if item.species == 'item' and item.pickup_time < 0 and self.inventory.add_item(item.item):
                item.onDeath()

class Arrow(Entity):
    straight_right =Textures.scale(Textures.rotate(Textures.load_image('Images/enemies/arrow/default_arrow.png').convert_alpha(),90+47),(BLOCK_SIZE,BLOCK_SIZE))
    def __init__(self,pos,velocity:Vector2,shooter:Entity):

        super().__init__(pos,'arrow')
        angle = -velocity.get_angle() 
        tex = Textures.rotate(self.straight_right,angle * 180 / pi)
        self.animation.add_state('going',0,[tex],[self.straight_right])
        self.image.offset = (-tex.get_width()/2,-tex.get_height()/2)
        self.animation.set_state('going')
        self.vel = velocity.copy()
        self.time_til_death = 10 #seconds
        self.range = 2 #blocks
        self.speed = self.vel.magnitude()
        self.animation.animate()
        self.shooter = shooter

        self.blocks_to_travel = self.range * self.speed
        self.base_damage = 2
        self.weight = .1 # in kg
        self.penetration = 10
        self.blocks_traveled = 0
        self.stopped = False

    def onDeath(self):
        super().onDeath()

    def update(self):
        self.time_til_death -= Time.deltaTime
        if self.time_til_death <= 0:
            self.onDeath()
        if self.dead or self.stopped: return
        #move x rect 
        self.collider.move_x(self.vel.x * Time.deltaTime) # move in world coordinates
        if collision_horizontal(self.collider,self.vel.x):
            self.attack(get_nearest_block(self.pos))
            self.stopped = True
        #move y rect 
        self.collider.move_y(self.vel.y * Time.deltaTime) # move in world coordinates

        if collision_vertical(self.collider,self.vel.y):
            self.attack(get_nearest_block(self.pos))
            self.stopped = True
        self.pos.from_tuple(self.collider.center)
        self.blocks_traveled += self.speed * Time.deltaTime
        if self.blocks_traveled >= self.blocks_to_travel:
            self.stopped = True
        for entity in collide_entities(self.collider):
            if entity.species in {'arrow','item'}: continue


            self.onDeath()
            self.attack(entity)
            break

    def onLoad(self):
        #Camera.add_collider(self.collider)
        return super().onLoad()
    
    def onLeave(self):
        #Camera.remove_collider(self.collider)
        return super().onLeave()


    def get_attack_damage(self) -> int:
        return( 0.5 * self.base_damage * (self.vel/2).magnitude_squared() * self.weight * max(0.01,self.penetration)).__trunc__()

class FireArrow(Arrow):
    def get_attack_type(self):
        return FIRE_DAMAGE

class Player(AliveEntity):
    def __init__(self,pos):
        super().__init__(pos,'human')

        self.cx = self.pos.x//CHUNK_SIZE
        self.cy = self.pos.y//CHUNK_SIZE
        recalculate_chunks(self.cx,self.cy)
        self.set_up_animation()

		# stats
        self.exp = 5000 #dont make attribute points (overused). make exp have another purpose. attribute points can lead to severely op setups and the player getting exactly what they want. 
        # damage timer
        self.can_move = True
        self.attacking = False
        self.hurt_time = None
        self.states = ['relaxed','focused']
        self.state = None
        self.set_state(0)
        self.showingInventory = False
        
        self.hotbar = HotbarInventory(9)
        self.ui = InventoryUI(self,(WIDTH*.7,HEIGHT*.7))
        self.hbui = HotBarUI(self)

        self.direction = 'right'

    def set_up_animation(self):
        walk_right,walk_left= Textures.import_folder('player/walk',True,(64,64),True)
        idle_right,idle_left = Textures.import_folder('player/idle',True,(64,64),True)
        attack_right,attack_left = Textures.import_folder('player/attack',True,(64,64),True)
        self.walking_particle = Textures.import_folder('Images/particles/Dirt',False,(PARTICLE_SIZE,PARTICLE_SIZE))[0]
        self.animation.add_state('walk',4,walk_right,walk_left)
        self.animation.add_state('idle',1.2,idle_right,idle_left)
        self.animation.add_state('attack',5,attack_right,attack_left)
        self.animation.set_state('idle')
        self.animation.on_animation_done = self.on_animate_done

    def set_state(self, number: int):
        if self.state is self.states[number]: return False
        self.state = self.states[number]
        if number == 0:
            Camera.set_mouse_assist(True)
        elif number == 1:
            Camera.set_mouse_assist(False)
            #Textures.texture['danger.png'].set_alpha(255)

    def attack(self):
        self.animation.set_state('attack')

    def _attack(self):
        if self.direction == 'right':
            c = Collider(self.pos.x+.2,self.pos.y-.5,.5,1)
        elif self.direction == 'left':
            c = Collider(self.pos.x-.7,self.pos.y-.5,.5,1)

    def take_damage(self, damage: int, type: str,appearance:Appearance = None) -> None:
        
        super().take_damage(damage, type,appearance)
    
    def input(self): #Time.deltaTime is in seconds
        if 'e' in Input.KDQueue:
            self.showingInventory = not self.showingInventory  
            if self.showingInventory:
                self.vel.reset()
                UI.current_ui = self.ui
                UI.ui_on = True
                
            else:
                UI.ui_on = False
                UI.current_ui = UI.Null
                item  = self.ui.in_hand
                if item is not None:
                    item:Item
                    #item.to_entity(self.pos,Input.m_pos_normalized)
                    spawn_item(item,self.pos,Input.m_pos_normalized)
                self.ui.in_hand = None
        if self.showingInventory:return
        self.hbui.update()
        if Input.m_1 and self.animation.state != 'attack':
            #use_item(self.inventory.)
            pass
        
        if 'r' in Input.KDQueue:
            #print('position is ',self.pos)
            place_block(TNT(Camera.world_position_from_normalized(Input.m_pos_normalized).floored()))

        if 'b' in Input.KDQueue:
            spawn_entity(Bunny(self.pos.copy()))
    
        if 'n' in Input.KDQueue:
            velocity = (Camera.world_position_from_normalized(Input.m_pos_normalized) - self.pos).normalized
            if velocity.isZero:
                velocity = Vector2.randdir
            spawn_entity(FireArrow(self.pos + velocity/2,velocity*3+self.vel,self))
        if Input.space_d:
            spawn_item(Items.getItem(HAT),self.pos,Vector2.randdir)
        if self.animation.state != 'attack':
            x,y=  set_mag(Input.d-Input.a,Input.s-Input.w,self.speed * self.ground.surface_friction)
            self.accelerate(x,y)
        else:
            self.vel.reset() #set to 0,0

        if self.vel.x > 0:
            self.animation.direction = 'right' 
        elif self.vel.x < 0:
            self.animation.direction = 'left'

    def move(self):
        super().update()
            
        #detect if in new chunk
        if self.pos.x//CHUNK_SIZE != self.cx:
            #in new chunk
            self.cx = floor(self.pos.x)//CHUNK_SIZE
            self.cy = floor(self.pos.y)//CHUNK_SIZE
            recalculate_chunks(self.cx,self.cy)
            
        elif self.pos.y//CHUNK_SIZE != self.cy:
            #in new chunk
            self.cx = floor(self.pos.x)//CHUNK_SIZE
            self.cy = floor(self.pos.y)//CHUNK_SIZE
            recalculate_chunks(self.cx,self.cy)
   
    def in_chunk(self,cx,cy):
        '''accepts coords in world chunk position'''
        return (cx == self.cx) and (cy == self.cy)

    def on_animate_done(self):
        if self.animation.state == 'attack':
            if self.vel:
                self.animation.set_state('walk')
            else:
                self.animation.set_state('idle')

        self.collect_items()
     
    def animate(self):
        if self.vel and self.animation.state == 'idle': self.animation.set_state('walk')
        elif not self.vel and self.animation.state == 'walk': self.animation.set_state('idle')
        
        if FPS != 0 and self.vel and not self.animation.frames_in_state % (FPS//12):
            #spawn a particle
            Particles.spawn(self.pos + Vector2(-0.07,.2),Vector2.random * 0.5,self.walking_particle,.5)
 
    def update_inventory_ui(self):
        self.ui.update()

    def collect_items(self):
        for item in collide_entities_in_range(self.pos,self.pickup_range):
            item:ItemWrapper
            if item.species == 'item' and item.pickup_time < 0 and (self.hotbar.add_item(item.item) or self.inventory.add_item(item.item) ): #this will never add the same object to both hotbar and inventory becasue the or will only try to add to inventory if the item couldn't be added to the hotbar
                item.onDeath()

    def update(self):
        Camera.program['danger'] = 1-(self.health / self.total_health)
        if self.showingInventory:
            self.update_inventory_ui()
        self.input()
        self.move()
        self.animate()
        
class Spirit(AliveEntity):

    enemies = {'bunny','human'}
    eats = set()# spirits eat nothing (for now)
    fears = set() #spirits fear nothing (for now)

    neutral_to = set()
    right_idle,left_idle = Textures.import_folder('Images/enemies/spirit/idle',True,(32,32),True)
    def __init__(self,pos):
        super().__init__(pos,'spirit')
        self.animation.add_state('idle',8,Spirit.right_idle,Spirit.left_idle)        
        self.animation.set_state('idle')
        self.vision_collider = Collider(0,0,Settings.VISION_BY_SPECIES['spirit']*2,Settings.VISION_BY_SPECIES['spirit']*2)
        self.vision_squared = Settings.VISION_BY_SPECIES['spirit'] ** 2
        self.attack_range_squared = self.stats['attack_range'] ** 2
        self.timer_to_vision = 1
        self.states = ['idle','wander','fight','afraid']
        self.state = self.states[0]
        self.mark:Entity = None
        self.time_to_introspection = 5
        #Set up animation
        for state in self.states:
            self.animation.add_state(state,8,self.right_idle,self.left_idle)

    def set_state(self,number:int):
        if super().set_state(number) is False: return
        if number == 0:
            self.vel.reset()
        elif number == 1:
            self.vel.set_to(Vector2.randdir)

    def update_state(self):
        entities_seen = list(self.get_entities_seen())

        for entity in entities_seen:
            entity:Entity
            if entity.species in self.fears:
                self.set_state(3)
                self.fear_producer = entity
                return 
        self.closest_enemy = None
        closest_distance_squared = float('inf')
        for entity in entities_seen:
            if entity.species in self.enemies:
                dist_squared = (self.pos - entity.pos).magnitude_squared()
                if dist_squared < closest_distance_squared:
                    closest_distance_squared = dist_squared
                    self.closest_enemy = entity
        if self.closest_enemy is not None:
            self.set_state(2)
            return
        else: 
            if self.state is self.states[2]:
                self.set_state(0)
                return

        if self.state is self.states[0]:
            self.set_state(1)
            pass
        elif self.state is self.states[1]:
            self.set_state(0)

    def update(self):
        super().update()
        self.time_to_introspection -= Time.deltaTime
        self.vision_collider.setCenter(*self.pos)
        if self.time_to_introspection < 0:
            self.time_to_introspection = 3
            self.update_state()
        if self.state is self.states[0]: # we are idling
            pass
        elif self.state is self.states[1]: # we are wandering
            pass
        elif self.state is self.states[2]: # we are figthing something
            if self.closest_enemy.dead: self.time_to_introspection = 0; return
            distance_to_enemy  = (self.closest_enemy.pos - self.pos)
            if distance_to_enemy.magnitude_squared() < self.attack_range_squared:
                self.attack(self.closest_enemy)
            self.vel = distance_to_enemy.normalized
        

    def onLoad(self):
        self.time_to_introspection = 0
        print('Loading Spirit')
        return super().onLoad()

class Driver:
    FOLLOW = 1
    AVOID = 2
        
    def __init__(self,pos:Vector2):
        self.pos = pos
        self.target:Vector2 = None
        self.spatial_tolerance = .1
        self.mode = self.FOLLOW

    @property
    def spatial_tolerance(self):
        return self._spatial_tolerance
    
    @spatial_tolerance.setter
    def spatial_tolerance(self,newVal):
        self._spatial_tolerance = newVal
        self.spatial_tolerance_squared = newVal * newVal

    

    def setTarget(self,target:Vector2):
        self.target = target.copy()

    def getAccelerationDirection(self):
        lineVec = self.target - self.pos
        if self.mode is self.AVOID:
            lineVec = -lineVec
        magSqrd = lineVec.magnitude_squared()
        if magSqrd < self.spatial_tolerance_squared:
            return Vector2.zero #this one can actually return a cached value Vector2.zero so it doesn't have to create new ones every frame but that is a microoptimization for later
        else:
            return lineVec/sqrt(magSqrd)
    
class Bunny(AliveEntity):

    enemies = set() #have no natural enemies for now
    eats = set()# bunny's eat nothing (for now)
    fears = {'spirit'}

    neutral_to = set()
    right_idle,left_idle = Textures.import_folder('Images/enemies/bamboo/idle',True,(32,32),True)
    def __init__(self,pos):
        super().__init__(pos,'bunny')
        self.fears = self.fears.copy()
        self.eats = self.eats.copy()
        self.enemies = self.enemies.copy()
        self.animation.add_state('idle',8,Bunny.right_idle,Bunny.left_idle)        
        self.animation.set_state('idle')
        self.vision_collider = Collider(0,0,Settings.VISION_BY_SPECIES['bunny']*2,Settings.VISION_BY_SPECIES['bunny']*2)
        self.vision_squared = Settings.VISION_BY_SPECIES['bunny'] ** 2
        self.driver = Driver(self.pos)

        self.time_to_introspection = 5
        self.timer_to_vision = 1
        self.states = ['idle','wander','afraid','hungry']
        for state in self.states:
            self.animation.add_state(state,8,self.right_idle,self.left_idle)
        self.state = self.states[0]
        self.mark:Entity = None
        self.hunger = 0
        self.sprinting = False

    def get_closest_enemy(self):
        closest:Entity|None = None
        for entity in collide_entities(self.vision_collider):
            if entity.species in Spirit.enemies:
                if closest is None or (closest.pos - self.pos).magnitude_squared() > (entity.pos - self.pos).magnitude_squared():
                    closest = entity 
        return closest 
    
    def set_state(self, number: int):
        if super().set_state(number) is False: return
        if number == 0:
            self.vel.reset()
        elif number == 1:
            self.driver.setTarget(self.pos + Vector2.randdir * 10)


    def update_state(self):
        
        entities_seen = list(self.get_entities_seen())
        for entity in entities_seen:
            entity:Entity
            if entity.species in self.fears:
                print('sees something that it is scared of')
                self.driver.mode = Driver.AVOID
                self.driver.setTarget(entity.pos)
                self.sprinting = True
                self.set_state(2)
                return   
        if self.hunger > 180:
            for entity in entities_seen:
                if entity.species in self.eats:
                    self.set_state(3)
                    self.driver.mode = Driver.FOLLOW
                    self.driver.setTarget(entity.pos)
                    return
        if self.state is self.states[0]:
            self.set_state(1)
        elif self.state is self.states[1]:
            self.set_state(0)
        print('updating state curr:',self.state)       

        #self.state = self.states[1]            

    

    def trySprinting(self) -> float:
        if self.sprinting:
            if self.canDoAction('RUN'):
                self.depleteEnergy('RUN')
                return self.get_energy_multiplier() + 0.5
            else:
                self.sprinting = False
        return 1.0

    def accelerate_with_driver(self):
        self.accelerate(*(self.driver.getAccelerationDirection() * self.ground.surface_friction * self.speed * self.trySprinting()))


    def update(self):
        super().update()

        self.time_to_introspection -= Time.deltaTime
        self.vision_collider.setCenter(*self.pos)
        if self.time_to_introspection < 0:
            self.time_to_introspection = 3
            self.update_state()

        if self.state is self.states[0]: # we are idling
            pass #do nothing
        else:
            self.accelerate_with_driver()
        ''' 
       elif self.state is self.states[1]: #we are wandering
            pass
        elif self.state is self.states[2]: # we are afraid of something
            pass
        elif self.state is self.states[3]: # we are hungry to to something
            pass'''

    def take_damage(self, damage: float, type: str,appearance:Appearance = None) -> None:
        if appearance is not None:
            self.fears.add(appearance.species)
        if self.state in ( self.states[0] , self.states[1]):
            self.time_to_introspection = 0 
        return super().take_damage(damage, type)
        

    def onLoad(self):
        print('Loading bunny')

        self.time_to_introspection = 0
        return super().onLoad()

#### UI ####
class InventoryUI(UI.UI):
    def __init__(self,entity:AliveEntity, surface_size:tuple|list = (WIDTH, HEIGHT)):
        screen_size = (surface_size[0]/WIDTH,surface_size[1]/HEIGHT)
        super().__init__(surface_size, (0,0), screen_size)
        self.screen_center = self.surface_size/2
        self.inventory:None|Inventory = entity.inventory
        self.inventory_size = entity.inventory.spaces
        self.armour_inventory = entity.armour_inventory
        self.has_hotbar = hasattr(entity,'hotbar')
        if self.has_hotbar:
            self.hb_inventory = entity.hotbar
            self.hb_size = entity.hotbar.spaces
            self.hotbar:Inventory = entity.hotbar

        self.collider = Collider(self.topleft.x,self.topleft.y,screen_size[0]*2,screen_size[1]*2)

        self.slots_width = 9
        self.entity = entity
        self.slot_spacing = ITEM_SIZE + 7
        self.slots_center = Vector2(0,100) # where should the center of the slots be?
        self.armour_slots_center = Vector2(-130,-120)
        self.hb_slots_center = Vector2(0,150)

        self.recalc_slots()
        self.in_hand = None

    def recalc_slots(self):
        slots_size = Vector2(self.slots_width * self.slot_spacing, self.inventory_size//self.slots_width * self.slot_spacing)
        self.items_offset = self.screen_center + self.slots_center - slots_size/2

        self.slots = [ItemSlot(((i%self.slots_width)*self.slot_spacing+self.items_offset[0],(i//self.slots_width)*self.slot_spacing+self.items_offset[1]),i,self.inventory) for i in range(self.inventory_size)]
        self.thingy = self.size.inverse()

        if self.has_hotbar:
            self.hb_offset = self.screen_center+self.hb_slots_center - Vector2(self.hb_size * self.slot_spacing,self.slot_spacing)/2 
            print(self.hb_offset,self.hb_size)
            self.hb_slots = [ItemSlot((i*self.slot_spacing+self.hb_offset[0],self.slot_spacing+self.hb_offset[1]),i,self.hotbar) for i in range(self.hb_size)]

        armour_size = Vector2(self.slot_spacing,self.slot_spacing * self.armour_inventory.spaces)
        self.armour_offset = self.screen_center + self.armour_slots_center - armour_size/2
        self.armour_slots = [ItemSlot((self.armour_offset[0],i*self.slot_spacing+self.armour_offset[1]),name,self.armour_inventory) for i,name in enumerate(self.armour_inventory.inventory)]
        for armour_slot in self.armour_slots:
            armour_slot.bg_color = (60,30,25)

    def update(self):
        self.surface.fill('grey')
        if self.collider.collide_point_inclusive(Input.m_pos_normalized.tuple): 
            self.relative_mouse_position_normalized = (Input.m_pos_normalized - self.center).vector_mul(self.thingy)
            self.rel_mouse_pos = (self.relative_mouse_position_normalized+ones).vector_mul(self.surface_size/2)
            for slot in self.slots:
                slot.update(self.rel_mouse_pos)
                if slot.state == slot.HOVER:
                    if Input.m_d1:
                        self.in_hand = self.inventory.set_item(self.in_hand,slot.index)
            if self.has_hotbar:
                for slot in self.hb_slots:
                    slot.update(self.rel_mouse_pos)
                    if slot.state == slot.HOVER:
                        if Input.m_d1:
                            self.in_hand = self.hotbar.set_item(self.in_hand,slot.index)            
            for slot in self.armour_slots:
                slot.update(self.rel_mouse_pos)
                if slot.state == slot.HOVER:
                    if Input.m_d1:
                        self.in_hand = self.armour_inventory.set_armour(self.in_hand,slot.index)

        else:
            if Input.m_d1 and self.in_hand is not None:
                spawn_item(self.in_hand,self.entity.pos,Input.m_pos_normalized*2)
                self.in_hand = None

    def draw(self):
        for slot in self.slots:
            slot.draw(self.surface)
        for slot in self.armour_slots:
            slot.draw(self.surface)
        if self.has_hotbar:
            for slot in self.hb_slots:
                slot.draw(self.surface)
        if self.in_hand is not None:
            self.in_hand:Item
            self.surface.blit(self.in_hand.animation.surf,(self.rel_mouse_pos.x-ITEM_SIZE//2,self.rel_mouse_pos.y-ITEM_SIZE//2))
        entity = pygame.transform.scale_by(self.entity.image.surf,2)
        draw.rect(self.surface,(70,70,70),entity.get_rect().move(self.screen_center.x-100,10))
        self.surface.blit(entity,(self.screen_center.x-100,10))

        super().draw()

class HotBarUI:
    def __init__(self,entity:AliveEntity):
        if not hasattr(entity,'hotbar'):
            raise RuntimeError('entity passed into HotBarUI does not seem to define its hotbar!')
        self.entity = entity
        self.slot_spacing = 4 #this is how many pixels will be between the edges of each
        self.hb_inventory:Inventory = entity.hotbar
        self.inventory_size = entity.hotbar.spaces
        self.background_color = [133,133,133,150]    #RGBA
        self.surface = Surface((self.hb_inventory.spaces * (self.slot_spacing + ITEM_SIZE) + self.slot_spacing, ITEM_SIZE + self.slot_spacing * 2),pygame.SRCALPHA)
        self.x = Camera.HALFSCREENSIZE.x - self.surface.get_width()/2
        self.y = Camera.HEIGHT - self.surface.get_height()
        self.topleft = Vector2(self.x,self.y)
        self.recalc_slots()
        Events.add_OnResize(self.onResize)
        self.collider = Collider(self.x / WIDTH,self.y / HEIGHT,self.surface.get_width()/WIDTH,self.surface.get_height()/HEIGHT)# this is a normalized collider e.g. its values are from [0,1] so that they work with the input
        Camera.ui_draw_method(self)
    
    def onResize(self,newWidth,newHeight):
        self.recalc_slots()

    def recalc_slots(self):

        self.slots = [ItemSlot((i*(ITEM_SIZE+self.slot_spacing)+self.slot_spacing,self.slot_spacing),i,self.hb_inventory) for i in range(self.inventory_size)]
        self.surface.fill(self.background_color)

    def update(self):
        m_pos = Input.m_pos.vector_mul(Camera.screen_size.inverse())
        if self.collider.collide_point_inclusive(m_pos.tuple):
            m_pos = m_pos.vector_mul(Camera.screen_size)
            m_pos -= self.topleft
            for slot in self.slots:
                slot.update(m_pos)
                if slot.state == slot.HOVER:
                    if Input.m_d1:
                        self.hb_inventory.selected = slot.index

    def draw(self):
        for slot in self.slots:
            slot.draw(self.surface)
        Camera.screen.blit(self.surface,self.topleft.tupled_ints)
        #if self.in_hand is not None:
        #    self.in_hand:Item
        #    self.surface.blit(self.in_hand.animation.surf,(self.rel_mouse_pos.x-ITEM_SIZE//2,self.rel_mouse_pos.y-ITEM_SIZE//2))

#######################################
########### BLOCK_CHUNKS ##############
#######################################


active_chunks = [] 
'''stores the x and y values of the loaded chunks'''

_DEBUG_ = True

def noise_to_ground(n):
  if n > 1 or n < 0: 
    return None
  if n > .73:
    return getGround(GROUND_STONE)
  if n > .43:
    return getGround(GROUND_GRASS)
  
  return getGround(GROUND_WATER) 
if __name__ == "__main__":
    mylist = [noise1(x*3) for x in range(1000)]
    mylist.sort()
    from matplotlib import pyplot
    pyplot.plot(mylist)
    pyplot.show()

class Chunk:  
    _insts:dict = {}

    @classmethod
    def exists_at(cls,chunk_pos:tuple|list) -> bool:
        return chunk_pos in cls._insts
    
    @classmethod
    def get_ground_at(cls,x,y) -> Ground|None:
        global chunks
        c_pos = (x//CHUNK_SIZE,y//CHUNK_SIZE)
        if c_pos in chunks:
            chunk = chunks[c_pos]
            return chunk._get_ground(x,y)
        return None
        
    def __new__(cls,pos:tuple[int,int]):
        if pos in cls._insts:
            return cls._insts[pos]
        else:
            chunk = super(Chunk,cls).__new__(cls)
            chunk.pos = Vector2(pos[0] * CHUNK_SIZE,pos[1] * CHUNK_SIZE)

            chunk.blocks = []
            chunk.onCreationFinish = []

            surf = Surface((CHUNK_SIZE*BLOCK_SIZE,CHUNK_SIZE*BLOCK_SIZE))
            chunk.csurf = CSurface(surf ,chunk.pos,(0,0))
            chunk.collider = Collider(pos[0]*CHUNK_SIZE,pos[1]*CHUNK_SIZE,CHUNK_SIZE,CHUNK_SIZE)
            
            x,y = pos
            chunk.subdivision_colliders = (Collider(x,y,HALF_CHUNK_SIZE,HALF_CHUNK_SIZE),Collider(x+HALF_CHUNK_SIZE,y,HALF_CHUNK_SIZE,HALF_CHUNK_SIZE),Collider(x,y+HALF_CHUNK_SIZE,HALF_CHUNK_SIZE,HALF_CHUNK_SIZE),Collider(x+HALF_CHUNK_SIZE,y+HALF_CHUNK_SIZE,HALF_CHUNK_SIZE,HALF_CHUNK_SIZE))
            chunk.biome = PLAINS #prefferably call a function <get_biome(chunk_pos)> 
            chunk.active = False
            chunk.dead_blocks = []
            cls._insts[pos] = chunk

            return cls._insts[pos]
        
    def __str__(self) -> str:
        return f"Chunk: {self.chunk_pos}"
    __slots__ = ('chunk_pos','pos','collider','id','data','blocks','biome','active','ground','subdivision_colliders','onCreationFinish','csurf','dead_blocks')
    # removed slots 'x','y','subdivision_lengths','items','items_sub',
    def __init__(self,pos:tuple[int,int]):
        self.chunk_pos = (pos[0].__trunc__(),pos[1].__trunc__())
        #for drawing to screen
        #self.x,self.y = pos[0] * CHUNK_SIZE, pos[1] * CHUNK_SIZE 
        self.pos:Vector2# = Vector2(pos[0] * CHUNK_SIZE,pos[1] * CHUNK_SIZE)
        self.collider:Collider
        
        self.id:int = hash(self.chunk_pos)
        self.data:np.ndarray #numpy.ndarray
        self.blocks:list[Block]
      
        self.biome:int
        self.active:bool
        self.ground:list
        self.subdivision_colliders:tuple[Collider,Collider,Collider,Collider]
        self.onCreationFinish:list
        self.csurf:CSurface 
        self.dead_blocks:list[Block]

    @property
    def surf(self) -> Surface:
        return self.csurf.surf
    
    @surf.setter
    def surf(self,__object):
        self.csurf.surf = __object

    def _get_ground(self,x,y) -> Ground:
        #this is a method to bypass all the checks made by normal ground_getter but only works if you already know what chunk the block is in
        x = floor(x) % CHUNK_SIZE
        y = floor(y) % CHUNK_SIZE
        return self.ground[y][x]
    
    def get_ground(self,x,y):
        assert (x//CHUNK_SIZE, y//CHUNK_SIZE) == self.chunk_pos, 'that block is not in this chunk'
        assert self.chunk_pos in chunks, 'this chunk is not fully loaded yet meaning it may not have all ground existing yet'
        return self._get_ground(x,y)
    
  

    def update(self):
        #we are being loaded and all of our blocks and items are being loaded
        #step one, update all of our blocks

        for block in self.dead_blocks:
            self.blocks.remove(block)
        self.dead_blocks.clear()

        if _DEBUG_:
            for block in reversed(self.blocks):
                if block.dead:
                    self.blocks.remove(block)
                    print('A block of type',block.type,'did not manually add itself to the dead_blockslist')
        
        for block in self.blocks:
            block.update()

    def add_block(self,block:Block):
        for existing_block in self.blocks:
            existing_block:Block
            if block.collider.collide_collider(existing_block.collider):
                return False
        self.blocks.append(block)
        if self in current_chunks:
            block.onLoad()
        return True
    
    def remove_block(self,block:Block):
        block.onLeave()
        self.blocks.remove(block)

    def get_blocks(self) -> list:
        print('Getting Blocks of Chunk',self.chunk_pos)
        return self.blocks.copy() #doesn't have to be a copy by just to make sure nothing breaks it is better to send a copy

    def load(self):
        if self.chunk_pos in chunks:
            self.active = True
            Camera.add_background(self.csurf)
            self.load_blocks()
        else:
            self.onCreationFinish.append(self.load)

    def unload(self):
        if self.chunk_pos in chunks:
            self.active = False
            Camera.remove_background(self.csurf)
            self.unload_blocks()
        else:
            self.onCreationFinish.append(self.unload)

    def load_blocks(self) -> None:
        for block in self.blocks:
            block:Block
            block.onLoad()
    
    def unload_blocks(self) -> None:
        for block in self.blocks:
            block:Block
            block.onLeave()

chunks:dict[tuple,Chunk] = {}
def _create(chunk:Chunk):

    ## PHASE 1 ##
    #generate layered noisemap
    xs = np.arange(CHUNK_SIZE)+chunk.chunk_pos[0]*CHUNK_SIZE
    ys = np.arange(CHUNK_SIZE)+chunk.chunk_pos[1]*CHUNK_SIZE
    chunk.data = noise2ali(xs,ys,OCTAVES,SCALE,ISLAND_BLEND,sigmoid_dist,MAPWIDTH,MAPHEIGHT)  

    yield  
    chunk.ground = make2dlist(CHUNK_SIZE)
    #draw layered noisemap onto surface
    #note this will not be represented in real time as it will still need to get loaded into the camera, which happens at the end of the creation process
    surf = chunk.surf
    for y, row in enumerate(chunk.data):
        for x, noise in enumerate(row):
            ground = noise_to_ground(noise) 
            chunk.ground[y][x] = ground
            #pygame.draw.rect(surf,(noise*255,)*3,(x*BLOCK_SIZE,y*BLOCK_SIZE,BLOCK_SIZE,BLOCK_SIZE))
            surf.blit(Textures.texture[ground.tex],(x*BLOCK_SIZE,y*BLOCK_SIZE))
            #surf.blit(myfont.render(str((x+chunk.chunk_pos[0]*CHUNK_SIZE,y+chunk.chunk_pos[1]*CHUNK_SIZE)),True,'black'),(x*BLOCK_SIZE,y*BLOCK_SIZE))
    #yield
    

    draw.lines(chunk.surf,(255,0,0),1,((0,0),(CHUNK_SIZE*BLOCK_SIZE,0),(CHUNK_SIZE*BLOCK_SIZE,CHUNK_SIZE*BLOCK_SIZE),(0,CHUNK_SIZE*BLOCK_SIZE)),3)    
    #to make trees we check the 8 immediately surrounding chunks if they exist and add them to a list
    cx ,cy = chunk.chunk_pos
    surrounding_chunks = [(cx-1,cy-1),(cx,cy-1),(cx+1,cy-1),(cx-1,cy),(cx+1,cy),(cx-1,cy+1),(cx,cy+1),(cx+1,cy+1)]
    existing_surrounding_chunks = []
    for chunk_pos in surrounding_chunks:
        if chunk_pos in chunks:
            existing_surrounding_chunks.append(chunk_pos)
            
    def isValid(x,y):
        for chunk_pos in existing_surrounding_chunks:
            o_chunk:Chunk = chunks[chunk_pos]
            for block in o_chunk.blocks:
                block:Block
                if block.type == 'tree':
                    if hypot(block.pos.x-x,block.pos.y-y) <= Settings.TREE_SPACING_BY_BIOME[chunk.biome]:
                        return False
        for block in chunk.blocks: #check own chunk
            block:Block
            if block.type == 'tree':
                if hypot(block.pos.x-x,block.pos.y-y) <= Settings.TREE_SPACING_BY_BIOME[chunk.biome]:
                    return False  
        return True

    for _ in range(10):
        x = random.randint(chunk.pos.x, chunk.pos.x + CHUNK_SIZE - 1)
        y = random.randint(chunk.pos.y, chunk.pos.y + CHUNK_SIZE - 1)
        g = chunk._get_ground(x,y)
        if Tree.spawnable_on(g) and isValid(x,y):
            chunk.blocks.append(Tree((x,y),g))

    chunks[chunk.chunk_pos] = chunk
    for cmd in chunk.onCreationFinish:
        cmd()
    chunk.onCreationFinish.clear()

    yield 'able to add'
    #returns a StopIteration exception
    yield 
    #if village_creater.isObject(cx,cy):
        #chunk.ground[4][4] = Village
        #surf.blit(Textures.texture[Village.tex],(4*BLOCK_SIZE,4*BLOCK_SIZE))
    
current_chunks:list[Chunk] = [] 
'''stores the chunk instances of the loaded chunks'''

chunk_loading_queue = deque()

def queue_chunk(chunk_pos:tuple|list):
    #first make some checks to make sure that its not loaded or currently being loaded
    assert chunk_pos not in chunks, 'chunk is already loaded'
    if chunk_pos in chunk_loaders:
        for chunk in chunk_loading_queue:
            chunk:Chunk
            if chunk.chunk_pos == chunk_pos:
                return chunk
        return chunk_loaders[chunk_pos]
    chunk = Chunk(chunk_pos)
    chunk_loading_queue.append(chunk)
    return chunk

chunk_loaders = {}
def _chunk_step(chunk:Chunk):
    
    if chunk.chunk_pos in chunk_loaders:
        try:
            return next(chunk_loaders[chunk.chunk_pos])
        except StopIteration:
            del chunk_loaders[chunk.chunk_pos]
            return 'done'
    else:
        chunk_loaders[chunk.chunk_pos] = _create(chunk)
        return next(chunk_loaders[chunk.chunk_pos])

def step():
    if not chunk_loading_queue and chunk_loaders: raise RuntimeError(f'there are 0 chunks in queue but {len(chunk_loaders)} chunk loaders')  #can be deleted later in prod
    if not chunk_loading_queue: return 
    chunk_to_load:Chunk = chunk_loading_queue[0]
    status = _chunk_step(chunk_to_load)

    match status:
        case 'able to add':
           pass
        case 'done':
            chunk_loading_queue.popleft()
        case _:
            #no status update
            pass
    chunk_loading_queue.rotate()

def place_block(block:Block):
    chunk:Chunk = chunks.get((block.pos//CHUNK_SIZE).tuple)
    return False if chunk is None else chunk.add_block(block)

#######################################
########### ENTITY CHUNKS #############
#######################################


entity_chunks:dict[tuple[int,int],list[Entity]] = {}
def get_entity_chunk(entity:Entity):
    return (entity.pos//CHUNK_SIZE).to_ints()

def print_entity_chunks():
    for chunk in active_chunks:
        if chunk not in entity_chunks:
            print(chunk,': Empty')
        else:
            print(chunk,':',[et.species for et in entity_chunks[chunk]])

def get_nearest_block(pos:Vector2):
    nearest = None
    dist_sqrd = float('inf')
    cpos = (pos//CHUNK_SIZE).tuple
    to_check = []
    for chunk in get_around_chunk(cpos[0],cpos[1]):
        if chunk in chunks:
            to_check.append(chunks[chunk])
    for chunk in to_check:
        for obs in chunk.blocks:
            obs:Block
            distance_squared = (obs.pos-pos).magnitude_squared()
            if distance_squared < dist_sqrd:
                dist_sqrd = distance_squared
                nearest = obs
    return nearest

def spawn_entity(entity:Entity):
    chunk_pos = (entity.pos//CHUNK_SIZE).tuple
    chunk = entity_chunks.get(chunk_pos) #try to get the chunk its in, if not found then create a new chunk(list)
    if chunk_pos in active_chunks:
        #print('Entity spawned is being shown!')
        entity.onLoad()
    if chunk is None: #
        entity_chunks[chunk_pos]  = chunk = []
    if _DEBUG_ and entity in chunk: raise RuntimeError("Entity already in chunk!")
    chunk.append(entity)

def find_entity_chunk(entity:Entity) -> tuple[int,int]:
    for chunk_pos in entity_chunks:
        chunk = entity_chunks[chunk_pos]
        if entity in chunk:
            return chunk_pos

def manage_chunks():
    #search for each entity and see if they crossed a chunk border
    for chunk_pos in active_chunks:
        if chunk_pos in entity_chunks:
            chunk = entity_chunks[chunk_pos]
            for entity in reversed(chunk): #could just do range(len(chunk),0,-1) and use pop instead of remove, which is faster
        
                entity_chunk = (entity.pos//CHUNK_SIZE).tuple
                if  entity_chunk != chunk_pos:            
                    chunk.remove(entity)

                    new_chunk = entity_chunks.get(entity_chunk) #try to get the chunk its in, if not found then create a new chunk(list)
                    if new_chunk is None:
                        entity_chunks[entity_chunk] = new_chunk = []
                    new_chunk.append(entity)
                    if entity_chunk not in active_chunks: #if the chunk that the entity moved to is not loaded then unload the entity
                        entity.onLeave()

    for dead_entity in dead_entities:
       remove_entity(dead_entity)
    dead_entities.clear()

def remove_entity(entity:Entity):
    chunk_pos = (entity.pos//CHUNK_SIZE).tuple
    entity_chunks[chunk_pos].remove(entity)
    if not entity_chunks[chunk_pos]: #if the entity chunk is now empty
        #delete the chunk because it is not needed anymore
        del entity_chunks[chunk_pos]
def update_entities():
    for chunk_pos in active_chunks:
        chunk = entity_chunks.get(chunk_pos,[])
        for entity in chunk:
            entity.update()

def collide_entities(collider:Collider):
    checked = set()
    for y in inclusive_range(floor(collider.top),ceil(collider.bottom),CHUNK_SIZE):
        for x in inclusive_range(floor(collider.left),ceil(collider.right),CHUNK_SIZE):
            cpos = (x//CHUNK_SIZE,y//CHUNK_SIZE)
            if cpos in checked: continue
            e_chunk = entity_chunks.get(cpos)
            if e_chunk is not None:
                for entity in e_chunk:
                    if entity.dead: continue
                    if collider.collide_collider(entity.collider):
                        yield entity
            checked.add(cpos)
    
def collide_entities_in_range(pos:Vector2,range:float):
    range_sqrd = range*range
    checked = set()
    for y in inclusive_range(floor(pos.y-range),ceil(pos.y+range),CHUNK_SIZE):
        for x in inclusive_range(floor(pos.x-range),ceil(pos.x+range),CHUNK_SIZE):  
            cpos = (x//CHUNK_SIZE,y//CHUNK_SIZE)
            if cpos in checked:continue
            e_chunk = entity_chunks.get(cpos)
            if e_chunk is not None:
                for entity in e_chunk:
                    if not entity.dead and (entity.pos-pos).magnitude_squared() <= range_sqrd:
                        yield entity

def spawn_item(item:Item,pos:Vector2,vel:Vector2|None=None):
    #step 1) create itemWrapper
    iw = ItemWrapper(pos,item)
    if vel is not None:
        iw.vel.set_to(vel)
    #step 2) Spawn Itemwrapper as entity
    spawn_entity(iw)
 
def get_chunk(cx,cy) -> Chunk:
    chunk:Chunk = chunks.get((cx,cy))
    if chunk is None:
        chunk = queue_chunk((cx,cy))
    return chunk
    
def get_around_chunk(cx,cy,xbuffer = 1):
    #returns perfect square
    return [(cx+x,cy + y) for x in range(-Settings.RenderDistance,Settings.RenderDistance+1,1) for y in range(-Settings.RenderDistance,Settings.RenderDistance+1,1)] 

def get_loaded_chunks_collided(collider:Collider):
    if _DEBUG_ and not is_collider(collider): raise RuntimeError("<collider> argument must be of type<settings.Collider>")
    for chunk in current_chunks:
        if collider.collide_collider(chunk.collider):
            yield chunk
    
def get_chunks_collided(collider:Collider):
    checked = set() 
    for y in inclusive_range(floor(collider.top),ceil(collider.bottom),CHUNK_SIZE):
        for x in inclusive_range(floor(collider.left),ceil(collider.right),CHUNK_SIZE):
            cpos = (x//CHUNK_SIZE,y//CHUNK_SIZE)
            if cpos in checked: continue
            chunk:Chunk = chunks.get(cpos)
            if chunk is not None:
                yield chunk
            checked.add(cpos)

def collide_blocks(collider:Collider): 
    if not is_collider(collider): raise RuntimeError("<collider> argument must be of type<settings.Collider>")
    for chunk in get_chunks_collided(collider):
        for obstacle in chunk.blocks:
            if collider.collide_collider(obstacle.collider):
                yield obstacle
                
def collision_horizontal(collider:Collider,vx:int|float) -> bool:
    if not is_collider(collider): raise RuntimeError("<collider> argument must be of type<settings.Collider>")
    if not vx: return False
    hit_smthng = False
    for chunk in get_chunks_collided(collider):
        for obstacle in chunk.blocks:
            if collider.collide_collider(obstacle.collider):
                if vx > 0: # moving right
                    collider.setRight(obstacle.collider.left)
                else: # moving left, we can guarantee this because vx != zero due to the safety clause earlier
                    collider.setLeft(obstacle.collider.right)
                hit_smthng = True   
    return hit_smthng

def collision_vertical(collider:Collider,vy:float|int):
    if not is_collider(collider): raise RuntimeError("<collider> argument must be of type<settings.Collider>")
    if not vy: return False
    hit_smthng = False
    for chunk in get_chunks_collided(collider):
        for obstacle in chunk.blocks:
            obstacle:Has_Collider
            if collider.collide_collider(obstacle.collider):
                if vy > 0: # moving down
                    collider.setBottom(obstacle.collider.top)
                if vy < 0: # moving up
                    collider.setTop(obstacle.collider.bottom)
                hit_smthng = True
    return hit_smthng

all_chunks_ever_added = set()

def recalculate_chunks(pcx,pcy):
    global active_chunks
    #get chunks that will be added
    new_chunks = get_around_chunk(floor(pcx),floor(pcy))
    added_chunks = []
    removed_chunks = []
    for chunk in new_chunks:
        if chunk not in active_chunks:
            added_chunks.append(chunk)
    for chunk in active_chunks:
      if chunk not in new_chunks:
        removed_chunks.append(chunk)
    
    if _DEBUG_: #check that a chunk was not removed and added in one go
        for chunk in added_chunks:
            if chunk in removed_chunks:
                raise RuntimeError("Cannot add and remove chunk at once!")
    
    #get chunks that will be removed
    for old_chunk in removed_chunks:
      if old_chunk not in all_chunks_ever_added:
          print('Something is seriously wrong, a chunk that was never added is currently trying to be removed')
      for entity in entity_chunks.get(old_chunk,[]):
        entity.onLeave()
      old_chunk = get_chunk(*old_chunk)
      old_chunk.unload()
      current_chunks.remove(old_chunk)



    for new_chunk in added_chunks:
        all_chunks_ever_added.add(new_chunk)
        for entity in entity_chunks.get(new_chunk,[]):
            entity.onLoad()
        new_chunk = get_chunk(*new_chunk)
        new_chunk.load()
        current_chunks.append(new_chunk)
    active_chunks = new_chunks

def update():
    for chunk in current_chunks:
        chunk:Chunk
        chunk.update()

@njit(cache =True)
def _sdtb(px,py,cx,cy,w,h):
    offset_x = abs(px - cx) - w/2
    offset_y = abs(py - cy) - h/2
    unsignedDst = hypot(max(offset_x,0),max(offset_y,0))
    dstInsideBox = max(min(offset_x,0),min(offset_y,0))
    return unsignedDst + dstInsideBox
_sdtb(1.0,1.0,1.0,1.0,1.0,1.0)

def signed_distance_to_box(x,y,collider:Collider):
    return _sdtb(x,y,collider.centerx,collider.centery,collider.width,collider.height)
def get_collider_offset(raydir:Vector2,half_width):
 
    #ch_over2 = collider.height/2
    rx,ry = raydir
    rx *= half_width
    ry *= half_width
    return Vector2(rx,ry)


def can_see_each_other(entity1:Entity,entity2:Entity) -> bool:
    return ray_can_reach(entity1.pos,entity2.pos)




def raycast(pos:Vector2,direction:Vector2):
    MAX_DIST = 500
    #we look at current chunk and all surrounding chunks to take the 
    dx,dy = direction
    offset_x = dx * HALF_CHUNK_SIZE
    offset_y = dy *  HALF_CHUNK_SIZE
    tl = [pos.x+offset_x-HALF_CHUNK_SIZE,pos.y+offset_y-HALF_CHUNK_SIZE]
    tr = [pos.x+offset_x+HALF_CHUNK_SIZE,pos.y+offset_y-HALF_CHUNK_SIZE]
    bl = [pos.x+offset_x-HALF_CHUNK_SIZE,pos.y+offset_y+HALF_CHUNK_SIZE]
    br = [pos.x+offset_x+HALF_CHUNK_SIZE,pos.y+offset_y+HALF_CHUNK_SIZE]
    def dist_to_closest(px,py):
        dist = CHUNK_SIZE
        x,y = tl
        x//=CHUNK_SIZE
        y//=CHUNK_SIZE
        chunk:Chunk = chunks.get((x,y))
        if chunk is not None:
            for obstacle in chunk.blocks:
                obstacle:Has_Collider
                d = signed_distance_to_box(px,py,obstacle.collider)
                if d < dist:
                    dist = d
        x,y = tr
        x//=CHUNK_SIZE
        y//=CHUNK_SIZE
        chunk:Chunk = chunks.get((x,y))
        if chunk is not None: 
            for obstacle in chunk.blocks:
                obstacle:Has_Collider
                d = signed_distance_to_box(px,py,obstacle.collider)
                if d < dist:
                    dist = d
        x,y = bl
        x//=CHUNK_SIZE
        y//=CHUNK_SIZE
        chunk:Chunk = chunks.get((x,y))
        if chunk is not None:
            for obstacle in chunk.blocks:
                obstacle:Has_Collider
                d = signed_distance_to_box(px,py,obstacle.collider)
                if d < dist:
                    dist = d
        x,y = br
        x//=CHUNK_SIZE
        y//=CHUNK_SIZE
        chunk:Chunk = chunks.get((x,y))
        if chunk is not None:
            for obstacle in chunk.blocks:
                obstacle:Has_Collider
                d = signed_distance_to_box(px,py,obstacle.collider)
                if d < dist:
                    dist = d
        return dist

    x,y = pos
    current_len = 0   
    raylen = dist_to_closest(x,y)
    while raylen > .001:
        cx = dx * raylen
        cy = dy * raylen
        x += cx
        y += cy
        tl[0] += cx
        tl[1] += cy
        tr[0] += cx
        tr[1] += cy
        bl[0] += cx
        bl[1] += cy
        br[0] += cx
        br[1] += cy
        current_len += raylen
        if current_len > MAX_DIST:
            return MAX_DIST
        raylen = dist_to_closest(x,y)

    return current_len

def ray_can_reach(pos:Vector2,end_pos:Vector2):
    #we look at current chunk and all surrounding chunks to take the 
    dist_to_each_other = (end_pos-pos).magnitude()
    direction = (end_pos - pos).normalized
    dx,dy = direction
    offset_x = dx * HALF_CHUNK_SIZE
    offset_y = dy *  HALF_CHUNK_SIZE
    tl = [pos.x+offset_x-HALF_CHUNK_SIZE,pos.y+offset_y-HALF_CHUNK_SIZE]
    tr = [pos.x+offset_x+HALF_CHUNK_SIZE,pos.y+offset_y-HALF_CHUNK_SIZE]
    bl = [pos.x+offset_x-HALF_CHUNK_SIZE,pos.y+offset_y+HALF_CHUNK_SIZE]
    br = [pos.x+offset_x+HALF_CHUNK_SIZE,pos.y+offset_y+HALF_CHUNK_SIZE]
    def dist_to_closest(px,py):
        dist = CHUNK_SIZE
        x,y = tl
        x//=CHUNK_SIZE
        y//=CHUNK_SIZE
        chunk:Chunk = chunks.get((x,y))
        if chunk is not None:
            for obstacle in chunk.blocks:
                obstacle:Has_Collider
                d = signed_distance_to_box(px,py,obstacle.collider)
                if d < dist:
                    dist = d
        x,y = tr
        x//=CHUNK_SIZE
        y//=CHUNK_SIZE
        chunk:Chunk = chunks.get((x,y))
        if chunk is not None: 
            for obstacle in chunk.blocks:
                obstacle:Has_Collider
                d = signed_distance_to_box(px,py,obstacle.collider)
                if d < dist:
                    dist = d
        x,y = bl
        x//=CHUNK_SIZE
        y//=CHUNK_SIZE
        chunk:Chunk = chunks.get((x,y))
        if chunk is not None:
            for obstacle in chunk.blocks:
                obstacle:Has_Collider
                d = signed_distance_to_box(px,py,obstacle.collider)
                if d < dist:
                    dist = d
        x,y = br
        x//=CHUNK_SIZE
        y//=CHUNK_SIZE
        chunk:Chunk = chunks.get((x,y))
        if chunk is not None:
            for obstacle in chunk.blocks:
                obstacle:Has_Collider
                d = signed_distance_to_box(px,py,obstacle.collider)
                if d < dist:
                    dist = d
        return dist

    x,y = pos
    current_len = 0   
    raylen = dist_to_closest(x,y)
    while raylen > .001:
        cx = dx * raylen
        cy = dy * raylen
        x += cx
        y += cy
        tl[0] += cx
        tl[1] += cy
        tr[0] += cx
        tr[1] += cy
        bl[0] += cx
        bl[1] += cy
        br[0] += cx
        br[1] += cy
        current_len += raylen
        if current_len > dist_to_each_other:
            return True
        raylen = dist_to_closest(x,y)
    return False


if __name__ == '__main__':
    from pympler.asizeof import asizeof
    chunk = Chunk((1,1))
    print(asizeof(chunk.ground if chunk.active else 0))
    ting = _create(chunk)
    for _ in ting:
        pass
    print(asizeof(chunk.ground))
