#!/usr/bin/env python

import sys
import time
import json
from onshape import Onshape
from pprint import pprint

ApiKey = 'onshape_partner'
ApiKey = 'onshape_production'
ApiKey = 'local-read-no-pii'
ApiKey = 'local-read-pii'
ApiKey = 'local-internal'
ApiKey = 'local-pii-only'


def outcome(note, resp):
    if (resp.status_code == 200):
        print(note + ' Succeeded')
    else:
        print(note + ' Failed ' + str(resp.status_code))

onshape = Onshape(ApiKey, 'os_accounts.json', logging=False)

print('testing api key ' + ApiKey)
resp = onshape.get('/api/users/session', raise_on_fail=False)
#result = resp.json()
#print('Current user email is ' + result['email'])
outcome('get users/session', resp)

resp = onshape.get('/api/users/apikeys', raise_on_fail=False)
outcome('get users/apikeys', resp)    

resp = onshape.get('/api/documents', raise_on_fail=False)
outcome('get documents', resp)

