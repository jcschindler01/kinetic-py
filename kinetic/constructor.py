

from kinetic.system import wall, species, system
from kinetic import ics

def hotcold(dt=0.01, mu=0.99, N=100, Nhc=50, r0=0.005, rhc=0.02, g=1, ghc=0, T0=(1,2,4)):

	sys = system(dt)

	hotwall = wall(loc=1, mu=mu)
	coldwall = wall(loc=0, mu=mu)

	main = species(N=N, m=1, r0=r0, g=g, walls=dict(b=0,t=100,l=coldwall,r=hotwall))
	hot = species(N=Nhc, m=100, r0=rhc, g=ghc, walls=dict(b=0,t=1,l=hotwall, r=1.5), sty=dict(c='r',ms=6))
	cold = species(N=Nhc, m=100, r0=rhc, g=ghc, walls=dict(b=0,t=1,l=-0.5, r=coldwall), sty=dict(c='b',ms=6))

	main.ic(ics.random,args=dict(xx=(0,.5),yy=(1,2), v=2))
	hot.ic(ics.random,args=dict(xx=(1,1.5),yy=(0,1),v=4))
	cold.ic(ics.random,args=dict(xx=(-.5,0),yy=(0,1),v=.1))

	sys.walls = [hotwall,coldwall]
	sys.gases = [cold, main, hot]

	return sys




