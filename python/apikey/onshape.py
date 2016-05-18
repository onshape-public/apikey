'''
onshape
======

Provides access to the Onshape REST API
'''

import utils

import os
import random
import string
import json
import hmac
import hashlib
import base64
import urllib
import datetime
import requests
from urlparse import urlparse
from urlparse import parse_qs

__all__ = [
    'Onshape'
]


class Onshape():
    '''
    Provides access to the Onshape REST API.

    Attributes:
        - stack (str): Base URL
        - creds (str, default='./creds.json'): Credentials location
    '''

    def __init__(self, stack, creds='./creds.json'):
        '''
        Instantiates an instance of the Onshape class. Reads credentials from a JSON file
        of this format:

            {
                "http://cad.onshape.com": {
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

        Args:
            - stack (str): Base URL
            - creds (str, default='./creds.json'): Credentials location
        '''

        if not os.path.isfile(creds):
            raise IOError('%s is not a file' % creds)

        with open(creds) as f:
            try:
                stacks = json.load(f)
                if stack in stacks:
                    self._url = stack
                    self._access_key = stacks[stack]['access_key'].encode('utf-8')
                    self._secret_key = stacks[stack]['secret_key'].encode('utf-8')
                else:
                    raise ValueError('specified stack not in file')
            except TypeError:
                raise ValueError('%s is not valid json' % creds)

        utils.log('onshape instance created: url = %s, access key = %s' % (self._url, self._access_key))

    def _make_nonce(self):
        '''
        Generate a unique ID for the request, 25 chars in length

        Returns:
            - str: Cryptographic nonce
        '''

        chars = string.digits + string.ascii_letters
        nonce = ''.join(random.choice(chars) for i in range(25))

        utils.log('nonce created: %s' % nonce)

        return nonce

    def _make_auth(self, method, date, nonce, path, query={}, ctype='application/json'):
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

        query = urllib.urlencode(query)

        hmac_str = (method + '\n' + nonce + '\n' + date + '\n' + ctype + '\n' + path +
                    '\n' + query + '\n').lower().encode('utf-8')

        signature = base64.b64encode(hmac.new(self._secret_key, hmac_str, digestmod=hashlib.sha256).digest())
        auth = 'On ' + self._access_key + ':HmacSHA256:' + signature.decode('utf-8')

        utils.log({
            'query': query,
            'hmac_str': hmac_str,
            'signature': signature,
            'auth': auth
        })

        return auth

    def _make_headers(self, method, path, query={}, headers={}):
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

        date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        nonce = self._make_nonce()
        ctype = headers.get('Content-Type') if headers.get('Content-Type') else 'application/json'

        auth = self._make_auth(method, date, nonce, path, query=query, ctype=ctype)

        req_headers = {
            'Content-Type': 'application/json',
            'Date': date,
            'On-Nonce': nonce,
            'Authorization': auth,
            'User-Agent': 'Onshape Python Sample App',
            'Accept': 'application/vnd.onshape.v1+json'
        }

        # add in user-defined headers
        for h in headers:
            req_headers[h] = headers[h]

        return req_headers

    def request(self, method, path, query={}, headers={}, body={}, base_url=None):
        '''
        Issues a request to Onshape

        Args:
            - method (str): HTTP method
            - path (str): Path  e.g. /api/documents/:id
            - query (dict, default={}): Query params in key-value pairs
            - headers (dict, default={}): Key-value pairs of headers
            - body (dict, default={}): Body for POST request
            - base_url (str, default=None): Host (if different from creds file)

        Returns:
            - requests.Response: Object containing the response from Onshape
        '''

        req_headers = self._make_headers(method, path, query, headers)
        if base_url is None:
            base_url = self._url
        url = base_url + path + '?' + urllib.urlencode(query)

        utils.log(body)
        utils.log(req_headers)
        utils.log('request url: ' + url)

        # only parse as json string if we have to
        body = json.dumps(body) if type(body) == dict else body

        res = requests.request(method, url, headers=req_headers, data=body, allow_redirects=False)

        if res.status_code == 307:
            loc = res.headers["Location"]
            utils.log('request redirected to: ' + loc)
            loc_components = urlparse(loc)
            scheme = loc_components.scheme
            netloc = loc_components.netloc
            new_path = loc_components.path
            parsed_query = parse_qs(loc_components.query)
            new_query = {}
            for key in parsed_query:
                new_query[key] = parsed_query[key][0] # this will not work for repeated query params
            new_base_url = scheme + '://' + netloc
            return self.request(method, new_path, query=new_query, headers=headers, base_url=new_base_url)
        elif res.status_code != 200:
            utils.log('request failed, details: ' + res.text, level=1)
        else:
            utils.log('request succeeded, details: ' + res.text)

        return res
