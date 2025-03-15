'''
This module has been ported over to python from java 
Made by ??? (found on reddit, search for supersimplex noise)
Ported by Hithere32123

'''

import numpy

from ..Math.Fast import njit

    

PRIME_X = 0x5205402B9270C86F
PRIME_Y = 0x598CD327003817B5
HASH_MULTIPLIER = 0x53A3F72DEEC546F5
ROOT2OVER2 = 0.7071067811865476
SKEW_2D = 0.366025403784439
UNSKEW_2D = -0.21132486540518713
N_GRADS_2D = 128
NORMALIZER_2D = 0.05481866495625118
RSQUARED_2D = 2.0 / 3.0
TWICE_UNSKEW_ONE = 1 + 2 * UNSKEW_2D
seed = 3

def set_seed(x:int):
    global seed
    seed = x

'''*
    * 2D OpenSimplex2S/SuperSimplex noise, standard lattice orientation.
'''
def noise2(x:float, y:float):
    global SKEW_2D
    # Get points for A2* lattice
    s = SKEW_2D * (x + y)
    xs = x + s
    ys = y + s
    return noise2_UnskewedBase(seed, xs, ys)

def noise2_s(seed,x,y):
    global SKEW_2D
    # Get points for A2* lattice
    s = SKEW_2D * (x + y)
    xs = x + s
    ys = y + s
    return noise2_UnskewedBase(seed, xs, ys)  

def noise2_array(xs:numpy.ndarray,ys:numpy.ndarray):
    noise = numpy.empty((ys.size, xs.size), dtype=numpy.double)
    for y_i in range(ys.size):
        for x_i in range(xs.size):
            noise[y_i, x_i] = noise2(xs[x_i], ys[y_i])
    return noise

'''*
    * 2D OpenSimplex2S/SuperSimplex noise, with Y pointing down the main diagonal.
    * Might be better for a 2D sandbox style game, where Y is vertical.
    * Probably slightly less optimal for heightmaps or continent maps,
    * unless your map is centered around an equator. It's a slight
    * difference, but the option is here to make it easy.
    '''
def noise2_ImproveX( seed,  x:float, y:float):
    global ROOT2OVER2, SKEW_2D
    # Skew transform and rotation baked into one.
    xx:float = x * ROOT2OVER2
    yy:float = y * (ROOT2OVER2 * (1 + 2 * SKEW_2D))
    return noise2_UnskewedBase(seed, yy + xx, yy - xx)


'''*
    * 2D  OpenSimplex2S/SuperSimplex noise base.
    '''
def noise2_UnskewedBase(seed:int, xs:float, ys:float):
    global PRIME_X,PRIME_Y,UNSKEW_2D,RSQUARED_2D, TWICE_UNSKEW_ONE
    # Get base points and offsets.
    
    xsb:int = xs.__floor__()
    ysb:int = ys.__floor__()
    xi:float = xs - xsb
    yi:float = ys - ysb

    # Prime pre-multiplication for hash.
    xsbp = xsb * PRIME_X
    ysbp = ysb * PRIME_Y
    # Unskew.
    t:float = (xi + yi) * UNSKEW_2D
    dx0:float = xi + t
    dy0:float = yi + t

    # First vertex.
    a0:float = RSQUARED_2D - dx0 * dx0 - dy0 * dy0
    value:float =  a0 * a0 * a0 * a0 * grad(seed, xsbp, ysbp, dx0, dy0)

    # Second vertex.
    #a1:float = (2 * (1 + 2 * UNSKEW_2D) * (1 / UNSKEW_2D + 2)) * t + ((-2 * (1 + 2 * UNSKEW_2D) * (1 + 2 * UNSKEW_2D)) + a0)
    a1:float = geta1(t,a0)

    dx1:float = dx0 - TWICE_UNSKEW_ONE
    dy1:float = dy0 - TWICE_UNSKEW_ONE
    value += a1 * a1 * a1 * a1 * grad(seed, xsbp + PRIME_X, ysbp + PRIME_Y, dx1, dy1)#

    # Third and fourth vertices.
    # Nested conditionals were faster than compact bit logic/arithmetic.
    xmyi:float = xi - yi
    if (t < UNSKEW_2D):
        if (xi + xmyi > 1):
            dx2:float = dx0 - (3 * UNSKEW_2D + 2)
            dy2:float = dy0 - (3 * UNSKEW_2D + 1)
            a2:float = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if (a2 > 0):
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp + (PRIME_X << 1), ysbp + PRIME_Y, dx2, dy2)
            
        else:
            dx2:float = dx0 - (UNSKEW_2D)
            dy2:float = dy0 - (UNSKEW_2D + 1)
            a2:float = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if (a2 > 0):
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp, ysbp + PRIME_Y, dx2, dy2)
            
        if (yi > 1 + xmyi):
            dx3:float = dx0 - (3 * UNSKEW_2D + 1)
            dy3:float = dy0 - (3 * UNSKEW_2D + 2)
            a3:float = RSQUARED_2D - dx3 * dx3 - dy3 * dy3
            if (a3 > 0):
                value += (a3 * a3) * (a3 * a3) * grad(seed, xsbp + PRIME_X, ysbp + (PRIME_Y << 1), dx3, dy3)
       
        else:
            dx3:float = dx0 - (UNSKEW_2D + 1)
            dy3:float = dy0 - (UNSKEW_2D)
            a3:float = RSQUARED_2D - dx3 * dx3 - dy3 * dy3
            if (a3 > 0):
                value += (a3 * a3) * (a3 * a3) * grad(seed, xsbp + PRIME_X, ysbp, dx3, dy3)
            
    else:
        if (xi + xmyi < 0):
            dx2:float = dx0 + (1 + UNSKEW_2D)
            dy2:float = dy0 + (UNSKEW_2D)
            a2:float = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if (a2 > 0):
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp - PRIME_X, ysbp, dx2, dy2)
          
        else:
            dx2:float = dx0 - (UNSKEW_2D + 1)
            dy2:float = dy0 - (UNSKEW_2D)
            a2:float = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if (a2 > 0):
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp + PRIME_X, ysbp, dx2, dy2)
            
        
        if (yi < xmyi):
            dx2:float = dx0 + (UNSKEW_2D)
            dy2:float = dy0 + (UNSKEW_2D + 1)
            a2:float = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if (a2 > 0):
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp, ysbp - PRIME_Y, dx2, dy2)
            
        else:
            dx2:float = dx0 - (UNSKEW_2D)
            dy2:float = dy0 - (UNSKEW_2D + 1)
            a2:float = RSQUARED_2D - dx2 * dx2 - dy2 * dy2
            if (a2 > 0):
                value += (a2 * a2) * (a2 * a2) * grad(seed, xsbp, ysbp + PRIME_Y, dx2, dy2)
    return value



