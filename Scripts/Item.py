class Item:
    stack_size:int = 64
    type:str = 'item'
    __slots__ = 'count'
    def __init__(self):
        self.count = 1
        
