
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
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
		self.sty = dict(c="k", marker="o", ms=4, ls="none", markeredgewidth=0)
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


	def ic(self, IC, args):
		self.xy, self.vxy = IC(self.N, **args)

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

	def E(self):
		kin = np.sum(0.5*self.m*self.vxy**2)
		pot = np.sum(self.m*self.g*self.xy[1])
		tot = pot + kin
		return tot

	def T(self):
		return self.E()/(self.N*alpha(self.g))




class system:

	def __init__(self, dt=0.1):
		self.n = 0
		self.t = 0.0
		self.dt = 1.*dt
		self.gases = []
		self.walls = []
		self.fig = None
		self.ax = None
		self.gdat = None

	def evolve(self):
		for gas in self.gases:
			gas.evolve(self.dt)
			self.t += self.dt
			self.n += 1

	def newfig(self):
		plt.ion()
		fig = plt.figure(figsize=(10,8))
		ax = plt.axes([0,0,.6,1])
		plt.xticks([])
		plt.yticks([])
		plt.xlim(-1,2)
		plt.ylim(-.1,2.9)
		ax.set_aspect(1)
		gdat = []
		plt.plot([0,0,1,1],[4,0,0,4], 'k-')
		plt.plot([1,1,1.5,1.5,1.5],[1,0,0,1,4], 'k-')		
		plt.plot([0,0,-.5,-.5,-.5],[1,0,0,1,4], 'k-')		
		for gas in self.gases:
			gdat += list(ax.plot(gas.xy[0], gas.xy[1], **gas.sty))
		plt.show(block=False)
		self.fig, self.ax, self.gdat = fig, ax, gdat

	def update(self, rate=1):
		self.evolve()
		for i in range(len(self.gases)):
			self.gdat[i].set_data(self.gases[i].xy[0], self.gases[i].xy[1])
		print("\rn = %8d, t = %8.3f, T = (%6.2f, %6.2f, %6.2f)"%(self.n,self.t,self.gases[0].T(),self.gases[1].T(),self.gases[2].T()), end="", flush=True)
		plt.pause(self.dt/rate)

	def live(self,rate=100):
		self.newfig()
		while plt.fignum_exists(self.fig.number):
			self.update(rate)
		print(flush=True)



