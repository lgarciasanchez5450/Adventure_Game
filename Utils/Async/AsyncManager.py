import typing
from collections.abc import Generator,Callable
from collections import deque

class AsyncManager:
    __slots__ = 'current_tasks'
    def __init__(self):
        self.current_tasks:deque[tuple[Callable,Generator[None,typing.Any,typing.Any]]] = deque()

    def submit_async(self,task:Generator[None,typing.Any,typing.Any],on_done:Callable = lambda *x:None):
        self.current_tasks.append((on_done,task))

    def run(self):
        while self.current_tasks:
            self.update_loop()

    def is_done(self):
        return not self.current_tasks

    def update_loop(self):
        '''only call when self.current_tasks has elements'''
        on_done,task = self.current_tasks.popleft()
        try:
            next(task)
        except StopIteration as e:
            on_done(e.value)
        else:
            self.current_tasks.append((on_done,task))
        
    
class Future:
    __slots__ = 'obj'
    def __init__(self):
        self.obj:typing.Any = None

import threading
def read_async(path:str):
    out=  Future() #type: ignore
    def inner(out:Future):
        nonlocal path
        with open(path,'rb') as file:
            out.obj=file.read()
    thread = threading.Thread(target=inner,args=[out])
    thread.start()
    while out.obj is None:
        yield
    return out.obj

