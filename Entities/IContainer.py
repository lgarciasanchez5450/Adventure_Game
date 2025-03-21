import typing
from Entities.IEntity import IEntity
from Scripts.Inventory import Inventory


class IContainerEntity(IEntity,typing.Protocol):
    inventory:Inventory

