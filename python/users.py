'''
users
===

Demos basic usage of the Onshape API users
'''

from apikey.client import Client

# stacks to choose from
stacks = {
    'staging': 'https://staging.dev.onshape.com'
}

# create instance of the onshape client; change key to test on another stack
c = Client(stack=stacks['staging'], logging=True)

# make a new document and grab the document ID and workspace ID
user = c.get_users_current()
print 'User: ' + user.json()
