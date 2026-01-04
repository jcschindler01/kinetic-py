
import kinetic as kin


params = dict(
	##
	dt=0.02,
	mu=0.8, 
	N=500, 
	Nhc=150, 
	r0=0.005, 
	rhc=0.02, 
	g=1, 
	ghc=0, 
	T0=(1,2,4)
	)

sys = kin.hotcold(**params)
sys.live(rate=200)





