
import numpy as np
from numba import njit
from kinetic.helpers import *



def wc(gas,wall,xy01=0,pm=1):
	"""
	xy01 = 0 for horizontal wall or 1 for vertical wall
	pm = 1 for "ball coord > wall coord" ie bottom or left wall, else -1
	"""
	##
	z, v, m, Z, V, M = 1.*gas.xy[xy01], 1.*gas.vxy[xy01], 1.*gas.m, 1.*wall.loc, 1.*wall.v, 1.*wall.M
	##
	gas.vxy[xy01], wall.V = WALLBOUNCE(m,v,z,M,V,Z,pm)

@njit
def WALLBOUNCE(m,v,z,M,V,Z,pm):
	for i in range(len(v)):
		if pm*(z[i]-Z)<=0 and pm*(v[i]-V)<0:
			V1   = v[i]*(2*m)/(m+M) + V*(M-m)/(m+M)
			v[i] = v[i]*(m-M)/(m+M) + V*(2*M)/(m+M)
			V    = V1
	return v, V



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
				isclose = dx**2 + dy**2 < 4*r0**2
				isapproaching = dx*dvx + dy*dvy < 0
				if isclose and isapproaching:
					## relative
					dz = 0.5*( xy[:,j]- xy[:,i])
					dv = 0.5*(vxy[:,j]-vxy[:,i])
					## update
					vxy[:,i] += 2. * (np.dot(dv,dz)/np.dot(dz,dz)) * dz
					vxy[:,j] -= 2. * (np.dot(dv,dz)/np.dot(dz,dz)) * dz




