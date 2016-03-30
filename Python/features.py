#!/usr/bin/env python

import sys
import time
import json
import random
from onshape import Onshape
from pprint import pprint

onshapeStack = 'onshape_partner'
# box studio
DWE = '/d/172441db448a476a8100c049/w/44a1c96d65aa4480b37e0587/e/f67fee1224354bfdbb8558c9'

onshape = Onshape(onshapeStack, 'os_accounts.json')

resp = onshape.get('/api/partstudios' + DWE + '/features')
featureList = resp.json()
features = featureList['features']

# find the width variable feature
widthFeature = {}
widthParams = {}
widthValue = {}

lengthFeature = {}
lengthParams = {}
lengthValue = {}

heightFeature = {}
heightParams = {}
heightValue = {}

radiusFeature = {}
radiusParams = {}
radiusValue = {}


for f in features:
    if (f['message']['featureType'] == 'assignVariable'):
        params = f['message']['parameters']
        for p in params:
            if (p['message']['parameterId'] == 'name') and (p['message']['value'] == 'width'):
                widthFeature = f
                widthParams = params
            if (p['message']['parameterId'] == 'name') and (p['message']['value'] == 'length'):
                lengthFeature = f
                lengthParams = params
            if (p['message']['parameterId'] == 'name') and (p['message']['value'] == 'height'):
                heightFeature = f
                heightParams = params
            if (p['message']['parameterId'] == 'name') and (p['message']['value'] == 'radius'):
                radiusFeature = f
                radiusParams = params
                


# find values in params
for p in widthParams:
    if (p['message']['parameterId'] == 'value'):
        widthValue = p
for p in lengthParams:
    if (p['message']['parameterId'] == 'value'):
        lengthValue = p
for p in heightParams:
    if (p['message']['parameterId'] == 'value'):
        heightValue = p
for p in radiusParams:
    if (p['message']['parameterId'] == 'value'):
        radiusValue = p

rad = 1
for i in range(20):
    radiusValue['message']['expression'] = str(rad)
    body = {'feature' : radiusFeature}
    onshape.post('/api/partstudios' + DWE + '/features/featureid/' + radiusFeature['message']['featureId'], body=body)
    rad = rad + 0.05

if 1:
    rad = 1
    radiusValue['message']['expression'] = str(rad)
    body = {'feature' : radiusFeature}
    onshape.post('/api/partstudios' + DWE + '/features/featureid/' + radiusFeature['message']['featureId'], body=body)
    


'''
for i in range(100):
    dim = random.randint(1,4)
    size = random.randint(1,10)

    if dim == 1:
        widthValue['message']['expression'] = str(size)
        body = {'feature' : widthFeature}
        onshape.post('/api/partstudios' + DWE + '/features/featureid/' + widthFeature['message']['featureId'], body=body)
    elif dim == 2:
        lengthValue['message']['expression'] = str(size)
        body = {'feature' : lengthFeature}
        onshape.post('/api/partstudios' + DWE + '/features/featureid/' + lengthFeature['message']['featureId'], body=body)
    elif dim == 3:
        heightValue['message']['expression'] = str(size)
        body = {'feature' : heightFeature}
        onshape.post('/api/partstudios' + DWE + '/features/featureid/' + heightFeature['message']['featureId'], body=body)
    elif dim == 4:
        radiusValue['message']['expression'] = str(size)
        body = {'feature' : radiusFeature}
        onshape.post('/api/partstudios' + DWE + '/features/featureid/' + radiusFeature['message']['featureId'], body=body)
    

    time.sleep(1)

'''