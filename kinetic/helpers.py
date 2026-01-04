
"""
Back and forth.
	xy  = np.stack([x,y])
	x,y = xy[0], xy[1].
Initialize.
	xy = np.zeros((2,N))
"""

import numpy as np

zrand = lambda N: np.random.random((2,N))
rms = lambda vxy: np.sqrt(np.sum(vxy**2))
rmsnorm = lambda vxy: vxy/rms(vxy)
vrand = lambda N: rmsnorm(zrand(N) - 0.5)

vsq = lambda v: np.sum(v**2)

quivstyle = dict(color='0.5', pivot='tip', headlength=0, headwidth=0, headaxislength=0)


isnum = lambda x: type(x) in [float,int]


alpha = lambda g,d=2: d/2.+1. if 1.*g>0. else d/2. 


