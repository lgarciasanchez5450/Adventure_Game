from typing import Callable, TypeVar, Any
onResize = []
def add_OnResize(func):
    if func.__name__ != 'onResize':
        raise RuntimeError('Function added to event onResize must be called onResize!')
    onResize.append(func)

def call_OnResize(width,height):
    for func in onResize:
        func(width,height)



