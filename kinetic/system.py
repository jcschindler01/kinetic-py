
import time, copy
import numpy as np

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
		self.sty = dict()
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

	def __init__(self, dt=0.1, rate=100):
		self.n = 0
		self.t = 0.0
		self.dt = 1.*dt
		self.rate = 1.*rate
		self.gases = []
		self.walls = []
		self.gdat = []
		##
		self.paused = False

	def pause(self):
		self.paused = not self.paused

	def reset(self):
		fresh = self.constructor(self.constructor_params)
		self.gases = fresh.gases
		self.walls = fresh.walls

	def set_rate(self, rate):
		self.rate = 1.*rate

	def set_dt(self, dt):
		self.dt = 1.*dt

	def evolve(self):
		for gas in self.gases:
			gas.evolve(self.dt)
		self.t += self.dt
		self.n += 1

	def liveprint(self):
		print("\rn = %8d, t = %8.3f, "%(self.n,self.t), end="")
		print("T = ("+", ".join(["%6.2f"%gas.T() for gas in self.gases])+")", end="", flush=True)
		


