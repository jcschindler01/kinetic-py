

import numpy as np
from bokeh.plotting import figure, curdoc, show, save
from bokeh.models import ColumnDataSource
from bokeh.models import Column as CC
from bokeh.models import Row as RR
import bokeh.models as bmod
from bokeh.layouts import layout
from kinetic import hotcold, ics
from kinetic.helpers import *
import threading
import time

#################
## Physics
#################

## define physics
params = dict(
		## live
		dt=0.005,
		rate=1,
		## wall
		mu=0.9,
		## balls
		N =500, m =1  , r =.01, g =1,
		Nh=100, mh=100, rh=.02, gh=0,
		Nc=100, mc=100, rc=.02, gc=0,
		## bounds
		b0=dict(t=99, b=0,   r=1, l=0),
		bh=dict(t=1 , r=1.5, b=0, l=1),
		bc=dict(t=1 , l=-.5, b=0, r=0),
		## ics
		# ic  = lambda gas:  kin.thermal(gas, T=1 ),
		ic  = lambda gas:  ics.random(gas, xx=(0,.5) , yy=(1,2), v=2 ),
		ich = lambda gas:  ics.random(gas, v=4 ),
		icc = lambda gas:  ics.random(gas, v=1 ),
		## sty
		s0=dict(color="black"),
		sh=dict(color="red"),
		sc=dict(color="blue"),
		)

## generate system
sys = hotcold(params)

## buffer variables
lock = threading.Lock()
buff_x = [gas.xy[0] for gas in sys.gases]
buff_y = [gas.xy[1] for gas in sys.gases]


## physics loop
def sys_live(tmax=100):
	global sys
	while sys.t < tmax:
		##
		time.sleep(sys.dt/sys.rate)
		if not sys.paused:
			# sys.liveprint()
			sys.evolve()
			##
			with lock:
				for i in range(len(sys.gases)):
					np.copyto(buff_x[i], sys.gases[i].xy[0])
					np.copyto(buff_y[i], sys.gases[i].xy[1])
	print(flush=True)

## start thread
golive = threading.Thread(target=sys_live, daemon=True)
golive.start()

## uncomment to force thread to finish
# golive.join()

#################
#################




#################
## Plotting
#################

## bokeh doc
doc = curdoc()

## data sources
gasdata = [ColumnDataSource(dict(x=buff_x[i],y=buff_y[i])) for i in range(len(sys.gases))]

## main plot
main = figure(
	frame_width = 300,
	frame_height = 500,
	output_backend = "webgl",
	toolbar_location = "left",
	tools = [
		bmod.PanTool(),
		bmod.BoxZoomTool(match_aspect=True),
		bmod.WheelZoomTool(modifiers="ctrl", maintain_focus=False),
		bmod.UndoTool(),
		bmod.RedoTool(),
		bmod.ResetTool(),
		]
	)

main.axis.visible = False
main.grid.visible = False
main.toolbar.logo = None

main.x_range = bmod.Range1d(-.7, 1.7)
main.y_range.start = -.1
main.y_range.end = main.y_range.start + (main.x_range.end - main.x_range.start)*(main.frame_height/main.frame_width)
main.y_range.bounds = (-1, 101)


for i in range(len(sys.gases)):
	main.circle(source=gasdata[i], radius=sys.gases[i].r0, **sys.gases[i].sty)
main.line([0,0,1,1,0],[100,0,0,100,100],color="black")
main.line([-1.5])

## controls
pause = bmod.Button(label="Play/Pause")
pause.on_click(sys.pause)

reset = bmod.Button(label="Reset")
def resethandler():
	global sys
	sys.reset()
	refresh()
reset.on_click(resethandler)

rateval = bmod.Slider(start=-2, end=2, value=np.log10(sys.rate), step=.01, title="Rate")
ratehandler = lambda attr, old, new: sys.set_rate(10.**new)
rateval.on_change("value", ratehandler)
rateval.format = bmod.CustomJSTickFormatter(code="return Math.pow(10, tick).toFixed(2);")

dtval = bmod.Slider(start=np.log10(.001), end=np.log10(.05), value=np.log10(sys.dt), step=.01, title="dt")
dthandler = lambda attr, old, new: sys.set_dt(10.**new)
dtval.on_change("value", dthandler)
dtval.format = bmod.CustomJSTickFormatter(code="return Math.pow(10, tick).toFixed(3);")

gval = bmod.Slider(start=10, end=0, value=sys.gases[0].g, step=.01,	title="Gravity (g)", 
	orientation="vertical", height=300, width=50, height_policy="fixed", width_policy="fixed")
ghandler = lambda attr, old, new: sys.gases[0].set_g(new)
gval.on_change("value", ghandler)

## layouts
controls = RR(CC(RR(pause,reset), rateval, dtval))

## add roots
doc.add_root(RR(main,controls))

## update loop
def update():
	global sys
	if not sys.paused:
		with lock:
			for i in range(len(sys.gases)):
				gasdata[i].data = dict(x=buff_x[i], y=buff_y[i])

## refresh
def refresh():
	global sys
	with lock:
		for i in range(len(sys.gases)):
			np.copyto(buff_x[i], sys.gases[i].xy[0])
			np.copyto(buff_y[i], sys.gases[i].xy[1])
			gasdata[i].data = dict(x=buff_x[i], y=buff_y[i])

## schedule callback
fps = 60
doc.add_periodic_callback(update, 1000/fps)

## save
save(main)

#################
#################






