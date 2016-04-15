'''
onshape
======

Provides access to the Onshape REST API
'''

import utils

from os.path import isfile
import random
import json
import hmac
import hashlib
import base64
import urllib
import datetime
import requests
import sys


class Onshape():
    '''
    Provides access to the Onshape REST API. Reads credentials from a JSON file
    of this format:

        {
            "http://localhost:8080": {
                "access_key": "YOUR KEY HERE",
                "secret_key": "YOUR KEY HERE"
            },
            "https://partner.dev.onshape.com": {
                "access_key": "YOUR KEY HERE",
                "secret_key": "YOUR KEY HERE"
            },
            etc... add new object for each stack to test on
        }

    The creds.json file should be stored in the root project folder; optionally,
    you can specify the location of a different file.

    Attributes:
        - stack (str, default='https://partner.dev.onshape.com'): Base URL
        - creds (str, default='../creds.json'): Credentials location
    '''
    def __init__(self, stack='https://partner.dev.onshape.com', creds='./creds.json'):
        if not isfile(creds):
            sys.exit('fatal: %s is not a file' % creds)

        with open(creds) as f:
            try:
                stacks = json.load(f)
                if stack in stacks:
                    self._url = stack
                    self._access_key = str(stacks[stack]['access_key'])
                    self._secret_key = str(stacks[stack]['secret_key']).encode('utf-8')
                else:
                    sys.exit('fatal: %s not in file' % stack)
            except TypeError:
                sys.exit('fatal: %s is not valid json' % creds)

    '''
    Generate a unique ID for the request, 25 chars in length

    Returns:
        - str: Cryptographic nonce
    '''
    def _make_nonce(self):
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        nonce = ''.join(random.choice(chars) for i in range(25))

        return nonce

    '''
    Create the request signature to authenticate

    Args:
        - method (str): HTTP method
        - date (str): HTTP date header string
        - nonce (str): Cryptographic nonce
        - path (str): URL pathname
        - query (dict, default={}): URL query string in key-value pairs
        - ctype (str, default='application/json'): HTTP Content-Type
    '''
    def _make_auth(self, method, date, nonce, path, query={}, ctype='application/json'):
        query = urllib.urlencode(query)

        hmac_str = (method + '\n' + nonce + '\n' + date + '\n' + ctype + '\n' + path +
                    '\n' + query + '\n').lower().encode('utf-8')

        signature = base64.b64encode(hmac.new(self._secret_key, hmac_str, digestmod=hashlib.sha256).digest())
        auth = 'On ' + self._access_key + ':HmacSHA256:' + signature.decode('utf-8')

        return auth

    '''
    Creates a headers object to sign the request

    Args:
        - method (str): HTTP method
        - path (str): Request path, e.g. /api/documents. No query string
        - query (dict, default={}): Query string in key-value format
        - headers (dict, default={}): Other headers to pass in

    Returns:
        - dict: Dictionary containing all headers
    '''
    def _make_headers(self, method, path, query={}, headers={}):
        date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        nonce = self._make_nonce()
        auth = self._make_auth(method, date, nonce, path, query=query)

        req_headers = {
            'Content-Type': 'application/json',
            'Date': date,
            'On-Nonce': nonce,
            'Authorization': auth,
            'User-Agent': 'Onshape Python Sample App'
        }

        # add in user-defined headers
        for h in headers:
            req_headers[h] = headers[h]

        return req_headers

    '''
    Issues a request to Onshape

    Args:
        - method (str): HTTP method
        - path (str): Path  e.g. /api/documents/:id
        - query (dict, default={}): Query params in key-value pairs
        - headers (dict, default={}): Key-value pairs of headers
        - body (dict, default={}): Body for POST request

    Returns:
        - dict: Object containing the response from Onshape
    '''
    def request(self, method, path, query={}, headers={}, body={}):
        req_headers = self._make_headers(method, path, query, headers)
        url = self._url + path + '?' + urllib.urlencode(query)

        res = requests.request(method, url, headers=req_headers, allow_redirects=False)
        return res

on = Onshape(stack='http://localhost:8080')
res = on.request('get', '/api/documents')
print res.json()
