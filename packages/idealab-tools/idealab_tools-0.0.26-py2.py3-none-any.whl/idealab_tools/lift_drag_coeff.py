# -*- coding: utf-8 -*-
"""
Created on Sun Jun  9 17:07:48 2019

@author: danaukes
"""

from math import pi, sin,cos,atan2
import matplotlib.pyplot as plt
import numpy

v = 1

def find_cdcl(t):
    vcx = v*cos(t*pi/180)
    vcy = v*sin(t*pi/180)
    
    angle_of_attack = -atan2(vcy,vcx)
    
    cd = 2*sin(angle_of_attack)**2
    cl = 2*cos(angle_of_attack)*sin(angle_of_attack)
    
    return cd,cl

thetas =  numpy.r_[-20:140:5]
cdcl = [find_cdcl(t) for t in thetas]
cdcl = numpy.array(cdcl)

plt.figure()
plt.plot(thetas,cdcl[:,0])

plt.figure()
plt.plot(thetas,cdcl[:,1])
