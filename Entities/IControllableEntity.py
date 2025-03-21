import typing
from Entities.IContainer import IContainerEntity
from Entities.IAliveEntity import IAliveEntity
from Scripts.Inventory import Hotbar

class IControllableEntity(IAliveEntity,IContainerEntity,typing.Protocol):
    hotbar:Hotbar