'''
app
===

Demos usage of the Onshape API
'''

from apikey.client import Client

# create instance of the onshape client
c = Client(stack='http://localhost:8080')

# make a new document and grab the ID
did = c.new_document(public=True).json()['id']

# get the document details
c.get_document(did)

# delete the doc
c.del_document(did)

# try to get the doc to make sure it's gone (should be in the trash)
trashed_doc = c.get_document(did)

if trashed_doc.json()['trash'] == True:
    print "Everything is as it should be!"
else:
    print "Oops! Something went wrong :("
