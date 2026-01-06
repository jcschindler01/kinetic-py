
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button, Slider
plt.style.use("classic")

from kinetic.helpers import *
from kinetic.collide import *

class wall:
	def __init__(self, loc, mu=1):
		self.E = 0.0
		self.z = 1.*loc
		self.mu = 1.*mu

class species:

	def __init__(self, N=3, m=1, r0=0, g=0, walls=dict(), sty=dict()):
		self.N  = 1*N
		self.m  = 1.*m
		self.r0 = 1.*r0
		self.g  = 1.*g
		self.sty = dict(c="k", marker="o", ls="none", markeredgewidth=0)
		self.sty.update(sty)
		self.walls = dict(l=0.,r=1.,b=0.,t=100.)
		self.walls.update(walls)
		self.xy  = np.zeros((2, self.N))
		self.vxy = np.zeros((2, self.N))

	def energies(self):
		kin = np.sum(0.5*self.m*self.vxy**2)
		pot = np.sum(self.m*self.g*self.xy[1])
		tot = pot + kin
		return kin, pot, tot

	def free(self,dt):
		self.xy[0] += self.vxy[0]*dt
		self.xy[1] += self.vxy[1]*dt - 0.5*self.g*dt**2
		self.vxy[1] -= self.g*dt

	def wall(self):
		"""
		"""
		## bottom
		if isnum(self.walls["b"]):
			self.vxy[1] = wc0(self.xy[1], self.vxy[1], self.walls["b"], pm=1)
		else:
			self.vxy[1], self.walls["b"].E = wc(self,self.walls["b"],z=1,pm=1)	
		## left
		if isnum(self.walls["l"]):
			self.vxy[0] = wc0(self.xy[0], self.vxy[0], self.walls["l"], pm=1)
		else:
			self.vxy[0], self.walls["l"].E = wc(self,self.walls["l"],z=0,pm=1)
		## right
		if isnum(self.walls["r"]):
			self.vxy[0] = wc0(self.xy[0], self.vxy[0], self.walls["r"], pm=-1)
		else:
			self.vxy[0], self.walls["r"].E = wc(self,self.walls["r"],z=0,pm=-1)
		## top
		if isnum(self.walls["t"]):
			self.vxy[1] = wc0(self.xy[1], self.vxy[1], self.walls["t"], pm=-1)
		else:
			self.vxy[1], self.walls["t"].E = wc(self,self.walls["t"],z=1,pm=-1)

	def collide(self):
		"""
		"""
		COLLIDE(self.xy, self.vxy, self.r0)

	def evolve(self, dt):
		self.free(dt/2)
		self.collide()
		self.wall()
		self.free(dt/2)

	def set_g(self, val):
		self.g = 1.*val

	def E(self):
		kin = np.sum(0.5*self.m*self.vxy**2)
		pot = np.sum(self.m*self.g*self.xy[1])
		tot = pot + kin
		return tot

	def T(self):
		return self.E()/(self.N*alpha(self.g))





class system:

	def __init__(self, dt=0.1, rate=100, dh=5):
		self.n = 0
		self.t = 0.0
		self.dt = 1.*dt
		self.rate = 1.*rate
		self.gases = []
		self.walls = []
		self.dh = 1.*dh
		self.fig = None
		self.ax = None
		self.axes = dict()
		self.slider = None
		self.gdat = None

	def evolve(self):
		for gas in self.gases:
			gas.evolve(self.dt)
		self.t += self.dt
		self.n += 1

	def newfig(self):
		## fig
		plt.ion()
		fig = plt.figure(figsize=(12,10))
		## main axis
		ax = plt.axes([.01,.01,.4,.98])
		b0 = extent(self)
		x0, x1, y0, y1 = b0['l'], b0['r'], b0['b'], b0['t']
		epsx, epsy = .2, .1
		plt.xticks([])
		plt.yticks([])
		plt.xlim(x0-epsx, x1+epsx)
		plt.ylim(y0-epsy, y0-epsy+self.dh)
		plt.ylim(0-.1,5-.1)
		ax.set_aspect(1)
		gdat = []
		rsty0 = dict(ec='0.8', lw=1, fc='none')
		rsty1 = dict(ec='k', lw=1, fc='none')
		for gas in self.gases:
			b = bounds(gas)
			ax.add_patch(Rectangle((b['l'],b['b']),(b['r']-b['l']),(b['t']-b['b']),**rsty0))
			ax.add_patch(Rectangle((b['l'],b0['b']),(b['r']-b['l']),(b0['t']-b0['b']),**rsty1))
			gdat += list(ax.plot(gas.xy[0], gas.xy[1], ms=gms(ax,gas.r0), **gas.sty))
		## controls
		gax = plt.axes([.42,.53,.1,.4])
		self.slider = Slider(
			ax=gax, 
			label=r"Gravity ($g$)", 
			valmin=0, valmax=5, 
			valinit=self.gases[0].g, 
			orientation="vertical",
			initcolor="g"
			)
		## go
		fig.canvas.draw()
		plt.show(block=False)
		self.fig, self.ax, self.gdat = fig, ax, gdat
		self.axes.update(dict(main=ax))
		self.liveprint()

	def update(self):
		self.gases[0].g = 1.*self.slider.val
		self.evolve()
		for i in range(len(self.gases)):
			self.gdat[i].set_data(self.gases[i].xy[0], self.gases[i].xy[1])
			self.gdat[i].set_markersize(gms(self.ax,self.gases[i].r0))
		self.liveprint()
		plt.pause(self.dt/self.rate)

	def live(self):
		self.newfig()
		while plt.fignum_exists(self.fig.number):
			self.update()
		print(flush=True)

	def liveprint(self):
		print("\rn = %8d, t = %8.3f, "%(self.n,self.t), end="")
		print("T = ("+", ".join(["%6.2f"%gas.T() for gas in self.gases])+")", end="", flush=True)
		


