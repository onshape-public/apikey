"""
part number fix utility

Uses the OnshapePy api to renumber parts imported from Solidworks.

OnShape does not set part numbers when importing files from Solidworks. Instead it sets the part
name to the file name. This utility looks for parts with no part number set and whose part name
matches a regular expression for a part number, and sets those parts part number to the part
name.

for more information about the API see:

        https://dev-portal.onshape.com/

    also useful to use the OnShape api-explorer app in OnShape

    this code uses  onshapepy to do authentication:

        https://github.com/lwanger/onshapepy


TODO:
    - Add: interactively get did, wfm, eid to get BOM, list elements and list parts... instead of hard-coded
    - read list of parts
    - figure out parts needing the new PN
    - set the part number from the name

Len Wanger
Copyright Impossible Objects, 2018

"""

import json
import re
import sys

from onshapepy.ext_client import ClientExtended
import cooked_input as ci

# DID, WVM and EID for Part numbering test example model
# https://cad.onshape.com/documents/d31dbb77700b695251588ff2/w/2c28968f83a53f9631d066fa/e/24f03732ef009163ad541a90
TEST_ASSEM_DOC_ID = 'd31dbb77700b695251588ff2'
MAIN_WORKSPACE = '2c28968f83a53f9631d066fa'
TEST_ASSEM_ELEM_ID = '24f03732ef009163ad541a90'

# Regular expression for default part numbering scheme (IOxxxx, where x is a digit)
DEFAULT_PN_RE = "^IO\d{4}$"

HELP_STR = """
OnShape Part Number fixing utility.

When importing from SolidWorks the part number for parts is not set. By default OnShape will use the file
name as the name of the part. This utility will set the part number to be the part name (assuming there is
no part number and the part name matches the part naming scheme for part numbers.)

To get the DID, WVM and EID, go to the model in Onshape and look at the URL. It should look something like:

    https://cad.onshape.com/documents/d31dbb77700b695251588ff2/w/2c28968f83a53f9631d066fa/e/24f03732ef009163ad541a90

    The string after 'documents' is the DID (e.g. d31dbb77700b695251588ff2)
    The string after 'w' is the WVM (e.g. 2c28968f83a53f9631d066fa)
    The string after 'e' is the EID (e.g. 24f03732ef009163ad541a90)
"""


def should_set_part_number(part, part_re) -> bool:
    part_pn = part['partNumber']
    part_name = part['name']
    if (part_pn is None or len(part_pn) == 0) and re.search(part_re, part_name):
        return True
    else:
        return False


if __name__ == '__main__':
    stacks = {'cad': 'https://cad.onshape.com'}
    c = ClientExtended(stack=stacks['cad'], logging=False)

    print(HELP_STR)

    did = ci.get_string(prompt="What DID (Onshape Document) to renumber", default=TEST_ASSEM_DOC_ID)
    wvm = ci.get_string(prompt="What WVM (Onshape Document) to renumber", default=MAIN_WORKSPACE)
    eid = ci.get_string(prompt="What EID (Onshape Document) to renumber", default=TEST_ASSEM_ELEM_ID)
    pn_re = ci.get_string(prompt="Regular expression for part names to set as part number", default=DEFAULT_PN_RE)

    # get part list
    print('\nParts identified to set:')
    response = c.get_parts_list(did, wvm)
    response_json = json.loads(response.text)
    filtered_parts = [part for part in response_json if should_set_part_number(part, pn_re)]

    fields = ['name', 'partNumber', 'revision', 'description', 'partId', 'elementId']
    field_names = ['Name', 'Part Number', 'Revision', 'Description', 'Part Id', 'Element Id']
    style = ci.TableStyle(show_border=True, hrules=ci.RULE_NONE)
    tbl = ci.create_table(filtered_parts, fields=fields, field_names=fields, gen_tags=None, item_data=None,
                          add_item_to_item_data=True, title=None, prompt=None, default_choice=None, default_str=None,
                          default_action='table_item', style=style)
    tbl.show_table()

    if ci.get_yes_no(prompt='Do you want to re-write the part numbers with the part names', default='no'):
        print('Re-writing part numbers\n')
        payload = [{'elementId': part['elementId'], 'partId': part['partId'], 'partNumber': part['name'] } for part in filtered_parts]
        result = c.set_parts_metadata(did, wvm, payload=payload)

        if not result.ok:
            part_names = ", ".join([part['name'] for part in filtered_parts])
            print('Error: Could not set part number for parts=[{}] (result code={}, err={})'.format(part_names,
                                                                            result.status_code, result.reason))

        # show results
        print('\nParts after setting part numbers:')
        filtered_part_set = {part['partId'] for part in filtered_parts}
        response = c.get_parts_list(did, wvm)
        response_json = json.loads(response.text)
        changed_parts = [part for part in response_json if part['partId'] in filtered_part_set]
        filtered_parts = [part for part in response_json if should_set_part_number(part, pn_re)]

        tbl = ci.create_table(response_json, fields=fields, field_names=fields, gen_tags=None, item_data=None,
                              add_item_to_item_data=True, title=None, prompt=None, default_choice=None,
                              default_str=None, default_action='table_item', style=style)
        tbl.show_table()
        sys.exit(0)
    else:
        print('Exiting without re-writing part numbers\n')
        sys.exit(0)
