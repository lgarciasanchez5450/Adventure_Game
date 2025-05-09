from gametypes import *

class SceneBehaviour:   
    _subclasses_:dict[str,type['SceneBehaviour']] = {}
    def __init_subclass__(cls):
        name = cls.__name__
        if name in SceneBehaviour._subclasses_:
            raise NameError(f'Behaviour {cls} conflicts with another. Maybe two behaviours have the same name? (<- this cannot happen)')
        SceneBehaviour._subclasses_[name] = cls

    __slots__ = ()
    def start(self,engine:EngineType,scene:SceneType): ...
    def update(self,engine:EngineType,scene:SceneType): ...
    def draw(self,engine:EngineType,scene:SceneType): ...
    def stop(self,engine:EngineType,scene:SceneType): ...