
import time

tic = time.time()

import kinetic as kin
import matplotlib


params = dict(
		## live
		dt=0.05,
		rate=2,
		## wall
		mu=0.9,
		## balls
		N =1000, m =1  , r =.01, g =1,
		Nh=200, mh=100, rh=.02, gh=0,
		Nc=200, mc=100, rc=.02, gc=0,
		## bounds
		b0=dict(t=99, b=0,   r=1, l=0),
		bh=dict(t=1 , r=1.5, b=0, l=1),
		bc=dict(t=1 , l=-.5, b=0, r=0),
		## ics
		# ic  = lambda gas:  kin.thermal(gas, T=1 ),
		ic  = lambda gas:  kin.random(gas, xx=(0,.5) , yy=(1,2), v=2 ),
		ich = lambda gas:  kin.random(gas, v=4 ),
		icc = lambda gas:  kin.random(gas, v=1 ),
		)

sys = kin.hotcold(params)
sys.live()

toc = time.time()

print("Finished in %.1fs"%(toc-tic))
