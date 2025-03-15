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


class EventChannel:
    def __init__(self):
        self.listeners:list[Callable] = []

    def getHandle(self,filter:Callable = lambda x: True):
        class Handle:
            def __init__(self) -> None:
                self.event = None
            def _(self,event):
                if filter(event):
                    self.event = event

            def poll(self):
                e = self.event
                if e is not None:
                    self.event = None
                    return e
        handle = Handle()
        self.register(handle._)
        return handle

    def register(self,function:Callable):
        self.listeners.append(function)
        return function
    
    def fire(self,event):
        self(event)

    def __call__(self,event):
        for listener in self.listeners:
            listener(event)