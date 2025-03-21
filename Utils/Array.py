import typing
T = typing.TypeVar('T')
class Array(list[T|None]):
    '''Subclass of list. Holds a fixed size and all size-changing methods raise SyntaxError'''
    def __init__(self,size:int):
        assert size >= 0, 'Array Size must be non-negative'
        super().__init__([None]*size)
        
    def append(self, __object): raise SyntaxError("Array Size cannot be changed")
    def insert(self, __index, __object): raise SyntaxError("Array Size cannot be changed")
    def clear(self): raise SyntaxError("Array Size cannot be changed")
    def extend(self, __iterable): raise SyntaxError("Array Size cannot be changed")
    def pop(self, __index = -1): raise SyntaxError("Array Size cannot be changed")
    def remove(self,__value): raise SyntaxError("Array Size cannot be changed")
    def __iadd__(self,__object): raise SyntaxError("Array Size cannot be changed")
    def __imul__(self, __value): raise SyntaxError("Array Size cannot be changed")
    def __delitem__(self, __index): raise SyntaxError("Array Size cannot be changed")

    def take(self,__index:int):
        item,self[__index] = self[__index],None
        return item

    def swap(self,__index:int,__object:T|None):
        item,self[__index] = self[__index],__object
        return item

    def swapIndices(self,__index1:int, __index2:int):
        self[__index1],self[__index2] = self[__index2],self[__index1]