'''
    * Utility
'''
def slong(value:int) -> int:
    #18446744073709551616 # 1<<64
    value %= 18446744073709551616
    #return value - base if value.bit_length() == 64 else value
    return value - 18446744073709551616 if value >= 9223372036854775808 else value
 
@njit(cache=True,inline = 'always')
def sinteger(value:int):
    #base = 4294967296
    value %= 4294967296
    return value - 4294967296 if value >=2147483648 else value

@njit(cache = True)
def custom_int(value:int) -> int:
    return sinteger(value ^ (value >> 58)) & 0b11111110

def grad(seed:int,  xsvp:int,  ysvp:int,  dx:float,  dy:float) -> float:
    global GRADIENTS_2D,HASH_MULTIPLIER
    gi:int = custom_int(slong((seed ^ xsvp ^ ysvp) * HASH_MULTIPLIER))
    return GRADIENTS_2D[gi] * dx + GRADIENTS_2D[gi | 1] * dy

@njit(cache = True)
def geta1(t,a0) -> float:
    return (2 * (1 + 2 * UNSKEW_2D) * (1 / UNSKEW_2D + 2)) * t + ((-2 * (1 + 2 * UNSKEW_2D) * (1 + 2 * UNSKEW_2D)) + a0)

    



'''
    * Lookup Tables & Gradients
'''

GRADIENTS_2D:list[float] = [0.0] * N_GRADS_2D * 2
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
    grad2[i] = grad2[i] / NORMALIZER_2D
del i #type:ignore

j = 0
for i in range(len(GRADIENTS_2D)):
    if (j == len(grad2)): j = 0
    GRADIENTS_2D[i] = grad2[j]
    j+=1
del j,i #type: ignore
    
def list_is_close_to(list1,list2):
    return max([abs(a-b) for a,b in zip(list1,list2)]) < .0000001    

