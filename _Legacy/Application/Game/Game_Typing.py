from typing import Protocol, Union, Callable, TypeVar
from .Constants import DEBUG
from .Errors import return_error,UnInstantiableError
from ..Utils.Math.Vector import Vector2
from ..Utils.Math.Collider import Collider

from .GameScreen.Appearance import Appearance
from pygame import Surface
import numpy
T = TypeVar("T")
Numeric = TypeVar("Numeric",numpy.ndarray,float)
PATH_DICT_TYPE = Union[Surface,dict[str,"PATH_DICT_TYPE"]]

class ImplementsDraw(Protocol):
    def draw(self,surf:Surface): ...

class UnInstantiable:
    def __init_subclass__(cls) -> None:
        cls.__init__ = return_error(UnInstantiableError())




class Moves(Protocol):
    typeid:str
    vel:Vector2
    pos:Vector2
    dead:bool
    collider:Collider
    def take_damage(self,damage:int,type:str,appearance:Appearance|None = None): ...

class NotMoves(Protocol):
    typeid:str
    pos:Vector2
    collider:Collider
    dead:bool
    def take_damage(self,damage:int,type:str,appearance:Appearance|None = None): ...

if DEBUG:

    def abstractmethod(func:Callable):
        assert callable(func), 'abstractmethod only works on callable objects'
        def default_abstract_method(*args,**kwargs):
            raise NotImplementedError("call to abstract method " + repr(func))
        default_abstract_method.__name__ = func.__name__
        return default_abstract_method

    def assert_type(object:object,type_:type[T]) ->T:
        assert isinstance(object,type_), f"Unexpected Type: Got -> {repr(object)}({type(object)})  Expected ->{type_}"
        return object

    def is_collider(object:object) -> bool:
        return isinstance(object,Collider)
