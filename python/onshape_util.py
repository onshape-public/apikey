"""
onshape_util

Experiments with the OnShape API.

for more information about the API see:

        https://dev-portal.onshape.com/

    also useful to use the OnShape api-explorer app in OnShape

    this code uses apikey to do authentication:

        https://github.com/onshape-public/apikey/tree/master/python

apis to play with:

    get user companies  https://cad.onshape.com/api/companies?  (no parms)
    get teams   https://cad.onshape.com/api/teams?  (no parms)

Len Wanger
Copyright Impossible Objects, 2017
"""

import json
from urllib.parse import urlparse, parse_qs

from apikey.ext_client import ClientExtended
import cooked_input as ci

IO_COMPANY_ID = '59f3676cac7f7c1075b79b71'
IO_ENGR_TEAM_ID = '59f396f9ac7f7c1075bf8687'
TEST_ASSEM_DOC_ID = '0f9c85ccbf253b470b931452'
MAIN_WORKSPACE = '5c9a0477134719bc5b930595'

def set_name_filter_action(row, action_dict):
    result = ci.get_string(prompt='Enter string for document name filter: ', required=False)
    action_dict['name_filter'] = result

def list_documents_action(row, action_dict):
    # Uses Documents API/Get Documents
    # parms - q - search for string in name of document
    # filter - 0-9 for filter, 0 - my docs, 6- by owner, 7 by company, 9 by team
    # owner - owner id for filter 6 or 7, team if 9
    # offset - offset into the page (max 20)
    # limit - number of documents returned per page

    c = action_dict['client']
    #filter_val, owner = (9, action_dict['team'])   # filter by team
    filter_val, owner =  (7, action_dict['company'])    # filter by company

    # doc_query = {'q': 'exercise', 'filter': 0, 'offset': 0}
    # doc_query = {'filter': filter_val, 'owner': owner, 'offset': 0, 'limit': 20}
    doc_query = {'filter': filter_val, 'owner': owner}

    if action_dict['name_filter'] is not None and len(action_dict['name_filter']) > 0:
        doc_query['q'] = action_dict['name_filter']

    docs = c.list_documents(query=doc_query)

    while True:
        docs_json = json.loads(docs.text)

        try:
            cur_offset = int(parse_qs(urlparse(docs.url)[4])['offset'][0])
        except KeyError:
            cur_offset = 0

        try:
            next_page = docs_json['next']
        except KeyError:
            next_page = None

        for i, item in enumerate(docs_json['items']):
            name = item['name']
            item_id = item['id']
            tags = item['tags']
            description = item['description']
            href = item['href']
            print('item {}: name={}, id={}, tags={}, description={}, href={}'.format(i+cur_offset, name, item_id, tags, description, href))

        if next_page is None:
            break
        else:
            qd = parse_qs(urlparse(next_page)[4])
            doc_query['offset'] = cur_offset + int(qd['offset'][0])
            docs = c.list_documents(query=doc_query)

    print('\n')


def list_teams_action(row, action_dict):
    c = action_dict['client']
    response = c.list_teams()

    while True:
        response_json = json.loads(response.text)
        next_page = response_json['next']
        cur_offset = 0

        for i, item in enumerate(response_json['items']):
            name = item['name']
            item_id = item['id']
            description = item['description']
            href = item['href']
            print('item {}: name={}, id={}, description={}, href={}'.format(i + cur_offset, name, item_id, description, href))

        if next_page is None:
            break
        else:
            response = c.get_next_page(next_page)
            cur_offset += 20

    print('\n')


def list_workspaces_action(row, action_dict):
    print('\n')

    c = action_dict['client']
    did = action_dict['did']
    response = c.get_workspaces(did)
    response_json = json.loads(response.text)

    # for i, item in enumerate(response_json['items']):
    for i, item in enumerate(response_json):
        read_only = item['isReadOnly']
        modified_at = item['modifiedAt']
        name = item['name']
        item_id = item['id']
        document_id = item['documentId']
        description = item['description']
        href = item['href']
        print('item {}: name={}, document_id={}, id={}, description={}, read_only={}, modified_at={}, href={}'.format(i, name, document_id, item_id, description, read_only, modified_at, href))

    print('\n')


def list_elements_action(row, action_dict):
    print('\n')

    c = action_dict['client']
    did = action_dict['did']
    wvm = action_dict['wvm']
    response = c.get_element_list(did, wvm, element_type=None, eid=None, with_thumbnails=False)
    response_json = json.loads(response.text)

    for i, item in enumerate(response_json):
        name = item['name']
        item_id = item['id']
        element_type = item['elementType']
        micro_version_id = item['microversionId']

        print('item {}: name={}, id={}, element_type={}, micro_version_id={}'.format(i, name, item_id, element_type, micro_version_id))

    print('\n')


if __name__ == '__main__':
    stacks = {'cad': 'https://cad.onshape.com'}
    c = ClientExtended(stack=stacks['cad'], logging=False)
    ad = {
        'client': c, 'did': TEST_ASSEM_DOC_ID,
        'team': IO_ENGR_TEAM_ID,
        'company': IO_COMPANY_ID,
        'did': TEST_ASSEM_DOC_ID,
        'wvm': MAIN_WORKSPACE,
        'name_filter': None,
    }

    tis = [
        ci.TableItem('Set document name filter string', action=set_name_filter_action),
        ci.TableItem('List Documents', action=list_documents_action),
        ci.TableItem('List Teams', action=list_teams_action),
        ci.TableItem('List Workspaces', action=list_workspaces_action),
        ci.TableItem('List Elements', action=list_elements_action),
    ]
    menu = ci.Table(tis, add_exit=ci.TABLE_ADD_EXIT, action_dict=ad)
    menu.run()

