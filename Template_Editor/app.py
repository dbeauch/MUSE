import sys
import os
import datetime

import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from pages import home, cells, surfaces, materials, universes, fuel_assemblies, options
from template_handler_instance import template_handler_instance as template

# Sizes and Colors
navbar_width = '15vw'
console_height = '20vh'
console_banner_height = '0.1vh'
page_background = '#D3D3D3'
navbar_color = '#004a80'

# Only runs preprocessing operation for the main server process not for monitor process
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    sys.setrecursionlimit(8000)
    # file_to_read = input(f"Template to read ('' to run default template):")
    # if file_to_read == '':
    #     file_to_read = '../mcnp_templates/NBSR_HEU_720[236]/NBSR_HEU_720.i'
    # file_to_read = '../mcnp_templates/NNR/test.i'
    # file_to_read = '../mcnp_templates/NNR/burn_Box9_v02_SU_cycle8.i'
    file_to_read = '../mcnp_templates/NBSR_HEU_720[236]/NBSR_HEU_720.i'
    template.read_template(file_to_read)

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.LUX]
)

banner = html.Header(
    "Py2MCNP Editor",
    style={
        'backgroundColor': navbar_color,
        'color': 'white',
        'padding': '0px',
        'fontSize': 'calc((3vh + 1vw) / 2)',
        'font-weight': 'bold',
        'textAlign': 'center'
    }
)

navbar = html.Div([
    banner,

    dbc.Nav(
        [
            dbc.NavLink("Home", href="/", active="exact"),
            dbc.NavLink("Cell Cards", href="/cells", active="exact"),
            dbc.NavLink("Surface Cards", href="/surfaces", active="exact"),
            dbc.NavLink("Material Cards", href="/materials", active="exact"),
            dbc.NavLink("Universes", href="/universes", active="exact"),
            dbc.NavLink("Fuel Assembly", href="/assembly", active="exact"),
            dbc.NavLink("Option Cards", href="/options", active="exact"),
        ],
        vertical=True,
        pills=True,
        style={
            'margin': '1vh',
            'fontSize': 'calc((2vh + 1vw) / 2)',
        },
    ),

    html.A(
        html.Img(src='/assets/NCNR_nonlogo.png',
                 style={
                     'height': '15vh',
                     'width': navbar_width,
                     'position': 'fixed',
                     'bottom': 0,
                     'padding': '1vw',
                 }),
        href='https://www.nist.gov/ncnr',
        target='_blank',
    ),
], style={
    'backgroundColor': navbar_color,
    'width': navbar_width,
    'height': '100vh',
    'position': 'fixed'
})

console = html.Div([
    dbc.Row([
        dbc.Col(html.Div("Console", style={'textAlign': 'left'}), width=3),
        dbc.Col(dcc.Input(id='file_path', type='text', placeholder='File path',
                        style={'textAlign': 'left'}, debounce=True), width='auto', style={'textAlign': 'right'}),
        dbc.Col(html.Button('Print File', id='print_button', n_clicks=0), width='auto', style={'marginRight': '6vw'}),
        dbc.Col(dcc.Checklist(id='element_comments', options=['Element Comments'], value=['Element Comments']), width='auto',
                        style={'textAlign': 'left'}),
        dbc.Col(html.Div(html.Button(" ", id="console_toggler",
                        className='minimize-button')), width='auto', style={'marginLeft': 'auto'})
    ], align='center',
        style={
            'marginTop': 20,
            'backgroundColor': 'black',
            'color': 'white',
            'padding': console_banner_height,
            'fontSize': 'calc((2vh + 1vw) / 2)',
        },
        className='gx-0'),

    dbc.Collapse(
        html.Div(
            id='console_output',
            style={
                'backgroundColor': '#333333',
                'color': '#A9A9A9',
                'border': '1px solid black',
                'height': console_height,
                'overflow': 'scroll',
                'overflow-x': 'hidden',
            }, className='scrollbar-hidden'
        ),
        id='console_output_window',
        is_open=True
    )
],
    style={
        'marginLeft': navbar_width,
        'position': 'fixed',
        'bottom': 0,
        'width': f'calc(100% - {navbar_width})',
    }
)

content = html.Div(
    id="page_content",
    style={'marginLeft': navbar_width,
           'backgroundColor': page_background,
           'overflow': 'auto',
           'width': f'calc(100vw - {navbar_width})',
           'height': f'calc(100vh)',
           }
)

app.layout = html.Div([
    dcc.Location(id="url"),
    dbc.Row([
        dbc.Col(navbar, width='auto'),
        dbc.Col([
            content,
            html.Hr(),
            console
        ])
    ], justify="start", className="g-0")
], style={'overflow': 'hidden',  # prevent scrolling
          'height': '100vh',
          'width': '100vw',
          }
)


@app.callback(
    Output('page_content', 'children'),
    Output("console_output_window", "is_open", allow_duplicate=True),
    Input('url', 'pathname'),
    prevent_initial_call=True,
)
def display_page(pathname):
    if pathname == '/':
        return home.layout(page_background), False
    elif pathname == '/cells':
        return cells.layout(page_background), True
    elif pathname == '/surfaces':
        return surfaces.layout(page_background), True
    elif pathname == '/materials':
        return materials.layout(page_background), True
    elif pathname == '/universes':
        return universes.layout(page_background), True
    elif pathname == '/assembly':
        return fuel_assemblies.layout(page_background), True
    elif pathname == '/options':
        return options.layout(page_background), True
    else:
        return '404 Error: This page does not exist...YET!', False


@app.callback(
    Output('console_output_window', 'is_open', allow_duplicate=True),
    Input('console_toggler', 'n_clicks'),
    State('console_output_window', 'is_open'),
    prevent_initial_call=True,
)
def toggle_console(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output('console_output', 'children', allow_duplicate=True),
    Input('print_button', 'n_clicks'),
    State('file_path', 'value'),
    State('element_comments', 'value'),
    State('console_output', 'children'),
    prevent_initial_call=True
)
def print_button(print_clicked, file_path, element_comments, current_messages):
    if not current_messages:
        current_messages = []

    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    if button_id == 'print_button':
        element_comments = element_comments != []
        printed = template.print_file(file_path, element_comments)
        message = f'({timestamp})\tPrinted the file to: {printed}'
        current_messages.insert(0, html.P(message))
    return current_messages


if __name__ == '__main__':
    app.run_server(debug=True, threaded=True)
