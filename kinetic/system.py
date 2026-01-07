
import time
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
# mpl.use("QtAgg")
mpl.use("TkAgg")
plt.style.use("classic")

# from matplotlib.patches import Rectangle
from matplotlib.widgets import Button, Slider


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

	def evolve(self):
		for gas in self.gases:
			gas.evolve(self.dt)
		self.t += self.dt
		self.n += 1

	def newfig(self):
		## main fig
		plt.ion()
		self.fig = plt.figure(num="Thermodynamics", figsize=(12,10))
		plt.get_current_fig_manager().window.wm_geometry("700x900+50+50")
		## main axis
		self.ax = plt.axes([0.01, 0.01, 0.99-.01, 0.99-.01])
		self.ax.set_xticks([])
		self.ax.set_yticks([])
		self.ax.set_xlim(-0.7, 1.7)
		self.ax.set_ylim(0-.1, 5)
		self.ax.set_aspect(1, adjustable="box")
		for gas in self.gases:
			self.gdat += list(self.ax.plot(gas.xy[0], gas.xy[1], ms=gms(self.ax,gas.r0), **gas.sty))
		## for testing
		self.tmax = np.inf
		self.controls=True
		print("controls = %s, tmax=%s"%(self.controls, self.tmax))
		## control fig
		if self.controls:
			self.cfig = plt.figure(num="Controls", figsize=(4,3))
			plt.get_current_fig_manager().window.wm_geometry("500x400+800+50")
			self.gslider = Slider(
				ax=plt.axes([.1, .1, .2-.1, .9-.1]), 
				label=r"Gravity ($g$)", 
				valmin=0, valmax=5, 
				valinit=self.gases[0].g, 
				orientation="vertical",
				initcolor="g"
				)
			self.rateslider = Slider(
				ax=plt.axes([.35,.4,.5,.1]), 
				label=r"Rate", 
				valmin=-2, valmax=2, 
				valinit=np.log10(self.rate),
				orientation="horizontal",
				initcolor="g",
				)
			self.dtslider = Slider(
				ax=plt.axes([.35,.3,.5,.1]), 
				label=r"dt", 
				valmin=0.001, valmax=0.1, 
				valinit=self.dt,
				orientation="horizontal",
				initcolor="g",
				)
			self.yzslider = Slider(
				ax=plt.axes([.35,.2,.5,.1]), 
				label=r"yzoom", 
				valmin=.1, valmax=50, 
				valinit=self.ax.get_ylim()[1],
				orientation="horizontal",
				initcolor="g",
				)
			self.yzslider.on_changed(self.set_yzoom)
			self.pausebutton = Button(
				ax=plt.axes([.3,.6,.3,.2]),
				label="Play/Pause"
				)
			self.pausebutton.on_clicked(self.toggle_paused)
			self.resetbutton = Button(
				ax=plt.axes([.65,.6,.3,.2]),
				label="Reset"
				)
			self.resetbutton.on_clicked(self.reset)
		## go
		plt.show(block=False)
		# self.liveprint()

	def toggle_paused(self,event):
		self.paused = not self.paused

	def set_yzoom(self,val):
		self.ax.set_ylim(top=val)

	def reset(self,event):
		fresh = self.constructor(self.constructor_params)
		self.gases = fresh.gases
		self.walls = fresh.walls
		for i in range(len(self.gases)):
			self.gdat[i].set_data(self.gases[i].xy[0], self.gases[i].xy[1])
			self.gdat[i].set_markersize(gms(self.ax,self.gases[i].r0))
		self.liveprint()

	def update(self):
		if self.controls:
			self.gases[0].g = 1.*self.gslider.val
			self.rate = 10.**self.rateslider.val
			self.dt = 1.*self.dtslider.val
		self.evolve()
		for i in range(len(self.gases)):
			self.gdat[i].set_data(self.gases[i].xy[0], self.gases[i].xy[1])
			self.gdat[i].set_markersize(gms(self.ax,self.gases[i].r0))
		self.liveprint()
		plt.pause(self.dt/self.rate)

	def live(self):
		tic = time.time()
		self.newfig()
		toc = time.time()
		print("Newfig time %.1fs"%(toc-tic), flush=True)
		tic = time.time()
		while (plt.fignum_exists(self.fig.number) and self.t<self.tmax):
			if not self.paused:
				self.update()
			if self.paused:
				plt.pause(self.dt/self.rate)
		print(flush=True)
		toc = time.time()
		print("Animation time %.1fs"%(toc-tic))

	def liveprint(self):
		print("\rn = %8d, t = %8.3f, "%(self.n,self.t), end="")
		print("T = ("+", ".join(["%6.2f"%gas.T() for gas in self.gases])+")", end="", flush=True)
		