def run_tests():
    from time import perf_counter
    import random
    test1_answers = {
                    1745:[-3.1138848356295195, -10.898877791019576, 3.1138848356295195, -11.225507697251212, -10.898877791019576, -3.1138848356295195, 10.787137804943775, 9.613642297817508, 3.1138848356295195, 10.787137804943775, -3.1138848356295195, 10.787137804943775, -11.225507697251212, 9.613642297817508, 10.787137804943775, -3.1138848356295195],
                    -9277:[5.425809208361919, 10.787137804943775, 10.787137804943775, -5.425809208361919, 10.787137804943775, 5.425809208361919, 10.787137804943775, -2.696865530357586, 10.787137804943775, 10.787137804943775, 5.425809208361919, 2.696865530357586, -5.425809208361919, -2.696865530357586, 2.696865530357586, 5.425809208361919],
                    -11291:[8.090272274586173, -2.696865530357586, -3.1138848356295195, -5.7996984888892955, -2.696865530357586, 8.090272274586173, 0.21586507675959954, 5.7996984888892955, -3.1138848356295195, 0.21586507675959954, 8.090272274586173, -10.787137804943775, -5.7996984888892955, 5.7996984888892955, -10.787137804943775, 8.090272274586173]
    }
    test2_answers = {
        1745:[0.10169742685383955, 0.34245590984126584, 0.07967682133056074, -0.02601645285787879, -0.08116975446510796, 0.149982080275581, -0.1186148982678273, -0.26280066008231967, 0.3284636267621121, 0.02612887445251281, -0.04093236322213979, -0.2673131491297672, 0.074535562825414, -0.1065087523931904, 0.6459546333150622, 0.2547685779146876],
        -9277:[0.48583832990251646, -0.310529829448389, -0.2957073644916285, 0.0755160913757486, 0.24375129912254737, 0.5393221770443897, 0.19356900603677038, 0.23030277129515317, 0.02939208117752142, -0.07498508020919241, 0.22606171163680483, 0.06871075034664653, 0.11970053463238242, 0.10958593092381776, 0.11306738461405622, 0.6343860412649428],
        -11291:[0.34299197417187843, 0.6625108211201022, -0.22597725464668145, -0.15586245281349032, 0.17985950231462391, -0.40435908152950295, 0.07454636640264611, -0.039062495221131026, 0.1694337399502514, -0.15539020601234055, 0.036185886657968486, 0.5319550237142369, -0.024920192350453965, -0.1134193248250248, 0.16457385472763136, 0.49623199869186324]
    }
    start = perf_counter()
    seeds = [1745, -9277, -11291]
    failed = False
    for seed in seeds:
        test1 = [grad(seed,x,y,0.384,.481) for x in range(1,50,15) for y in range(1,50,15) ]
        if list_is_close_to(test1_answers[seed],test1):
            print('Test Passed')
        else:
            print(f'Test1 failed with seed: {seed}')
            failed = True
        test2 = [noise2_s(seed,x/3,y/3) for x in range(1,50,15) for y in range(1,50,15) ]
        if list_is_close_to(test2_answers[seed], test2):
            print('Test Passed')
        else:
            print(f'Test2 failed with seed: {seed}') 
            failed = True  
    if failed:
        print(f'Tests Failed in {perf_counter() - start} seconds')
    else:
        print(f'Tests Passed in {perf_counter() - start} seconds')
    print("Starting Stress Test. Rating Goal: 500")
    cycles = 1_000
    import multiprocessing
    cache = ((x,y) for x in range(cycles) for y in range(cycles))
    start = perf_counter()
    # with multiprocessing.Pool() as pool:

        # pool.starmap(noise2,[(x,y) for x in range(cycles) for y in range(cycles)])
    [noise2(x,y) for x,y in cache]
    time = perf_counter()-start
    cycles_per_second = cycles*cycles / time
    print("Rating:",cycles_per_second.__trunc__()/1000)
    if cycles_per_second >500000:#above a rating of 500
        print(f'Stress Test Passed in {time} seconds')
    else:
        print(f'Stress Test Failed in {time} seconds')

'''
class LayeredNoiseMap:
    def __init__(self,noise_scales,noise_strengths):
        assert len(noise_scales) == len(noise_strengths), "all arguments must be of the same length"

        self.noise_scales = array('d',noise_scales)
        self.noise_strengths = array('f',noise_strengths)
        self.noise_counts = tuple(range(len(self.noise_scales)))

        self.noise_normalizer = sum(noise_strengths)
    
    def getAt(self,x,y):
        data = 0
        for scale,strength in zip(self.noise_scales,self.noise_strengths):
            data += noise2(x*scale,y*scale) * strength
        data /= self.noise_normalizer
        return data
    
    def getArr(self,xs:numpy.ndarray,ys:numpy.ndarray):
        data = numpy.zeros(shape=(ys.size,xs.size))
        for scale,strength in zip(self.noise_scales,self.noise_strengths):
            data += noise2_array(xs*scale,ys*scale) * strength
        data /= self.noise_normalizer
        return data
    

    def getArrShifted(self,xs:numpy.ndarray,ys:numpy.ndarray):
        xshift = 3.141
        yshift = 2.718
        data = numpy.zeros(shape=(ys.size,xs.size),dtype = numpy.float32)
        for scale,strength,i in zip(self.noise_scales,self.noise_strengths,self.noise_counts):
            data += noise2_array((xs+xshift*i)*scale,(ys+yshift*i)*scale) * strength
        data /= self.noise_normalizer
        return data
'''


if __name__ == '__main__':
    run_tests()