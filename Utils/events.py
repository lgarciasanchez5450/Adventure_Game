from typing import Callable, Generic,ParamSpec
P = ParamSpec("P")
class Event(Generic[P]):
    def __init__(self):
        self.listeners:list[Callable[P,None]] = []

    def register(self,function:Callable[P,None]):
        self.listeners.append(function)
        return function
    
    def clearListeners(self):
        self.listeners.clear()

    def fire(self,*args:P.args,**kwargs:P.kwargs):
        self(*args,**kwargs)

    def __call__(self,*args:P.args,**kwargs:P.kwargs):
        for listener in self.listeners:
            listener(*args,**kwargs)





