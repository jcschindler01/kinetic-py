
import kinetic as kin


params = dict(
	##
	dt=0.01,
	mu=0.99, 
	N=100, 
	Nhc=10, 
	r0=0.005, 
	rhc=0.02, 
	g=1, 
	ghc=0, 
	T0=(1,2,4)
	)

sys = kin.hotcold(**params)
sys.live(rate=200)





