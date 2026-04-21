
import numpy as np
import threading
import time

from bokeh.plotting import figure, curdoc, show, save
from bokeh.models import ColumnDataSource
from bokeh.models import Column as CC
from bokeh.models import Row as RR
import bokeh.models as mod
from bokeh.layouts import layout

from kinetic import hotcold, ics
from kinetic.helpers import *


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
		Nh=50, mh=100, rh=.02, gh=0,
		Nc=50, mc=100, rc=.02, gc=0,
		## bounds
		b0=dict(t=99, b=0,   r=1, l=0),
		bh=dict(t=1 , r=1.5, b=0, l=1),
		bc=dict(t=1 , l=-.5, b=0, r=0),
		## ics
		ic  = lambda gas:  ics.random(gas, v=2, lr=(0,.5) , bt=(1,2)),
		ich = lambda gas:  ics.random(gas,  v=4 ),
		icc = lambda gas:  ics.random(gas,  v=1 ),
		## sty
		s0=dict(color="black"),
		sh=dict(color="red"),
		sc=dict(color="blue"),
		)

## generate system
sys = hotcold(params)

## buffer variables
lock = threading.Lock()
buff_t = 1.*sys.t
buff_x = [np.array(gas.xy[0], dtype='float64', order='C') for gas in sys.gases]
buff_y = [np.array(gas.xy[1], dtype='float64', order='C') for gas in sys.gases]
buff_E = [gas.E() for gas in sys.gases]
buff_T = [gas.T() for gas in sys.gases]
buff_S = [gas.dS() for gas in sys.gases]
buff_go = 1

## physics loop
def sys_live(tmax=1000):
	global buff_t
	while sys.t < tmax:
		time.sleep(sys.dt/sys.rate)
		if not sys.paused:
			# sys.liveprint()
			sys.evolve()
			t  = 1.*sys.t
			E = [gas.E() for gas in sys.gases]
			T = [gas.T() for gas in sys.gases]
			S = [gas.dS() for gas in sys.gases]
			with lock:
				if buff_go==1:
					buff_t = 1.*sys.t
					for i in range(len(sys.gases)):
						np.copyto(buff_x[i], sys.gases[i].xy[0])
						np.copyto(buff_y[i], sys.gases[i].xy[1])
						buff_t = 1.*t
						buff_E[i] = 1.*E[i]
						buff_T[i] = 1.*T[i]
						buff_S[i] = 1.*S[i]
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
streamdata = ColumnDataSource(dict(
	t  = [buff_t],
	E  = [buff_E[0]], 
	Ec = [buff_E[1]], 
	Eh = [buff_E[2]],
	T  = [buff_T[0]], 
	Tc = [buff_T[1]], 
	Th = [buff_T[2]],
	S  = [buff_S[0]], 
	Sc = [buff_S[1]], 
	Sh = [buff_S[2]],
	St = [np.nansum(buff_S)],
	))

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

dots = [main.circle(source=gasdata[i], radius=sys.gases[i].r0, **sys.gases[i].sty) for i in range(len(sys.gases))]

## plots
maxent = figure(
	title = "MaxEnt",
	frame_width = 200,
	frame_height = 100,
	output_backend = "canvas",
	toolbar_location = None,
	)
maxent.xaxis.visible = False
maxent.line(x="t", y="S" , source=streamdata, color="green")
maxent.line(x="t", y="Sc", source=streamdata, color="blue")
maxent.line(x="t", y="Sh", source=streamdata, color="red")
maxent.line(x="t", y="St", source=streamdata, color="black")
maxent.y_range.min_interval = 100

temperature = figure(
	title = "Temperature",
	frame_width = 200,
	frame_height = 100,
	output_backend = "canvas",
	toolbar_location = None,
	)
temperature.xaxis.visible = False
temperature.line(x="t", y="T" , source=streamdata, color="green")
temperature.line(x="t", y="Tc", source=streamdata, color="blue")
temperature.line(x="t", y="Th", source=streamdata, color="red")
temperature.y_range.min_interval = 1

energy = figure(
	title = "Total Energy",
	frame_width = 200,
	frame_height = 100,
	output_backend = "canvas",
	toolbar_location = None,
	)
energy.xaxis.visible = False
energy.line(x="t", y="E" , source=streamdata, color="green")
energy.line(x="t", y="Ec", source=streamdata, color="blue")
energy.line(x="t", y="Eh", source=streamdata, color="red")
energy.y_range.min_interval = 5

for p in [maxent, temperature, energy]:
    p.min_border_left = 60
    p.min_border_right = 20
    p.lod_threshold = 1000

## controls
pause = mod.Button(label="Play/Pause")
def pausehandler():
	global sys
	sys.pause()
pause.on_click(pausehandler)

