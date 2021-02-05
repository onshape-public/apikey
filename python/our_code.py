from __future__ import print_function

'''
app
===

Demos basic usage of the Onshape API
'''

#from apikey.client import Client
from onshapepy.client import Client

# stacks to choose from
stacks = {
    'cad': 'https://cad.onshape.com'
}

# create instance of the onshape client; change key to test on another stack
c = Client(stack=stacks['cad'], logging=True)

did = "bac5ea84d6aad3153db5452c"

# get the document details
details = c.get_document(did)
print('Document name: ' + details.json()['name'])

