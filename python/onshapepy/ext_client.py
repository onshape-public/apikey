
"""
Extended onshape api client
"""

import json
from urllib.parse import urlparse, parse_qs

from .client import Client


class Pager():
    """
    Iterator to return pages of data for OnShape calls that use a paging mechanism with next/prev page (Teams,
    Companies, GetDocuments, etc.).  This allow you to call the function like this:

    team_names = []
    first_response = c.list_teams()
    for response_json in onshape_pager(first_response):
        team_names += [item['name'] for item in response_json['items']]

    :param first_response: The response from running the query the first time (first page of results)
    :return: a json version of the result data for the next page of response data
    """
    def __init__(self, c, first_response, offset=0, limit=20):
        self.client = c
        self. first_response = True
        self.response = first_response
        self.cur_offset = offset
        self.limit = limit

    def __iter__(self):
        return self

    def __next__(self):
        response_json = json.loads(self.response.text)

        if self.first_response is True:
            self.first_response = False
            return response_json

        next_page = response_json['next']

        if next_page is None:   # Note: never hitting here... limit offsets back to 20
            raise StopIteration

        self.cur_offset += 20
        self.response = self.client.get_next_page(next_page)
        return json.loads(self.response.content)

    def get_offset(self):
        return self.cur_offset


class ClientExtended(Client):
    def __init__(self, stack='https://cad.onshape.com', creds='./creds.json', logging=True):
        super(ClientExtended, self).__init__(stack, creds, logging)

    # def get_next_page(self, next_page_url):
    def get_next_page(self, next_page_url, offset=None, limit=20):
        '''
        Get next page of results for a query. Some api calls (such as get teams) give a 'next' URL.

        Returns:
            - requests.Response: Onshape response data
        '''

        parsed_url = urlparse(next_page_url)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        use_query = {k: v[0] for k,v in query.items()}

        if offset is not None:
            use_query['offset'] = offset

        if limit is not None:
            use_query['limit'] = limit

        return self._api.request('get', path, use_query)


    def list_teams(self):
        '''
        Get list of teams for current user.

        Returns:
            - requests.Response: Onshape response data
        '''

        return self._api.request('get', '/api/teams')

    def get_element_list(self, did, wvm, element_type=None, eid=None, with_thumbnails=False):
        '''
        Gets workspaces list for specified document

        Args:
            - did (str): Document ID
            - wvm (str): workspace ID or version id or microversion id
            - element_type (str, optional): element type - 'PARTSTUDIO', 'ASSEMBLY'
            - eid (str, optional): return only elements with element id
            - with_thumbnail (bool, optional): include element thumbnail info

        Returns:
            - requests.Response: Onshape response data

        / documents / d /: did / [wvm] /:wvm / elements

        '''

        payload = {}

        if element_type:
            payload['elementType'] = element_type

        if eid:
            payload['elementType'] = eid

        if with_thumbnails:
            payload['elementType'] = with_thumbnails

        return self._api.request('get', '/api/documents/d/' + did + '/w/' + wvm + '/elements', payload)


    def get_workspaces(self, did, no_read_only=False):
        '''
        Gets workspaces list for specified document

        Args:
            - did (str): Document ID
            - no_read_only (bool): whether to show read only documents

        Returns:
            - requests.Response: Onshape response data

        https://cad.onshape.com/api/documents/d/0f9c85ccbf253b470b931452/workspaces?noreadonly=false
        '''

        payload = {
            'noreadonly': no_read_only
        }

        return self._api.request('get', '/api/documents/d/' + did + '/workspaces', payload)


    def get_assembly_bom(self, did, wvm, eid, indented=False, multi_level=False, generate_if_absent=True):
        '''
        Gets bom assoicated with an assembly

        Args:
            - did (str): Document ID
            - wvm (str): Workspace ID or version id or microversion id
            - eid (str): Element ID

            - indented (bool, optional): if True, returns an indented BOM
            - multi_level (bool, optional): if True, returns a multi-level BOM
            - generate_if_absent (bool, optional): if True, creates a BOM if not already one with the assembly

            bomColumnIDs not implemented yet

        Returns:
            - requests.Response: Onshape response data

        / assemblies / d / : did / [wvm] / :wvm / e / :eid / bom


        '''

        payload = {}
        payload['indented'] = indented
        payload['generateIfAbsent'] = generate_if_absent
        payload['multiLevel'] = multi_level

        route = '/api/assemblies/d/' + did + '/w/' + wvm + '/e/' + eid + '/bom'
        return self._api.request('get', route, payload)


    def get_parts_list(self, did, wvm):
        # parts
        '''
        Get list  of parts in a document

        Args:
            - did (str): Document ID
            - wvm (str): Workspace ID or version id or microversion id

        Returns:
            - requests.Response: Onshape response data

        / parts / d / : did / [wvm] / :wvm
        '''

        payload = {}
        route = '/api/parts/d/' + did + '/w/' + wvm
        return self._api.request('get', route, payload)
