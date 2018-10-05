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

import datetime
import json
import re
import sys
import tkinter as tk

from onshapepy.ext_client import ClientExtended
import cooked_input as ci

# DID, WVM and EID for Part numbering test example model
# DEFAULT_URL="https://cad.onshape.com/documents/d31dbb77700b695251588ff2/w/2c28968f83a53f9631d066fa/e/24f03732ef009163ad541a90"

# DID, WVM and EID for Part numbering test example model (with no part studio)
DEFAULT_URL="https://cad.onshape.com/documents/380c689c8f030496317ad561/w/00debd62a8452d0523ac7d03/e/0545c3d2e4c8885e9ca603f6"

# 698 re-write test
# DEFAULT_URL="https://cad.onshape.com/documents/fe9493f7f250db296dc27535/w/a224fcfe4bc446366ed2d270/e/115ef5787ce2f4aa63465d9d"

# 698 (production)
# DEFAULT_URL="https://cad.onshape.com/documents/3d51153e276619e952362208/w/542e0a82b6fb6c53aa2d5bb3/e/c541ad347688e4da725f3c4c"

# Regular expression for default part numbering scheme (IOxxxx, where x is a digit)
# DEFAULT_PN_RE = "^IO\d{4}$"   # IO style part numbers
DEFAULT_PN_RE = "^LW-\d{3}$"    # LW-123 style part numbers

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

# which method to use to get and set the parts numbers
USE_GET_PARTS = 1
USE_ASMBLY_DEFN = 2
USE_ASMBLY_BOM = 3
# GET_PARTS_METHOD = USE_GET_PARTS  # TODO - doesn't set part numbers if not in part studio
# GET_PARTS_METHOD = USE_ASMBLY_DEFN    # TODO - crashes
GET_PARTS_METHOD = USE_ASMBLY_BOM   # TODO - HTTP 400 error (bad request) on setting part numbers

SET_PART = 1
SET_PARTS = 1
SET_PARTS_METHOD = SET_PARTS


def should_set_part_number(part, part_re) -> bool:
    part_pn = part['partNumber']
    part_name = part['name']
    if (part_pn is None or len(part_pn) == 0) and re.search(part_re, part_name):
        return True
    else:
        return False


def set_part_info_from_bom(part_from_bom):
    return {
        'name': part_from_bom['name'],
        'partNumber': part_from_bom['partNumber'],
        'revision': part_from_bom['revision'],
        'description': part_from_bom['description'],
        'partId': part_from_bom['itemSource']['partId'],
        'elementId': part_from_bom['itemSource']['elementId']
    }


def parse_url(url):
    """
    parse an Onshape document URL into the components: did, wvm and eid.

    :param url: URL to parse
    :return: tuple of (did, wvm, eid)

    URL looks like: https://cad.onshape.com/documents/d31dbb77700b695251588ff2/w/2c28968f83a53f9631d066fa/e/24f03732ef009163ad541a90

    returns (d31dbb77700b695251588ff2, 2c28968f83a53f9631d066fa, 24f03732ef009163ad541a90)
    """
    split_list = url.split('/')

    did = wvm = eid = None

    if split_list[3] == 'documents':
        did = split_list[4]
    if split_list[5] == 'w':
        wvm = split_list[6]
    if split_list[7] == 'e':
        eid = split_list[8]

    return did, wvm, eid


def get_url_and_pn_re(default=DEFAULT_URL, default_re=DEFAULT_PN_RE):
    if True:   # use cooked_input
        url = ci.get_string(prompt="What Onshape document URL do want to renumber", default=default)
        pn_re = ci.get_string(prompt="Regular expression for part names to set as part number", default=DEFAULT_PN_RE)

        did, wvm, eid = parse_url(url)
        return did, wvm, eid, pn_re
    else:   # use tkinter
        # TODO -- need to clean up -- add instructions, tables, etc.
        window = tk.Tk()
        window.title("Onshape Part Re-numbering Utility")
        window.geometry('500x150')

        url_str_var = tk.StringVar()
        url_str_var.set(default)
        re_str_var = tk.StringVar()
        re_str_var.set(default_re)

        lbl = tk.Label(window, text="Onshape model document URL:")
        lbl.grid(column=0, row=0)

        txt = tk.Entry(window, textvariable=url_str_var, width=40)
        txt.grid(column=1, row=0)

        lbl = tk.Label(window, text="Part number regular expression:")
        lbl.grid(column=0, row=1)

        txt = tk.Entry(window, textvariable=re_str_var, width=40)
        txt.grid(column=1, row=1)

        lbl = tk.Label(window, text="")
        lbl.grid(column=0, row=2)

        btn = tk.Button(window, text="Submit", command=window.quit)
        btn.grid(column=1, row=3)

        txt.focus()
        window.mainloop()
        url = url_str_var.get()
        pn_re = re_str_var.get()
        window.destroy()
        did, wvm, eid = parse_url(url)
        return did, wvm, eid, pn_re


