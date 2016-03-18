#!/usr/bin/env python

import sys
import time
import json
from onshape import Onshape
from pprint import pprint

import pyglet
from pyglet.gl import *
from pyglet.window import *

ApiKey = 'onshape_partner'
ApiKey = 'local-internal'
ApiKey = 'local-all'



# Test IDs for local partstudio cube
docId  = '6dcc732d763f4e8b8a7e782b'
workId = 'e64fc70d326a4d949a8fe2f1'
eltId  = 'a0456f4b9735484aa2119129'

# Test IDs for local tech marketing screw pump
docId  = 'fdf7685f0bba4df4b1720040'
workId = '9a199a6778d64ec984a76a44'
eltId  = '32351df2301b48c1b88d5ef0'


onshape = Onshape(ApiKey, 'os_accounts.json', logging=False, raise_on_fail=True)

resp = onshape.get('/api/users/session')
result = resp.json()
email = result['email']

DWE = '/d/' + docId + '/w/' + workId + '/e/' + eltId

# read the feature list
resp = onshape.get('/api/partstudios' + DWE + '/features')
featureResponse = resp.json()
featureList = featureResponse["features"]

global edgeList
edgeList = []

print('reading rollback data')

maxRollback = len(featureList) + 1
maxCount = 100
stride = 1
if (maxRollback > maxCount):
    # don't show every stage
    stride = maxRollback / maxCount

count = min(maxCount, maxRollback)

#length = min(200, len(featureList) + 1)

for index in range(0, count):
    idx = min(maxRollback, int(index * stride))

    onshape.post('/api/partstudios' + DWE + '/features/rollback', body = { "rollbackIndex" : str(idx) } )
    resp = onshape.get('/api/partstudios' + DWE + '/tessellatededges')
    edges = resp.json()
    if (len(edges) > 0):
        edgeList.append(edges)
    print('stage ' + str(idx) + ' (' + str(index) + ' / ' + str(count) + ')' )

print('rollback features complete ' + str(len(edgeList)) + ' stages found')


#global allEdges
#resp = onshape.get('/api/partstudios' + DWE + '/tessellatededges')
#print(str(resp))
#allEdges = resp.json()


window = pyglet.window.Window(resizable=True)

global rollback
rollback = 0

def drawEdges():
    global edgeList
    global rollback

    pyglet.graphics.glBegin(GL_LINES);

    for part in edgeList[rollback]:
        if len(part) > 0:
            edges = part["edges"]
            for edge in edges:
                v0 = edge["vertices"][0]
                v1 = edge["vertices"][1]
                pyglet.graphics.glVertex3f(v0[0], v0[1], v0[2])
                pyglet.graphics.glVertex3f(v1[0], v1[1], v1[2])
    pyglet.graphics.glEnd()


def rollUpdate(dt):
    global rollback
    rollback += 1
    if (rollback >= len(edgeList)):
        rollback = 0

global angle
angle = 0.0

def update(dt):
    global angle
    angle += 1
    if (angle > 360.):
        angle = 0
    
    glMatrixMode(gl.GL_MODELVIEW)
    glLoadIdentity()

    scale = 800.0
    xtran = 400.0
    ytran = 400.0
    ztran = 1.0

    glTranslatef(xtran, ytran, ztran)
    glRotatef(angle, 1.0, 0.5, 0.75)
    glScalef(scale, scale, scale)
    
pyglet.clock.schedule_interval(update, 0.02)
pyglet.clock.schedule_interval(rollUpdate, 0.5)

@window.event
def on_resize(width, height):
    glViewport(0, 0, width, height)
    glEnable(GL_DEPTH_CLAMP)
    glMatrixMode(gl.GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-width/2.0, width/2.0, -height/2.0, height/2.0, .01, 10.)
    glMatrixMode(gl.GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0.0, 0.0, 100.,
              0.0, 0.0, 0.0,
              0.0, 1.0, 0.0)
    

@window.event
def on_draw():
    window.clear()
    drawEdges()

def setup():
    # One-time GL setup
    glClearColor(1, 1, 1, 1)
    glColor3f(1, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)
 
    # Uncomment this line for a wireframe view
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
 
    # Simple light setup.  On Windows GL_LIGHT0 is enabled by default,
    # but this is not the case on Linux or Mac, so remember to always
    # include it.
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)

# setup()

pyglet.app.run()

