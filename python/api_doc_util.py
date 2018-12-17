"""
Onshape API Documentation utility

Uses the OnshapePy api to create documentation for the Onshape api

Returns a list of endpoints, each a dictionary with:

    for more information about the API see:
        https://dev-portal.onshape.com/

    also useful to use the OnShape api-explorer app in OnShape

    this code uses  onshapepy to do authentication:
        https://github.com/lwanger/onshapepy

TODO:
    - Export as PDF from ReportLab
    - use text-align:left and vertical align:top in style tag..., not align="left"
    - Add search bar to docs...
    - Add toggle to toc to show deprecated


Len Wanger
Copyright Impossible Objects, 2018
"""

import datetime
import json
import os
from pathlib import Path

from onshapepy.ext_client import ClientExtended
from onshapepy.utils import convert_response

import cooked_input as ci

ONSHAPEPY_URL = 'https://github.com/lwanger/onshapepy'
TOC_FILENAME = '_toc.html'
CACHED_ENDPOINT_FILE = 'endpoints_cache.json'
FETCH_BY_DEFAULT = 'no'

TITLE_BLOCK= """
<!DOCTYPE html>
<html lang="en">
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js"></script>
  <script> function loadUrl(url) {{document.getElementById("content-frame").src = url;}}</script>

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
        .anyClass {{
            height:600px;
            overflow-y: scroll;
        }}
    </style>
	<title>{title}</title>
</head>
<body>
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


def wrap_in_aref(url, text, target="_top"):
    return f'<a href="{url}" target="{target}">{text}</a>'


def bootstrap_radio_button(f, text, active=''):
    f.write(f'<label class="btn btn-secondary {active}>\n')
    f.write(f'<input type="radio" name="options" id="{text}" autocomplete="off" checked>{text}\n')
    f.write('</label>\n')


def bootstrap_button(f, text, url=None, active=''):
    f.write('<label class="btn btn btn-sm">\n')
    f.write(f'<button target="content-frame" class="btn btn {active}" role="button" onclick="loadUrl(\'{url}\')">{text}</button>\n')
    f.write('</label>\n')


def make_html_table_rows(f, vals, fields):
    rows = []
    rows.append([wrap_in_th(s.capitalize()) for s in fields])
    for row in vals:
        response_row_vals = [row[v] if v in row else '--' for v in fields]
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
                rows = make_html_table_rows(f, error[1], fields)
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

    print('\n\n\n')


def show_group_endpoints_action(row, action_dict):
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


def create_toc(f, endpoints, created):
    title_block = TITLE_BLOCK.format(title='Onshape REST API Documentation', name='toc')
    f.write(title_block)

    # write jumbotron div
    f.write('<div class ="jumbotron text-center">\n')
    f.write('<h1> Onshape REST API Documentation</h1>\n')
    f.write(f'<p> Created on {str(created)} using {wrap_in_aref(ONSHAPEPY_URL, "onshapepy")} </p>\n')
    f.write('</div>\n')

    # write toc button group
    f.write('<div id="top-frame" class="container-fluid" style="margin-top:30px">\n')
    f.write('<div class="row">\n')
    f.write('<div class="col-sm-4 anyClass">\n')
    f.write('<h2>Table of Contents</h2>\n')
    f.write('<div class="btn-group-vertical btn-group-toggle" id="toc" name="toc" data-toggle="buttons">\n')

    active = 'active'
    for group in endpoints:
        bootstrap_radio_button(f, group["groupTitle"], active='disabled')

        for endpt in group['endpoints']:
            deprecated, replaced_by = is_deprecated(endpt)
            row_str = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + endpt["name"]
            if deprecated:
                row_str += f' ({wrap_in_bold("deprecated")})'

            url = endpt["name"] + '.html'
            bootstrap_button(f, row_str, url=url, active=active)
            if len(active) > 0:
                first_url = url
            else:
                active = ''

    # end toc button group and add iframe
    f.write('</div>\n</div>\n')
    f.write('<div class="col-sm-8">\n')
    f.write(f'<iframe id="content-frame" name="content-frame" data-target="toc" src="{first_url}" width="100%" style="height:100%; border:none"></iframe>\n')
    f.write('</div>\n')
    f.write('</div> <! row -->\n')
    f.write('</div> <! top-frame -->\n')

    # end page
    end_block = END_BLOCK.format()
    f.write(end_block)


def create_html_action(row, action_dict):
    endpoints = action_dict['endpoints']
    created = action_dict['created']
    export_dir = Path.home().joinpath('export')
    dir_validator = ci.SimpleValidator(os.path.isdir)

    try:
        export_dir = ci.get_string(prompt='directory for html export: ', validators=dir_validator, default=str(export_dir))
    except (ci.ValidationError):
        if ci.get_yes_no(prompt='Should I create the directory', default='no') == 'yes':
            os.mkdir(export_dir)
        else:
            print('Unable to export html')
            return

    toc_filename = Path(export_dir, TOC_FILENAME)

    with open(toc_filename, mode='w', encoding='utf-8') as f:
        create_toc(f, endpoints, created)

    for group in endpoints:
        for endpt in group['endpoints']:
            filename = Path(export_dir, endpt["name"] + '.html')
            with open(filename, mode='w', encoding='utf-8') as f:
                export_individual_endpoint_as_html(f, endpt)

    print('\n\n')


if __name__ == '__main__':
    if ci.get_yes_no(prompt='Fetch API endpoint information from Onshape (vs. use cached version)', default='no') == 'yes':
        stacks = {'cad': 'https://cad.onshape.com'}
        c = ClientExtended(stack=stacks['cad'], logging=False)

        print('Getting api endpoints from Onshape...\n')
        response = c.get_endpoints()
        endpoints = convert_response(response)
        created = datetime.datetime.now()

        if ci.get_yes_no(prompt='Save API endpoint information to file', default=FETCH_BY_DEFAULT) == 'yes':
            cache_content = (created.timestamp(), endpoints)
            with open(CACHED_ENDPOINT_FILE, 'w') as f:
                f.write( json.dumps(cache_content) )
    else:
        print('Using saved api endpoints...\n')

        with open(CACHED_ENDPOINT_FILE, 'r') as f:
            content_str = f.read()
            cache_content = json.loads(content_str)
            created = datetime.date.fromtimestamp(cache_content[0])
            endpoints = cache_content[1]

    style = ci.TableStyle(rows_per_page=99, show_cols=False, show_border=False)
    item_data = {'endpoints': endpoints, 'style': style }
    action_dict = {'endpoints': endpoints, 'created': created, 'style': style }

    main_menu_items = [
        ci.TableItem(col_values=["Get info for an individual endpoint"], action=get_endpoint_groups_action, item_data=item_data),
        ci.TableItem(col_values=["Export api documentation as html"], action=create_html_action, item_data=item_data),
    ]
    main_menu = ci.Table(rows=main_menu_items, prompt='Choose a menu item', style=style, add_exit=True, action_dict=action_dict)
    main_menu.run()
