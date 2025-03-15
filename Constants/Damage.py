'''Types of Damage that can be dealt'''
from typing import NewType
DamageType = NewType('DamageType',str)
FIRE_DAMAGE = DamageType('fire')
ICE_DAMAGE = DamageType('ice')
PHYSICAL_DAMAGE = DamageType('physical')
ETHEREAL_DAMAGE = DamageType('ethereal')
EXPLOSION_DAMAGE = DamageType('explosion')
INTERNAL_DAMAGE = DamageType('internal') # this one is like for if an entity needs to do an action that it cant afford to(energy wise) it will take damage proportional to the amount of energy needed
