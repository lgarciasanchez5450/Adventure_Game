def getComplementary(r:int,g:int,b:int,a:int|None = None):
    '''
    Input: RGB(A) as integers from 0 - 255
    Reuturns: the complementary color in the same format as inputted'''
    MAX = max(r,g,b) + min(r,g,b)
    if a:
        return MAX-r,MAX-g,MAX-b,a
    return MAX-r,MAX-g,MAX-b

def getLightness(r:int,g:int,b:int):
    return (max(r,g,b)+min(r,g,b))/510

def toHex(r:int,g:int,b:int):
    return hex(r<<16 | g<<8 | b)

def fromHex(h:str):
    a = int(h,base=0)
    return a>>16,a>>8&0xFF,a&0xFF

def darken(r:int,g:int,b:int,amount:int):
    return max(r-amount,0),max(g-amount,0),max(b-amount,0)

def lighten(r:int,g:int,b:int,amount:int):
    return min(r+amount,255),min(g+amount,255),min(b+amount,255)