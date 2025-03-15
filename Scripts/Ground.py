WATER = 0
SAND = 1
GRASS = 2

from Utils.Math.Fast import cache

@cache
def ground_to_surf(ground:int):
    if ground == WATER:
        pass

    elif ground == SAND:
        pass

    elif ground == GRASS:
        pass

    raise RuntimeError("Not a valid ground")