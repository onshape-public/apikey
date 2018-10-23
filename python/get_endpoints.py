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

Len Wanger
Copyright Impossible Objects, 2018
"""

# import pprint

from onshapepy.ext_client import ClientExtended
from onshapepy.utils import convert_response


if __name__ == '__main__':
    stacks = {'cad': 'https://cad.onshape.com'}
    c = ClientExtended(stack=stacks['cad'], logging=False)

    print('Getting endpoints...\n')
    response = c.get_endpoints()
    endpoints = convert_response(response)

    print('printing some samples:\n')
    endpoint_18 = endpoints[18]['endpoints'][6]
    print(f'endpoint 18 is: {endpoint_18["title"]} ({endpoint_18["name"]} - {endpoint_18["description"]})\n')
    print(endpoint_18)
    # pprint.pprint(endpoint_18)
    print('\nget_parts parameter:\n')
    print(endpoint_18['parameter'])
    # pprint.pprint(endpoint_18['parameter'])
    print('\nget_parts success:\n')
    print(endpoint_18['success'])
    # pprint.pprint(endpoint_18['success'])
    print('\ndone')

