"""
get endpoints utility

Uses the OnshapePy api to get information about the Onshape api

Returns a list of endpoints, each a dictionary with:

    'Group' - str
    'GroupTitle' - str
    'Endpoints' - list of:
        'type' - type of endpoint (post, get, delete, etc.)
        'url' - URL for the endpoint
        'title' - title for the endpoint
        'name' - name for the endpoint
        'description' - description for the endpoint
        'group' - group for the endpoint (matches parent group)
        'version' - version # (str) for the endpoint
        'permission' - list of permissions (each a dictionary with 'name')
        'parameter' - dictionary of parameters. Each with 'fields' being a dict with 'PathParam' and sometime 'QueryParam'
                e.g {'group': 'PathParam', 'type': 'String', 'optional': False, 'field': 'pid', 'description': 'Purchase id'}
        'success' = dict with 'fields'. Fields is a list of response items which are dicts
            e.g. {'group': 'Response', 'type': 'Object[]', 'optional': False, 'field': 'parts', 'description': 'Parts list'}
        'error' - dictionary with 'fields'. e.g. <class 'list'>: [{'group': 'ReplacedBy', 'optional': False, 'field': 'Accounts-cancelPurchaseNew', 'description': ''}]
        'groupTitle' - groupTitle for the endpoint (matches parent groupTitle)
        'header' -  dictionary with 'fields'. Fields is a dict with 'Header', which is a list of dicts
            e.g. {'group': 'Header', 'type': 'String', 'optional': False, 'field': 'Content-Type', 'defaultValue': 'application/json', 'description': 'Content type'}


        For example - the get parts endpoint is at: endpoints[18]['endpoints'][6]

    for more information about the API see:
        https://dev-portal.onshape.com/

    also useful to use the OnShape api-explorer app in OnShape

    this code uses  onshapepy to do authentication:
        https://github.com/lwanger/onshapepy

TODO:
    - export HTML of endpoints? Export as PDF from ReportLab

Len Wanger
Copyright Impossible Objects, 2018
"""

import pprint

from onshapepy.ext_client import ClientExtended
from onshapepy.utils import convert_response

import cooked_input as ci



def show_individual_endpoint_action(row, action_dict):
    """
    row.item_data['item'] is list of: type, url, title, name, description, group, version, permission (list), success (dict),
        groupTitle, header (dict), parameter (dict)
    """
    ri = row.item_data["item"]
    # print('-'*60)
    print(f'\nname: {ri["name"]}\ttitle: {ri["title"]}')
    print(f'description: {ri["description"]}')
    print(f'url: {ri["url"]}')
    print(f'type: {ri["type"]}\tversion: {ri["version"]}')
    permissions = ','.join([ str(i) for i in ri["permission"] ])
    print(f'permissions: {permissions}')

    if 'success' in ri:
        print()
        response = ri['success']['fields']['Response']
        fields = 'field group type optional description'.split()
        field_names = [f.capitalize() for f in fields]
        tbl = ci.create_table(items=response, fields=fields, field_names=field_names, gen_tags=False, add_exit=False, title='Response:')
        tbl.show_table()

    if 'success' in ri:
        header = ri['header']['fields']['Header']
        fields = 'field group type optional defaultValue description'.split()
        field_names = [f.capitalize() for f in fields]
        tbl = ci.create_table(items=header, fields=fields, field_names=field_names, gen_tags=False, add_exit=False,
                              title='\nHeader:')
        tbl.show_table()

    if 'parameter' in ri:
        if 'PathParam' in ri['parameter']['fields']:
            path_param = ri['parameter']['fields']['PathParam']
            fields = 'field group type optional description'.split()
            field_names = [f.capitalize() for f in fields]
            tbl = ci.create_table(items=path_param, fields=fields, field_names=field_names, gen_tags=False, add_exit=False,
                                  title='PathParam:')
            tbl.show_table()

        if 'QueryParam' in ri['parameter']['fields']:
            query_param = ri['parameter']['fields']['QueryParam']
            fields = 'field group type optional defaultValue description'.split()
            field_names = [f.capitalize() for f in fields]
            tbl = ci.create_table(items=query_param, fields=fields, field_names=field_names, gen_tags=False, add_exit=False,
                                  title='QueryParam:')
            tbl.show_table()

    print('\n\n\n')


def show_group_endpoints_action(row, action_dict):
    """
    row.item_data['item'] has: 'group', 'groupTitle', 'endpoints'
    row.item_data['item']['endpoints'] is list of: type, url, title, name, description, group, version, permission (list), success (dict),
        groupTitle, header (dict), parameter (dict)
    """
    print(f'Received row for endpoint: {row.item_data["item"]["groupTitle"]}')

    style = ci.TableStyle(rows_per_page=99)
    items = row.item_data['item']['endpoints']
    fields = 'title name type url'.split()
    field_names = [f.capitalize() for f in fields]
    tbl = ci.create_table(items=items, fields=fields, field_names=field_names, style=style, gen_tags=True,
                          default_action=show_individual_endpoint_action,
                          add_item_to_item_data=True, add_exit=ci.TABLE_ADD_RETURN, prompt='Chooose an endpoint')
    tbl.run()


if __name__ == '__main__':
    stacks = {'cad': 'https://cad.onshape.com'}
    c = ClientExtended(stack=stacks['cad'], logging=False)

    print('Getting endpoints...\n')
    response = c.get_endpoints()
    endpoints = convert_response(response)

    # list endpoints as a table
    style = ci.TableStyle(rows_per_page=99)
    items = endpoints
    fields = 'group groupTitle'.split()
    field_names = [f.capitalize() for f in fields]
    tbl = ci.create_table(items=items, fields=fields, field_names=field_names, style=style, gen_tags=True,
                          default_action=show_group_endpoints_action, add_item_to_item_data=True, add_exit=True,
                          prompt='Chooose an endpoint')
    tbl.run()

