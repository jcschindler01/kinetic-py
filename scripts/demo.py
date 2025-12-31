
import kinetic as kin
import kinetic.ics as ics

##
sys = kin.system(dt=0.01)

hotwall = kin.wall(loc=1, mu=.99)
coldwall = kin.wall(loc=0, mu=.99)

main = kin.species(N=1000, m=1, r0=.005, g=1, walls=dict(b=0,t=10,l=coldwall,r=hotwall))
hot = kin.species(N=300, m=100, r0=.02, g=0, walls=dict(b=0,t=1,l=hotwall, r=1.5), sty=dict(c='r',ms=6))
cold = kin.species(N=300, m=100, r0=.02, g=0, walls=dict(b=0,t=1,l=-0.5, r=coldwall), sty=dict(c='b',ms=6))

main.ic(ics.random,args=dict(xx=(0,.5),yy=(1,2), v=2))
hot.ic(ics.random,args=dict(xx=(1,1.5),yy=(0,1),v=10))
cold.ic(ics.random,args=dict(xx=(-.5,0),yy=(0,1),v=.1))

sys.walls = [hotwall,coldwall]
sys.gases = [main, hot, cold]

sys.newfig()

while True:
	sys.update(rate=2)







