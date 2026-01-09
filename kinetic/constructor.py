

from kinetic.system import wall, species, system
from kinetic import ics

from types import SimpleNamespace
import copy

def hotcold(params):

	defaults = dict(
		## live
		dt=0.01,
		rate=100,
		## wall
		mu=0.9,
		## balls
		N =500, m =1  , r =.01, g =1,
		Nh=200, mh=100, rh=.02, gh=0,
		Nc=200, mc=100, rc=.02, gc=0,
		## bounds
		b0=dict(b=0, t=100, l=0  , r=1  ),
		bh=dict(b=0, t=1  , l=1  , r=1.5),
		bc=dict(b=0, t=1  , l=-.5, r=0  ),
		## ics
		ic  = lambda gas:  ics.random(gas, xx=(0,.5) , yy=(1,2), v=2 ),
		ich = lambda gas:  ics.random(gas, xx=(1,1.5), yy=(0,1), v=4 ),
		icc = lambda gas:  ics.random(gas, xx=(-.5,0), yy=(0,1), v=.1),
		## sty
		s0=dict(color="black"),
		sh=dict(color="red"),
		sc=dict(color="blue"),
		)

	defaults.update(params)
	p = SimpleNamespace(**defaults)

	sys = system(p.dt,p.rate)

	main = species(N=p.N,  m=p.m,  r0=p.r,  g=p.g,  walls=dict(p.b0), sty=p.s0)
	main.xy, main.vxy = p.ic(main)

	sys.gases = [main]
	sys.walls = []

	if p.Nc>0:
		coldwall = wall(loc=p.bc['r'], mu=p.mu)
		cold = species(N=p.Nc, m=p.mc, r0=p.rc, g=p.gc, walls=dict(p.bc,r=coldwall), sty=p.sc)
		cold.xy, cold.vxy = p.icc(cold)

		sys.walls += [coldwall,]
		sys.gases += [cold,]
		main.walls.update(l=coldwall)

	if p.Nh>0:
		hotwall  = wall(loc=p.bh['l'], mu=p.mu)
		hot  = species(N=p.Nh, m=p.mh, r0=p.rh, g=p.gh, walls=dict(p.bh,l=hotwall), sty=p.sh)
		hot.xy,  hot.vxy  = p.ich(hot)

		sys.walls += [hotwall,]
		sys.gases += [hot,]
		main.walls.update(r=hotwall)

	sys.constructor = hotcold
	sys.constructor_params = params
	sys.init_xy  = [1.*gas.xy  for gas in sys.gases]
	sys.init_vxy = [1.*gas.vxy for gas in sys.gases]

	return sys

