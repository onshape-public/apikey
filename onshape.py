#!/usr/bin/env python

import requests, json, string, random, hmac, hashlib, base64, datetime, sys, urllib
import pprint

'''
The credential file is a JSON file with this format:
 {
    "onshape_partner" : {
        "baseUrl":   "https://partner.dev.onshape.com",
        "accessKey": "API-KEY",
        "userId":    "USER-ID",
        "secretKey": "API-KEY-SECRET"
        },
    "onshape_production" : {
       ...
       }
 }

 To create an API Key and Secret, POST to /api/users/apikeys
 (later, this will be done through the developer portal)

'''

class Onshape():
    '''
    Define APIKey interface to Onshape
    '''

    def __init__(self, stackName, credsFile, logging=True, raise_on_fail=True):
        self.logging = logging
        self.raise_on_fail = raise_on_fail

        with open(credsFile) as accounts:
            logins = json.load(accounts)
        if stackName in logins:
            self.creds = logins[stackName]
        else:
            raise ValueError('No credentials found for requested stack', stackName)

    def setLogging(self, opt):
        self.logging = opt

    def __buildHeaders(self, method, path, query, body, headers):
        if (self.logging):
            print('Call onshape: ' + method + ' ' + self.creds['baseUrl'] + path)

        auth_date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        auth_key = str(self.creds['accessKey'])
        auth_skey = str(self.creds['secretKey']).encode('utf-8')
        on_nonce = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(25))
        query_string = urllib.urlencode(query)
        hmac_string = (method + '\n' + on_nonce + '\n' + auth_date + '\napplication/json\n' + path + '\n' +query_string + '\n').lower().encode('utf-8')
        signature = base64.b64encode(hmac.new(auth_skey, hmac_string, digestmod=hashlib.sha256).digest())
        asign = 'On ' + auth_key + ':HmacSHA256:' + signature.decode('utf-8')

        # Build API Key headers
        on_headers = {'content-type':'application/json', 'On-Nonce':on_nonce, 'Date':auth_date, 'Authorization':asign}

        # add user requested headers
        for h in headers:
            on_headers[h[0]] = h[1]
        return on_headers

    def __logAndReturn(self, resp, raise_on_fail):
        if (self.logging):
            print('Response status is ' + str(resp.status_code))

        if (resp.status_code == 307):
            # we don't handle redirection results
            # todo: add code to create new signed header with updated path and params
            raise ValueError('Redirection not currently handled')

        if (raise_on_fail == None):
            raise_on_fail = self.raise_on_fail

        if (raise_on_fail and resp.status_code < 200 and resp.status_code > 206):
            result = resp.json()
            message = 'Unexpected status ' + str(resp.status_code) + ' (' + result['message'] + ')'
            raise ValueError(message, resp.status_code)

        return resp

    def get(self, path, query={}, body={}, headers=[], raise_on_fail=True):
        onshapeHeaders = self.__buildHeaders('get', path, query, body, headers)
        resp = requests.get(self.creds['baseUrl'] + path, params=query, headers=onshapeHeaders, allow_redirects=False)
        return self.__logAndReturn(resp, raise_on_fail)

    def delete(self, path, query={}, body={}, headers=[], raise_on_fail=True):
        onshapeHeaders = self.__buildHeaders('delete', path, query, body, headers)
        resp = requests.delete(self.creds['baseUrl'] + path, params=query, headers=onshapeHeaders, allow_redirects=False)
        return self.__logAndReturn(resp, raise_on_fail)

    def post(self, path, query={}, body={}, headers=[], raise_on_fail=True):
        onshapeHeaders = self.__buildHeaders('post', path, query, body, headers)
        resp = requests.post(self.creds['baseUrl'] + path, params=query, data=json.dumps(body), headers=onshapeHeaders, allow_redirects=False)
        return self.__logAndReturn(resp, raise_on_fail)
