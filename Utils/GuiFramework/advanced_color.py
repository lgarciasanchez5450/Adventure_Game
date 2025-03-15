from math import acos
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

def rgb_to_hsv(r,g,b): 
	M = max(r, g, b)
	m = min(r, g, b)

	#And then V and S are defined by the equations

	V = M/255
	S = 1 - m/M  if M > 0 else 0

	#As in the HSI and HSL color schemes, the hue H is defined by the equations
	d = (r*r+g*g+b*b-r*g-r*b-g*b)**0.5
	H = acos((r - g/2 - b/2)/d)  if g >= b else 3.14159265358979 - acos( (r - g/2 - b/2)/d)  
	return H/3.14159265358979,S,V

def hsv_to_rgb(h,s,v): 
	h *= 360
	M = 255*v
	m = M*(1-s)
	#Now compute another number, z, defined by the equation
	z = (M-m)*(1-abs((h/60)%2-1))
	#Now you can compute R, G, and B according to the angle measure of H. There are six cases. 
	R,G,B = 0,0,0
	if 0 <= h < 60:
		R = M
		G = z + m
		B = m

	elif 60 <= h < 120:
		R = z + m
		G = M
		B = m

	elif 120 <= h < 180:
		R = m
		G = M
		B = z + m

	elif 180 <= h < 240:
		R = m
		G = z + m
		B = M

	elif 240 <= h < 300:
		R = z + m
		G = m
		B = M

	elif 300 <= h <= 360:
		R = M
		G = m
		B = z + m
	return R,G,B