reset = mod.Button(label="Reset")
def resethandler():
	with lock:
		buff_go = 0
	global ispaused
	ispaused = sys.paused
	sys.paused = True
	clearstream()
	doc.add_next_tick_callback(clearstream)
	sys.reset()
	doc.add_next_tick_callback(refresher)
reset.on_click(resethandler)

checkboxes = mod.CheckboxGroup(labels=["Lock Aspect", "Regen Rate"], active=[0], align="end")
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

regentext = CC(mod.Spacer(height=5), mod.Div(text="<b>Regenerate:</b>", height=10))

paramstyle = mod.InlineStyleSheet(css="""
.bk-input {
    font-family: "Courier New", monospace !important;
    padding: 2px 2px;
    white-space: nowrap;
}
""")
paraminputs = mod.TextAreaInput(title="params = ", value=param_inputs(params), rows=7, cols=44, stylesheets=[paramstyle])

regen = mod.Button(label="Regenerate")

def regenhandler():
	global sys, buff_go, buff_x, buff_y, ispaused
	with lock:
		buff_go = 0
	ispaused = sys.paused
	sys.paused = True
	clearstream()
	doc.add_next_tick_callback(clearstream)
	IC = ICbuttons.labels[ICbuttons.active]
	params.update(dicts(paraminputs.value))
	params.update(ics.IC_get(IC, s=ICparams.value))
	with lock:
		sys = hotcold(params)
		sys.paused = True
		buff_x = [np.array(gas.xy[0], dtype='float64', order='C') for gas in sys.gases]
		buff_y = [np.array(gas.xy[1], dtype='float64', order='C') for gas in sys.gases]
	doc.add_next_tick_callback(refresher)
regen.on_click(regenhandler)

ICbuttons = mod.RadioGroup(labels=["Default", "Random", "Thermal", "ConstE"], active=0)
currentICtext = [ics.IC_kwargs(label) for label in ICbuttons.labels]
ICparams  = mod.TextAreaInput(value=currentICtext[ICbuttons.active], rows=4, cols=35, stylesheets=[paramstyle])
ICoptions = RR(ICbuttons, ICparams)
def ICtexthandler(attr, old, new):
	currentICtext[ICbuttons.active] = new
def ICbuttonhandler(attr, old, new):
	ICparams.value = currentICtext[ICbuttons.active]
ICparams.on_change("value", ICtexthandler)
ICbuttons.on_change("active", ICbuttonhandler)

## clearstream
def clearstream():
	streamdata.data = {k: [np.nan] for k in streamdata.data.keys()}
	streamdata.data = {k: [] for k in streamdata.data.keys()}
	for i in range(len(gasdata)):
		gasdata[i].data = dict(x=[],y=[])

## refresher
def refresher(ticks=0):
	doc.add_next_tick_callback(refresh)

## refresh
def refresh():
	global buff_go, buff_t
	with lock:
		for i in range(len(sys.gases)):
			np.copyto(buff_x[i], sys.gases[i].xy[0])
			np.copyto(buff_y[i], sys.gases[i].xy[1])
			buff_t = sys.t
			buff_E[i] = sys.gases[i].E()
			buff_T[i] = sys.gases[i].T()
			buff_S[i] = sys.gases[i].dS()
	for i in range(len(sys.gases)):
		dots[i].glyph.radius = sys.gases[i].r0
	if 1 not in checkboxes.active:
		sys.set_rate(10.**rateval.value)
		sys.set_dt(10.**dtval.value)
		sys.gases[0].set_g(gmax - gval.value)
	rateval.value = np.log10(sys.rate)
	dtval.value = np.log10(sys.dt)
	gval.value = gsliderval(sys.gases[0].g)
	with lock:
		for i in range(len(sys.gases)):
			gasdata[i].data = dict(x=buff_x[i], y=buff_y[i])
		buff_go = 1
	sys.paused = ispaused

## update loop
frame = 0
skip = 6
def update():
	global frame
	if not sys.paused:
		with lock:
			if buff_go==1:
				for i in range(len(sys.gases)):
					gasdata[i].data = dict(x=buff_x[i], y=buff_y[i])
				if frame%skip==0:
					streamdata.stream(
						dict(
							t = [buff_t], 
							E = [buff_E[0]], Ec = [buff_E[1]], Eh = [buff_E[2]],
							T = [buff_T[0]], Tc = [buff_T[1]], Th = [buff_T[2]],
							S = [buff_S[0]], Sc = [buff_S[1]], Sh = [buff_S[2]],
							St = [np.nansum(buff_S)],
						),
					rollover=500)
				frame += 1

## layouts
controls = RR(gval, CC(RR(pause,reset,regen,checkboxes), rateval, dtval, yzoom, paraminputs, ICoptions))
plots = CC(maxent,temperature,energy)
# plots = CC()

## add roots
doc.add_root(RR(main,plots,controls))

## schedule callback
fps = 60
doc.add_periodic_callback(update, 1000/fps)

## save
save(doc)

#################
#################






