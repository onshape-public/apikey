#!/usr/bin/env python

import sys
import time
import json
from onshape import Onshape
from pprint import pprint


if 0:
    # test on staging stack
    server = 'https://staging.dev.onshape.com'
    infile = 'stage1.txt'

if 1:
    # test on partner stack
    onshapeStack = 'onshape_partner'
    infile = 'oauthall3.txt'

if 0:
    # test against local stack
    server = 'http://localhost:8080'

if 1:
    onshape = Onshape(onshapeStack, 'os_accounts.json', logging=False)

    # build api bucket list
    apiMap = [
        {'str' : 'api/users/session', 'bkt' : 'signin'},
        {'str' : 'api/users', 'bkt' : 'user settings'},
        {'str' : 'api/documents', 'bkt' : 'documents' },
        {'str' : 'metadata', 'bkt' : 'metadata' },
        {'str' : 'api/elements', 'bkt' : 'deprecated elements' },
        {'str' : 'api/models', 'bkt' : 'deprecated models' },
        {'str' : 'tessellated', 'bkt' : 'mesh' },
        {'str' : 'parasolid', 'bkt' : 'parasolid' },  
        {'str' : 'api/thumbnails', 'bkt' : 'thumbnails' },
        {'str' : '/stl?', 'bkt' : 'stl' },
        {'str' : '/webhooks', 'bkt' : 'webhooks' },
        {'str' : '/accounts/purchases', 'bkt' : 'billing' },
        {'str' : '/billing/plans', 'bkt' : 'billing' },
        {'str' : 'api/appelements', 'bkt' : 'appelement' },
        {'str' : 'api/applications/clients', 'bkt' : 'appsettings' },
        {'str' : 'api/assemblies', 'bkt' : 'assemblies' },
        {'str' : 'api/partstudios', 'bkt' : 'partstudios' },
        {'str' : 'api/blobelements', 'bkt' : 'blobs' },
        {'str' : 'api/parts', 'bkt' : 'parts' },
        {'str' : 'api/companies', 'bkt' : 'companies' },
        {'str' : 'api/teams', 'bkt' : 'teams' },
        {'str' : 'api/translations', 'bkt' : 'translations' },
        {'str' : 'associativedata', 'bkt' : 'deprecated associative' },
        {'str' : 'api/partners', 'bkt' : 'traceparts' },
        {'str' : 'api/build', 'bkt' : 'deprecated build' },
        {'str' : 'api/notifications', 'bkt' : 'deprecated notifications' },
        {'str' : 'api/elements/application/', 'bkt' : 'deprecated application' },
        {'str' : 'api/capabilities', 'bkt' : 'internal capabilities' },
        {'str' : 'api/comments', 'bkt' : 'internal comments' }
    ]

    def getBucket(path):
        for b in apiMap:
            if path.find(b['str']) != -1:
                return b['bkt']
        return 'unknown'

    userMap = {}
    clientMap = {}

if 1:
    def lookupUser(userId):
        if not userId in userMap:
            try:
                resp = onshape.get('/api/users/' + userId)
                user = resp.json()
                userMap[userId] = user["email"]
            except:
                userMap[userId] = 'unknown'
        return userMap[userId]
        
if 1:
    def lookupClient(clientId):
        if not clientId in clientMap:
            try:
                resp = onshape.get('/api/applications/' + clientId)
                client = resp.json()
                clientMap[clientId] = client["name"]
            except:
                clientMap[clientId] = 'unknown'
        return clientMap[clientId]

# read data file
if 1:
    with open(infile) as data_file:
        data = json.load(data_file)
        hits = data['hits']
        recs = hits['hits']
        print (str (len(recs)) + ' records found')

        print('time, app, user, verb, path, status, bucket')
        for raw in recs:
            rec = raw['_source']
            r = {}

            # 2015-11-03T18:52:49.144Z input format
            # 09/12/2013 09:08:08:07.6546 output format
            d, t = rec['@timestamp'].split('T', 2)
            y,m,dy = d.split('-')
            r['time'] = str(m) + '/' + str(dy) + '/' + str(y) + ' ' + t[:-1]
            r['app'] = lookupClient(rec['clientId'])
            r['user'] = lookupUser(rec['userId'])
            # uri1 starts with verb, eg GET uri:/api/documents/d/9e00694816954e05812e1a19/w/553e2387555f4e0d92d3b63c/elements?elementType=assembly status:200
            uri1 = rec['messageBody'].split(':',1)[1]
            r['verb'] = uri1.split(' ', 1)[0]

            # uri2 starts with path
            uri2 = uri1.split(':', 1)[1]
            r['path'], uri3 = uri2.split(' ', 1)
            r['path'] = r['path'].replace('"', "'")
            
            # uri3 starts with "status:"
            r['status'] = uri3[7:]

            # find bucket
            r['bucket'] = getBucket(r['path'])

            if r['user'] != 'unknown' and r['user'].find('test.onshape.com') == -1 and r['app'] != 'AppStore' and r['app'] != 'unknown':
                print('"{}","{}","{}","{}","{}","{}","{}"'.format( r['time'], r['app'], r['user'], r['verb'], r['path'], r['status'], r['bucket']) )

