"""
Test getting next page from OnShape API

Len Wanger
Copyright Impossible Objects, 2018
"""

import sys
import json

if sys.version_info.major == 2:
    from urlparse import urlparse, parse_qs
else:
    from urllib.parse import urlparse, parse_qs

from onshapepy.ext_client import ClientExtended, Pager

IO_COMPANY_ID = '59f3676cac7f7c1075b79b71'

if __name__ == '__main__':
    stacks = {'cad': 'https://cad.onshape.com'}
    c = ClientExtended(stack=stacks['cad'], logging=False)
    doc_query = {'offset': 0, 'q': 'IO', filter: 7, 'owner': IO_COMPANY_ID}
    docs = c.list_documents(query=doc_query)

    print('fetching documents ', end='', flush=True)
    for page in Pager(c, docs):
        print(f'page._next="{page["next"]}"')
