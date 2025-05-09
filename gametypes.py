import typing
if typing.TYPE_CHECKING:
    from GameApp import GLEngine
    from GameObject import GameObject
    from GLScene import GLScene
    from Behaviours import Behaviour

type EngineType = 'GLEngine'
type GameObjectType = 'GameObject'
type SceneType = 'GLScene'
type BehaviourType = 'Behaviour'
type CPOS = tuple[int,int,int]

__all__ = [
    'typing',
    'EngineType',
    'GameObjectType',
    'SceneType',
    'BehaviourType',
    'CPOS'
]