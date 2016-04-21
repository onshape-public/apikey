'''
app
===

Demos usage of the Onshape API
'''

from apikey.client import Client

# stacks to choose from
stacks = {
    'partner': 'https://partner.dev.onshape.com',
    'cad': 'https://cad.dev.onshape.com'
}

# create instance of the onshape client; change key to test on another stack
c = Client(stack=stacks['partner'])

# make a new document and grab the document ID and workspace ID
new_doc = c.new_document(public=True).json()
did = new_doc['id']
wid = new_doc['defaultWorkspace']['id']

# get the document details
c.get_document(did)

# create a new assembly
asm = c.create_assembly(did, wid)

if asm.json()['name'] == 'My Assembly':
    print "Assembly created!"
else:
    print "Assembly did not get created properly :("

# upload blob
blob = c.upload_blob(did, wid)

# delete the doc
c.del_document(did)

# try to get the doc to make sure it's gone (should be in the trash)
trashed_doc = c.get_document(did)

if trashed_doc.json()['trash'] is True:
    print "Everything is as it should be!"
else:
    print "Oops! Something went wrong :("
