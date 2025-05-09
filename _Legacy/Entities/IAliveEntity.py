import typing
from Entities.IEntity import IEntity

class IAliveEntity(IEntity,typing.Protocol):
    health:float
    max_health:float


