
import numpy as np
from numba import njit
from kinetic.helpers import *

def wc(b,w,z=1,pm=1):
	##
	y, vy, m, y0, wE0, mu = 1.*b.xy[z], 1.*b.vxy[z], 1.*b.m, 1.*w.z, 1.*w.E, 1.*w.mu
	##
	mask = (pm*(y-y0) <= 0)
	##
	if len(y[mask])>0:
		bE0 = 0.5*m*vsq(vy[mask]) if len(y[mask])>0 else 1
		E0 = bE0 + wE0
		bE1, wE1 = mu*E0, (1.-mu)*E0
		##
		vy[mask] = pm * np.sqrt(bE1/bE0) * np.abs(vy[mask])
		BE1 = 0.5*m*vsq(vy[mask])
		##
		return 1.*vy, 1.*wE1
	else:
		return 1.*vy, 1.*wE0

def wc0(y,vy,y0,pm=1):
	mask = (pm*(y-y0) <= 0) & (pm*vy < 0)
	vy[mask] *= -1
	return vy


@njit
def COLLIDE(xy, vxy, r0):
	## loop
	if r0>0.:
		x, y, vx, vy = xy[0], xy[1], vxy[0], vxy[1]
		for i in range(len(x)):
			for j in range(i,len(x)):
				## values
				dx  =  x[j] -  x[i]
				dy  =  y[j] -  y[i]
				dvx = vx[j] - vx[i]
				dvy = vy[j] - vy[i]
				## conditions
				isclose = np.sqrt(dx**2 + dy**2) < 2*r0
				isapproaching = dx*dvx + dy*dvy < 0
				if isclose and isapproaching:
					## relative
					dz = 0.5*( xy[:,j]- xy[:,i])
					dv = 0.5*(vxy[:,j]-vxy[:,i])
					## update
					vxy[:,i] += 2. * (np.dot(dv,dz)/np.dot(dz,dz)) * dz
					vxy[:,j] -= 2. * (np.dot(dv,dz)/np.dot(dz,dz)) * dz
