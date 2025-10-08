# -*- coding: utf-8 -*-
"""
copyright 2016-2017 Dan Aukes
"""

def equal_axes(ax, out):
    out_max = out.max(0)
    out_min = out.min(0)
    out_mid = (out_max+out_min)/2
    max_range = (out_max-out_min).max()/2

    ax.set_xlim(out_mid[0] - max_range, out_mid[0] + max_range)
    ax.set_ylim(out_mid[1] - max_range, out_mid[1] + max_range)
    ax.set_zlim(out_mid[2] - max_range, out_mid[2] + max_range)


def equal_axes2(ax,out):
    import numpy
#    out = numpy.array([x,y,z])
    
    if out.shape.index(3)==0:
        out = out.T
    
    out_max = out.max(0)
    out_min = out.min(0)
    out_mid = (out_max+out_min)/2
    max_range = (out_max-out_min).max()/2
    
    xmin = out_mid[0] - max_range
    ymin = out_mid[1] - max_range
    zmin = out_mid[2] - max_range
    xmax = out_mid[0] + max_range
    ymax = out_mid[1] + max_range
    zmax = out_mid[2] + max_range
    
    from itertools import product
    #for a in product([xmin,xmax],[ymin,ymax],[zmin,zmax]):
    a = numpy.array(list(product([xmin,xmax],[ymin,ymax],[zmin,zmax])))
#    print(a)
#    a = numpy.array(a)
    b = ax.plot(a[:,0],a[:,1],a[:,2],zorder = -1,linestyle='', marker='',color=(0,0,0,0))
    
#    for item in b:
#        item.remove()
    #b.remove()
    #ax.figure.canvas.draw()
#    ax.draw_idle()