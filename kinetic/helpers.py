
"""
Back and forth.
	xy  = np.stack([x,y])
	x,y = xy[0], xy[1].
Initialize.
	xy = np.zeros((2,N))
"""

import numpy as np
from matplotlib.pyplot import axes

rng = np.random.default_rng(seed=150)

zrand = lambda N: rng.random((2,N))
rms = lambda vxy: np.sqrt(np.sum(vxy**2))
rmsnorm = lambda vxy: vxy/rms(vxy)
vrand = lambda N: rmsnorm(zrand(N) - 0.5)

vsq = lambda v: np.sum(v**2)

quivstyle = dict(color='0.5', pivot='tip', headlength=0, headwidth=0, headaxislength=0)


isnum = lambda x: type(x) in [float,int]


alpha = lambda g,d=2: d/2.+1. if 1.*g>0. else d/2. 

gms = lambda ax,r0: 2.*r0*(72./ax.figure.dpi)*ax.get_window_extent().width/(ax.get_xlim()[1]-ax.get_xlim()[0])

def bounds(gas):
	b = dict()
	for key in gas.walls.keys():
		if isnum(gas.walls[key]):
			b[key] = 1.*gas.walls[key]
		else:
			b[key] = 1.*gas.walls[key].z
	return b

def extent(sys):
	x0 = np.min([bounds(gas)['l'] for gas in sys.gases])
	x1 = np.max([bounds(gas)['r'] for gas in sys.gases])
	y0 = np.min([bounds(gas)['b'] for gas in sys.gases])
	y1 = np.max([bounds(gas)['t'] for gas in sys.gases])
	return dict(l=x0,r=x1,b=y0,t=y1)

axlbrt = lambda l,b,r,t: axes([l,b,r-l,t-b])