if __name__ == '__main__':
    stacks = {'cad': 'https://cad.onshape.com'}
    c = ClientExtended(stack=stacks['cad'], logging=False)

    print(HELP_STR)
    did, wvm, eid, pn_re = get_url_and_pn_re(default=DEFAULT_URL)

    # get part list
    print('\nFetching part information from Onshape...')
    start_time = datetime.datetime.now()

    if GET_PARTS_METHOD==USE_GET_PARTS:   # Use get_parts_list (returning an empty list of parts if no part studio)
        response = c.get_parts_list(did, wvm)
        end_time = datetime.datetime.now()
        response_json = json.loads(response.text)
        filtered_parts = [part for part in response_json if should_set_part_number(part, pn_re)]
    elif GET_PARTS_METHOD==USE_ASMBLY_DEFN:
        response = c.get_assembly_definition(did, wvm, eid) # use assempbly definiton - slow and doesn't provide part name or number
        end_time = datetime.datetime.now()
        response_json = json.loads(response.text)
        # TODO - this crashes as there is no 'partNumber' or 'name' returned on parts
        filtered_parts = [part for part in response_json['parts'] if should_set_part_number(part, pn_re)]
    else:   # USE_ASMBLY_BOM - use assembly bom - very slow but works
        response = c.get_assembly_bom(did, wvm, eid)
        end_time = datetime.datetime.now()
        response_json = json.loads(response.text)
        filtered_parts = [set_part_info_from_bom(part) for part in response_json['bomTable']['items'] if should_set_part_number(part, pn_re)]

    time_delta = end_time - start_time
    print(f'Onshape call time = {str(time_delta)} seconds')
    fields = ['name', 'partNumber', 'revision', 'description', 'partId', 'elementId']
    field_names = ['Name', 'Part Number', 'Revision', 'Description', 'Part Id', 'Element Id']
    style = ci.TableStyle(show_border=True, hrules=ci.RULE_NONE)
    tbl = ci.create_table(filtered_parts, fields=fields, field_names=fields, gen_tags=None, item_data=None,
                          add_item_to_item_data=True, title=None, prompt=None, default_choice=None, default_str=None,
                          default_action='table_item', style=style)
    print('\nParts identified to set:')
    tbl.show_table()

    if ci.get_yes_no(prompt='Do you want to re-write the part numbers with the part names', default='no') == 'yes':
        print('Re-writing part numbers\n')

        if SET_PARTS_METHOD==SET_PARTS:  # set_parts_metadata (one call)
            payload = [{'elementId': part['elementId'], 'partId': part['partId'], 'partNumber': part['name'] } for part in filtered_parts]
            result = c.set_parts_metadata(did, wvm, payload=payload)
        else:   # SET_PART -- set_part_metadata (one call per part)
            for part in filtered_parts:
                payload = { 'partNumber': part['name'] }
                result = c.set_part_metadata(did, wvm, part['elementId'], part['partId'], payload=payload)
                if not result.ok:
                    break

        if not result.ok:
            part_names = ", ".join([part['name'] for part in filtered_parts])
            print('Error: Could not set part number for parts=[{}] (result code={}, err={})'.format(part_names,
                                                                            result.status_code, result.reason))
            sys.exit(1)

        # show results
        print('\nParts after setting part numbers:')
        filtered_part_set = {part['partId'] for part in filtered_parts}

        if GET_PARTS_METHOD==USE_GET_PARTS:
            response = c.get_parts_list(did, wvm)
            response_json = json.loads(response.text)
            changed_parts = [part for part in response_json if part['partId'] in filtered_part_set]
        elif GET_PARTS_METHOD==USE_ASMBLY_DEFN:
            response = c.get_assembly_definition(did, wvm, eid)
            response_json = json.loads(response.text)
            changed_parts = [part for part in response_json['parts'] if part['partId'] in part['partId'] in filtered_parts]
        else: # USE_ASMBLY_BOM
            response = c.get_assembly_bom(did, wvm, eid)
            response_json = json.loads(response.text)
            changed_parts = [part for part in response_json['bomTable']['items'] if part['partId'] in part['partId'] in filtered_parts]

        tbl = ci.create_table(changed_parts, fields=fields, field_names=fields, gen_tags=None, item_data=None,
                              add_item_to_item_data=True, title=None, prompt=None, default_choice=None,
                              default_str=None, default_action='table_item', style=style)
        tbl.show_table()
        sys.exit(0)
    else:
        print('Exiting without re-writing part numbers\n')
        sys.exit(0)
