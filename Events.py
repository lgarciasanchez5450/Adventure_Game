from typing import Callable, TypeVar, Any
onResize = []
def add_OnResize(func):
    if func.__name__ != 'onResize':
        raise RuntimeError('Function added to event onResize must be called onResize!')
    onResize.append(func)

def call_OnResize(width,height):
    for func in onResize:
        func(width,height)



class Event:
    def __init__(self, *types:Any):
        self.listeners:list = []
        self.types = types
    
    def register(self, func:Callable) -> Callable:
        self.listeners.append(func)
        return func
    
    def __call__(self,*data:Any):
        assert len(data) == len(self.types) and all([isinstance(d,ty) for d,ty in zip(data,self.types)]), 'wrong args buddy' # TODO when project is finished and it is guaranteed that no events will raise errors then the checks can be deleted  
        for subscriber in self.listeners:
            try: #TODO this try catch statement can be deleted tooo
                subscriber(*data)
            except TypeError as err:
                raise TypeError('Subsciber accepts incorrect arguments')
                


if __name__ == '__main__':
    event1 = Event(str)
    @event1.register
    def spam(he:str,two:int) -> None:
        
        return print(he.upper())
    
    event1('wassup!???!')
    


