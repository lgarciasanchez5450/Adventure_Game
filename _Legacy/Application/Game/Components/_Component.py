from typing import TypeVar,Any
from collections.abc import Callable
import sys 
T = TypeVar('T')

components:dict[str,Any] = {}

def register(cls):
    global components
    if cls.__name__ in components:  #type: ignore
        raise SyntaxError("Cannot have two similiarly named components")
    components[sys.intern(cls.__name__)] = cls #type: ignore
    return cls

