from Constants import DEBUG
from typing import Protocol,Any, Union, Callable, TypeVar, Dict, TYPE_CHECKING, Optional,final
from warnings import warn
from Errors import return_error,UnInstantiableError
from game_math import Vector2
from Appearance import Appearance
from pygame import Surface
T = TypeVar("T")
PATH_DICT_TYPE = Union[Surface,Dict[str,"PATH_DICT_TYPE"]]

class ImplementsDraw(Protocol):
    def draw(self): ...

class UnInstantiable:
    def __init_subclass__(cls) -> None:
        cls.__init__ = return_error(UnInstantiableError())
        
class Moves(Protocol):
    typeid:str
    vel:Vector2
    pos:Vector2
    def take_damage(self,damage:int,type:str,appearance:Appearance|None = None): ...

if DEBUG:

    def abstractmethod(func:Callable):
        assert callable(func), 'abstractmethod only works on callable objects'
        def default_abstract_method(*args,**kwargs):
            raise NotImplementedError("call to abstract method " + repr(func))
        default_abstract_method.__name__ = func.__name__
        return default_abstract_method

    def assert_type(object:object,type:type[T]) ->T:
        assert isinstance(object,type), f"Unexpected Type: Got ->{repr(object)}  Expected ->{type}"
        return object

    def is_collider(object:object) -> bool:
        from game_math import Collider
        return isinstance(object,Collider)
