from typing import Generator, Union,Callable,Optional
from .Constants import *
from pygame import Surface,draw,font,transform,constants as const
from .. import debug
import numpy as np
from ..Utils.Math.Vector import Vector2, ones
from ..Utils.Math.Collider import Collider
from ..Utils.Noise import WorleyNoiseSimple,LayeredNoiseMap, rescale, unit_smoothstep
from ..Utils.Math.game_math import  half_sqrt_2, Vector2Int,TO_DEGREES, hypot, inclusive_range,make2dlist,collide_chunks
from ..Utils.Math.Fast import njit
from random import randint
from .. import Textures
from collections import deque
from . import Camera
from .Errors import GenerationError, EntitySetupError
from math import log,sqrt 
from . import Settings
from . import InputGame as Input
from . import ground
from . import Time
from .Camera import CSurface
from . import Particles
from .Inventory import ArmorInventory

from .Inventory import UniversalInventory, Hotbar
from sys import intern
from .Entities import GameObject
from .EntityEffects import *
from . import Explosion
from .GameScreen.Appearance import Appearance
from .GameScreen.Animation import Animation
dead_entities = []



#### BLOCKS ####
class Block(GameObject):
    tex_name = '<tex_name> NOT SET!!!'
    anim_fps = 0
    @staticmethod
    def spawnable_on(ground):
      return True
    __slots__ = 'collider','tags','blast_resistance','hardness','animation'
    def __init__(self,pos: Vector2Int,typeid:str):
        hb = Settings.HITBOX_SIZE.get(typeid,(1,1))
        self.collider = Collider.SpawnOnBlockCenter(pos.x,pos.y,hb[0],hb[1])
        super().__init__(Vector2(*self.collider.center),typeid)#hp -> huan pablo
        self.tags = set()
        self.csurface = CSurface.inferOffset(Textures.blocks[self.tex_name][0],self.pos)
        self.blast_resistance = 0 
        self.hardness = 1
        self.animation = Animation.SimpleAnimation(self.csurface,self.anim_fps,Textures.blocks[self.tex_name])
        self.dead = False
        self.csurface.offset = Settings.SURFACE_OFFSET.get(typeid,(-BLOCK_SIZE//2,-BLOCK_SIZE//2))

    def take_damage(self,damage:int,type:str,appearance:Appearance|None = None):
        if type is EXPLOSION_DAMAGE:
            if damage > self.blast_resistance:
                self.onDeath()
        elif type is PHYSICAL_DAMAGE:
            pass 

    def onDeath(self):
        if super().onDeath():
            chunk = chunks[(self.pos//CHUNK_SIZE).tuple]
            chunk.dead_blocks.append(self)
            return True
        return False

    def update(self):
        self.animation.animate()

class Tree(Block):
    tex_name = '03.png'
    anim_fps = 0

    @staticmethod
    def spawnable_on(ground:ground.Ground) -> bool:
        return ground.name is Settings.GROUND_NAME_BY_NUMBER[GROUND_DIRT]
    #this class is an "obstacle" 
    def __init__(self,pos:Vector2Int,ground:ground.Ground):
        assert Tree.spawnable_on(ground), f"Tree was spawned on illegal block: {ground}"
        super().__init__(pos,'tree')
        self.blast_resistance = 10
        
class TNT(Block):
    tex_name = 'tnt'
    @staticmethod
    def spawnable_on(ground:ground.Ground):
        return ground.name is GROUND_DIRT
    __slots__ = 'timer','energy'
    def __init__(self, pos:Vector2Int):
        super().__init__(pos, 'tnt')
        self.blast_resistance = 10
        self.csurface.surf =Textures.blocks['tnt'][0]
        self.timer = 4.0
        self.energy = 15

    def take_damage(self, damage: int, type: str,entity = None):
        if self.dead:return
        if type is FIRE_DAMAGE or type is EXPLOSION_DAMAGE:
            self.onDeath()
            return
        return super().take_damage(damage, type,entity)

    def onDeath(self):
        if super().onDeath():
            spawn_entity(LiveTNT(self.pos,4.0,10))
            return True
        return False

class WoodenPlank(Block):
    tex_name = 'Wooden_Plank'
    anim_fps = 0
    @staticmethod
    def spawnable_on(ground:ground.Ground):
        return ground.is_solid
    __slots__ = ()
    def __init__(self,pos:Vector2Int):
        super().__init__(pos,'woodplank')
        surf = Textures.blocks[self.tex_name][0]
        self.csurface.surf = surf
        self.blast_resistance = 1000

#### ENTITIES ####
class Entity(GameObject):
    abstract:bool
    species:str
    def __init_subclass__(cls) -> None:
        if not hasattr(cls,'species'):
            if hasattr(cls,'abstract'):                
                if cls.abstract:
                    print(f"Marking class: {cls.__name__} as abstract!")
                    return 
            raise EntitySetupError(cls.__name__)
        if cls.species in Settings.SPAWNABLE_ENTITIES:
            raise RuntimeError("No two entities may share the same species attribute value! Error on -> " + cls.species)
        Settings.SPAWNABLE_ENTITIES[cls.species] = cls
        if cls.species == '':
            print(cls.__name__ + " has \"species\" as an empty string, this cannot happen plz fix." )
    __slots__ = 'vel','collider','animation','speed','appearance'

    def __init__(self,pos:Vector2):
        super().__init__(pos,self.species)
        self.vel = Vector2.zero()
        self.typeid = self.species
        self.csurface = CSurface(Textures.NULL,self.pos,Settings.SURFACE_OFFSET[self.species])
        self.collider = Collider(0,0,*Settings.HITBOX_SIZE[self.species])
        self.collider.setCenter(*self.pos)
        self.animation = Animation.Animation(self.csurface)
        self.speed = 1.0
        self.appearance = Appearance(*Settings.APPEARANCE_BY_SPECIES[self.species],species=self.species)
        self.dead = False

    def onLoad(self): 
        if _DEBUG_: Camera.add_collider(self.collider)
        Camera.add(self.csurface)

    def onLeave(self):
        if _DEBUG_: Camera.remove_collider(self.collider)
        Camera.remove(self.csurface)

    def onDeath(self):
        if super().onDeath():
            dead_entities.append(self)
            return True
        return False

    def update(self):
        if self.dead: return
        frame_speed = self.speed * Time.deltaTime
        #move x rect 
        self.collider.move_x(self.vel.x * frame_speed) # move in world coordinates
        collision_horizontal(self.collider,self.vel.x)
        #move y rect 
        self.collider.move_y(self.vel.y * frame_speed) # move in world coordinates
        collision_vertical(self.collider,self.vel.y)
        self.pos.x = self.collider.centerx
        self.pos.y = self.collider.centery
        self.animation.animate()

    def attack(self,entity):
        assert isinstance(entity,(Entity,Block))
        entity.take_damage(self.get_attack_damage(),self.get_attack_type(),self.appearance)
    
    def attack_custom_damage(self,entity: Union["Entity" , Block],damage:int):
        entity.take_damage(damage,self.get_attack_type(),self.appearance)

    def take_damage(self,damage:int,type:str,appearance:Appearance|None = None):
        self.onDeath()

    def get_attack_damage(self) -> int: ...

    def get_attack_type(self) -> str:
        return PHYSICAL_DAMAGE
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.typeid}"

    def place_block(self,block:Block):
        place_block(block)

class ItemWrapper(Entity):
    species = 'item'
    def __init__(self,pos,item:"Application.Game.Items.Item"):
        super().__init__(pos)
        assert isinstance(item,Application.Game.Items.Item)
        self.pickup_time = ITEM_PICKUP_TIME
        self.item = item
        item.animation.csurface = self.csurface
        self.animation = item.animation
        self.alive_time = ITEM_MAX_LIFESPAN
        
    def update(self):
        self.pickup_time -= Time.deltaTime
        self.alive_time -= Time.deltaTime
        if self.alive_time <= 0: self.onDeath()
        super().update()
        if not self.vel: return
        ground = Chunk.get_ground_at(self.pos.x,self.pos.y)
        if ground is not None:
            friction = ground.surface_friction * Time.deltaTime *.1
            if friction*friction > self.vel.magnitude_squared():
                self.vel.reset()
            else:
                self.vel += -self.vel.normalized * friction

class LiveTNT(Entity):
    @staticmethod
    def damage_func_getter(joules:float) -> Callable[[float],int]:
        E = 2.718281828
        return lambda dist : (joules * E ** (-dist)).__trunc__()
    species = 'tnt'
    def __init__(self,pos:Vector2,time:float,energy:int):
        super().__init__(pos)
        self.animation.add_state('1',1,Textures.blocks['tnt'])
        self.animation.set_state('1')
        self.animation.animate()
        self.timer = time
        self.energy = energy
        self.particle_timer = .15
        self.particle_emit = Vector2(0,-0.7)

    def onDeath(self):
        if super().onDeath():
            create_explosion(self.pos,self.energy)
            #c = Collider.spawnFromCenter(self.pos.x,self.pos.y,self.energy*2,self.energy*2)
            #for x in range(4):
            #    #print(Textures.particles_transparent['Explosion'][0].get_size())
            #    Particles.spawn_animated(
            #        Particles.CheapAnimation(CSurface.inferOffset(Textures.particles_transparent['Explosion'][0],self.pos+ Vector2.randdir/3),Textures.particles_transparent['Explosion'],38+x))
            #damage_function = self.damage_func_getter(self.energy)
            #for entity in collide_entities(c):
            #    if entity.typeid == 'tnt': continue #tnt in entity form will be immune to other exploding tnt
            #    entity.take_damage(damage_function((self.pos - entity.pos).magnitude()),self.get_attack_type(),None)   
            #for block in collide_blocks(c):
            #    block.take_damage(damage_function((self.pos-block.pos).magnitude()),self.get_attack_type(),None)     
            return True
        return False
    

    def update(self):
        super().update()
        self.timer -= Time.deltaTime
        self.particle_timer -= Time.deltaTime
        while self.particle_timer <= 0:
            Particles.spawn(CSurface.inferOffset(Textures.particles_opaque['grey'],self.pos+self.particle_emit),1.0,Vector2.randdir()*1.5,True)
            self.particle_timer += .15
        if self.timer <= 0:
            self.onDeath()


    def get_attack_type(self):
        return EXPLOSION_DAMAGE

class Arrow(Entity):
    species = 'arrow'
    def __init__(self,pos:Vector2,velocity:Vector2,shooter:Entity|None):
        super().__init__(pos)     
        angle = -velocity.angle() 
        tex = Textures.rotate(Textures.entity_arrow,angle*TO_DEGREES)
        self.animation.add_state('going',0,(tex,),(Textures.entity_arrow,))
        self.csurface.offset = (-tex.get_width()//2,-tex.get_height()//2)
        self.animation.set_state('going')
        self.vel = velocity.copy()
        if shooter: 
            self.vel += shooter.vel # add the shooters velocity to our own because its relative to the shooters vel in real life
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
        self.pos.fromTuple(self.collider.center)
        self.blocks_traveled += self.speed * Time.deltaTime
        if self.blocks_traveled >= self.blocks_to_travel:
            self.stopped = True
        for entity in collide_entities(self.collider):
            if entity.typeid in {'arrow','item'}: continue
            self.onDeath()
            entity.take_damage(self.calculate_damage_to(entity),self.get_attack_type(),self.appearance)
            break

    def onLoad(self):
        #Camera.add_collider(self.collider)
        return super().onLoad()
    
    def onLeave(self):
        #Camera.remove_collider(self.collider)
        return super().onLeave()
    
    def calculate_damage_to(self,entity:Entity):
        return ( 0.5 * self.base_damage * (self.vel - entity.vel/2).magnitude_squared() * self.weight * max(0.01,self.penetration)).__trunc__()

class ArrowInciendiary(Arrow):
    species = 'firearrow'
    def get_attack_type(self):
        return FIRE_DAMAGE

class ArrowExplosive(Arrow):
    species = 'explosivearrow'
    __slots__ = 'energy'
    def __init__(self, pos, velocity: Vector2, shooter: Entity | None = None):
        self.energy = 5 # in joules
        super().__init__(pos, velocity, shooter)


    def get_attack_type(self) -> str:
        return EXPLOSION_DAMAGE
    
    def onDeath(self):
        if super().onDeath():
            d = log(self.energy) + 3.5
            c = Collider.spawnFromCenter(self.pos.x,self.pos.y,d*2,d*2)
            for x in range(5):
                Particles.spawn_animated(Particles.CheapAnimation(CSurface.inferOffset(Textures.blocks['tnt'][0],self.pos+Vector2.randdir()/3),Textures.blocks['tnt'],38+x))
            def damage_from_dist(dist:float) -> int:
                E = 2.718281828
                return (self.energy * E ** (-dist)).__trunc__()
            for entity in collide_entities(c):
                if entity.typeid == 'tnt':continue #tnt in entity form will be immune to other exploding tnt
                self.attack_custom_damage(entity,damage_from_dist((self.pos - entity.pos).magnitude()))
            for block in collide_blocks(c):
                self.attack_custom_damage(block,damage_from_dist((self.pos - block.pos).magnitude()))
            return True
        return False

class ArrowFunny(Arrow):
    species = 'funnyarrow'
    def onDeath(self):
        if super().onDeath():
            spawn_entity(LiveTNT(self.pos.copy(),1.0,5))
            return True
        return False

class AliveEntity(Entity):
    abstract = True
    __slots__ = 'actions','pickup_range','inventory','armour_inventory','stats','exp','max_speed','total_health','defense','regen_multiplier','health','strength','max_energy', \
    'energy','attack_speed','time_between_attacks','time_to_attack','time_to_regen','regen_time','vision_collider','vision_squared','states','ground','invulnerability_time', \
    'time_til_vulnerable','direction','extra_speed','extra_speed_sum','extra_total_health','extra_total_health_sum','extra_regen','extra_regen_sum','extra_strength' ,\
    'extra_strength_sum','extra_energy','extra_energy_sum','extra_defense','extra_defense_sum','effects','state','healthbar'
    def __init__(self,pos):
        super().__init__(pos)
        self.actions = Settings.ACTIONS_BY_SPECIES[self.species]
        self.pickup_range = max(*Settings.HITBOX_SIZE[self.species]) * half_sqrt_2 # just a shortcut for finding the length to the corner of a box from the middle when you only know a side length
        self.inventory = UniversalInventory(Settings.INVENTORY_SPACES_BY_SPECIES[self.species],self)
        self.armour_inventory = ArmorInventory(*Settings.ARMOUR_SLOTS_BY_SPECIES[self.species])
        #Stats
        self.stats = Settings.STATS_BY_SPECIES[self.species].copy()
        self.exp = 5000 #dont make attribute points (overused). make exp have another purpose. attribute points can lead to severely op setups and the player getting exactly what they want. 
        self.max_speed = Settings.MAX_SPEED_BY_SPECIES[self.species] 
        speed = self.stats['speed'] 
        self.speed = self.max_speed * speed / (speed + 100)
        self.total_health = self.stats['constitution'] * 5 + self.stats['strength'] + self.stats['stamina']
        assert isinstance(self.stats['defense'],int)
        self.defense = self.stats['defense']
        self.regen_multiplier = self.stats['constitution'] + self.stats['strength']
        self.regen_multiplier = self.regen_multiplier / (self.regen_multiplier + 100) + 1
        self.health = self.total_health
        self.strength = self.stats['strength'] * 5 + self.stats['constitution'] + self.stats['stamina']
        self.max_energy = self.stats['energy']
        assert isinstance(self.stats['energy'],int)
        self.energy = self.stats['energy']
        self.attack_speed = self.energy / 10
        self.time_between_attacks = 1/self.attack_speed
        self.time_to_attack = self.time_between_attacks
        self.time_to_regen = 0.0 # regen timer
        self.regen_time = 1.0 # how long in seconds should we wait between regen ticks
        self.vision_collider = Collider(0,0,Settings.VISION_BY_SPECIES[self.species]*2,Settings.VISION_BY_SPECIES[self.species]*2)
        self.vision_squared = Settings.VISION_BY_SPECIES[self.species] ** 2
        self.states = []
        self.ground:ground.Ground = ground.Invalid()
        # damage timer
        self.invulnerability_time = 0.5
        self.time_til_vulnerable = 0.0

        self.direction = 'right'
        
        self.extra_speed:dict[str,float] = {}; self.extra_speed_sum = 0.0
        self.extra_total_health:dict[str,int] = {}; self.extra_total_health_sum = 0.0
        self.extra_regen:dict[str,float] = {}; self.extra_regen_sum = 0.0
        self.extra_strength:dict[str,int] = {}; self.extra_strength_sum = 0.0
        self.extra_energy:dict[str,int] = {}; self.extra_energy_sum = 0.0
        self.extra_defense:dict[str,int] = {}; self.extra_defense_sum = 0.0

        self.effects:list[EntityEffect] = []

    ### SET STATS ###
    
    def setStatSpeed(self,newSpeed:int):
        self.stats['speed'] = newSpeed
        #update speed
        speed = self.stats['speed'] 
        self.speed = self.max_speed * speed / (speed + 100)

    def setStatConstitution(self,newConstitution:int):
        self.stats['constitution'] = newConstitution
        self.strength = self.stats['strength'] * 5 +newConstitution + self.stats['stamina']
        self.regen_multiplier = newConstitution + self.stats['strength']
        self.regen_multiplier = self.regen_multiplier / (self.regen_multiplier + 100) + 1

    def setStatStrength(self,newStrength:int):
        self.stats['strength'] = newStrength
        self.strength = newStrength * 5 + self.stats['constitution'] + self.stats['stamina']
        self.regen_multiplier = self.stats['constitution'] + newStrength
        self.regen_multiplier = self.regen_multiplier / (self.regen_multiplier + 100) + 1

    def setStatStamina(self,newStamina:int):
        self.stats['stamina'] = newStamina
        self.strength = self.stats['strength'] * 5 + self.stats['constitution'] + newStamina // 2

    def setStatEnergy(self,newEnergy:int):
        self.stats['energy'] = newEnergy
        self.max_energy = newEnergy

    def setStatDefense(self,newDefense:int):
        self.stats['defense'] = newDefense
    
    def setStatAttack(self,newAttack:int):
        self.stats['attack'] = newAttack

    ### SET ADDED STATS ###

    def setExtraStatSpeed(self,tag:str,addedSpeed:float):
        self.extra_speed[tag] = addedSpeed
        self.extra_speed_sum = sum(self.extra_speed.values())

    def setExtraStatTotalHealth(self,tag:str,addedTotalHealth:int):
        self.extra_total_health[tag] = addedTotalHealth
        self.extra_total_health_sum = sum(self.extra_total_health.values())

    def setExtraStatRegen(self,tag:str,addedRegen:float):
        self.extra_regen[tag] = addedRegen
        self.extra_regen_sum = sum(self.extra_regen.values())

    def setExtraStatStrength(self,tag:str,addedStrength:int):
        self.extra_strength[tag] = addedStrength
        self.extra_strength_sum = sum(self.extra_strength.values())

    def setExtraStatEnergy(self,tag:str,addedEnergy:int):
        self.extra_energy[tag] = addedEnergy
        self.extra_energy_sum = sum(self.extra_energy.values())
    
    def setExtraStatDefense(self,tag:str,addedDefense:int):
        self.extra_defense[tag] = addedDefense
        self.extra_defense_sum = sum(self.extra_defense.values())
    
    ### REMOVE ADDED STATS ###
   
    def removeExtraStatSpeed(self,tag:str):
        del self.extra_speed[tag]
        self.extra_speed_sum = sum(self.extra_speed.values())

    def removeExtraStatTotalHealth(self,tag:str):
        del self.extra_total_health[tag]
        self.extra_total_health_sum = sum(self.extra_total_health.values())

    def removeExtraStatRegen(self,tag:str):
        del self.extra_regen[tag]
        self.extra_regen_sum = sum(self.extra_regen.values())

    def removeExtraStatStrength(self,tag:str):
        del self.extra_strength[tag]
        self.extra_strength_sum = sum(self.extra_strength.values())

    def removeExtraStatEnergy(self,tag:str):
        del self.extra_energy[tag]
        self.extra_energy_sum = sum(self.extra_energy.values())
    
    def removeExtraStatDefense(self,tag:str):
        del self.extra_defense[tag]
        self.extra_defense_sum = sum(self.extra_defense.values())
     
    ### GET STATS ###

    def getTotalSpeed(self):
        return self.speed + self.extra_speed_sum
    
    def getTotalTotalHealth(self):
        return self.total_health + self.extra_total_health_sum
    
    def getTotalRegen(self):
        return self.regen_multiplier + self.extra_speed_sum
    
    def getTotalStrength(self):
        return self.strength + self.extra_strength_sum
    
    
    @property
    def selected_item(self) -> Optional['Application.Game.Items.Item']:
        if self.inventory.spaces == 0 :return None
        return self.inventory.inventory[0]

    def depleteEnergy(self,action):
        assert action in self.actions, f'{self.typeid} has tried to do actions: {action}, which is not in its list of actions!'
        self.energy -= Settings.ACTION_ENERGY_CONSUMPTION[action]
        if self.energy < 0:
            self.take_damage(-self.energy,INTERNAL_DAMAGE,None)
            self.energy = 0
        
    def canDoAction(self,action):
        '''Returns if self HAS ENOUGH ENERGY to do the action, keep in mind that the action can still be taken if this returns False, just with consequences...'''
        assert action in self.actions,  f'{self.typeid} has tried to do actions: {action}, which is not in its list of actions!'
        return self.energy >= Settings.ACTION_ENERGY_CONSUMPTION[action]

    def get_entities_seen(self):
        for entity in collide_entities(self.vision_collider):
            if entity is not self and (entity.pos - self.pos).magnitude_squared() <= self.vision_squared and can_see_each_other(self,entity):
                yield entity    

    def onDeath(self):
        if super().onDeath():
            for i in range(10):
                Particles.spawn(CSurface.inferOffset(Textures.particles_opaque['white'],self.pos + Vector2.random()/5),1.0,Vector2.random()/2,slows_coef=0)
            Particles.spawn(self.animation.csurface.copy(),1.0)
            return True
        return False

    def set_state(self,number:int):
        '''Returns False if failed.
        Reasons for failing:
            * The Entity is already in that state'''
        if self.state is self.states[number]: return False
        self.state = self.states[number]
        self.animation.set_state(self.state)

    def set_regen_time(self,speed:float) -> None:
        self.regen_time = speed
        if self.time_to_regen > speed:
            self.time_to_regen = speed

    def update_state(self): ...

    def accelerate(self,x:float,y:float):
        self.vel.x += x *Time.deltaTime * self.ground.surface_friction
        self.vel.y += y *Time.deltaTime * self.ground.surface_friction
        mag_sqrd = self.vel.magnitude_squared()

        
        if mag_sqrd > 1:
            self.vel /= (mag_sqrd)**0.5

    def update(self):
        if self.dead: return
        self.time_to_attack -= Time.deltaTime
        self.time_til_vulnerable -= Time.deltaTime
        frame_speed = (self.getTotalSpeed()) * Time.deltaTime
        #move x rect 
        self.collider.move_x(self.vel.x * frame_speed) # move in world coordinates
        collision_horizontal(self.collider,self.vel.x)
        #move y rect 
        self.collider.move_y(self.vel.y * frame_speed) # move in world coordinates
        collision_vertical(self.collider,self.vel.y)
        self.pos.x = self.collider.centerx
        self.pos.y = self.collider.centery

        self.ground = Chunk.get_ground_at(self.pos.x,self.pos.y)
        if self.ground is not None:
            friction = self.ground.surface_friction * Time.deltaTime
            if friction*friction > self.vel.magnitude_squared():
                self.vel.reset()
            else:
                self.vel += -self.vel.normalized * friction
        else:
            self.ground = ground.Invalid()
        self.natural_regen()
        for effect in self.effects:
            effect.update()
        self.animation.animate()

    def get_damage_resisted(self,damage:int,type:str) -> int:
        '''Returns damage resisted'''
        if type is INTERNAL_DAMAGE: return 0

        defense:int = self.defense + self.inventory.added_def
        damage_reduction = damage * defense/ (defense+100) 
        return damage_reduction.__trunc__()
    
    def take_damage(self,damage:int,type:str,appearance:Appearance|None = None) -> None:
            
        if self.time_til_vulnerable < 0 or type is INTERNAL_DAMAGE: 
            damage -= self.get_damage_resisted(damage,type)
            if damage == 0:
                return
            Particles.spawn_hit_particles(self.pos,.5)
            self.health -= damage
            print('taking damage',damage,'now health is',self.health)
            if self.health <= 0:
                self.onDeath()
    
    def get_energy_multiplier(self) -> float:
        return (self.energy/self.stats['energy'] + 1)/2

    def get_attack_damage(self) -> int:
        '''Returns final attack damage'''
        #get total damage stat
        damage =  self.getTotalStrength() # start with strength stat
        damage *= 1.0 + self.strength / 100 * self.get_energy_multiplier()
        return damage.__trunc__()

    def get_attack_type(self) -> str:
        return PHYSICAL_DAMAGE
    
    def natural_regen(self):
        if self.health != self.total_health and self.time_til_vulnerable < -10: # if 10 seconds have passed since we have been dealth damage that resets our invulnerability timer
            self.time_to_regen -= Time.deltaTime
            if self.time_to_regen < 0:
                self.time_to_regen = self.regen_time
                self.health += max(1,(self.total_health/100 *  self.regen_multiplier * self.get_energy_multiplier()).__trunc__())
                if self.health > self.total_health:
                    self.health = self.total_health
                print(self.health)

    def collect_items(self):
        for item in collide_entities_in_range_species(self.pos,self.pickup_range,'item'): # type: ignore
            item:ItemWrapper
            if item.pickup_time < 0 :
                i = self.inventory.fitItem(item.item) #this will never add the same object to both hotbar and inventory becasue the or will only try to add to inventory if the item couldn't be added to the hotbar
                if i is None:
                    item.onDeath()

    ## Interact with the world ##

    def place_block(self,block:Block):
        place_block(block)

    def spawn_entity(self,entity:Entity):
        spawn_entity(entity)

class Player(AliveEntity):
    species ='human'
    __slots__ = 'cx','cy','can_move','attacking','state','showingInventory','hotbar','ui','hbui','walking_particle'
    def __init__(self,pos:Vector2):
        super().__init__(pos)
        self.cx = (self.pos.x//CHUNK_SIZE).__floor__()
        self.cy = (self.pos.y//CHUNK_SIZE).__floor__()
        recalculate_chunks(self.cx,self.cy)
        self.set_up_animation()

        # stats
        self.exp = 5000 #dont make attribute points (overused). make exp have another purpose. attribute points can lead to severely op setups and the player getting exactly what they want. 
        # damage timer
        self.can_move = True
        self.attacking = False
        self.states = ['relaxed','focused']
        self.state = None
        self.set_state(0)
        self.showingInventory = False
        
        #humans have 27 inventory spots and 9 hotbar spots
        self.hotbar = Hotbar(self.inventory,27,28,29,30,31,32,33,34,35) # the numbers at the end mean the inventory slots that the hotbar should use in order
        
        self.direction = 'right'

    def set_up_animation(self):
        walk_right = Textures.player_walk
        walk_left = Textures.flipXArray(walk_right)
        idle_right = Textures.player_idle
        idle_left = Textures.flipXArray(idle_right)
        attack_right = Textures.player_attack
        attack_left = Textures.flipXArray(attack_right)

        self.walking_particle = Textures.particles_opaque['dirt_particle']
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

    def take_damage(self, damage: int, type: str,appearance:Appearance|None = None) -> None:
        if type is EXPLOSION_DAMAGE:
            print(damage, 'of explosion type')
            super().take_damage(damage,type,appearance)
        else:
            super().take_damage(damage, type,appearance)
    
    def input(self): #Time.deltaTime is in seconds

        if 'r' in Input.KDQueue:
            pos = Camera.world_position(Input.m_pos).floored()
            place_block(WoodenPlank(Vector2Int(int(pos.x),int(pos.y))))

        if 'b' in Input.KDQueue:
            b = Bunny(self.pos.copy())
            spawn_entity(b)
        
        if 'h' in Input.KDQueue:
            create_explosion(Camera.world_position(Input.m_pos) ,20)
    
        if 'n' in Input.KDQueue:
            return
            velocity = (Camera.world_position_from_normalized(Input.m_pos_normalized) - self.pos).normalized
            if velocity.isZero:
                velocity = Vector2.randdir
            spawn_entity(ArrowInciendiary(self.pos + velocity/2,velocity*3,self))
        if Input.space_d:
            spawn_item(Application.Game.Items.BunnyEgg(),self.pos,Vector2.randdir())
        if self.animation.state != 'attack':
            v = Vector2(Input.d-Input.a,Input.s-Input.w)
            v.setMagnitude(self.getTotalSpeed() * self.ground.surface_friction)
            self.accelerate(v.x,v.y)
        else:
            self.vel.reset() #set to 0,0

        if self.vel.x > 0:
            self.animation.direction = 'right' 
        elif self.vel.x < 0:
            self.animation.direction = 'left'

        #item usage

        if Input.m_1 and self.animation.state != 'attack':
            #use_item(self.inventory.)
            pass

        if Input.m_d1:
            item = self.hotbar.seeSelected()
            print('attacked with item',item)
        if Input.m_d3:
            self.hotbar.start_use_selected()
        elif Input.m_u3:
            self.hotbar.stop_use_selected()
        elif Input.m_3:
            self.hotbar.during_use_selected()

        if Input.m_2 and Time.frameCount%21 == 0:
            Particles.spawn_smoke_particle(Camera.world_position_from_normalized(Input.m_pos_normalized),Vector2.randdir(),(Vector2.random().x*100).__trunc__())

    def move(self):
        super().update() 
        #detect if in new chunk
        if self.pos.x//CHUNK_SIZE != self.cx:
            #in new chunk
            self.cx = (self.pos.x).__floor__()//CHUNK_SIZE
            self.cy = (self.pos.y).__floor__()//CHUNK_SIZE
            recalculate_chunks(self.cx,self.cy)
            
        elif self.pos.y//CHUNK_SIZE != self.cy:
            #in new chunk
            self.cx = self.pos.x.__floor__()//CHUNK_SIZE
            self.cy = self.pos.y.__floor__()//CHUNK_SIZE
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
        
        if FPS != 0 and self.vel and self.animation.frame_in_frame % (FPS//3) == 0:
            #spawn a particle
            if self.ground.id == GROUND_INVALID:
                pass
            elif self.ground.id == GROUND_GRASS:
                Particles.spawn(CSurface.inferOffset(self.walking_particle,self.pos + Vector2(0,.4)),.5,Vector2.random() * 0.5)
            elif self.ground.id == GROUND_WATER:
                Particles.spawn(CSurface.inferOffset(Textures.particles_opaque['water'],self.pos + Vector2(0,.4)),.5,Vector2.random() * 0.5)
 
    def collect_items(self): ## TODO : Make it so that in order to pick up items you click on them instead of just getting close to them

        for item in collide_entities_in_range_species(self.pos,self.pickup_range,'item'): # type: ignore
            item:ItemWrapper
            if item.pickup_time < 0 :
                i = self.hotbar.fitItem(item.item)
                if i is not None:
                    i = self.inventory.fitItem(i) #this will never add the same object to both hotbar and inventory becasue the or will only try to add to inventory if the item couldn't be added to the hotbar
                if i is None:
                    item.onDeath()

    def update(self):
        #Camera.program['danger'] = 1-(self.health / self.total_health)
        self.input()
        self.move()
        self.animate()

class Spirit(AliveEntity):
    species = 'spirit'
    enemies = {'bunny','human'}
    eats = set()# spirits eat nothing (for now)
    fears = set() #spirits fear nothing (for now)

    neutral_to = set()
    def __init__(self,pos):
        idle =  Textures.entities['spirit']['idle'] # type: ignore
        assert isinstance(idle,tuple)
        super().__init__(pos)
        self.animation.add_state('idle',8,idle,idle)        
        self.animation.set_state('idle')
        self.vision_collider = Collider(0,0,Settings.VISION_BY_SPECIES['spirit']*2,Settings.VISION_BY_SPECIES['spirit']*2)
        self.vision_squared = Settings.VISION_BY_SPECIES['spirit'] ** 2
        self.attack_range_squared = self.stats['attack_range'] ** 2
        self.timer_to_vision = 1
        self.states = ['idle','wander','fight','afraid']
        self.state = self.states[0]
        self.mark:Entity|None = None
        self.time_to_introspection = 5
        #Set up animation
        for state in self.states:
            self.animation.add_state(state,8,idle,idle)

    def set_state(self,number:int):
        if super().set_state(number) is False: return
        if number == 0:
            self.vel.reset()
        elif number == 1:
            self.vel.setFrom(Vector2.randdir())

    def update_state(self):
        entities_seen = list(self.get_entities_seen())

        for entity in entities_seen:
            entity:Entity
            if entity.typeid in self.fears:
                self.set_state(3)
                self.fear_producer = entity
                return 
        self.closest_enemy = None
        closest_distance_squared = POSITIVE_INFINITY
        for entity in entities_seen:
            if entity.typeid in self.enemies:
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
            assert not isinstance(self.closest_enemy,type(None)),'closest enemy was somehow none when we were fighting something'
            if self.closest_enemy.dead: self.time_to_introspection = 0; return
            distance_to_enemy  = (self.closest_enemy.pos - self.pos)
            if distance_to_enemy.magnitude_squared() < self.attack_range_squared:
                self.attack(self.closest_enemy)
            self.vel = distance_to_enemy.normalized
        
    def onLoad(self):
        self.time_to_introspection = 0
        print('Loading Spirit')
        return super().onLoad()

class Bunny(AliveEntity):
    enemies = set() #have no natural enemies for now
    eats = set()# bunny's eat nothing (for now)
    fears = {'spirit'}
    species = 'bunny'
    neutral_to = set()
    #__slots__ = 'right_idle','left_idle','fears','eats','enemies','driver','mark','hunger','sprinting','states'
    def __init__(self,pos):
        super().__init__(pos)
        #idle = tuple(Textures.entities['bamboo']['idle'].values()) #type: ignore

        self.fears = self.fears.copy()
        self.eats = self.eats.copy()
        self.enemies = self.enemies.copy()
        self.animation.add_state('idle',8,tuple(Textures.entities[self.species].values()))     #type: ignore    
        self.animation.set_state('idle')
        self.vision_collider = Collider(0,0,Settings.VISION_BY_SPECIES['bunny']*2,Settings.VISION_BY_SPECIES['bunny']*2)
        self.vision_squared = Settings.VISION_BY_SPECIES['bunny'] ** 2
        self.driver = Driver(self.pos)

        self.time_to_introspection = 5
        self.timer_to_vision = 1
        self.states = ['idle','wander','afraid','hungry']
        for state in self.states:
            self.animation.add_state(state,8,tuple(Textures.entities[self.species].values()))     #type: ignore    

        self.state = self.states[0]
        self.mark:Entity|None = None

        self.hunger = 0
        self.sprinting = False

    def get_closest_enemy(self):
        closest:Entity|None = None
        for entity in collide_entities(self.vision_collider):
            if entity.typeid in Spirit.enemies:
                if closest is None or (closest.pos - self.pos).magnitude_squared() > (entity.pos - self.pos).magnitude_squared():
                    closest = entity 
        return closest 
    
    def set_state(self, number: int):
        if super().set_state(number) is False: return False
        if number == 0:
            self.vel.reset()
        elif number == 1:
            self.driver.setTarget(self.pos + Vector2.randdir() * 10)


    def update_state(self):
        
        entities_seen = list(self.get_entities_seen())
        for entity in entities_seen:
            entity:Entity
            if entity.typeid in self.fears:
                print('sees something that it is scared of')
                self.driver.mode = Driver.AVOID
                self.driver.setTarget(entity.pos)
                self.sprinting = True
                self.set_state(2)
                return   
        if self.hunger > 180:
            for entity in entities_seen:
                if entity.typeid in self.eats:
                    self.set_state(3)
                    self.driver.mode = Driver.FOLLOW
                    self.driver.setTarget(entity.pos)
                    return
        if self.state is self.states[0]:
            self.set_state(1)
        elif self.state is self.states[1]:
            self.set_state(0)
        #print('updating state curr:',self.state)       

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
        self.accelerate(*(self.driver.getAccelerationDirection() * self.ground.surface_friction * self.getTotalSpeed() * self.trySprinting()))


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

    def take_damage(self, damage: int, type: str,appearance:Appearance|None = None) -> None:
        if appearance is not None:
            self.fears.add(appearance.species)
        if self.state in ( self.states[0] , self.states[1]):
            self.time_to_introspection = 0 
        return super().take_damage(damage, type)
        

    def onLoad(self):
        self.time_to_introspection = 0
        return super().onLoad()

#### DRIVERS ####
class Driver:
    FOLLOW = 1
    AVOID = 2
        
    def __init__(self,pos:Vector2):
        self.pos = pos
        self.target:Vector2|None = None
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
        if self.target is None: return Vector2.zero()
        lineVec = self.target - self.pos
        if self.mode is self.AVOID:
            lineVec = -lineVec
        magSqrd = lineVec.magnitude_squared()
        if magSqrd < self.spatial_tolerance_squared:
            return Vector2.zero() #this one can actually return a cached value Vector2.zero() so it doesn't have to create new ones every frame but that is a microoptimization for later
        else:
            return lineVec/sqrt(magSqrd)
 
import Application.Game.Items as Items #This must happen after all entities have been initialized


########## NOTE : for custom classes that dont define __eq__ method python defaults to check identity, being equal to "is"

#######################################
########### BLOCK_CHUNKS ##############
#######################################


active_chunks = [] 
'''stores the x and y values of the loaded chunks'''

_DEBUG_ = False

def noise_to_ground(n) -> ground.Ground:
  if n > 1 or n < 0: 
    return ground.Invalid()
  if n > .85:
    return ground.Stone()
  if n > .5:
    return ground.Grass()
  if n > 0.48:
    return ground.Sand()
  
  return ground.Water()


class Chunk:  
    _insts:dict = {}

    @classmethod
    def exists_at(cls,chunk_pos:tuple|list) -> bool:
        return chunk_pos in cls._insts
    
    @classmethod
    def get_ground_at(cls,x,y) -> 'ground.Ground':
        global chunks
        c_pos = (x//CHUNK_SIZE,y//CHUNK_SIZE)
        try:
            return chunks[c_pos]._get_ground(x,y)
        except: 
            return ground.Invalid()
        
    def __new__(cls,pos:tuple[int,int]):
        if pos in cls._insts:
            return cls._insts[pos]
        else:
            chunk = super(Chunk,cls).__new__(cls)
            chunk.chunk_pos = pos[0].__floor__(),pos[1].__floor__()
            chunk.pos = Vector2(pos[0] * CHUNK_SIZE,pos[1] * CHUNK_SIZE)

            chunk.blocks = []
            chunk.onCreationFinish = []

            surf = Surface((CHUNK_SIZE*BLOCK_SIZE,CHUNK_SIZE*BLOCK_SIZE))
            chunk.csurf = CSurface(surf ,chunk.pos,(0,0))
            chunk.collider = Collider(pos[0]*CHUNK_SIZE,pos[1]*CHUNK_SIZE,CHUNK_SIZE,CHUNK_SIZE)
            
            chunk.biome = PLAINS #prefferably call a function <get_biome(chunk_pos)> 
            chunk.active = False
            chunk.dead_blocks = []
            cls._insts[pos] = chunk

            return cls._insts[pos]
        
    def __repr__(self) -> str:
        return f"Chunk: {self.chunk_pos}"

    __slots__ = ('chunk_pos','pos','collider','id','data','blocks','biome','active','ground','onCreationFinish','csurf','dead_blocks')
    # removed slots 'x','y','subdivision_lengths','items','items_sub',
    def __init__(self,pos:tuple[int,int]):
        self.chunk_pos:tuple[int,int]
        #for drawing to screen
        #self.x,self.y = pos[0] * CHUNK_SIZE, pos[1] * CHUNK_SIZE 
        self.pos:Vector2# = Vector2(pos[0] * CHUNK_SIZE,pos[1] * CHUNK_SIZE)
        self.collider:Collider
        
        self.id:int = hash(self.chunk_pos)
        '''identifiying integer'''
        self.data:np.ndarray #numpy.ndarray 
        '''Heightmap'''
        self.blocks:list[Block]

      
        self.biome:int
        self.active:bool
        self.ground:tuple[list[ground.Ground]]
        self.onCreationFinish:list[Callable]
        self.csurf:CSurface 
        self.dead_blocks:list[Block]

    @property
    def surf(self) -> Surface:
        return self.csurf.surf
    
    @surf.setter
    def surf(self,__object):
        self.csurf.surf = __object

    def _get_ground(self,x:int,y:int) -> 'ground.Ground':
        #this is a method to bypass all the checks made by normal ground_getter but only works if you already know what chunk the block is in
        x = (x).__floor__() % CHUNK_SIZE
        y = (y).__floor__() % CHUNK_SIZE
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
                    print('A block of type',block.typeid,'did not manually add itself to the dead_blockslist')
        
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

    def get_blocks(self):
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

ContinentNP = LayeredNoiseMap(
    (1.0 * SCALE, 2.0 * SCALE, 4.0 * SCALE, 8.0 * SCALE),
    (1.0, 0.5, 0.25, 0.125)
)

WorleyNP = WorleyNoiseSimple(2,SCALE*1)
# from Utils.WorldGen import Gen, Village
# gen = Gen()
# gen.passes.append(Village())

def _create(chunk:Chunk):
    ## PHASE 1 ##
    #generate layered noisemap
    xs = np.arange(CHUNK_SIZE)+chunk.chunk_pos[0]*CHUNK_SIZE
    ys = np.arange(CHUNK_SIZE)+chunk.chunk_pos[1]*CHUNK_SIZE
    a = WorleyNP.getArrShifted(xs,ys)

    chunk.data = rescale(ContinentNP.getArrShifted(xs,ys)) + np.power(a,2)#noise2ali(xs,ys,OCTAVES,SCALE,ISLAND_BLEND,sigmoid_dist,MAPWIDTH,MAPHEIGHT)  
    chunk.data /= 2
    
    yield  
    chunk.ground = make2dlist(CHUNK_SIZE) #type: ignore
    #draw layered noisemap onto surface
    #note this will not be represented in real time as it will still need to get loaded into the camera, which happens at the end of the creation process
    surf = chunk.surf
    for y, row in enumerate(chunk.data):
        for x, noise in enumerate(row):
            ground = noise_to_ground(noise) 
            chunk.ground[y][x] = ground #type: ignore
            #pygame.draw.rect(surf,(noise*255,)*3,(x*BLOCK_SIZE,y*BLOCK_SIZE,BLOCK_SIZE,BLOCK_SIZE))
            surf.blit(Textures.ground[ground.tex],(x*BLOCK_SIZE,y*BLOCK_SIZE))
            #surf.blit(myfont.render(str((x+chunk.chunk_pos[0]*CHUNK_SIZE,y+chunk.chunk_pos[1]*CHUNK_SIZE)),True,'black'),(x*BLOCK_SIZE,y*BLOCK_SIZE))
    #yield
    
    if _DEBUG_:
        draw.lines(chunk.surf,
                   (255,0,0),
                   True,
                   [(0,0),(CHUNK_SIZE*BLOCK_SIZE,0),(CHUNK_SIZE*BLOCK_SIZE,CHUNK_SIZE*BLOCK_SIZE),(0,CHUNK_SIZE*BLOCK_SIZE)], #type: ignore
                   3)    
    #to make trees we check the 8 immediately surrounding chunks if they exist and add them to a list
    cx ,cy = chunk.chunk_pos
    surrounding_chunks = [(cx-1,cy-1),(cx,cy-1),(cx+1,cy-1),(cx-1,cy),(cx+1,cy),(cx-1,cy+1),(cx,cy+1),(cx+1,cy+1)]
    existing_surrounding_chunks = []
    for chunk_pos in surrounding_chunks:
        if chunk_pos in chunks:
            existing_surrounding_chunks.append(chunk_pos)
    yield     
    def isValid(x,y):
        for chunk_pos in existing_surrounding_chunks:
            o_chunk = chunks[chunk_pos]
            for block in o_chunk.blocks:
                if block.typeid == 'tree':
                    if hypot(block.pos.x-x,block.pos.y-y) <= Settings.TREE_SPACING_BY_BIOME[chunk.biome]:
                        return False
        for block in chunk.blocks: #check own chunk
            if block.typeid == 'tree':
                if hypot(block.pos.x-x,block.pos.y-y) <= Settings.TREE_SPACING_BY_BIOME[chunk.biome]:
                    return False  
        return True

    for _ in range(CHUNK_SIZE*CHUNK_SIZE//6):
        x = randint(chunk.pos.x, chunk.pos.x + CHUNK_SIZE - 1) #type: ignore
        y = randint(chunk.pos.y, chunk.pos.y + CHUNK_SIZE - 1) #type: ignore
        g = chunk._get_ground(x,y)
        if Tree.spawnable_on(g) and isValid(x,y):
            print('spawinging tree')
            chunk.blocks.append(Tree(Vector2Int(x,y),g))
    yield
    # gen.processChunk(chunk)
    yield
    chunks[chunk.chunk_pos] = chunk
    for cmd in chunk.onCreationFinish:
        cmd()
    chunk.onCreationFinish.clear()

    yield 'able to add'
    #returns a StopIteration exception
    #if village_creater.isObject(cx,cy):
        #chunk.ground[4][4] = Village
        #surf.blit(Textures.texture[Village.tex],(4*BLOCK_SIZE,4*BLOCK_SIZE))
    
current_chunks:list[Chunk] = [] 
'''stores the chunk instances of the loaded chunks'''

chunk_loading_queue = deque()

def queue_chunk(chunk_pos:tuple[int,int]):
    '''Will queue the chunk at the inputed pos and return it'''
    #first make some checks to make sure that its not loaded or currently being loaded
    assert chunk_pos not in chunks, 'chunk is already loaded'
    for chunk in chunk_loading_queue:
        chunk:Chunk
        if chunk.chunk_pos == chunk_pos:
            return chunk
    chunk = Chunk(chunk_pos)
    chunk_loading_queue.append(chunk)
    return chunk

chunk_loaders:dict[tuple[int,int],Generator] = {}
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
        case 'done':
            chunk_loading_queue.popleft()
        case _:
            #no status update
            pass
    chunk_loading_queue.rotate()

def place_block(block:Block):
    chunk:Chunk|None = chunks.get((block.pos//CHUNK_SIZE).tuple_ints)
    return False if chunk is None else chunk.add_block(block)

#######################################
########### ENTITY CHUNKS #############
#######################################


entity_chunks:dict[tuple[int,int],list[Entity]] = {}
def get_entity_chunk(entity:Entity):
    return (entity.pos//CHUNK_SIZE).tuple_ints

def print_entity_chunks():
    for chunk in active_chunks:
        if chunk not in entity_chunks:
            print(chunk,': Empty')
        else:
            print(chunk,':',[et.typeid for et in entity_chunks[chunk]])

def get_nearest_block(pos:Vector2):
    nearest = None
    dist_sqrd = POSITIVE_INFINITY
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
    chunk_pos = (entity.pos//CHUNK_SIZE).tuple_ints
    chunk = entity_chunks.get(chunk_pos) #try to get the chunk its in, if not found then create a new chunk(list)

    if chunk_pos in active_chunks:
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
    return (0,0)

def manage_chunks():
    #search for each entity and see if they crossed a chunk border
    for chunk_pos in active_chunks:
        if chunk_pos in entity_chunks:
            chunk = entity_chunks[chunk_pos]
            for entity in reversed(chunk): #could just do range(len(chunk),0,-1) and use pop instead of remove, which is faster
                entity_chunk = (entity.pos//CHUNK_SIZE).tuple_ints
                if entity_chunk != chunk_pos:            
                    chunk.remove(entity)
                    if not chunk: # chunk is empty
                        del entity_chunks[chunk_pos]

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
    chunk_pos = (entity.pos//CHUNK_SIZE).tuple_ints
    entity_chunks[chunk_pos].remove(entity)
    if not entity_chunks[chunk_pos]: #if the entity chunk is now empty
        #delete the chunk because it is not needed anymore
        del entity_chunks[chunk_pos]

def update_entities():
    for chunk_pos in active_chunks:
        chunk = entity_chunks.get(chunk_pos,[])
        for entity in chunk:
            entity.update()

def active_entity_count():
    count = 0
    for chunk_pos in active_chunks:
        count += len(entity_chunks.get(chunk_pos,[]))
    return count

def collide_entities(collider:Collider):
    for cpos in collide_chunks(collider.left,collider.top,collider.right,collider.bottom,CHUNK_SIZE):
            e_chunk = entity_chunks.get(cpos)
            if e_chunk is None: continue
            for entity in e_chunk:
                if entity.dead: continue
                if collider.collide_collider(entity.collider):
                    yield entity
    
def collide_entities_in_range(pos:Vector2,range:float) -> Generator[Entity,None,None]:
    range_sqrd = range*range
    for cpos in collide_chunks(pos.x-range,pos.y-range,pos.x+range,pos.y+range,CHUNK_SIZE):
        for entity in entity_chunks.get(cpos,()):
            if not entity.dead and (entity.pos-pos).magnitude_squared() <= range_sqrd:
                yield entity

def collide_entities_in_range_species(pos:Vector2,range:float,typeid:str) -> Generator[Entity,None,None]:
    range_sqrd = range*range
    for cpos in collide_chunks(pos.x-range,pos.y-range,pos.x+range,pos.y+range,CHUNK_SIZE):
        for entity in entity_chunks.get(cpos,()):
            if not entity.dead and (entity.typeid == typeid) and (entity.pos-pos).magnitude_squared() <= range_sqrd:
                yield entity

def spawn_item(item:"Items.Item",pos:Vector2,vel:Vector2|None=None):
    #step 1) create itemWrapper
    iw = ItemWrapper(pos,item)
    if vel is not None:
        iw.vel.setFrom(vel)
    #step 2) Spawn Itemwrapper as entity
    spawn_entity(iw)
 
def get_chunk(cx:int,cy:int) -> Chunk:
    chunk:Chunk|None = chunks.get((cx,cy))
    if chunk is None:
        chunk = queue_chunk((cx,cy))
    return chunk
    
def get_around_chunk(cx,cy):
    #returns perfect square
    return [(cx+x,cy + y) for x in range(-Settings.RenderDistance,Settings.RenderDistance+1,1) for y in range(-Settings.RenderDistance,Settings.RenderDistance+1,1)] 

def get_loaded_chunks_collided(collider:Collider):
    for chunk in current_chunks:
        if collider.collide_collider(chunk.collider):
            yield chunk
    
def get_chunks_collided(collider:Collider):
    for cpos in collide_chunks(collider.left,collider.top,collider.right,collider.bottom,CHUNK_SIZE):
        chunk = chunks.get(cpos) 
        if chunk is not None:
            yield chunk

def collide_blocks(collider:Collider): 
    for chunk in get_chunks_collided(collider):
        for obstacle in chunk.blocks:
            if collider.collide_collider(obstacle.collider):
                yield obstacle

def collide_blocks_in_range(pos:Vector2,range:float):
    range_sqrd = range*range
    for cpos in collide_chunks(pos.x-range,pos.y-range,pos.x+range,pos.y+range,CHUNK_SIZE):
        chunk = chunks.get(cpos)
        if chunk is not None:
            for block in chunk.blocks:
                if not block.dead and (block.pos-pos).magnitude_squared() <= range_sqrd:
                    yield block


def collision_horizontal(collider:Collider,vx:int|float) -> bool:
    '''Returns whether the collider collided with any block'''
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

def collision_vertical(collider:Collider,vy:float|int) -> bool:
    '''Returns whether the collider collided with any block'''
    if not vy: return False
    hit_smthng = False
    for chunk in get_chunks_collided(collider): # TODO: maybe as an optimization if we collide with one thing then we can break early so we dont have to keep the hit_smthng variable and directly return
        for obstacle in chunk.blocks:
            if collider.collide_collider(obstacle.collider):
                if vy > 0: # moving down
                    collider.setBottom(obstacle.collider.top)
                if vy < 0: # moving up
                    collider.setTop(obstacle.collider.bottom)
                hit_smthng = True
    return hit_smthng

all_chunks_ever_added = set()

def recalculate_chunks(pcx:int,pcy:int):
    global active_chunks
    #get chunks that will be added
    new_chunks = get_around_chunk(pcx,pcy)
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
def _sdtb(px:float,py:float,cx:float,cy:float,w:float,h:float):
    offset_x = abs(px - cx) - w/2
    offset_y = abs(py - cy) - h/2
    unsignedDst = hypot(max(offset_x,0),max(offset_y,0))
    dstInsideBox = max(min(offset_x,0),min(offset_y,0))
    return unsignedDst + dstInsideBox

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
        chunk:Chunk|None = chunks.get((x,y))
        if chunk is not None:
            for obstacle in chunk.blocks:
                d = signed_distance_to_box(px,py,obstacle.collider)
                if d < dist:
                    dist = d
        x,y = tr
        x//=CHUNK_SIZE
        y//=CHUNK_SIZE
        chunk:Chunk|None = chunks.get((x,y))
        if chunk is not None: 
            for obstacle in chunk.blocks:
                d = signed_distance_to_box(px,py,obstacle.collider)
                if d < dist:
                    dist = d
        x,y = bl
        x//=CHUNK_SIZE
        y//=CHUNK_SIZE
        chunk:Chunk|None = chunks.get((x,y))
        if chunk is not None:
            for obstacle in chunk.blocks:
                d = signed_distance_to_box(px,py,obstacle.collider)
                if d < dist:
                    dist = d
        x,y = br
        x//=CHUNK_SIZE
        y//=CHUNK_SIZE
        chunk:Chunk|None = chunks.get((x,y))
        if chunk is not None:
            for obstacle in chunk.blocks:
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
        chunk:Chunk|None = chunks.get((x,y))
        if chunk is not None:
            for obstacle in chunk.blocks:
                d = signed_distance_to_box(px,py,obstacle.collider)
                if d < dist:
                    dist = d
        x,y = tr
        x//=CHUNK_SIZE
        y//=CHUNK_SIZE
        chunk:Chunk|None = chunks.get((x,y))
        if chunk is not None: 
            for obstacle in chunk.blocks:
                d = signed_distance_to_box(px,py,obstacle.collider)
                if d < dist:
                    dist = d
        x,y = bl
        x//=CHUNK_SIZE
        y//=CHUNK_SIZE
        chunk:Chunk|None = chunks.get((x,y))
        if chunk is not None:
            for obstacle in chunk.blocks:
                d = signed_distance_to_box(px,py,obstacle.collider)
                if d < dist:
                    dist = d
        x,y = br
        x//=CHUNK_SIZE
        y//=CHUNK_SIZE
        chunk:Chunk|None = chunks.get((x,y))
        if chunk is not None:
            for obstacle in chunk.blocks:
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

explosions:list[Explosion.Explosion] = []

def create_explosion(pos:Vector2,energy:float):
    e = Explosion.Explosion(pos,energy)
    e.setEntities(collide_blocks_in_range(pos,Explosion.prediction(energy)),collide_entities_in_range(pos,Explosion.prediction(energy)))
    Particles.spawn_smoke(e.particles,10)
    #for vx,vy in zip(e.particles.vx[::5],e.particles.vy[::5]):
    #    Particles.spawn_smoke_particle(pos.copy(),Vector2(vx/2,vy/2),(Vector2.random.x*360).__trunc__())
    explosions.append(e)

def update_explosions():
    a = 0
    while a < explosions.__len__():
        explosions[a].update()
        # t = explosions[a].particles.s[explosions[a].particles.s > explosions[a].energy]
        if explosions[a].isDone:
            explosions.pop(a) 
        else:
            a+=1 

def generate_world():
    '''Generate the world, should run once per world'''
    def checkIsGen() -> None:
        if (Settings.game_state is not GENERATING_WORLD):
            raise GenerationError('Game state must be <GENERATING_WORLD>')
    checkIsGen()

    if len(Chunk._insts) != 0 or len(chunks) != 0: # if we have tried to create some chunks previously
        raise GenerationError('The game has tried to generate a world that already has chunks!??!??!')
    yield 0,TOTAL_GENERATED_CHUNKS
    checkIsGen()
    to_generate = set()
    for cy in range(INITIAL_GEN_SIZE):
        cy -= INITIAL_GEN_SIZE//2
        for cx in range(INITIAL_GEN_SIZE):
            cx -= INITIAL_GEN_SIZE//2

            cpos = (cx,cy)
            queue_chunk(cpos)
            to_generate.add(cpos)
    if len(to_generate) != TOTAL_GENERATED_CHUNKS:
        raise GenerationError("Math error: Chunks loaded to generate are not the amount that should be.")
    done = 0
    while True:
        checkIsGen()
        yield done, len((to_generate))
        if len(chunk_loading_queue) == 0: break
        chunk_to_load:Chunk = chunk_loading_queue[0]
        status = _chunk_step(chunk_to_load)
        match status:
            case 'done':
                chunk_loading_queue.popleft()
                done += 1

        #chunk_loading_queue.rotate()

if __name__ == '__main__':
    from pympler.asizeof import asizeof
    Textures.ground = {}
    Textures.ground[ground.Grass().tex] = Surface(((BLOCK_SIZE,BLOCK_SIZE)))
    Textures.ground[ground.Stone().tex] = Surface(((BLOCK_SIZE,BLOCK_SIZE)))
    Textures.ground[ground.Invalid().tex] = Surface(((BLOCK_SIZE,BLOCK_SIZE)))
    Textures.ground[ground.Water().tex] = Surface(((BLOCK_SIZE,BLOCK_SIZE)))
    chunk = Chunk((1,1))
    import sys
    print(asizeof(chunk.ground) if chunk.active else 'Inactive')
    ting = _create(chunk)
    for _ in ting: #finish the creation of the chunk
        pass
    print(asizeof(chunk.ground))
    print(asizeof(chunk))

