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

# make a new document and grab the document ID and workspace ID
new_doc = c.new_document(public=True).json()
did = new_doc['id']
wid = new_doc['defaultWorkspace']['id']

# get the document details
details = c.get_document(did)
print('Document name: ' + details.json()['name'])

# create a new assembly
asm = c.create_assembly(did, wid)

if asm.json()['name'] == 'My Assembly':
    print('Assembly created')
else:
    print('Error: Assembly not created')

# upload blob
blob = c.upload_blob(did, wid)

# delete the doc
c.del_document(did)

# try to get the doc to make sure it's gone (should be in the trash)
trashed_doc = c.get_document(did)

if trashed_doc.json()['trash'] is True:
    print('Document now in trash')
else:
    print('Error: Document not trashed')
