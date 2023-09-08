
PRIME_X = 0x5205402B9270C86F
PRIME_Y = 0x598CD327003817B5

HASH_MULTIPLIER = 0x53A3F72DEEC546F5

ROOT2OVER2 = 0.7071067811865476
SKEW_2D = 0.366025403784439
UNSKEW_2D = -0.21132486540518713

N_GRADS_2D_EXPONENT = 7
N_GRADS_2D = 128


NORMALIZER_2D = 0.05481866495625118

RSQUARED_2D = 2.0 / 3.0
import typing 
#float = typing.TypeVar('float',bound = float)
'''
    * Noise Evaluators
'''

'''*
    * 2D OpenSimplex2S/SuperSimplex noise, standard lattice orientation.
'''
def noise2(seed, x, y):
    # Get points for A2* lattice
    s = SKEW_2D * (x + y)
    xs = x + s
    ys = y + s

    return noise2_UnskewedBase(seed, xs, ys)


'''*
    * 2D OpenSimplex2S/SuperSimplex noise, with Y pointing down the main diagonal.
    * Might be better for a 2D sandbox style game, where Y is vertical.
    * Probably slightly less optimal for heightmaps or continent maps,
    * unless your map is centered around an equator. It's a slight
    * difference, but the option is here to make it easy.
    '''
def noise2_ImproveX( seed,  x:float, y:float):

    # Skew transform and rotation baked into one.
    xx:float = x * ROOT2OVER2
    yy:float = y * (ROOT2OVER2 * (1 + 2 * SKEW_2D))

    return noise2_UnskewedBase(seed, yy + xx, yy - xx)


'''*
    * 2D  OpenSimplex2S/SuperSimplex noise base.
    '''
def noise2_UnskewedBase( seed, xs:float, ys:float):

    # Get base points and offsets.
    xsb:int = fastFloor(xs)
    ysb:int = fastFloor(ys)
    xi:float = float(xs - xsb)
    yi:float = float(ys - ysb)

    # Prime pre-multiplication for hash.
    xsbp = xsb * PRIME_X
    ysbp = ysb * PRIME_Y

    # Unskew.
    t:float = (xi + yi) * float(UNSKEW_2D)
    dx0:float = xi + t
    dy0:float = yi + t

    # First vertex.
    a0:float = RSQUARED_2D - dx0 * dx0 - dy0 * dy0
    value:float = (a0 * a0) * (a0 * a0) * grad(seed, xsbp, ysbp, dx0, dy0)

    # Second vertex.
    a1:float = float(2 * (1 + 2 * UNSKEW_2D) * (1 / UNSKEW_2D + 2)) * t + (float(-2 * (1 + 2 * UNSKEW_2D) * (1 + 2 * UNSKEW_2D)) + a0)
    dx1:float = dx0 - float(1 + 2 * UNSKEW_2D)
    dy1:float = dy0 - float(1 + 2 * UNSKEW_2D)
    value += (a1 * a1) * (a1 * a1) * grad(seed, xsbp + PRIME_X, ysbp + PRIME_Y, dx1, dy1)

    # Third and fourth vertices.
    # Nested conditionals were faster than compact bit logic/arithmetic.
    xmyi:float = xi - yi
    if (t < UNSKEW_2D):
        if (xi + xmyi > 1):
            dx2:float = dx0 - float(3 * UNSKEW_2D + 2)
            dy2:float = dy0 - float(3 * UNSKEW_2D + 1)
            a2:float = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if (a2 > 0):
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp + (PRIME_X << 1), ysbp + PRIME_Y, dx2, dy2)
            
        else:
            dx2:float = dx0 - float(UNSKEW_2D)
            dy2:float = dy0 - float(UNSKEW_2D + 1)
            a2:float = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if (a2 > 0):
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp, ysbp + PRIME_Y, dx2, dy2)
            
        if (yi - xmyi > 1):
            dx3:float = dx0 - float(3 * UNSKEW_2D + 1)
            dy3:float = dy0 - float(3 * UNSKEW_2D + 2)
            a3:float = RSQUARED_2D - dx3 * dx3 - dy3 * dy3
            if (a3 > 0):
                value += (a3 * a3) * (a3 * a3) * grad(seed, xsbp + PRIME_X, ysbp + (PRIME_Y << 1), dx3, dy3)
            
        
        else:
            dx3:float = dx0 - float(UNSKEW_2D + 1)
            dy3:float = dy0 - float(UNSKEW_2D)
            a3:float = RSQUARED_2D - dx3 * dx3 - dy3 * dy3
            if (a3 > 0):
                value += (a3 * a3) * (a3 * a3) * grad(seed, xsbp + PRIME_X, ysbp, dx3, dy3)
            
        
    
    else:
        if (xi + xmyi < 0):
            dx2:float = dx0 + float(1 + UNSKEW_2D)
            dy2:float = dy0 + float(UNSKEW_2D)
            a2:float = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if (a2 > 0):
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp - PRIME_X, ysbp, dx2, dy2)
            
        
        else:
            dx2:float = dx0 - float(UNSKEW_2D + 1)
            dy2:float = dy0 - float(UNSKEW_2D)
            a2:float = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if (a2 > 0):
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp + PRIME_X, ysbp, dx2, dy2)
            
        

        if (yi < xmyi):
            dx2:float = dx0 + float(UNSKEW_2D)
            dy2:float = dy0 + float(UNSKEW_2D + 1)
            a2:float = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if (a2 > 0):
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp, ysbp - PRIME_Y, dx2, dy2)
            
        else:
            dx2:float = dx0 - float(UNSKEW_2D)
            dy2:float = dy0 - float(UNSKEW_2D + 1)
            a2:float = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if (a2 > 0):
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp, ysbp + PRIME_Y, dx2, dy2)
            
        
    

    return value





