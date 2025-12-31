
import numpy as np

from kinetic.helpers import *

def corner(N,l=.5):
	return l*zrand(N), vrand(N)

def random(N,xx,yy, v=1):
	x = xx[0] + (xx[1]-xx[0])*np.random.random(N)
	y = yy[0] + (yy[1]-yy[0])*np.random.random(N)
	return np.stack([x,y]), v*vrand(N)


