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
    - export HTML of endpoints -- also make TOC page and page for each group. Add hyperlinks too
    - Export as PDF from ReportLab
    - use text-align:left and vertical align:top in style tag..., not align="left"
    - use bootstrap formatting

Len Wanger
Copyright Impossible Objects, 2018
"""

import json

from onshapepy.ext_client import ClientExtended
from onshapepy.utils import convert_response

import cooked_input as ci

CACHED_ENDPOINT_FILE = 'endpoints_cache.json'
FETCH_BY_DEFAULT = 'no'

TITLE_BLOCK= """
<html>
<head>
    <style>
        #p2 {{
            margin-left: 5%;
        }}
        #p3 {{
            margin-left: 10%;
        }}
        #t2 {{
            margin-left: 5%;
        }}
        #t3 {{
            margin-left: 10%;
        }}
    </style>
	<title>{title}</title>
</head>
<body>

<h1>{title}: {name}</h1>
"""

END_BLOCK="""
</body>
</html>
"""

def write_html_table(f, row_values, border=1, width=None, css_id=None):
    """
    write html for a table

    :param f: file to write to
    :param row_values: list of tuples, each tuple is the values for a row. each cell value is the html for the
                        cell (incl. <td> tags)
    :param border: an integer for the border size
    :param width: an integer of the percentage width of the page for the table
    :return: None
    """
    f.write('<p>')
    args = ''
    if css_id is not None:
        args += f', id="{css_id}"'
    if width is not None:
        args += f', width="{width}"'

    f.write(f'<table border="{border}"{args}>')
    for row in row_values:
        f.write('<tr>\n')
        for cell in row:
            f.write(cell + '\n')
        f.write('</tr>\n')
    f.write('</table></p>\n')

def wrap_in_paragraph(s, css_id=None):
    # return the string (s) wrapped in html tags to make it a paragraph
    args = ''
    if css_id is not None:
        args += f'id="{css_id}"'
    return f'<p {args}>\n{s}\n</p>\n'

def wrap_in_bold(s):
    # return the string (s) wrapped in html tags to make it bold
    return f'<b>{s}</b>'

def wrap_in_td(s, align="left"):
    # return the string (s) wrapped in html tags for a table data item
    return f'<td align="{align}">{s}</td>'

def wrap_in_th(s, align="left"):
    # return the string (s) wrapped in html tags for a table data item
    return f'<th align="{align}">{s}</th>'

# class html_paragraph(object):
#     def __init__(self, f, css_id=None):
#         self.f = f
#         self.css_id = css_id
#
#     def __enter__(self):
#         args = ''
#         if self.css_id is not None:
#             args += f' id="{self.css_id}";'
#         self.f.write(f'<p {args}>\n')
#
#     def __exit__(self, exc_type, exc_val, exc_tb):
#         self.f.write(f'</p>\n')


# def make_html_table_rows(f, vals, fields, title):
def make_html_table_rows(f, vals, fields):
    # f.write(wrap_in_bold(title))
    rows = []
    rows.append([wrap_in_th(s.capitalize()) for s in fields])
    for row in vals:
        response_row_vals = [row[v] for v in fields]
        rows.append([wrap_in_td(s) for s in response_row_vals])
    return rows


def is_deprecated(ri):
    if 'permission' in ri and 'error' in ri and 'fields' in ri['error']:
        for p in ri['permission']:
            if p['name'].endswith('deprecated'):
                replaced_by = None
                for e in ri['error']['fields']['ReplacedBy']:
                    if e['group'] == 'ReplacedBy':
                        replaced_by =  e['field']
                        break
                return True, replaced_by

    return False, None


def export_individual_endpoint_as_html(f, ri):
    """
    Export an individual end point as an html page

    :param f: file pointer to write the html to
    :param ri: the endpoint item
    :return: None
    """

    deprecated, replaced_by = is_deprecated(ri)
    permissions = ', '.join([i['name'] for i in ri['permission']])
    title_block = TITLE_BLOCK.format(**ri)
    f.write(title_block)

    # write top-level infomation
    vals = 'name title description url type permission version'.split()
    rows = []

    if deprecated:
        rows.append((wrap_in_bold('deprecated - replaced by:'), replaced_by))
        rows.append((wrap_in_td(''), wrap_in_td('')))  # blank row...
    for val in vals:
        l_cell_val = wrap_in_th( wrap_in_bold(f'{val}:') )
        if val == 'permission':
            r_cell_val = wrap_in_td(permissions)
        else:
            r_cell_val = wrap_in_td(f'{ri[val]}')
        rows.append((l_cell_val, r_cell_val))

    write_html_table(f, rows, border=0, width="75%")

    # write response
    if 'success' in ri:
        f.write(wrap_in_paragraph(wrap_in_bold('Success Entries:'), css_id="p2"))

        for field in  ri['success']['fields'].items():
            f.write(wrap_in_paragraph(wrap_in_bold(field[0]+':'), css_id="p3"))
            fields = 'field type optional description'.split()
            rows = make_html_table_rows(f, field[1], fields)
            write_html_table(f, rows, border=1, width="75%", css_id="t3")
    else:
        f.write(wrap_in_paragraph('No response block'))

    # write header
    if 'header' in ri:
        vals = ri['header']['fields']['Header']
        fields = 'field type optional defaultValue description'.split()
        f.write(wrap_in_paragraph(wrap_in_bold('Header:'), css_id="p2"))
        rows = make_html_table_rows(f, vals, fields)
        write_html_table(f, rows, border=1, width="75%", css_id="t2")
    else:
        f.write(wrap_in_paragraph('No header block'))

    # write parameter block
    if 'parameter' in ri:
        f.write(wrap_in_paragraph(wrap_in_bold('Parameter:'), css_id="p2"))

        if 'Body' in ri['parameter']['fields']:
            vals = ri['parameter']['fields']['Body']
            fields = 'field type optional description'.split()
            title = 'Body:'
            f.write(wrap_in_paragraph(wrap_in_bold(title), css_id="p3"))
            rows = make_html_table_rows(f, vals, fields)
            write_html_table(f, rows, border=1, width="75%", css_id="t3")

        if 'PathParam' in ri['parameter']['fields']:
            vals = ri['parameter']['fields']['PathParam']
            fields = 'field type optional description'.split()
            title = 'PathParam:'
            f.write(wrap_in_paragraph(wrap_in_bold(title), css_id="p3"))
            rows = make_html_table_rows(f, vals, fields)
            write_html_table(f, rows, border=1, width="75%", css_id="t3")

        if 'QueryParam' in ri['parameter']['fields']:
            vals = ri['parameter']['fields']['QueryParam']
            fields = 'field type optional defaultValue description'.split()
            title = 'QueryParam:'
            f.write(wrap_in_paragraph(wrap_in_bold(title), css_id="p3"))
            rows = make_html_table_rows(f, vals, fields)
            write_html_table(f, rows, border=1, width="75%", css_id="t3")

        if 'error' in ri:
            f.write(wrap_in_paragraph(wrap_in_bold('Error:'), css_id="p2"))
            errors = ri['error']['fields']
            fields = 'field optional description'.split()

            for error in errors.items():
                title = error[0]
                f.write(wrap_in_paragraph(wrap_in_bold(title), css_id="p3"))
                rows = make_html_table_rows(f, error[1], fields, title)
                write_html_table(f, rows, border=1, width="75%", css_id="t3")

    end_block = END_BLOCK.format(ri=ri)
    f.write(end_block)


def show_individual_endpoint_action(row, action_dict):
    """
    row.item_data['item'] is list of: type, url, title, name, description, group, version, permission (list), success (dict),
        groupTitle, header (dict), parameter (dict)
    """
    ri = row.item_data["item"]
    deprecated, replaced_by = is_deprecated(ri)

    print(f'\nname: {ri["name"]}\ttitle: {ri["title"]}')
    print(f'description: {ri["description"]}')
    print(f'url: {ri["url"]}')
    print(f'type: {ri["type"]}\tversion: {ri["version"]}')
    if deprecated:
        replaced_by_str = 'True' + ' - replaced by: ' + replaced_by
        print(f'deprecated: {replaced_by_str}')

    permissions = ', '.join([i['name'] for i in ri['permission']])
    print(f'permissions: {permissions}')

    if 'success' in ri:
        # Response is a dict with multiple items. Each looks like Response
        print('\nSuccess Entries:\n')
        for field in  ri['success']['fields'].items():
            fields = 'field type optional description'.split()
            field_names = [f.capitalize() for f in fields]
            tbl = ci.create_table(items=field[1], fields=fields, field_names=field_names, gen_tags=False, add_exit=False, title=f'{field[0]}:')
            tbl.show_table()

    if 'header' in ri:
        header = ri['header']['fields']['Header']
        fields = 'field type optional defaultValue description'.split()
        field_names = [f.capitalize() for f in fields]
        tbl = ci.create_table(items=header, fields=fields, field_names=field_names, gen_tags=False, add_exit=False,
                              title='\nHeader:')
        tbl.show_table()

    if 'parameter' in ri:
        # add body - list of: type optional field description
        if 'Body' in ri['parameter']['fields']:
            body = ri['parameter']['fields']['Body']
            fields = 'field type optional description'.split()
            field_names = [f.capitalize() for f in fields]
            tbl = ci.create_table(items=body, fields=fields, field_names=field_names, gen_tags=False, add_exit=False, title='PathParam:')
            tbl.show_table()

        if 'PathParam' in ri['parameter']['fields']:
            path_param = ri['parameter']['fields']['PathParam']
            fields = 'field type optional description'.split()
            field_names = [f.capitalize() for f in fields]
            tbl = ci.create_table(items=path_param, fields=fields, field_names=field_names, gen_tags=False, add_exit=False,
                                  title='PathParam:')
            tbl.show_table()

        if 'QueryParam' in ri['parameter']['fields']:
            query_param = ri['parameter']['fields']['QueryParam']
            fields = 'field type optional defaultValue description'.split()
            field_names = [f.capitalize() for f in fields]
            tbl = ci.create_table(items=query_param, fields=fields, field_names=field_names, gen_tags=False, add_exit=False,
                                  title='QueryParam:')
            tbl.show_table()

        if 'error' in ri:
            # 'error' - dict with 'fields' each with group, optional, field, desciption
            errors = ri['error']['fields']
            for error in errors.items():
                fields = 'field optional description'.split()
                field_names = [f.capitalize() for f in fields]
                tbl = ci.create_table(items=error[1], fields=fields, field_names=field_names, gen_tags=False, add_exit=False, title=error[0])
                tbl.show_table()

    print('\n')
    if ci.get_yes_no(prompt='Export to html?', default='no') == 'yes':
        filename = ci.get_string(prompt='Export filename', default=ri["name"]+'.html')
        with open(filename, mode='w', encoding='utf-8') as f:
            export_individual_endpoint_as_html(f, ri)

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


def get_endpoint_groups_action(row, action_dict):
    # list endpoints as a table
    fields = 'group groupTitle'.split()
    field_names = [f.capitalize() for f in fields]
    tbl = ci.create_table(items=action_dict['endpoints'], fields=fields, field_names=field_names, style=action_dict['style'],
                          gen_tags=True, default_action=show_group_endpoints_action, add_item_to_item_data=True, add_exit=True,
                          prompt='Chooose an endpoint')
    tbl.run()


def create_toc_action(row, action_dict):
    endpoints = action_dict['endpoints']
    for group in endpoints:
        print(f'{group["groupTitle"]}')
        for endpt in group['endpoints']:
            # fields = 'title name type url description'.split()
            print(f'\t{endpt["name"]}')

    if ci.get_yes_no(prompt='Export as html?', default='no') == 'yes':
        filename = ci.get_string(prompt='Export filename', default='endpoints_toc.html')
        print(f'Exporting as html to file {filename}')

        with open(filename, mode='w', encoding='utf-8') as f:
            title_block = TITLE_BLOCK.format(title='Table of Contents', name='toc')
            f.write(title_block)

            rows = []
            for group in endpoints:
                row_str = wrap_in_bold( group["groupTitle"] )
                row_str = wrap_in_td(row_str)
                rows.append( (row_str,) )

                for endpt in group['endpoints']:
                    deprecated, replaced_by = is_deprecated(endpt)

                    row_str = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + endpt["name"]
                    if deprecated:
                        row_str += f' ({wrap_in_bold("deprecated")} - replaced by {replaced_by})'
                    row_str = wrap_in_td(row_str)
                    rows.append( (row_str,) )

            write_html_table(f, rows, border=0, width="75%")

            # end page
            end_block = END_BLOCK.format()
            f.write(end_block)


    print('\n\n')


if __name__ == '__main__':
    if ci.get_yes_no(prompt='Fetch API endpoint information from Onshape (vs. use cached version)', default='no') == 'yes':
        stacks = {'cad': 'https://cad.onshape.com'}
        c = ClientExtended(stack=stacks['cad'], logging=False)

        print('Getting api endpoints from Onshape...\n')
        response = c.get_endpoints()
        endpoints = convert_response(response)

        if ci.get_yes_no(prompt='Save API endpoint information to file', default=FETCH_BY_DEFAULT) == 'yes':
            with open(CACHED_ENDPOINT_FILE, 'w') as f:
                f.write( json.dumps(endpoints) )
    else:
        print('Using saved api endpoints...\n')

        with open(CACHED_ENDPOINT_FILE, 'r') as f:
            endpoints_str = f.read()
            endpoints = json.loads(endpoints_str)

    style = ci.TableStyle(rows_per_page=99, show_cols=False, show_border=False)
    item_data = {'endpoints': endpoints, 'style': style }
    action_dict = {'endpoints': endpoints, 'style': style }

    main_menu_items = [
        ci.TableItem(col_values=["Get info for an individual endpoint"], action=get_endpoint_groups_action, item_data=item_data),
        ci.TableItem(col_values=["Create table of contents"], action=create_toc_action, item_data=item_data),
    ]
    main_menu = ci.Table(rows=main_menu_items, prompt='Choose a menu item', style=style, add_exit=True, action_dict=action_dict)
    main_menu.run()
