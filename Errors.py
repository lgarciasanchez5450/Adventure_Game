class GenerationError(Exception):
    '''An error occured during generation of the game world'''
    def __init__(self,*args):
        super().__init__(*args)

class UnInstantiableError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__("An object deriving from the base class \"UnInstantiable\" was created")



def return_error(error):
    def _(*args,**kwargs):
        raise error()
    return _