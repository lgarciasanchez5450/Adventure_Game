from Constants import DEBUG
from typing import Protocol,Any
from Errors import return_error,UnInstantiableError

class ImplementsDraw(Protocol):
    def draw(self):...

class UnInstantiable:
    def __init_subclass__(cls) -> None:
        cls.__init__ = return_error(UnInstantiableError)
        
if DEBUG:
    def assert_type(object,type):
        assert isinstance(object,type), f"Unexpected Type: Got ->{repr(object)}  Expected ->{type}"

    def is_collider(object) -> bool:
        from game_math import Collider
        return isinstance(object,Collider)
