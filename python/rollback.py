'''
rollback
========

Demonstrates more advanced usage of the Onshape API; visualizes a part studio's
history via pyglet.

Pass in arguments for document, workspace, and element via the CLI
'''

from apikey.client import Client

from pyglet.gl import *
from pyglet.window import *
import pyglet

# stacks to choose from
stacks = {
    'partner': 'https://partner.dev.onshape.com',
    'cad': 'https://cad.onshape.com'
}

# create instance of the onshape client; change key to test on another stack
c = Client(stack=stacks['partner'])

# get features for doc
did = raw_input('Enter document ID: ')
wid = raw_input('Enter workspace ID: ')
eid = raw_input('Enter element ID: ')

# grab feature list for doc
features = c.get_features(did, wid, eid).json()['features']

# read rollback data and display it using pyglet
edge_list = []
max_rollback = len(features) + 1
max_count = 100
stride = 1

if max_rollback > max_count:
    stride = max_rollback / max_count

count = min(max_count, max_rollback)

for i in range(0, count):
    idx = min(max_rollback, int(i * stride))

    payload = {
        'rollbackIndex': str(idx)
    }

    c.update_rollback(did, wid, eid, payload)
    edges = c.get_partstudio_tessellatededges(did, wid, eid).json()

    if len(edges) > 0:
        edge_list.append(edges)

# at this point we have the tesselation data for the whole feature history; time to display it!
window = pyglet.window.Window(resizable=True)

rollback = 0
angle = 0.0


def drawEdges():
    global edge_list
    global rollback

    pyglet.graphics.glBegin(GL_LINES)

    for part in edge_list[rollback]:
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
    if (rollback >= len(edge_list)):
        rollback = 0


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
pyglet.clock.schedule_interval(rollUpdate, 1)


@window.event
def on_resize(width, height):
    glViewport(0, 0, width, height)
    glEnable(GL_DEPTH_CLAMP)

    glMatrixMode(gl.GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-width / 2.0, width / 2.0, -height / 2.0, height / 2.0, .01, 10)

    glMatrixMode(gl.GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0.0, 0.0, 100, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)


@window.event
def on_draw():
    window.clear()
    drawEdges()


def setup():
    glClearColor(1, 1, 1, 1)
    glColor3f(1, 0, 0)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    glDisable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)

# display ui
pyglet.app.run()
