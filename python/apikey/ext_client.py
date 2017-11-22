
"""
Extended onshape api client
"""

from .client import Client

class ClientExtended(Client):
    def __init__(self, stack='https://cad.onshape.com', logging=True):
        super(ClientExtended, self).__init__(stack, logging)

    def get_next_page(self, next_page_url):
        '''
        Get next page of results for a query. Some api calls (such as get teams) give a 'next' URL.

        Returns:
            - requests.Response: Onshape response data
        '''

        return self._api.request('get', next_page_url)

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

