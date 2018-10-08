'''
apikey
======

Demonstrates usage of API keys for the Onshape REST API
'''

__copyright__ = 'Copyright (c) 2016 Onshape, Inc.'
__license__ = 'All rights reserved.'
__title__ = 'apikey'
__all__ = ['onshape', 'client', 'ext_client', 'utils']


from .ext_client import Client, ClientExtended, Pager
from .utils import parse_url

__version__ = "0.0.1"
