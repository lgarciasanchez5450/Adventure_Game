import os
import json
import typing
from pyglm import glm
from Utils import utils as Utils
from Utils import parse
from GameObject import GameObject
from Behaviours.Behaviour import Behaviour


T = typing.TypeVar('T')

PATH = [
    './Prefabs',
]

def loadGameObject(e:str|dict) -> GameObject:
    if type(e) is str: #prefab name
        for directory in PATH:
            try:
                filenames = os.listdir(directory)
            except FileNotFoundError:
                continue
            if e in filenames:
                fqn = os.path.join(directory,e)
                with open(fqn,'r') as file:
                    return loadGameObject(json.load(file))
        raise FileNotFoundError(f"Prefab {repr(e)} could not be found in PATH")
    elif type(e) is dict:
        e_name = e.get('name','NAME NOT FOUND')
        try:
            return _parseGameObjectData(e)
        except Exception as err:
            err.add_note(f'GameObject: {e_name}')
            raise err
    else:
        raise TypeError(f'Cannot Convert type {type(e).__name__} to GameObject')


def _parseGameObjectData(data:dict[str,typing.Any]) -> GameObject:
    try:
        name = str(data['name'])
    except KeyError:
        raise KeyError(f'GameObject Property "name" not found.')
    pos = glm.vec3(data['pos'])
    vel = glm.vec3(data.get('vel',(0,0,0)))
    mass = str(data.get('mass',1))
    if mass in ('infinity','inf'):
        mass = float('inf')
    else:
        mass = float(mass)
    size = glm.vec3(data['size'])

    behavs:list[str] = list(data.get('behaviours',[]))
    behaviours:list[Behaviour] = []
    for behav in behavs:
        if '(' in behav :
            i = behav.index('(')
            args = behav[i:]
            behav = behav[:i]
        else:
            args = '()'
        args,kwargs = parse.evalArgs(args)
        b = Behaviour._subclasses_.get(behav)
        if b is None:
            likely_meant = Utils.sortBySimilarity(behav,Behaviour._subclasses_.keys())
            raise LookupError(f'Behaviour {behav} not found! Did you mean {likely_meant[0]}')
        behaviours.append(b(*args,**kwargs))
    if mass < 1e-6:
        raise ValueError(f'Invalid Mass: {mass}')
    #make GameObject
    ent = GameObject(name,pos,vel,mass,size,behaviours)
    return ent

def parseComplexType(s:str,parentType:type[T],only_subtypes:bool = True) -> T:
    lookup:dict[str,type[T]] = {}
    if only_subtypes:
        if not hasattr(parentType,'_subclasses_'):
            raise LookupError('Could not find subclasses')
        lookup = parentType._subclasses_
    else:
        if not hasattr(parentType,'_subclasses_'):
            lookup = {parentType.__name__:parentType}
    if '(' in s:
        i = s.index('(')
        args = s[i:]
        s = s[:i] 
    else:
        args = '()'
    args,kwargs = parse.evalArgs(args)
    try:
        t = lookup[s]
    except KeyError:
        likely_meant = Utils.sortBySimilarity(s,lookup.keys())[0]
        raise LookupError(f'{parentType.__name__} {s} not found! Did you mean {likely_meant}')
    else:
        return t(*args,**kwargs)