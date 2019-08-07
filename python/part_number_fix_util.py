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

Text-based progress bars shown if tqdm is installed
Len Wanger
Copyright Impossible Objects, 2018
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

# DID, WVM and EID for Part numbering test example model
# DEFAULT_URL="https://cad.onshape.com/documents/d31dbb77700b695251588ff2/w/2c28968f83a53f9631d066fa/e/24f03732ef009163ad541a90"

# DID, WVM and EID for Part numbering test example model (with no part studio)
DEFAULT_URL="https://cad.onshape.com/documents/380c689c8f030496317ad561/w/00debd62a8452d0523ac7d03/e/0545c3d2e4c8885e9ca603f6"

# 698 re-write test
# DEFAULT_URL="https://cad.onshape.com/documents/fe9493f7f250db296dc27535/w/a224fcfe4bc446366ed2d270/e/115ef5787ce2f4aa63465d9d"

# 698 (production)
# DEFAULT_URL="https://cad.onshape.com/documents/3d51153e276619e952362208/w/542e0a82b6fb6c53aa2d5bb3/e/c541ad347688e4da725f3c4c"

# Regular expression for default part numbering scheme (IOxxxx, where x is a digit)
DEFAULT_PN_RE = "^IO\d{4}$"   # IO style part numbers
# DEFAULT_PN_RE = "^LW-\d{3}$"    # LW-123 style part numbers

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


def should_set_part_number(part_pn, part_name, part_re) -> bool:
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


def get_url_and_pn_re(default=DEFAULT_URL, default_re=DEFAULT_PN_RE, use_gui=True):
    if not use_gui:   # use cooked_input
        url = ci.get_string(prompt="What Onshape document URL do want to renumber", default=default)
        pn_re = ci.get_string(prompt="Regular expression for part names to set as part number", default=DEFAULT_PN_RE)

        did, wvm, eid = parse_url(url, w_required=True)
        return did, wvm, eid, pn_re
    else:   # use tkinter
        # TODO -- need to clean up -- add instructions, tables, etc.
        window = tk.Tk()
        window.title("Onshape Part Re-numbering Utility")
        window.geometry('950x150')

        url_str_var = tk.StringVar()
        url_str_var.set(default)
        re_str_var = tk.StringVar()
        re_str_var.set(default_re)

        lbl = tk.Label(window, text="Onshape model document URL:")
        lbl.grid(column=0, row=0)

        txt = tk.Entry(window, textvariable=url_str_var, width=120)
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
        did, wvm, eid = parse_url(url, w_required=True)
        return did, wvm, eid, pn_re


def rewrite_part(part):
    part_id = part['itemSource']['partId']
    wvm_type = part['itemSource']['wvmType']
    part_wvm = part['itemSource']['wvmId']
    part_did = part['itemSource']['documentId']
    part_eid = part['itemSource']['elementId']
    payload = {'partNumber': part['name']}

    result = c.set_part_metadata(part_did, part_wvm, part_eid, part_id, payload, wvm_type)
    if not result.ok:
        print('Error: Could not set part number for parts={} (result code={}, err={})'.format(part["name"],
                                                                                              result.status_code,
                                                                                              result.reason))
        return False

    return True


def rewrite_part_numbers(did, parts):
    """
    Sets the part number to the part name for a list of parts

    :param did:
    :param parts: list of part studio parts from the assembly bom endpoint
    :return: True if rewrote parts successfully

    assumes part is from the bom table (i.e. has itemSource)
    """
    print(f'Re-writing part numbers for did={did}\n')

    if parts is not None:
        if tqdm_installed is True:
            with tqdm(total=len(parts)) as pbar:
                for i, part in enumerate(parts):
                    pbar.set_description(f'Rewriting part {part["name"]}')
                    result = rewrite_part(part)
                    pbar.update(i)

                    if result is False:
                        return False
        else:
            for part in parts:
                print('Rewriting part number for part {}'.format(part["name"]))
                result = rewrite_part(part)

                if result is False:
                    return False

    return True


def get_bom(c, did, wvm, eid, pn_re):
    print('\nFetching part information from Onshape...')
    start_time = datetime.datetime.now()
    # bom = c.get_assembly_bom(did, wvm, eid)
    bom = c.get_assembly_bom(did, wvm, eid, multi_level=False)

    if bom.ok is False:
        print(f'\n\nError: Could not fetch the BOM (status code={bom.status_code}, reason={bom.reason})\n\n')
        sys.exit(1)

    bom_json = json.loads(bom.text)
    end_time = datetime.datetime.now()
    time_delta = end_time - start_time

    return bom_json, time_delta


def show_pre_table(fields):
    style = ci.TableStyle(show_border=True, hrules=ci.RULE_NONE, rows_per_page=None)
    tbl = ci.create_table(filtered_parts, fields=fields, field_names=fields, gen_tags=None, item_data=None,
                          add_item_to_item_data=True, title=None, prompt=None, default_choice=None, default_str=None,
                          default_action='table_item', style=style)
    print('\nParts identified to set:')
    tbl.show_table()


def rewrite_parts_and_show_post_table(fields):
    if ci.get_yes_no(prompt='Do you want to re-write the part numbers with the part names', default='no') == 'yes':
        rewrite_part_numbers(did, filtered_parts)

        # show results
        print('\nParts after setting part numbers:')
        filtered_part_set = {part['name'] for part in filtered_parts}

        bom = c.get_assembly_bom(did, wvm, eid)
        bom_json = json.loads(bom.text)
        changed_parts = [part for part in bom_json['bomTable']['items'] if part['name'] in filtered_part_set]
        for part in changed_parts:
            part['partId'] = part['itemSource']['partId']
            part['elementId'] = part['itemSource']['elementId']

        style = ci.TableStyle(show_border=True, hrules=ci.RULE_NONE, rows_per_page=None)
        tbl = ci.create_table(changed_parts, fields=fields, field_names=fields, gen_tags=None, item_data=None,
                              add_item_to_item_data=True, title=None, prompt=None, default_choice=None,
                              default_str=None, default_action='table_item', style=style)
        tbl.show_table()
        sys.exit(0)
    else:
        print('Exiting without re-writing part numbers\n')
        sys.exit(0)


if __name__ == '__main__':
    print('WARNING: Does not find parts without part names that are assemblies')

    stacks = {'cad': 'https://cad.onshape.com'}
    c = ClientExtended(stack=stacks['cad'], logging=False)

    print(HELP_STR)
    did, wvm, eid, pn_re = get_url_and_pn_re(default=DEFAULT_URL)

    filtered_parts = None
    linked_docs = None

    bom_json, time_delta = get_bom(c, did, wvm, eid, pn_re)

    filtered_parts = []
    for part in bom_json['bomTable']['items']:
        if should_set_part_number(part['partNumber'], part['name'], pn_re):
            filtered_parts.append(part)

    if len(filtered_parts) == 0:
        print(f'\n\nNo parts matching the regular expression without a part number found (re={pn_re}).\n\n')
        sys.exit(0)

    print(f'Onshape call time = {str(time_delta)} seconds')
    fields = ['name', 'partNumber', 'revision', 'description', 'partId', 'elementId']
    show_pre_table(fields)

    rewrite_parts_and_show_post_table(fields)
