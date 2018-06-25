"""
Test getting next page from OnShape API

Len Wanger
Copyright Impossible Objects, 2018
"""

import datetime
from onshapepy.ext_client import ClientExtended, Pager

IO_COMPANY_ID = '59f3676cac7f7c1075b79b71'

if __name__ == '__main__':
    stacks = {'cad': 'https://cad.onshape.com'}
    c = ClientExtended(stack=stacks['cad'], logging=False)
    doc_query = {'offset': 0, 'q': 'IO', 'filter': 7, 'owner': IO_COMPANY_ID}
    docs = c.list_documents(query=doc_query)

    print('fetching documents ', end='', flush=True)
    start_time = datetime.datetime.now()
    fetch_time = start_time

    for page in Pager(c, docs):
        href = page['href']
        offset_idx = href.find("offset")
        offset_end_idx = offset_idx + href[offset_idx:].find('&')
        elapsed_time = (datetime.datetime.now() - fetch_time).microseconds / 1_000_000
        print(f'fetch_time{elapsed_time}\t{href[offset_idx: offset_end_idx]}')
        fetch_time = datetime.datetime.now()

    end_time = datetime.datetime.now()
    print(f'Total time = {end_time-start_time}')

