

import numpy as np
from bokeh.plotting import figure, curdoc, show, save
from bokeh.models import ColumnDataSource
from bokeh.models import Column as CC
from bokeh.models import Row as RR
import bokeh.models as mod
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
		time.sleep(sys.dt/sys.rate)
		if not sys.paused:
			# sys.liveprint()
			sys.evolve()
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
		mod.PanTool(),
		mod.BoxZoomTool(match_aspect=True),
		mod.WheelZoomTool(modifiers="ctrl", maintain_focus=False),
		mod.UndoTool(),
		mod.RedoTool(),
		mod.ResetTool(),
		]
	)

main.axis.visible = False
main.grid.visible = False
main.toolbar.logo = None

edges = extent(sys)
center = (edges['r'] + edges['l'])/2
xpad = .2
main.x_range = mod.Range1d(edges['l']-xpad, edges['r']+xpad)
main.y_range = mod.Range1d(0,1)
main.y_range.start = -.1
main.y_range.end = main.y_range.start + (main.x_range.end - main.x_range.start)*(main.frame_height/main.frame_width)
main.y_range.bounds = (-1, edges['t']+5)
xperim = np.array([0,0,1,1,0])
yperim = np.array([1,0,0,1,1])*edges['t']
main.line(xperim, yperim, color="black")

for i in range(len(sys.gases)):
	main.circle(source=gasdata[i], radius=sys.gases[i].r0, **sys.gases[i].sty)

## controls
pause = mod.Button(label="Play/Pause")
pause.on_click(sys.pause)

reset = mod.Button(label="Reset")
def resethandler():
	global sys
	sys.reset()
	refresh()
reset.on_click(resethandler)

checkboxes = mod.CheckboxGroup(labels=["Lock Aspect"], active=[0], align="end")
def checkhandler(attr, old, new): 
	if 0 in new: 
		lock_aspect()
checkboxes.on_change("active", checkhandler)

gmin, gmax = 0, 5
gvalstyle = mod.InlineStyleSheet( # fixes broken Bokeh vertical slider
	css="""
	.bk-slider { width: 50px; }
	.noUi-vertical .noUi-origin { top: 0%; }
	.noUi-base .noUi-connects { height: 200px; }
	.noUi-target.noUi-vertical { margin: 10px 0px 0px 25px; }
	"""
	)
gsliderval = lambda g: gmax - g
gval = mod.Slider(start=gmin, end=gmax, value=gsliderval(sys.gases[0].g), step=.01, title="Gravity (g)", 
	orientation="vertical", stylesheets=[gvalstyle], width=90)
ghandler = lambda attr, old, new: sys.gases[0].set_g(gmax - new)
gval.on_change("value", ghandler)
gval_format_codestring = "return (%s - tick).toFixed(2)"%(gmax)
gval.format = mod.CustomJSTickFormatter(code=gval_format_codestring)

rateval = mod.Slider(start=-2, end=2, value=np.log10(sys.rate), step=.01, title="Rate")
ratehandler = lambda attr, old, new: sys.set_rate(10.**new)
rateval.on_change("value", ratehandler)
rateval.format = mod.CustomJSTickFormatter(code="return Math.pow(10, tick).toFixed(2);")

dtval = mod.Slider(start=np.log10(.001), end=np.log10(.05), value=np.log10(sys.dt), step=.01, title="dt")
dthandler = lambda attr, old, new: sys.set_dt(10.**new)
dtval.on_change("value", dthandler)
dtval.format = mod.CustomJSTickFormatter(code="return Math.pow(10, tick).toFixed(3);")

yzoom = mod.Slider(start=.1, end=edges['t']+5, value=1.*main.y_range.end, step=.01, title="yzoom")
def lock_aspect():
		width = (main.y_range.end - main.y_range.start)*(main.frame_width/main.frame_height)
		main.x_range.start, main.x_range.end = center-width/2, center+width/2
def yzoomhandler(attr, old, new):
	main.y_range.end = 1.*new
	if 0 in checkboxes.active:
		lock_aspect()
yzoom.on_change("value", yzoomhandler)



## layouts
controls = RR(gval, CC(RR(pause,reset,checkboxes), rateval, dtval, yzoom))

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
	gval.value = gsliderval(sys.gases[0].g)

## schedule callback
fps = 60
doc.add_periodic_callback(update, 1000/fps)

## save
save(doc)

#################
#################