'''
    * Utility
'''

def correct(value, bits, signed) -> int:
    base = 1 << bits
    value %= base
    return value - base if signed and value.bit_length() == bits else value


ubyte, sbyte, uinteger, sinteger, ulong, slong = (
    lambda v: correct(v, 8, False), lambda v: correct(v, 8, True),
    lambda v: correct(v, 32, False), lambda v: correct(v, 32, True),
    lambda v: correct(v, 64, False), lambda v: correct(v, 64, True)
)

def grad( seed,  xsvp,  ysvp,  dx:float,  dy:float) -> float:
    hash = seed ^ xsvp ^ ysvp
    hash *= HASH_MULTIPLIER
    hash = slong(hash)
    hash ^= hash >> (64 - N_GRADS_2D_EXPONENT + 1)
    gi:int = sinteger(hash) & ((N_GRADS_2D - 1) << 1)
    return GRADIENTS_2D[gi | 0] * dx + GRADIENTS_2D[gi | 1] * dy


def fastFloor( x:float):
    xi:int = int(x)
    return xi-1 if x < xi else xi


'''
    * Lookup Tables & Gradients
'''

GRADIENTS_2D:list[float] = [None] * 128 * 2
grad2 = [
        0.38268343236509,   0.923879532511287,
        0.923879532511287,  0.38268343236509,
        0.923879532511287, -0.38268343236509,
        0.38268343236509,  -0.923879532511287,
        -0.38268343236509,  -0.923879532511287,
        -0.923879532511287, -0.38268343236509,
        -0.923879532511287,  0.38268343236509,
        -0.38268343236509,   0.923879532511287,
        #-------------------------------------#
        0.130526192220052,  0.99144486137381,
        0.608761429008721,  0.793353340291235,
        0.793353340291235,  0.608761429008721,
        0.99144486137381,   0.130526192220051,
        0.99144486137381,  -0.130526192220051,
        0.793353340291235, -0.60876142900872,
        0.608761429008721, -0.793353340291235,
        0.130526192220052, -0.99144486137381,
        -0.130526192220052, -0.99144486137381,
        -0.608761429008721, -0.793353340291235,
        -0.793353340291235, -0.608761429008721,
        -0.99144486137381,  -0.130526192220052,
        -0.99144486137381,   0.130526192220051,
        -0.793353340291235,  0.608761429008721,
        -0.608761429008721,  0.793353340291235,
        -0.130526192220052,  0.99144486137381,
]
for i in range(len(grad2)):
    grad2[i] = float(grad2[i] / NORMALIZER_2D)

j = 0
for i in range(len(GRADIENTS_2D)):
    if (j == len(grad2)): j = 0
    GRADIENTS_2D[i] = grad2[j]
    j+=1
    

