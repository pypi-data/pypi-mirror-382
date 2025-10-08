# -*- coding: utf-8 -*-
"""
copyright 2016-2017 Dan Aukes
"""
import PyQt5.QtGui as qg
import PyQt5.QtWidgets as qw
import pyqtgraph.opengl as pgo
import sys
import numpy

def prep():
    app = qw.QApplication(sys.argv)
    w = pgo.GLViewWidget()    
    return app,w

def plot_mi(mi):
    app,w = prep()
    w.addItem(mi)
    w.show()
    sys.exit(app.exec_())

def plot_tris(*args,**kwargs):
    mi = make_mi(*args,**kwargs)
    plot_mi(mi)

def plot_mesh_object(mo,*args,**kwargs):
    points = mo.points
    tris = mo.cells['triangle']
    mi = make_mi(points,tris,*args,**kwargs)
    plot_mi(mi)
    
def make_mi(verts,tris,verts_colors = None,face_colors = None, draw_edges = False, edge_color = (1,1,1,1)):
    face_colors_a = numpy.array(face_colors)
    if len(face_colors_a.shape)==1 or (len(face_colors_a.shape)>1 and face_colors_a.shape[0]==1):
        face_colors = numpy.array([list(face_colors)]*len(tris))
    md = pgo.MeshData(vertexes = verts,faces = tris,vertexColors = verts_colors,faceColors = face_colors)
    mi = pgo.GLMeshItem(meshdata = md,shader='balloon',drawEdges=draw_edges,edgeColor = edge_color,smooth=False,computeNormals = False,glOptions='translucent')
#    mi = pgo.GLMeshItem(meshdata = md,shader='shaded',drawEdges=False,smooth=True,computeNormals = True,glOptions='opaque')
    return mi
    
if __name__=='__main__':
    import numpy
    verts = []
    verts.append([0,0,0])
    verts.append([1,0,0])
    verts.append([0,1,0])
    verts.append([1,1,0])
    verts = numpy.array(verts)
    
    verts_colors = []
    verts_colors.append([1,0,0,1])
    verts_colors.append([0,1,0,1])
    verts_colors.append([0,0,1,1])
    verts_colors.append([1,1,0,1])
    verts_colors = numpy.array(verts_colors)
    
    tris = []
    tris.append([0,1,2])
    tris.append([1,2,3])
    tris = numpy.array(tris)
    
    app,w = prep()
    mi = make_mi(verts,tris,verts_colors,draw_edges = True, edge_color=(1,1,1,1))
#    w.addItem(mi)
    
    
    w.opts['center'] =qg.QVector3D(.5,.5,0)
    w.opts['elevation'] =90
    w.opts['azimuth'] = 0
    w.opts['distance'] = 1
    w.resize(1000,1000)
    w.show()

    w.paintGL()
    w.grabFrameBuffer().save('multimaterial.png')
    plot_mi(mi)
