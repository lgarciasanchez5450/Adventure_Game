
from random import _inst
from math import pi,cos,sin

def generate_point_from(x0,y0,min_rad,max_rad):
	theta = 2*pi * _inst.random()
	mag = _inst.random() * (max_rad- min_rad) + min_rad
	x1 = x0 + cos(theta) * mag
	y1 = y0 + sin(theta) * mag
	return (x1,y1)