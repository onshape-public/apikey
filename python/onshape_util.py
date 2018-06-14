"""
onshape_util

Experiments with the OnShape API.

for more information about the API see:

        https://dev-portal.onshape.com/

    also useful to use the OnShape api-explorer app in OnShape

    this code uses apikey to do authentication:

        https://github.com/onshape-public/apikey/tree/master/python


TODO:
    - Clean up - remove the name filter
    - Add cooked_input commands (for scrolling)
    - More apis to play with:

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

from apikey.ext_client import ClientExtended, Pager
import cooked_input as ci

IO_COMPANY_ID = '59f3676cac7f7c1075b79b71'
IO_ENGR_TEAM_ID = '59f396f9ac7f7c1075bf8687'
TEST_ASSEM_DOC_ID = '0f9c85ccbf253b470b931452'
MAIN_WORKSPACE = '5c9a0477134719bc5b930595'
TEST_ASSEM_ELEM_ID = 'fc5140cca987ed4102c2eb3f'


def help_cmd_action(cmd_str, cmd_vars, cmd_dict):
    print('\nCommands:\n')
    print('/?, /h\tDisplay this help message')
    print('/cancel\tCancel the current operation')
    print('/first (/f)\tGo to first page of the table')
    print('/last (/l)\tGo to last page of the table')
    print('/prev (/p)\tGo to previous page of the table')
    print('/next (/n)\tGo to next page of the table')
    print()

    return (ci.COMMAND_ACTION_NOP, None)


def cancel_cmd_action(cmd_str, cmd_vars, cmd_dict):
    print('\nCommand cancelled...')
    return (ci.COMMAND_ACTION_CANCEL, None)


std_commands = {
    '/?': ci.GetInputCommand(help_cmd_action),
    '/h': ci.GetInputCommand(help_cmd_action),
    '/help': ci.GetInputCommand(help_cmd_action),
    '/cancel': ci.GetInputCommand(cancel_cmd_action),
}

table_commands = {
    '/?': ci.GetInputCommand(help_cmd_action),
    '/h': ci.GetInputCommand(help_cmd_action),
    '/help': ci.GetInputCommand(help_cmd_action),
    '/cancel': ci.GetInputCommand(cancel_cmd_action),
    '/first': ci.GetInputCommand(ci.first_page_cmd_action),
    '/last': ci.GetInputCommand(ci.last_page_cmd_action),
    '/prev': ci.GetInputCommand(ci.prev_page_cmd_action),
    '/next': ci.GetInputCommand(ci.next_page_cmd_action),
}


class DocRow():
    # class to represent an OnShape document
    def __init__(self, doc_json):
        self.did = doc_json['id']
        self.href = doc_json['href']
        self.name = doc_json['name']
        self.owner_id = doc_json['owner']['id']
        self.owner = doc_json['owner']
        self.default_workspace_id = doc_json['defaultWorkspace']['id']
        self.default_workspace = doc_json['defaultWorkspace']['name']
        self.created_at = doc_json['createdAt']
        self.created_by_id = doc_json['createdBy']['id']
        self.created_by = doc_json['createdBy']['name']
        self.modified_at = doc_json['modifiedAt']
        self.modified_by_id = doc_json['modifiedBy']['id']
        self.modified_by = doc_json['modifiedBy']['name']

    def __repr__(self):
        return f'{self.name} ({self.did})'


def create_docs_table(c, docs):
    rows = []
    print('fetching documents ', end='', flush=True)
    for page in Pager(c, docs):
        print('.', end='', flush=True)
        for item in page['items']:
            rows.append(DocRow(item))

    print('\n\n')
    fields = ["Name", "did", "CreatedAt", "Default Workspace", "ModifiedAt"]
    tis = [ci.TableItem([row.name, row.did, row.created_at, row.default_workspace, row.modified_at], tag=None, item_data={'row': row}) for row in rows]
    tbl = ci.Table(tis, fields, default_action=ci.TABLE_RETURN_TABLE_ITEM, add_exit=False,
                   show_cols=True, show_border=True, hrules=ci.RULE_FRAME, vrules=ci.RULE_ALL)
    return tbl


def list_documents_action(row, action_dict):
    # Uses Documents API/Get Documents
    # parms - q - search for string in name of document
    # filter - 0-9 for filter, 0 - my docs, 6- by owner, 7 by company, 9 by team
    # owner - owner id for filter 6 or 7, team if 9
    # offset - offset into the page (max 20)
    # limit - number of documents returned per page
    c = action_dict['client']
    doc_query = {'offset': 0, 'limit': 20}

    name_filter = ci.get_string(prompt='String to filter document names (hit enter for no filter)', required=False, commands=std_commands)
    if name_filter is not None and len(name_filter) > 0:
        doc_query['q'] = name_filter

    if ci.get_yes_no(prompt='Show only your documents', default='no', commands=std_commands) == 'yes':
        filter_val, owner = (0, None)  # filter by company
        doc_query = {'filter': 0}
    elif ci.get_yes_no(prompt='Show documents for your company', default='no', commands=std_commands) == 'yes':
        doc_query = {'filter': 7, 'owner': action_dict['company']}  # filter by company
    # elif ...:
        # TODO - implement other filters - team, owner, etc.
        #filter_val, owner = (9, action_dict['team'])   # filter by team
        #doc_query = {'filter': 9, 'owner': action_dict['team']}  # filter by team

    else:
        if ci.get_yes_no(prompt="Are you sure you want to fetch with no filters... this could take a long time!", default='no')=='no':
            print('Cancelling action')
            raise ci.COMMAND_ACTION_CANCEL

    docs = c.list_documents(query=doc_query)
    tbl = create_docs_table(c, docs)
    tbl.get_table_choice(required=False, commands=table_commands)
    print('\n')


def get_document_action(row, action_dict):
    # Uses Documents API/Get Documents
    # parms - q - search for string in name of document
    # filter - 0-9 for filter, 0 - my docs, 6- by owner, 7 by company, 9 by team
    # owner - owner id for filter 6 or 7, team if 9
    # offset - offset into the page (max 20)
    # limit - number of documents returned per page

    fname_filter_str = ci.get_string(prompt='Document string to search for', commands=std_commands)

    c = action_dict['client']
    filter_val, owner =  (7, action_dict['company'])    # filter by company
    doc_query = {'filter': filter_val, 'owner': owner}
    doc_query['q'] = fname_filter_str
    docs = c.list_documents(query=doc_query)
    tbl = create_docs_table(c, docs)

    if tbl.get_num_rows() == 1: # TODO - this doesn't work!
        choice = tbl.get_row(tag='1')
    else:
        choice = tbl.get_table_choice(prompt='choose a document', commands=table_commands)
    doc = choice.item_data['row']
    print(f'chose doc {doc.name} ({doc.did})')
    print('\n')


def list_teams_action(row, action_dict):
    c = action_dict['client']
    response = c.list_teams()

    rows = []

    for response_json in Pager(c, response):
        for item in response_json['items']:
            name = item['name']
            item_id = item['id']
            description = item['description']
            href = item['href']
            rows.append(ci.TableItem([name, item_id, description, href]))

    col_names = "Name Id Description HREF".split()
    ci.Table(rows, col_names=col_names, title='OnShape Teams', tag_str='#').show_table()
    print('\n')


def list_workspaces_action(row, action_dict):
    print('\n')

    c = action_dict['client']
    did = action_dict['did']
    response = c.get_workspaces(did)
    response_json = json.loads(response.text)

    rows = []
    for i, item in enumerate(response_json):
        read_only = item['isReadOnly']
        modified_at = item['modifiedAt']
        name = item['name']
        item_id = item['id']
        href = item['href']
        rows.append(ci.TableItem([name, item_id, read_only, modified_at, href[:50]]))

    col_names = "Name ItemId ReadOnly Modified HREF".split()
    ci.Table(rows, col_names=col_names, title='OnShape Workspaces', tag_str='#').show_table()
    print('\n')


def list_elements_action(row, action_dict):
    print('\n')

    c = action_dict['client']
    did = action_dict['did']
    wvm = action_dict['wvm']
    response = c.get_element_list(did, wvm, element_type=None, eid=None, with_thumbnails=False)
    response_json = json.loads(response.text)

    rows = []
    for i, item in enumerate(response_json):
        name = item['name']
        item_id = item['id']
        element_type = item['elementType']
        micro_version_id = item['microversionId']
        rows.append(ci.TableItem([name, item_id, element_type, micro_version_id]))

    col_names = "Name Id ElementType MicroversionId".split()
    ci.Table(rows, col_names=col_names, title='OnShape Elements', tag_str='#').show_table()
    print('\n')


def list_parts_action(row, action_dict):
    print('\n')

    c = action_dict['client']
    did = action_dict['did']
    wvm = action_dict['wvm']
    response = c.get_parts_list(did, wvm)
    response_json = json.loads(response.text)

    rows = []
    for i, item in enumerate(response_json):
        name = item['name']
        desc = item['description']
        state = item['state']
        element_id = item['elementId']
        part_num = item['partNumber']
        revision = item['revision']
        microversion_id = item['microversionId']
        is_hidden = item['isHidden']
        # is_mesh = item['isMesh']
        # lots more... appearance, bodyType, etc.

        # print('item {}: name={}, desc={}, state={},  elementID={}, partNumber={}, revision={}, microversionId={}, isHidden={}'.format(i,
        #         name, desc, state, element_id, part_num, revision, microversion_id, is_hidden))
        rows.append(ci.TableItem([name, desc, state, element_id, part_num, revision, microversion_id, is_hidden]))

    col_names = "Name Description State Id PartNum Revision, MicroversionId isHidden".split()
    ci.Table(rows, col_names=col_names, title='OnShape Parts', tag_str='#').show_table()
    print('\n')


def get_bom_action(row, action_dict):
    print('\n')

    c = action_dict['client']
    did = action_dict['did']
    wvm = action_dict['wvm']
    eid = action_dict['eid']

    types = ["flattened", "top-level", "multi-level"]
    type_vals = {"flattened": (False, False), "top-level": (True, False), "multi-level": (True, True)}
    prompt_str = f'BOM type ({", ".join(types)})'
    type_cleaner = ci.ChoiceCleaner(types)
    use_type = ci.get_string(prompt=prompt_str, cleaners=type_cleaner, default="flattened", commands=std_commands)
    indented, multi_level = type_vals[use_type]

    response = c.get_assembly_bom(did, wvm, eid, indented=indented, multi_level=multi_level, generate_if_absent=True)
    response_json = json.loads(response.text)


    try:
        status = response_json['status']
        if status == 404:
            msg = response_json['message']
            print("\nStatus 404 returned: {}\n".format(msg))
            return
    except:
        pass

    bom_table = response_json['bomTable']
    format_ver = bom_table['formatVersion']
    name = bom_table['name']
    bom_type = bom_table['type']
    created_at = bom_table['createdAt']
    doc_name = bom_table['bomSource']['document']['name']
    top_pn = bom_table['bomSource']['element']['partNumber']
    top_revision = bom_table['bomSource']['element']['revision']
    state = bom_table['bomSource']['element']['state']
    title = (f"\n\n{bom_type} {name} (format version {format_ver}) - {doc_name} ({state} {top_pn}{top_revision}) created_at: {created_at}")

    rows = []
    for idx,item in enumerate(bom_table['items']):
        item_num = item['item']
        qty = item['quantity']
        part_num = item['partNumber']
        desc = item['description']
        revision = item['revision']
        state = item['state']
        rows.append(ci.TableItem([qty, part_num, revision, state, desc], tag=item_num))

    col_names = "Qty PartNum Rev State Desc".split()
    ci.Table(rows, col_names=col_names, title=title, tag_str='ItemNums').show_table()
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
        # ci.TableItem('Set document name filter string', action=set_name_filter_action),
        ci.TableItem('List Documents', action=list_documents_action),
        ci.TableItem('Get did for a document', action=get_document_action),
        ci.TableItem('List Teams', action=list_teams_action),
        ci.TableItem('List Workspaces', action=list_workspaces_action),
        ci.TableItem('List Elements', action=list_elements_action),
        ci.TableItem('List Parts', action=list_parts_action),
        ci.TableItem('Get BOM', action=get_bom_action),
    ]
    print()
    menu = ci.Table(tis, add_exit=ci.TABLE_ADD_EXIT, show_cols=False, action_dict=ad)
    menu.run()

