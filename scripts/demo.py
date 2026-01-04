
import kinetic as kin


params = dict(
	##
	dt=0.01,
	mu=0.8, 
	N=500, 
	Nhc=50, 
	r0=0.02, 
	rhc=0.05, 
	g=1, 
	ghc=0, 
	T0=(1,2,4)
	)

sys = kin.hotcold(**params)
sys.live(rate=2)





