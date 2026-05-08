
import numpy as np
from numba import njit
from kinetic.helpers import *



def wc(gas,wall,xy01=0,pm=1):
	"""
	xy01 = 0 for horizontal wall or 1 for vertical wall
	pm = 1 for "ball coord > wall coord" ie bottom or left wall, else -1
	"""
	##
	z, v, Z = 1.*gas.xy[xy01], 1.*gas.vxy[xy01], 1.*wall.loc
	##
	if wall.c==0:
		return wc0(z,v,Z,pm,gas.r0), wall.E
	##
	else:
		mask = np.logical_and(pm*(z-Z)<=gas.r0, pm*v<=0)
		vc = v[mask]
		wall.E += 0.5*gas.m*np.sum(vc**2)
		EC = np.random.exponential(scale=wall.T(), size=len(vc))
		E0 = np.sum(EC)
		if E0 > wall.E:
			EC = EC * wall.E / E0
			E0 = wall.E
		wall.E -= E0
		v[mask] = pm*np.sqrt(2.*EC/gas.m)
		return v, wall.E




def wc0(y,vy,y0,pm=1,r0=0):
	mask = (pm*(y-y0) <= r0) & (pm*vy < 0)
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
				isclose = dx**2 + dy**2 < 4*r0**2
				isapproaching = dx*dvx + dy*dvy < 0
				if isclose and isapproaching:
					## relative
					dz = 0.5*( xy[:,j]- xy[:,i])
					dv = 0.5*(vxy[:,j]-vxy[:,i])
					## update
					vxy[:,i] += 2. * (np.dot(dv,dz)/np.dot(dz,dz)) * dz
					vxy[:,j] -= 2. * (np.dot(dv,dz)/np.dot(dz,dz)) * dz




