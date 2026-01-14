
"""
Back and forth.
	xy  = np.stack([x,y])
	x,y = xy[0], xy[1].
Initialize.
	xy = np.zeros((2,N))
"""

import numpy as np
import inspect


rng = np.random.default_rng(seed=150)

zrand = lambda N: rng.random((2,N))
rms = lambda vxy: np.sqrt(np.sum(vxy**2))
rmsnorm = lambda vxy: vxy/rms(vxy)
vrand = lambda N: rmsnorm(zrand(N) - 0.5)

vsq = lambda v: np.sum(v**2)

isnum = lambda x: type(x) in [float,int]

alpha = lambda g,d=2: d/2.+1. if 1.*g>0. else d/2. 

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


def param_inputs(params):
	keys = ["N","m","r","g"]
	gases = ["", "c", "h"]
	s = ""
	for key in keys:
		for gas in gases:
			s0 = "%s%s"%(key,gas)
			s1 = "%s, "%(params[s0])
			s += s0.ljust(2) + " = " + s1.ljust(8)
		s+="\n"
	for key in ["mu"]:
		s0 = "mu"
		s1 = "%s, "%(params["mu"])
		s += s0.ljust(2) + " = " + s1.ljust(8)
	return s


def get_kwargs(f):
    sig = inspect.signature(f)
    parts = [
        f"{k}={repr(v.default)}" 
        for k, v in sig.parameters.items() 
        if v.default is not inspect.Parameter.empty
    ]
    return ", ".join(parts)


def dicts(s):
	return eval("dict("+s+")")

