#!/usr/bin/env python

import sys
import time
import json
from onshape import Onshape

from pprint import pprint

if 0:
    # test on staging stack
    server = 'https://staging.dev.onshape.com'

    # stevelb simple boxes
    documentId = 'ebfaa67ba5704c2f8bbaa4ed'
    workspaceId = '71f06402a2bc421caac9f5f1'
    sourceAssemblyId = '8da71b60bed54a66997956c6'

    # stevelb simple boxes
    # documentId = 'ebfaa67ba5704c2f8bbaa4ed'
    # workspaceId = '71f06402a2bc421caac9f5f1'
    # sourceAssemblyId = '8da71b60bed54a66997956c6'

    # johnmcc stirling engine
    #documentId = '098be6406b2c435bae008328'
    #workspaceId = '831d5f372e794dc899aaa960'
    #sourceAssemblyId = 'ab834de3dfad44ffb8ead172'

    # ducati (700+ parts)
    #documentId = '8737164ae769455babbc8325'
    #workspaceId = 'b0d96680281447f7b47a8444'
    #sourceAssemblyId = '00d9522672e64266a81aa733'

if 1:
    # stevelb simple with subassembly

    onshapeStack = 'onshape_partner'
    documentId = '8c6ded2bb806441f9c1983ca'
    workspaceId = '9b8612136aa84c769dd9875c'
    sourceAssemblyId = '07e8c681fa7b4ddca4044f3a'


if 1:
    onshape = Onshape(onshapeStack, 'os_accounts.json')

    DW = 'd/' + documentId + '/w/' + workspaceId
    sourceDWE = DW + '/e/' + sourceAssemblyId

    # get the bounding box of the original assembly
    res = onshape.get('/api/assemblies/' + sourceDWE + '/boundingboxes')
    sourceBox = res.json()

    centerX = sourceBox['lowX'] + (sourceBox['highX'] - sourceBox['lowX']) / 2
    centerY = sourceBox['lowY'] + (sourceBox['highY'] - sourceBox['lowY']) / 2
    centerZ = sourceBox['lowZ'] + (sourceBox['highZ'] - sourceBox['lowZ']) / 2

    # read the assembly definition
    res = onshape.get('/api/assemblies/' + sourceDWE)
    assy = res.json()
    # pprint(assy)

    partList = assy['parts']
    rootAssembly = assy['rootAssembly']
    subAssemblyList = assy['subAssemblies']
    rootInstanceList = rootAssembly['instances']

    # create a flat instance map to find instances by id
    instanceMap = {}
    for inst in rootInstanceList:
        instanceMap[inst['id']] = inst
    for sub in subAssemblyList:
        for inst in sub['instances']:
            instanceMap[inst['id']] = inst

    rootOccurrenceList = rootAssembly['occurrences']

    # create new assembly tab
    res = onshape.post('/api/assemblies/' + DW, body={'name' : 'New Stress Assembly'})
    newAssembly = res.json()
    newDWE = DW + '/e/' + newAssembly['id']

    # add all part occurrences

    transformList = []
    # add all root occurrences
    for occ in rootOccurrenceList:
        path = occ['path']
        transform = occ['transform']
        instance = instanceMap[path[-1]]
        if (instance['type'] == 'Part'):
            body = {'documentId' : instance['documentId'],
                    'elementId'  : instance['elementId'],
                    'microversionId' : instance['documentMicroversion'],
                    'isAssembly' : False,
                    'isWholePartStudio' : False,
                    'partId' : instance['partId']}
            # insert instance
            onshape.post('/api/assemblies/' + newDWE + '/instances', body=body)

            # remember the source transforms
            st = {}
            st['transform'] = transform
            st['body'] = body
            transformList.append(st)


    #print('Exiting early, after insert but without transform')
    #sys.exit()

    # get definition structure for new assembly with all instances created but not yet moved into place

    res = onshape.get('/api/assemblies/' + newDWE)
    newAssemblyDef = res.json()

    newRootAssembly = newAssemblyDef['rootAssembly']
    newRootOccurrences = newRootAssembly['occurrences']

    # create a flat instance map to find instances by id
    newInstanceMap = {}
    for inst in newRootAssembly['instances']:
        newInstanceMap[inst['id']] = inst


    def findPart(instance, transformList):
        for xform in transformList:
            xbody = xform['body']
            if (instance['partId'] == xbody['partId'] and
                instance['elementId'] == xbody['elementId'] and
                instance['documentId'] == xbody['documentId']):
                    transform = xform['transform']
                    transformList.remove(xform)
                    return transform
        return None

    for occ in newRootOccurrences:
        # find (and remove) this part in the old transform list
        xform = findPart(newInstanceMap[occ['path'][0]], transformList)

        # construct a transform
        body = {}
        body['occurrences'] = [{'path' : occ['path']}]
        # original position
        body['isRelative'] = False

        # define distance for move - 0.2 = 20% farther from center
        # use 0.0 for no move

        dist = 0.2

        x = xform[3]
        newx = x + (x - centerX) * dist
        xform[3] = newx

        y = xform[7]
        newy = y + (y - centerY) * dist
        xform[7] = newy

        z = xform[11]
        newz = z + (z - centerZ) * dist
        xform[11] = newz

        body['transform'] = xform

        onshape.post('/api/assemblies/' + newDWE + '/occurrencetransforms', body=body)
