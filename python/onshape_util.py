"""
onshape_util

Experiments with the OnShape API.

for more information about the API see:

        https://dev-portal.onshape.com/

    also useful to use the OnShape api-explorer app in OnShape

    this code uses apikey to do authentication:

        https://github.com/onshape-public/apikey/tree/master/python

apis to play with:

    - try walking a project - get document for a project - get its parts, for each part of assembly get the part number and tags
        then get instances, subassemblies, parts in each assembly and recurse.

    get user companies  https://cad.onshape.com/api/companies?  (no parms)
    get teams   https://cad.onshape.com/api/teams?  (no parms)
    Document API - get document - can get tags
    Assembly API - assembly definition - gets "instances" (w/ "id", "name", "type" (e.g. "Assembly"), "suppressed" (true/false),
                "documentId", "documentMicroversion", "elementId"), "subassemblies" (w/ "documentId", "documentMicroversion",
                "elementId", "instances" (w/ "id", "name", "partId", "type", "suppressed", "documentId", "documentMicroversion",
                 "elementId")
    Elements API - get metadata - gets metadata including part number for an element (e.g. a part of assembly). Includes:
                "type" (e.g. "ASSEMBLY"), "state" (e.g. "IN_PROGRESS"), "description", "revision", "href", "vendor", "id",
                "elementId", "partNumber", "project", "name"

    Parts API - get parts

    Play with iFrames!

Len Wanger
Copyright Impossible Objects, 2017

---

Notes:
    Element types: fields (name, id, element_type, micro_version_id, and various unit information (for parts and assemblies)

    - Part Studio (zero or more parts) (element_type="PARTSTUDIO")
    - Assembly (zero or more parts or assemblies) (element_type="ASSEMBLY")
    - Blob ("Binary Large OBject") This can be data provided by a partner, or by the end user. For example,
        the user can upload a PDF file, an image or a text file. Partner applications can store arbitrary data,
        but we recommend using the structured storage available in an Application element for better integration. (element_type="BLOB)
    - Application. This is an element that presents an IFrame to the user. The user interface in the IFrame is
        managed by a server that can be provided by a third-party. Note that Onshape Drawings are a special
        case of an application element. (element_type="APPLCIATION")

"""

import sys
import json

if sys.version_info.major == 2:
    from urlparse import urlparse, parse_qs
else:
    from urllib.parse import urlparse, parse_qs

from apikey.ext_client import ClientExtended
import cooked_input as ci

IO_COMPANY_ID = '59f3676cac7f7c1075b79b71'
IO_ENGR_TEAM_ID = '59f396f9ac7f7c1075bf8687'
TEST_ASSEM_DOC_ID = '0f9c85ccbf253b470b931452'
MAIN_WORKSPACE = '5c9a0477134719bc5b930595'
TEST_ASSEM_ELEM_ID = 'fc5140cca987ed4102c2eb3f'

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
    #sys.stdout = open('temp.txt', 'w')

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
    #sys.stdout = sys.__stdout__


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

        print('item {}: name={}, id={}, elementType={}, microversionId={}'.format(i, name, item_id, element_type, micro_version_id))

    print('\n')


def get_bom_action(row, action_dict):
    print('\n')

    c = action_dict['client']
    did = action_dict['did']
    wvm = action_dict['wvm']
    eid = action_dict['eid']
    response = c.get_assembly_bom(did, wvm, eid, indented=False, generate_if_absent=True)
    response_json = json.loads(response.text)


    try:
        status = response_json['status']
        if status == 404:
            msg = response_json['message']
            print("\nStatus 404 returned: {}\n".format(msg))
            return
    except:
        pass

    print(f"\nBOM:\n")

    bom_table = response_json['bomTable']
    format_ver = bom_table['formatVersion']
    name = bom_table['name']
    doc_name = bom_table['bomSource']['document']['name']
    top_pn = bom_table['bomSource']['element']['partNumber']
    top_revision = bom_table['bomSource']['element']['revision']
    print(f"format_version: {format_ver}, name: {name}, doc_name; {doc_name}, pn: {top_pn}{top_revision}")

    print(f"\nheaders:\n")
    for idx,hdr in enumerate(bom_table['headers']):
        name = hdr['name']
        visible = hdr['visible']
        prop_id = hdr['propertyId']
        print(f"{idx}: name: {name}, visible: {visible}, prop_id: {prop_id}")

    print(f"\nitems:\n")
    for idx,item in enumerate(bom_table['items']):
        item_num = item['item']
        qty = item['quantity']
        part_num = item['partNumber']
        desc = item['description']
        revision = item['revision']
        print(f"{idx}: item: {item_num}, qty: {qty}, pn: {part_num}{revision}, desc: {desc}")


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
        'eid': TEST_ASSEM_ELEM_ID,
        'name_filter': None,
    }

    tis = [
        ci.TableItem('Set document name filter string', action=set_name_filter_action),
        ci.TableItem('List Documents', action=list_documents_action),
        ci.TableItem('List Teams', action=list_teams_action),
        ci.TableItem('List Workspaces', action=list_workspaces_action),
        ci.TableItem('List Elements', action=list_elements_action),
        ci.TableItem('Get BOM', action=get_bom_action),
    ]
    menu = ci.Table(tis, add_exit=ci.TABLE_ADD_EXIT, action_dict=ad)
    menu.run()

