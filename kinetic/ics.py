
import numpy as np

from kinetic.helpers import *

def random(gas, xx=None, yy=None, v=1):
	if xx==None:
		xx = (bounds(gas)['l'], bounds(gas)['r'])
	if yy==None:
		yy = (bounds(gas)['b'], bounds(gas)['t'])
	x = xx[0] + (xx[1]-xx[0])*np.random.random(gas.N)
	y = yy[0] + (yy[1]-yy[0])*np.random.random(gas.N)
	return np.stack([x,y]), v*vrand(gas.N)

def thermal(gas, T=1):
	b = bounds(gas)
	x0, x1, y0, y1 = b["l"], b["r"], b["b"], b["t"]
	x = x0 + (x1-x0)*np.random.random(gas.N)
	if gas.g==0:
		y = y0 + (y1-y0)*np.random.random(gas.N)
	if gas.g>0:
		y = rng.exponential(scale=1.*T/(gas.m*gas.g), size=gas.N)
		y = np.clip(y, y0, y1)
	vx = rng.normal(scale=np.sqrt(1.*T/gas.m), size=gas.N)
	vy = rng.normal(scale=np.sqrt(1.*T/gas.m), size=gas.N)
	return np.stack([x,y]), np.stack([vx,vy])

def constE(gas, E=1):
	b = bounds(gas)
	x0, x1, y0, y1 = b["l"], b["r"], b["b"], b["t"]
	x = x0 + (x1-x0)*np.random.random(gas.N)
	pot = E*np.random.random(gas.N)
	if gas.g==0:
		y = y0 + (y1-y0)*np.random.random(gas.N)
		pot *= 0.
	if gas.g>0:
		y = pot/(gas.m*gas.g)
	kin = E-pot
	v = np.sqrt(2.*kin/gas.m)
	theta = np.random.random(gas.N)
	vx = np.cos(2.*np.pi*theta)*v
	vy = np.sin(2.*np.pi*theta)*v
	return np.stack([x,y]), np.stack([vx,vy])


ICX = dict(Thermal=thermal, Random=random, ConstE=constE)

def IC_kwargs(ic):
	if isinstance(ic,str):
		ic = ICX[ic]
	s = "\n".join([label + get_kwargs(ic) for label in ["0: ", "c: ", "h: "]])
	return s

def IC_get(ic, s):
	##
	s = [ss[2:].strip() for ss in s.split("\n")]
	args = [dicts(ss) for ss in s]
	if isinstance(ic,str):
		ic = ICX[ic]
	##
	IC = dict(
		ic   = lambda gas:  ic(gas, **args[0]),
		icc  = lambda gas:  ic(gas, **args[1]),
		ich  = lambda gas:  ic(gas, **args[2]),
		)
	return IC


if __name__=="__main__":
	IC_get("Thermal", "")