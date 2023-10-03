class GenerationError(Exception):
    '''An error occured during generation of the game world'''
    def __init__(self,*args):
        super().__init__(*args)
