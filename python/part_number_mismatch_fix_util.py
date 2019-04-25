"""
part number mismatch fix utility

Uses the OnshapePy api to check for parts with mismatched part number and name (i.e. check that they weren't updated)

I have seen a number of errors where the engineer updates the part number in only one place. Thus utility checks for
that.

for more information about the API see:
        https://dev-portal.onshape.com/

    also useful to use the OnShape api-explorer app in OnShape

    this code uses  onshapepy to do authentication:
        https://github.com/lwanger/onshapepy

Text-based progress bars shown if tqdm is installed
Len Wanger
Copyright Impossible Objects, 2019
"""

import datetime
import json
import re
import sys
import tkinter as tk

from onshapepy.ext_client import ClientExtended
from onshapepy.utils import parse_url
import cooked_input as ci

# If TQDM is installed then import it to display progress bars
try:
    from tqdm import tqdm
    tqdm_installed = True
except (ImportError):
    tqdm_installed = False

from part_number_fix_util import DEFAULT_PN_RE, get_bom, get_url_and_pn_re, rewrite_part_numbers
from part_number_fix_util import show_pre_table, rewrite_parts_and_show_post_table


# DID, WVM and EID for Part numbering test example model
# DEFAULT_URL="https://cad.onshape.com/documents/d31dbb77700b695251588ff2/w/2c28968f83a53f9631d066fa/e/24f03732ef009163ad541a90"

# DID, WVM and EID for Part numbering test example model (with no part studio)
DEFAULT_URL="https://cad.onshape.com/documents/380c689c8f030496317ad561/w/00debd62a8452d0523ac7d03/e/0545c3d2e4c8885e9ca603f6"

# 698 re-write test
# DEFAULT_URL="https://cad.onshape.com/documents/fe9493f7f250db296dc27535/w/a224fcfe4bc446366ed2d270/e/115ef5787ce2f4aa63465d9d"

# 698 (production)
# DEFAULT_URL="https://cad.onshape.com/documents/3d51153e276619e952362208/w/542e0a82b6fb6c53aa2d5bb3/e/c541ad347688e4da725f3c4c"

HELP_STR = """
OnShape Part Number mismatch part number fixing utility.

This utility checks for parts where the part number and part name look like valid part numbers but don't match.

To get the DID, WVM and EID, go to the model in Onshape and look at the URL. It should look something like:

    https://cad.onshape.com/documents/d31dbb77700b695251588ff2/w/2c28968f83a53f9631d066fa/e/24f03732ef009163ad541a90

    The string after 'documents' is the DID (e.g. d31dbb77700b695251588ff2)
    The string after 'w' is the WVM (e.g. 2c28968f83a53f9631d066fa)
    The string after 'e' is the EID (e.g. 24f03732ef009163ad541a90)
"""


def should_set_part_number(part_pn: str, part_name: str, part_re: str) -> bool:
    if part_pn is not None and part_name is not None and part_pn != part_name \
        and re.search(part_re, part_pn) and re.search(part_re, part_name):
        return True
    else:
        return False


if __name__ == '__main__':
    filtered_parts = []
    linked_docs = None

    stacks = {'cad': 'https://cad.onshape.com'}
    c = ClientExtended(stack=stacks['cad'], logging=False)

    print(HELP_STR)
    did, wvm, eid, pn_re = get_url_and_pn_re(default=DEFAULT_URL, default_re=DEFAULT_PN_RE, use_gui=True)
    bom_json, time_delta = get_bom(c, did, wvm, eid, pn_re)

    ###

    filtered_parts = []
    for part in bom_json['bomTable']['items']:
        if should_set_part_number(part['partNumber'], part['name'], pn_re):
            filtered_parts.append(part)

    if len(filtered_parts) == 0:
        print(f'\n\nNo parts matching the regular expression with mismatch part numbers found (re={pn_re}).\n\n')
        sys.exit(0)

    print(f'Onshape call time = {str(time_delta)} seconds')
    fields = ['name', 'partNumber', 'revision', 'description', 'partId', 'elementId']
    show_pre_table(fields)

    # For now only show mismatched parts (don't fix) -- can uncomment to change that
    # rewrite_parts_and_show_post_table(fields)
