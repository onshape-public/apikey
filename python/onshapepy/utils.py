'''
utils
=====

Handy functions for API key sample app
'''

import logging
from logging.config import dictConfig
import json


__all__ = [
    'log'
]


def log(msg, level=0):
    '''
    Logs a message to the console, with optional level paramater

    Args:
        - msg (str): message to send to console
        - level (int): log level; 0 for info, 1 for error (default = 0)
    '''

    red = '\033[91m'
    endc = '\033[0m'

    # configure the logging module
    cfg = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'stdout': {
                'format': '[%(levelname)s]: %(asctime)s - %(message)s',
                'datefmt': '%x %X'
            },
            'stderr': {
                'format': red + '[%(levelname)s]: %(asctime)s - %(message)s' + endc,
                'datefmt': '%x %X'
            }
        },
        'handlers': {
            'stdout': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'stdout'
            },
            'stderr': {
                'class': 'logging.StreamHandler',
                'level': 'ERROR',
                'formatter': 'stderr'
            }
        },
        'loggers': {
            'info': {
                'handlers': ['stdout'],
                'level': 'INFO',
                'propagate': True
            },
            'error': {
                'handlers': ['stderr'],
                'level': 'ERROR',
                'propagate': False
            }
        }
    }

    dictConfig(cfg)

    lg = 'info' if level == 0 else 'error'
    lvl = 20 if level == 0 else 40

    logger = logging.getLogger(lg)
    logger.log(lvl, msg)


def parse_url(url, w_required=False):
    """
    parse an Onshape document URL into the components: did, wvm and eid.

    :param url: URL to parse
    :return: tuple of (did, wvm, eid)

    URL looks like: https://cad.onshape.com/documents/d31dbb77700b695251588ff2/w/2c28968f83a53f9631d066fa/e/24f03732ef009163ad541a90

    returns (d31dbb77700b695251588ff2, 2c28968f83a53f9631d066fa, 24f03732ef009163ad541a90)
    """
    split_list = url.split('/')

    did = wvm = eid = None

    try:
        if split_list[3] == 'documents':
            did = split_list[4]
        else:
            raise RuntimeError("Bad URL -- no documents specified")

        if (w_required and split_list[5] == 'w'):
            wvm = split_list[6]
        elif split_list[5] in { 'v', 'm' }:
            wvm = split_list[6]
        else:
            if w_required is true:
                raise RuntimeError("Bad URL -- no w specified")
            else:
                raise RuntimeError("Bad URL -- no wvm specified")

        if split_list[7] == 'e':
            eid = split_list[8]
        else:
            raise RuntimeError("Bad URL -- no eid specified")
    except (IndexError):
        pass    # fail on first index error and keep items set to None from there on

    return did, wvm, eid


def convert_response(response):
    """
    Convert Onshape api response data to a Python data structure (i.e. json conversion usually to a dictionary)
    :param response:
    :return:
    """
    return json.loads(response.text)
