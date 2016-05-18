'''
exportstl
===

Demos 307 redirects with the Onshape API
'''

from apikey.client import Client

# stacks to choose from
stacks = {
    'partner': 'https://partner.dev.onshape.com',
    'cad': 'https://cad.onshape.com'
}

# create instance of the onshape client; change key to test on another stack
c = Client(stack=stacks['cad'])

# change these to your own IDs
did = 'DOCUMENT_ID'
wid = 'WORKSPACE_ID'
eid = 'ELEMENT_ID'

# get the STL export
stl = c.part_studio_stl(did, wid, eid)

# print it to the console (because the imagination is the "best" STL visualization tool)
print stl